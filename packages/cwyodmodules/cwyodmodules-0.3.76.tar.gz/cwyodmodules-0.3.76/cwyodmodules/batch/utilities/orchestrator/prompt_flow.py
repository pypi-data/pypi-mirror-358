from typing import List
import json
import tempfile

from .orchestrator_base import OrchestratorBase
from ..common.answer import Answer
from ..common.source_document import SourceDocument
from ..helpers.llm_helper import LLMHelper
from ..helpers.env_helper import EnvHelper

from mgmt_config import logger
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT


class PromptFlowOrchestrator(OrchestratorBase):
    """
    Orchestrator class for managing the flow of prompts and responses in a chat application.
    This class handles the orchestration of user messages, chat history, and interactions with
    the Prompt Flow service, including content safety checks and response formatting.
    """

    def __init__(self) -> None:
        """
        Initialize the PromptFlowOrchestrator instance.
        Sets up the necessary helpers and retrieves configuration for the ML client, endpoint, and deployment names.
        """
        super().__init__()
        self.llm_helper = LLMHelper()
        self.env_helper = EnvHelper()

        # Get the ML client, endpoint and deployment names
        self.ml_client = self.llm_helper.get_ml_client()
        self.enpoint_name = self.env_helper.PROMPT_FLOW_ENDPOINT_NAME
        self.deployment_name = self.env_helper.PROMPT_FLOW_DEPLOYMENT_NAME

        logger.info("PromptFlowOrchestrator initialized.")

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    async def orchestrate(
        self, user_message: str, chat_history: List[dict], **kwargs: dict
    ) -> list[dict]:
        """
        Orchestrate the flow of a user message and chat history through the Prompt Flow service.

        Args:
            user_message (str): The message from the user.
            chat_history (List[dict]): The history of the chat as a list of dictionaries.
            **kwargs (dict): Additional keyword arguments.

        Returns:
            list[dict]: The formatted response messages for the UI.
        """
        logger.info("Orchestration started.")

        # Call Content Safety tool on question
        if self.config.prompts.enable_content_safety:
            logger.info("Content safety check enabled for input.")
            if response := self.call_content_safety_input(user_message):
                logger.info("Content safety flagged the input. Returning response.")
                return response

        transformed_chat_history = self.transform_chat_history(chat_history)

        file_name = self.transform_data_into_file(
            user_message, transformed_chat_history
        )
        logger.info(f"File created for Prompt Flow: {file_name}")

        # Call the Prompt Flow service
        try:
            logger.info("Invoking Prompt Flow service.")
            response = self.ml_client.online_endpoints.invoke(
                endpoint_name=self.enpoint_name,
                request_file=file_name,
                deployment_name=self.deployment_name,
            )
            logger.info("Prompt Flow service invoked successfully.")
            result = json.loads(response)
            logger.debug(result)
        except Exception as error:
            logger.error("The request failed: %s", error)
            raise RuntimeError(f"The request failed: {error}") from error

        # Transform response into answer for further processing
        logger.info("Processing response from Prompt Flow.")
        answer = Answer(
            question=user_message,
            answer=result["chat_output"],
            source_documents=self.transform_citations_into_source_documents(
                result["citations"]
            ),
        )
        logger.info("Answer processed successfully.")

        # Call Content Safety tool on answer
        if self.config.prompts.enable_content_safety:
            logger.info("Content safety check enabled for output.")
            if response := self.call_content_safety_output(user_message, answer.answer):
                logger.info("Content safety flagged the output. Returning response.")
                return response

        # Format the output for the UI
        logger.info("Formatting output for UI.")
        messages = self.output_parser.parse(
            question=answer.question,
            answer=answer.answer,
            source_documents=answer.source_documents,
        )
        logger.info("Orchestration completed successfully.")
        return messages

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def transform_chat_history(self, chat_history: List[dict]) -> List[dict]:
        """
        Transform the chat history into a format suitable for the Prompt Flow service.

        Args:
            chat_history (List[dict]): The history of the chat as a list of dictionaries.

        Returns:
            List[dict]: The transformed chat history.
        """
        logger.info("Transforming chat history.")
        transformed_chat_history = []
        for i, message in enumerate(chat_history):
            if message["role"] == "user":
                user_message = message["content"]
                assistant_message = ""
                if (
                    i + 1 < len(chat_history)
                    and chat_history[i + 1]["role"] == "assistant"
                ):
                    assistant_message = chat_history[i + 1]["content"]
                transformed_chat_history.append(
                    {
                        "inputs": {"chat_input": user_message},
                        "outputs": {"chat_output": assistant_message},
                    }
                )
        logger.info("Chat history transformation completed.")
        return transformed_chat_history

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def transform_data_into_file(
        self, user_message: str, chat_history: List[dict]
    ) -> str:
        """
        Transform the user message and chat history into a temporary file for the Prompt Flow service.

        Args:
            user_message (str): The message from the user.
            chat_history (List[dict]): The transformed chat history.

        Returns:
            str: The name of the temporary file created.
        """
        logger.info("Creating temporary file for Prompt Flow input.")
        data = {"chat_input": user_message, "chat_history": chat_history}
        body = str.encode(json.dumps(data))
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(body)
        logger.info("Temporary file created")
        return file.name

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def transform_citations_into_source_documents(
        self, citations: dict
    ) -> List[SourceDocument]:
        """
        Transform the citations from the Prompt Flow response into SourceDocument objects.

        Args:
            citations (dict): The citations from the Prompt Flow response.

        Returns:
            List[SourceDocument]: The list of SourceDocument objects.
        """
        logger.info("Transforming citations into source documents.")
        source_documents = []

        for _, doc_id in enumerate(citations):
            citation = citations[doc_id]
            source_documents.append(
                SourceDocument(
                    id=doc_id,
                    content=citation.get("content"),
                    source=citation.get("filepath"),
                    chunk_id=str(citation.get("chunk_id", 0)),
                )
            )
        logger.info("Citations transformation completed.")
        return source_documents
