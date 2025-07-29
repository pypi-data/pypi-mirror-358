from uuid import uuid4
from typing import List, Optional
from abc import ABC, abstractmethod
from ..loggers.conversation_logger import ConversationLogger
from ..helpers.config.config_helper import ConfigHelper
from ..parser.output_parser_tool import OutputParserTool
from ..tools.content_safety_checker import ContentSafetyChecker

from ...utilities.helpers.env_helper import EnvHelper
from mgmt_config import logger
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT

class OrchestratorBase(ABC):
    """
    OrchestratorBase is an abstract base class that provides a framework for handling user messages,
    logging interactions, and ensuring content safety. It initializes configuration, message ID,
    token counters, and various utility tools required for orchestrating conversations.
    """

    def __init__(self) -> None:
        """
        Initializes the OrchestratorBase with configuration settings, a unique message ID,
        token counters, and instances of ConversationLogger, ContentSafetyChecker, and OutputParserTool.
        """
        super().__init__()
        self.config = ConfigHelper.get_active_config_or_default()
        self.message_id = str(uuid4())
        self.tokens = {"prompt": 0, "completion": 0, "total": 0}
        logger.debug(f"New message id: {self.message_id} with tokens {self.tokens}")
        if str(self.config.logging.log_user_interactions).lower() == "true":
            self.conversation_logger: ConversationLogger = ConversationLogger()
        self.content_safety_checker = ContentSafetyChecker()
        self.output_parser = OutputParserTool()

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def log_tokens(self, prompt_tokens: int, completion_tokens: int) -> None:
        """
        Logs the number of tokens used in the prompt and completion phases of a conversation.

        Args:
            prompt_tokens (int): The number of tokens used in the prompt.
            completion_tokens (int): The number of tokens used in the completion.
        """
        self.tokens["prompt"] += prompt_tokens
        self.tokens["completion"] += completion_tokens
        self.tokens["total"] += prompt_tokens + completion_tokens

    @abstractmethod
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    async def orchestrate(
        self,
        user_message: str,
        chat_history: List[dict],
        request_headers,
        **kwargs: dict,
    ) -> list[dict]:
        """
        Abstract method to orchestrate the conversation. This method must be implemented by subclasses.

        Args:
            user_message (str): The message from the user.
            chat_history (List[dict]): The history of the chat as a list of dictionaries.
            **kwargs (dict): Additional keyword arguments.

        Returns:
            list[dict]: The response as a list of dictionaries.
        """
        pass

    def call_content_safety_input(self, user_message: str) -> Optional[list[dict]]:
        """
        Validates the user message for harmful content and replaces it if necessary.

        Args:
            user_message (str): The message from the user.

        Returns:
            Optional[list[dict]]: Parsed messages if harmful content is detected, otherwise None.
        """
        logger.debug("Calling content safety with question")
        filtered_user_message = (
            self.content_safety_checker.validate_input_and_replace_if_harmful(
                user_message
            )
        )
        if user_message != filtered_user_message:
            logger.warning("Content safety detected harmful content in question")
            messages = self.output_parser.parse(
                question=user_message, answer=filtered_user_message
            )
            return messages

        return None

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def call_content_safety_output(
        self, user_message: str, answer: str
    ) -> Optional[list[dict]]:
        """
        Validates the output message for harmful content and replaces it if necessary.

        Args:
            user_message (str): The message from the user.
            answer (str): The response to the user message.

        Returns:
            Optional[list[dict]]: Parsed messages if harmful content is detected, otherwise None.
        """
        logger.debug("Calling content safety with answer")
        filtered_answer = (
            self.content_safety_checker.validate_output_and_replace_if_harmful(answer)
        )
        if answer != filtered_answer:
            logger.warning("Content safety detected harmful content in answer")
            messages = self.output_parser.parse(
                question=user_message, answer=filtered_answer
            )
            return messages

        return None

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    async def handle_message(
        self,
        user_message: str,
        chat_history: List[dict],
        conversation_id: Optional[str],
        request_headers,
        **kwargs: Optional[dict],
    ) -> dict:
        """
        Handles the user message by orchestrating the conversation, logging token usage,
        and logging user interactions if configured.

        Args:
            user_message (str): The message from the user.
            chat_history (List[dict]): The history of the chat as a list of dictionaries.
            conversation_id (Optional[str]): The ID of the conversation.
            **kwargs (Optional[dict]): Additional keyword arguments.

        Returns:
            dict: The result of the orchestration as a dictionary.
        """
        result = await self.orchestrate(
            user_message, chat_history, request_headers, **kwargs
        )
        if str(self.config.logging.log_tokens).lower() == "true":
            custom_dimensions = {
                "conversation_id": conversation_id,
                "message_id": self.message_id,
                "prompt_tokens": self.tokens["prompt"],
                "completion_tokens": self.tokens["completion"],
                "total_tokens": self.tokens["total"],
            }
            logger.info("Token Consumption", extra=custom_dimensions)
        if str(self.config.logging.log_user_interactions).lower() == "true":
            self.conversation_logger.log(
                messages=[
                    {
                        "role": "user",
                        "content": user_message,
                        "conversation_id": conversation_id,
                    }
                ]
                + result
            )
        return result
