from typing import List
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.chains.llm import LLMChain
from langchain_community.callbacks import get_openai_callback

from .orchestrator_base import OrchestratorBase
from ..helpers.llm_helper import LLMHelper
from ..tools.post_prompt_tool import PostPromptTool
from ..tools.question_answer_tool import QuestionAnswerTool
from ..tools.text_processing_tool import TextProcessingTool
from ..common.answer import Answer

from ...utilities.helpers.env_helper import EnvHelper
from mgmt_config import logger
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT


class LangChainAgent(OrchestratorBase):
    """
    LangChainAgent is responsible for orchestrating the interaction between various tools and the user.
    It extends the OrchestratorBase class and utilizes tools for question answering and text processing.
    """

    def __init__(self) -> None:
        """
        Initializes the LangChainAgent with necessary tools and helper classes.
        """
        super().__init__()
        self.question_answer_tool = QuestionAnswerTool()
        self.text_processing_tool = TextProcessingTool()
        self.llm_helper = LLMHelper()

        self.tools = [
            Tool(
                name="Question Answering",
                func=self.run_tool,
                description="Useful for when you need to answer questions about anything. Input should be a fully formed question. Do not call the tool for text processing operations like translate, summarize, make concise.",
                return_direct=True,
            ),
            Tool(
                name="Text Processing",
                func=self.run_text_processing_tool,
                description="""Useful for when you need to process text like translate to Italian, summarize, make concise, in Spanish.
                Always start the input with a proper text operation with language if mentioned and then the full text to process.
                e.g. translate to Spanish: <text to translate>""",
                return_direct=True,
            ),
        ]

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def run_tool(self, user_message: str) -> str:
        """
        Executes the question answering tool with the provided user message.

        Args:
            user_message (str): The message from the user containing the question.

        Returns:
            str: The answer in JSON format.
        """
        answer = self.question_answer_tool.answer_question(
            user_message, chat_history=[]
        )
        return answer.to_json()

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def run_text_processing_tool(self, user_message: str) -> str:
        """
        Executes the text processing tool with the provided user message.

        Args:
            user_message (str): The message from the user containing the text to process.

        Returns:
            str: The processed text in JSON format.
        """
        answer = self.text_processing_tool.answer_question(
            user_message, chat_history=[]
        )
        return answer.to_json()

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    async def orchestrate(
        self, user_message: str, chat_history: List[dict], **kwargs: dict
    ) -> list[dict]:
        """
        Orchestrates the interaction between the user and the tools, managing the conversation flow.

        Args:
            user_message (str): The message from the user.
            chat_history (List[dict]): The history of the chat conversation.
            **kwargs (dict): Additional keyword arguments.

        Returns:
            list[dict]: The formatted messages for the UI.
        """
        logger.info("Method orchestrate of lang_chain_agent started")

        # Call Content Safety tool
        if self.config.prompts.enable_content_safety:
            if response := self.call_content_safety_input(user_message):
                return response

        # Call function to determine route
        prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
        suffix = """Begin!"

        {chat_history}
        Question: {input}
        {agent_scratchpad}"""
        prompt = ZeroShotAgent.create_prompt(
            self.tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )

        # Create conversation memory
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        for message in chat_history:
            if message["role"] == "user":
                memory.chat_memory.add_user_message(message["content"])
            elif message["role"] == "assistant":
                memory.chat_memory.add_ai_message(message["content"])

        # Define Agent and Agent Chain
        llm_chain = LLMChain(llm=self.llm_helper.get_llm(), prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=self.tools, verbose=True)
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=self.tools, verbose=True, memory=memory
        )

        # Run Agent Chain
        with get_openai_callback() as cb:
            answer = agent_chain.run(user_message)
            self.log_tokens(
                prompt_tokens=cb.prompt_tokens,
                completion_tokens=cb.completion_tokens,
            )

        try:
            answer = Answer.from_json(answer)
        except Exception:
            answer = Answer(question=user_message, answer=answer)

        if self.config.prompts.enable_post_answering_prompt:
            logger.debug("Running post answering prompt")
            post_prompt_tool = PostPromptTool()
            answer = post_prompt_tool.validate_answer(answer)
            self.log_tokens(
                prompt_tokens=answer.prompt_tokens,
                completion_tokens=answer.completion_tokens,
            )

        # Call Content Safety tool
        if self.config.prompts.enable_content_safety:
            if response := self.call_content_safety_output(user_message, answer.answer):
                return response

        # Format the output for the UI
        messages = self.output_parser.parse(
            question=answer.question,
            answer=answer.answer,
            source_documents=answer.source_documents,
        )
        logger.info("Method orchestrate of lang_chain_agent ended")
        return messages
