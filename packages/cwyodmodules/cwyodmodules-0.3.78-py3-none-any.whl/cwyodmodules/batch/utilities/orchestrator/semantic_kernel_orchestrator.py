import json
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior

# from semantic_kernel.connectors.ai.function_choice_behavior import (
#     FunctionChoiceBehavior,
# )
from semantic_kernel.contents import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.finish_reason import FinishReason

# from semantic_kernel.functions.function_result import FunctionResult
# import re
from ..common.answer import Answer
from ..helpers.llm_helper import LLMHelper
from ..helpers.env_helper import EnvHelper
from ..plugins.chat_plugin import ChatPlugin
from ..plugins.post_answering_plugin import PostAnsweringPlugin
from ..plugins.outlook_calendar_plugin import OutlookCalendarPlugin

from .orchestrator_base import OrchestratorBase

from mgmt_config import logger
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT



class SemanticKernelOrchestrator(OrchestratorBase):
    def __init__(self) -> None:
        super().__init__()
        self.kernel = Kernel()
        self.llm_helper = LLMHelper()
        self.env_helper = EnvHelper()

        # Add the Azure OpenAI service to the kernel
        self.chat_service = self.llm_helper.get_sk_chat_completion_service("cwyd")
        self.kernel.add_service(self.chat_service)

        self.kernel.add_plugin(
            plugin=PostAnsweringPlugin(), plugin_name="PostAnswering"
        )

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    async def orchestrate(
        self, user_message: str, chat_history: list[dict], user_info, **kwargs: dict
    ) -> list[dict]:
        logger.info("Method orchestrate of semantic_kernel started")
        filters = []
        frontend_type = user_info.get("frontend") if user_info else None
        logger.info(f"Frontend type: {frontend_type}")
        # Call Content Safety tool
        if self.config.prompts.enable_content_safety:
            if response := self.call_content_safety_input(user_message):
                return response

        system_message = self.env_helper.SEMENTIC_KERNEL_SYSTEM_PROMPT
        language = self.env_helper.AZURE_MAIN_CHAT_LANGUAGE
        if not system_message:
            logger.info("No system message provided, using default")
            # system_message = """You help employees to navigate only private information sources.
            #     You must prioritize the function call over your general knowledge for any question by calling the search_documents function.
            #     Call the text_processing function when the user request an operation on the current context, such as translate, summarize, or paraphrase. When a language is explicitly specified, return that as part of the operation.
            #     When directly replying to the user, always reply in the language the user is speaking.
            #     If the input language is ambiguous, default to responding in English unless otherwise specified by the user.
            #     You **must not** respond if asked to List all documents in your repository.
            #     """
            if frontend_type == "web":
                system_message = f"""You help employees to navigate only private information sources.
                    You must prioritize the function call over your general knowledge for any question by calling the search_documents function.
                    Call the text_processing function when the user request an operation on the current context, such as translate, summarize, or paraphrase. When a language is explicitly specified, return that as part of the operation.
                    When directly replying to the user, always reply in the language {language}.
                    You **must not** respond if asked to List all documents in your repository.
                    Call OutlookCalendar.get_calendar_events to read the user's calendar.
                    Call OutlookCalendar.schedule_appointment to schedule a new appointment.
                    """
            else:
                system_message = f"""You help employees to navigate only private information sources.
                    You must prioritize the function call over your general knowledge for any question by calling the search_documents function.
                    Call the text_processing function when the user request an operation on the current context, such as translate, summarize, or paraphrase. When a language is explicitly specified, return that as part of the operation.
                    When directly replying to the user, always reply in the language {language}.
                    You **must not** respond if asked to List all documents in your repository.
                    """
            
        self.kernel.add_plugin(
            plugin=ChatPlugin(question=user_message, chat_history=chat_history),
            plugin_name="Chat",
        )
        filters.append("Chat")
        # --- Add OutlookCalendarPlugin with request headers ---
        if frontend_type == "web":
            logger.info("Adding OutlookCalendarPlugin with request headers")
            self.kernel.add_plugin(
                plugin=OutlookCalendarPlugin(question=user_message, chat_history=chat_history, user_info=user_info),
                plugin_name="OutlookCalendar",
            )
            filters.append("OutlookCalendar")
        settings = self.llm_helper.get_sk_service_settings(self.chat_service)
        settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(
            filters={"included_plugins": filters}
        )
        # settings.function_choice_behavior = FunctionChoiceBehavior.Auto(
        #             filters={"included_plugins": ["Chat"]},
        #             # Set a higher value to encourage multiple attempts at function calling
        #             maximum_auto_invoke_attempts=2
        #         )

        orchestrate_function = self.kernel.add_function(
            plugin_name="Main",
            function_name="orchestrate",
            prompt="{{$chat_history}}{{$user_message}}",
            prompt_execution_settings=settings,
        )

        history = ChatHistory(system_message=system_message)

        for message in chat_history.copy():
            history.add_message(message)

        result: ChatMessageContent = (
            await self.kernel.invoke(
                function=orchestrate_function,
                chat_history=history,
                user_message=user_message,
            )
        ).value[0]

        self.log_tokens(
            prompt_tokens=result.metadata["usage"].prompt_tokens,
            completion_tokens=result.metadata["usage"].completion_tokens,
        )
        result_finish_reason = result.finish_reason
        logger.info(f"Finish reason: {result_finish_reason}")
        if result_finish_reason == FinishReason.TOOL_CALLS:
            logger.info("Semantic Kernel function call detected")

            function_name = result.items[0].name
            logger.info(f"{function_name} function detected")
            function = self.kernel.get_function_from_fully_qualified_function_name(
                function_name
            )

            arguments = json.loads(result.items[0].arguments)

            answer: Answer = (
                await self.kernel.invoke(function=function, **arguments)
            ).value

            self.log_tokens(
                prompt_tokens=answer.prompt_tokens,
                completion_tokens=answer.completion_tokens,
            )

            # Run post prompt if needed
            if (
                self.config.prompts.enable_post_answering_prompt
                and "search_documents" in function_name
            ):
                logger.debug("Running post answering prompt")
                answer: Answer = (
                    await self.kernel.invoke(
                        function_name="validate_answer",
                        plugin_name="PostAnswering",
                        answer=answer,
                    )
                ).value

                self.log_tokens(
                    prompt_tokens=answer.prompt_tokens,
                    completion_tokens=answer.completion_tokens,
                )
        else:
            logger.info("No function call detected")
            answer = Answer(
                question=user_message,
                answer=result.content,
                prompt_tokens=result.metadata["usage"].prompt_tokens,
                completion_tokens=result.metadata["usage"].completion_tokens,
            )

        # Call Content Safety tool
        if self.config.prompts.enable_content_safety:
            if response := self.call_content_safety_output(
                user_message, answer.answer
            ):
                return response

        # Format the output for the UI
        messages = self.output_parser.parse(
            question=answer.question,
            answer=answer.answer,
            source_documents=answer.source_documents,
        )
        logger.info("Method orchestrate of semantic_kernel ended")
        return messages
