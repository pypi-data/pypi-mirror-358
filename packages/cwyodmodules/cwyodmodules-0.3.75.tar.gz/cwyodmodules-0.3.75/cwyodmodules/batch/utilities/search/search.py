from ..search.postgres_search_handler import AzurePostgresHandler
from ..helpers.config.database_type import DatabaseType
from ..search.azure_search_handler import AzureSearchHandler
from ..search.integrated_vectorization_search_handler import (
    IntegratedVectorizationSearchHandler,
)
from ..search.search_handler_base import SearchHandlerBase
from ..common.source_document import SourceDocument
from ..helpers.env_helper import EnvHelper

from ..search.lightrag_search_handler import LightRAGSearchHandler

from mgmt_config import logger
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT


class Search:
    """
    The Search class provides methods to obtain the appropriate search handler
    based on the environment configuration and to retrieve source documents
    based on a search query.
    """

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def get_search_handler(env_helper: EnvHelper) -> SearchHandlerBase:
        """
        Determines and returns the appropriate search handler based on the
        environment configuration provided by the EnvHelper instance.

        Args:
            env_helper (EnvHelper): An instance of EnvHelper containing environment
                                    configuration details.

        Returns:
            SearchHandlerBase: An instance of a class derived from SearchHandlerBase
                               that handles search operations.

        Note:
            Since the full workflow for PostgreSQL indexing is not yet complete,
            you can comment out the condition checking for PostgreSQL.
        """
        logger.info("Getting search handler...")
        # if env_helper.DATABASE_TYPE == DatabaseType.POSTGRESQL.value:
        #     logger.info("Using LightRAGSearchHandler.")
        #     return LightRAGSearchHandler(env_helper)
        if env_helper.DATABASE_TYPE == DatabaseType.POSTGRESQL.value:
            logger.info("Using AzurePostgresHandler.")
            return AzurePostgresHandler(env_helper)
        else:
            if env_helper.AZURE_SEARCH_USE_INTEGRATED_VECTORIZATION:
                logger.info("Using IntegratedVectorizationSearchHandler.")
                return IntegratedVectorizationSearchHandler(env_helper)
            else:
                logger.info("Using AzureSearchHandler.")
                return AzureSearchHandler(env_helper)

    @staticmethod
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def get_source_documents(
        search_handler: SearchHandlerBase, question: str
    ) -> list[SourceDocument]:
        """
        Retrieves source documents based on the provided search query using the
        specified search handler.

        Args:
            search_handler (SearchHandlerBase): An instance of a class derived from
                                                SearchHandlerBase that handles search
                                                operations.
            question (str): The search query string.

        Returns:
            list[SourceDocument]: A list of SourceDocument instances that match the
                                  search query.
        """
        logger.info(f"Getting source documents for question: {question}")
        return search_handler.query_search(question)
