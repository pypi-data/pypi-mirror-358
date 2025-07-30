"""
Tests for Azure helper modules.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from cwyodmodules.batch.utilities.helpers.azure_blob_storage_client import AzureBlobStorageClient
from cwyodmodules.batch.utilities.helpers.azure_search_helper import AzureSearchHelper
from cwyodmodules.batch.utilities.helpers.llm_helper import LLMHelper


class TestAzureBlobStorageClient:
    """Test Azure Blob Storage client."""

    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.BlobServiceClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.env_helper')
    def test_init_with_rbac(self, mock_env_helper, mock_blob_service):
        """Test initialization with RBAC authentication."""
        mock_env_helper.AZURE_STORAGE_ACCOUNT_ENDPOINT = "https://test.blob.core.windows.net/"
        mock_env_helper.is_auth_type_keys.return_value = False
        
        client = AzureBlobStorageClient()
        
        mock_blob_service.from_blob_url.assert_called_once()

    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.BlobServiceClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.env_helper')
    def test_init_with_keys(self, mock_env_helper, mock_blob_service):
        """Test initialization with API keys."""
        mock_env_helper.AZURE_STORAGE_ACCOUNT_ENDPOINT = "https://test.blob.core.windows.net/"
        mock_env_helper.is_auth_type_keys.return_value = True
        mock_env_helper.AZURE_STORAGE_ACCOUNT_KEY = "test-key"
        
        client = AzureBlobStorageClient()
        
        mock_blob_service.assert_called_once()

    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.BlobServiceClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.logger')
    def test_upload_file_success(self, mock_logger, mock_env_helper, mock_blob_service):
        """Test successful file upload."""
        mock_env_helper.AZURE_STORAGE_ACCOUNT_ENDPOINT = "https://test.blob.core.windows.net/"
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_blob_client = Mock()
        mock_blob_service.from_blob_url.return_value.get_blob_client.return_value = mock_blob_client
        
        client = AzureBlobStorageClient()
        result = client.upload_file(b"test content", "test.txt", "test-container")
        
        mock_blob_client.upload_blob.assert_called_once()
        assert result is True

    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.BlobServiceClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.logger')
    def test_download_file_success(self, mock_logger, mock_env_helper, mock_blob_service):
        """Test successful file download."""
        mock_env_helper.AZURE_STORAGE_ACCOUNT_ENDPOINT = "https://test.blob.core.windows.net/"
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_blob_client = Mock()
        mock_blob_client.download_blob.return_value.readall.return_value = b"test content"
        mock_blob_service.from_blob_url.return_value.get_blob_client.return_value = mock_blob_client
        
        client = AzureBlobStorageClient()
        result = client.download_file("test.txt", "test-container")
        
        assert result == b"test content"


class TestAzureSearchHelper:
    """Test Azure Search helper."""

    @patch('cwyodmodules.batch.utilities.helpers.azure_search_helper.SearchClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_search_helper.env_helper')
    def test_init_with_rbac(self, mock_env_helper, mock_search_client):
        """Test initialization with RBAC."""
        mock_env_helper.AZURE_SEARCH_SERVICE_ENDPOINT = "https://test.search.windows.net/"
        mock_env_helper.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_env_helper.is_auth_type_keys.return_value = False
        
        helper = AzureSearchHelper()
        
        mock_search_client.assert_called_once()

    @patch('cwyodmodules.batch.utilities.helpers.azure_search_helper.SearchClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_search_helper.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.azure_search_helper.logger')
    def test_search_success(self, mock_logger, mock_env_helper, mock_search_client):
        """Test successful search operation."""
        mock_env_helper.AZURE_SEARCH_SERVICE_ENDPOINT = "https://test.search.windows.net/"
        mock_env_helper.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_client = Mock()
        mock_client.search.return_value = [{"id": "1", "content": "test"}]
        mock_search_client.return_value = mock_client
        
        helper = AzureSearchHelper()
        results = helper.search("test query")
        
        assert len(results) == 1
        assert results[0]["id"] == "1"

    @patch('cwyodmodules.batch.utilities.helpers.azure_search_helper.SearchClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_search_helper.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.azure_search_helper.logger')
    def test_upload_documents_success(self, mock_logger, mock_env_helper, mock_search_client):
        """Test successful document upload."""
        mock_env_helper.AZURE_SEARCH_SERVICE_ENDPOINT = "https://test.search.windows.net/"
        mock_env_helper.AZURE_SEARCH_INDEX_NAME = "test-index"
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_client = Mock()
        mock_search_client.return_value = mock_client
        
        documents = [{"id": "1", "content": "test document"}]
        
        helper = AzureSearchHelper()
        result = helper.upload_documents(documents)
        
        mock_client.upload_documents.assert_called_once_with(documents)
        assert result is True


class TestLLMHelper:
    """Test LLM helper functionality."""

    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.AsyncAzureOpenAI')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.env_helper')
    def test_init_with_rbac(self, mock_env_helper, mock_openai):
        """Test initialization with RBAC."""
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_TOKEN_PROVIDER = "mock_provider"
        
        helper = LLMHelper()
        
        mock_openai.assert_called_once_with(
            azure_endpoint="https://test.openai.azure.com/",
            api_version="2024-02-01",
            azure_ad_token_provider="mock_provider"
        )

    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.AsyncAzureOpenAI')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.env_helper')
    def test_init_with_keys(self, mock_env_helper, mock_openai):
        """Test initialization with API keys."""
        mock_env_helper.is_auth_type_keys.return_value = True
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_OPENAI_API_KEY = "test-key"
        
        helper = LLMHelper()
        
        mock_openai.assert_called_once_with(
            azure_endpoint="https://test.openai.azure.com/",
            api_version="2024-02-01",
            api_key="test-key"
        )

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.AsyncAzureOpenAI')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.logger')
    async def test_generate_completion_success(self, mock_logger, mock_env_helper, mock_openai):
        """Test successful completion generation."""
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_TOKEN_PROVIDER = "mock_provider"
        mock_env_helper.AZURE_OPENAI_MODEL = "gpt-4"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Generated response"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        helper = LLMHelper()
        result = await helper.generate_completion([{"role": "user", "content": "Hello"}])
        
        assert result["content"] == "Generated response"
        assert result["prompt_tokens"] == 10
        assert result["completion_tokens"] == 20

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.AsyncAzureOpenAI')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.logger')
    async def test_generate_embedding_success(self, mock_logger, mock_env_helper, mock_openai):
        """Test successful embedding generation."""
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_TOKEN_PROVIDER = "mock_provider"
        mock_env_helper.AZURE_OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        helper = LLMHelper()
        result = await helper.generate_embedding("test text")
        
        assert result == [0.1, 0.2, 0.3]

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.AsyncAzureOpenAI')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.logger')
    async def test_generate_completion_exception(self, mock_logger, mock_env_helper, mock_openai):
        """Test completion generation with exception."""
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_TOKEN_PROVIDER = "mock_provider"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("OpenAI error")
        mock_openai.return_value = mock_client
        
        helper = LLMHelper()
        
        with pytest.raises(Exception, match="OpenAI error"):
            await helper.generate_completion([{"role": "user", "content": "Hello"}])
        
        mock_logger.exception.assert_called()


class TestAzureFormRecognizerHelper:
    """Test Azure Form Recognizer helper."""

    @patch('cwyodmodules.batch.utilities.helpers.azure_form_recognizer_helper.DocumentAnalysisClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_form_recognizer_helper.env_helper')
    def test_init_with_rbac(self, mock_env_helper, mock_client):
        """Test initialization with RBAC."""
        from cwyodmodules.batch.utilities.helpers.azure_form_recognizer_helper import AzureFormRecognizerHelper
        
        mock_env_helper.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
        mock_env_helper.is_auth_type_keys.return_value = False
        
        helper = AzureFormRecognizerHelper()
        
        mock_client.assert_called_once()

    @patch('cwyodmodules.batch.utilities.helpers.azure_form_recognizer_helper.DocumentAnalysisClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_form_recognizer_helper.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.azure_form_recognizer_helper.logger')
    def test_analyze_document_success(self, mock_logger, mock_env_helper, mock_client_class):
        """Test successful document analysis."""
        from cwyodmodules.batch.utilities.helpers.azure_form_recognizer_helper import AzureFormRecognizerHelper
        
        mock_env_helper.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_client = Mock()
        mock_result = Mock()
        mock_result.content = "Extracted text content"
        mock_client.begin_analyze_document.return_value.result.return_value = mock_result
        mock_client_class.return_value = mock_client
        
        helper = AzureFormRecognizerHelper()
        result = helper.analyze_document(b"pdf content")
        
        assert result.content == "Extracted text content"
        mock_client.begin_analyze_document.assert_called_once()


class TestIntegrationScenarios:
    """Test integration scenarios across Azure helpers."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.BlobServiceClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_form_recognizer_helper.DocumentAnalysisClient')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.AsyncAzureOpenAI')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper')
    async def test_document_processing_pipeline(self, mock_env_helper, mock_openai, mock_form_recognizer, mock_blob_service):
        """Test complete document processing pipeline."""
        # Setup environment
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_env_helper.AZURE_STORAGE_ACCOUNT_ENDPOINT = "https://test.blob.core.windows.net/"
        mock_env_helper.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_TOKEN_PROVIDER = "mock_provider"
        mock_env_helper.AZURE_OPENAI_MODEL = "gpt-4"
        
        # Setup blob storage
        mock_blob_client = Mock()
        mock_blob_client.download_blob.return_value.readall.return_value = b"pdf content"
        mock_blob_service.from_blob_url.return_value.get_blob_client.return_value = mock_blob_client
        
        # Setup form recognizer
        mock_fr_client = Mock()
        mock_result = Mock()
        mock_result.content = "Extracted document text"
        mock_fr_client.begin_analyze_document.return_value.result.return_value = mock_result
        mock_form_recognizer.return_value = mock_fr_client
        
        # Setup OpenAI
        mock_openai_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Document summary"
        mock_openai_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_openai_client
        
        # Test the pipeline
        blob_client = AzureBlobStorageClient()
        form_recognizer_client = AzureFormRecognizerHelper()
        llm_client = LLMHelper()
        
        # Download document
        document_content = blob_client.download_file("test.pdf", "documents")
        assert document_content == b"pdf content"
        
        # Extract text
        analysis_result = form_recognizer_client.analyze_document(document_content)
        assert analysis_result.content == "Extracted document text"
        
        # Generate summary
        messages = [{"role": "user", "content": f"Summarize: {analysis_result.content}"}]
        summary = await llm_client.generate_completion(messages)
        assert summary["content"] == "Document summary"


class TestErrorHandling:
    """Test error handling across Azure helpers."""

    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.BlobServiceClient')
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.azure_blob_storage_client.logger')
    def test_blob_storage_exception_handling(self, mock_logger, mock_env_helper, mock_blob_service):
        """Test blob storage exception handling."""
        mock_env_helper.AZURE_STORAGE_ACCOUNT_ENDPOINT = "https://test.blob.core.windows.net/"
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        mock_blob_client = Mock()
        mock_blob_client.upload_blob.side_effect = Exception("Storage error")
        mock_blob_service.from_blob_url.return_value.get_blob_client.return_value = mock_blob_client
        
        client = AzureBlobStorageClient()
        
        with pytest.raises(Exception, match="Storage error"):
            client.upload_file(b"test", "test.txt", "container")
        
        mock_logger.exception.assert_called()

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.AsyncAzureOpenAI')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.env_helper')
    @patch('cwyodmodules.batch.utilities.helpers.llm_helper.logger')
    async def test_llm_rate_limit_handling(self, mock_logger, mock_env_helper, mock_openai):
        """Test LLM rate limit exception handling."""
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_TOKEN_PROVIDER = "mock_provider"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        mock_openai.return_value = mock_client
        
        helper = LLMHelper()
        
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await helper.generate_completion([{"role": "user", "content": "Hello"}])
        
        mock_logger.exception.assert_called() 