"""
Tests for chat history API endpoints.
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from flask import Flask
from cwyodmodules.api.chat_history import (
    bp_chat_history_response,
    init_database_client,
    init_openai_client,
    list_conversations,
    rename_conversation,
    get_conversation,
    delete_conversation,
    delete_all_conversations,
    update_conversation,
    get_frontend_settings,
    generate_title
)


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(bp_chat_history_response)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestDatabaseClientInitialization:
    """Test database client initialization."""

    @patch('cwyodmodules.api.chat_history.DatabaseFactory')
    @patch('cwyodmodules.api.chat_history.logger')
    def test_init_database_client_success(self, mock_logger, mock_factory):
        """Test successful database client initialization."""
        mock_client = Mock()
        mock_factory.get_conversation_client.return_value = mock_client
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        result = init_database_client()
        
        assert result == mock_client
        mock_factory.get_conversation_client.assert_called_once()

    @patch('cwyodmodules.api.chat_history.DatabaseFactory')
    @patch('cwyodmodules.api.chat_history.logger')
    def test_init_database_client_exception(self, mock_logger, mock_factory):
        """Test database client initialization with exception."""
        mock_factory.get_conversation_client.side_effect = Exception("Database error")
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        with pytest.raises(Exception, match="Database error"):
            init_database_client()
        
        mock_logger.exception.assert_called_once()


class TestOpenAIClientInitialization:
    """Test OpenAI client initialization."""

    @patch('cwyodmodules.api.chat_history.AsyncAzureOpenAI')
    @patch('cwyodmodules.api.chat_history.env_helper')
    @patch('cwyodmodules.api.chat_history.logger')
    def test_init_openai_client_with_keys(self, mock_logger, mock_env_helper, mock_openai):
        """Test OpenAI client initialization with API keys."""
        mock_env_helper.is_auth_type_keys.return_value = True
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_OPENAI_API_KEY = "test-api-key"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        result = init_openai_client()
        
        assert result == mock_client
        mock_openai.assert_called_once_with(
            azure_endpoint="https://test.openai.azure.com/",
            api_version="2024-02-01",
            api_key="test-api-key"
        )

    @patch('cwyodmodules.api.chat_history.AsyncAzureOpenAI')
    @patch('cwyodmodules.api.chat_history.env_helper')
    @patch('cwyodmodules.api.chat_history.logger')
    def test_init_openai_client_with_rbac(self, mock_logger, mock_env_helper, mock_openai):
        """Test OpenAI client initialization with RBAC."""
        mock_env_helper.is_auth_type_keys.return_value = False
        mock_env_helper.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
        mock_env_helper.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_env_helper.AZURE_TOKEN_PROVIDER = "mock_token_provider"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        result = init_openai_client()
        
        assert result == mock_client
        mock_openai.assert_called_once_with(
            azure_endpoint="https://test.openai.azure.com/",
            api_version="2024-02-01",
            azure_ad_token_provider="mock_token_provider"
        )

    @patch('cwyodmodules.api.chat_history.AsyncAzureOpenAI')
    @patch('cwyodmodules.api.chat_history.env_helper')
    @patch('cwyodmodules.api.chat_history.logger')
    def test_init_openai_client_exception(self, mock_logger, mock_env_helper, mock_openai):
        """Test OpenAI client initialization with exception."""
        mock_env_helper.is_auth_type_keys.return_value = True
        mock_openai.side_effect = Exception("OpenAI initialization error")
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        with pytest.raises(Exception, match="OpenAI initialization error"):
            init_openai_client()
        
        mock_logger.exception.assert_called_once()


class TestListConversationsEndpoint:
    """Test /history/list endpoint."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_list_conversations_success(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test successful conversation listing."""
        # Setup mocks
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversations = AsyncMock(return_value=[
            {"id": "conv1", "title": "Conversation 1"},
            {"id": "conv2", "title": "Conversation 2"}
        ])
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        # Make request
        response = client.get('/history/list')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]["id"] == "conv1"
        assert data[1]["id"] == "conv2"
        
        # Verify database calls
        mock_db_client.connect.assert_called_once()
        mock_db_client.get_conversations.assert_called_once_with("test-user-id", offset=0, limit=25)
        mock_db_client.close.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_list_conversations_chat_history_disabled(self, mock_logger, mock_config_helper, client):
        """Test conversation listing when chat history is disabled."""
        mock_config = Mock()
        mock_config.enable_chat_history = False
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        response = client.get('/history/list')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "Chat history is not available"

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_list_conversations_database_unavailable(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test conversation listing when database is unavailable."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        mock_init_db.return_value = None
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        response = client.get('/history/list')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["error"] == "Database not available"

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_list_conversations_no_conversations_found(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test conversation listing when no conversations are found."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversations = AsyncMock(return_value="not a list")
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        response = client.get('/history/list')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "No conversations for test-user-id were found" in data["error"]

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_list_conversations_with_offset(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test conversation listing with offset parameter."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversations = AsyncMock(return_value=[])
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        response = client.get('/history/list?offset=10')
        
        mock_db_client.get_conversations.assert_called_once_with("test-user-id", offset=10, limit=25)

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_list_conversations_database_exception(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test conversation listing with database exception."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversations = AsyncMock(side_effect=Exception("Database error"))
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        response = client.get('/history/list')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["error"] == "Error while listing historical conversations"
        
        # Verify database cleanup
        mock_db_client.close.assert_called_once()


class TestRenameConversationEndpoint:
    """Test /history/rename endpoint."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_rename_conversation_success(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test successful conversation renaming."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        existing_conversation = {
            "id": "conv1",
            "title": "Old Title",
            "user_id": "test-user-id"
        }
        updated_conversation = {
            "id": "conv1",
            "title": "New Title",
            "user_id": "test-user-id"
        }
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversation = AsyncMock(return_value=existing_conversation)
        mock_db_client.upsert_conversation = AsyncMock(return_value=updated_conversation)
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {
            "conversation_id": "conv1",
            "title": "New Title"
        }
        
        response = client.post('/history/rename', 
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["title"] == "New Title"
        
        # Verify database calls
        mock_db_client.get_conversation.assert_called_once_with("test-user-id", "conv1")
        mock_db_client.upsert_conversation.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_rename_conversation_chat_history_disabled(self, mock_logger, mock_config_helper, client):
        """Test conversation renaming when chat history is disabled."""
        mock_config = Mock()
        mock_config.enable_chat_history = False
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {"conversation_id": "conv1", "title": "New Title"}
        
        response = client.post('/history/rename',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "Chat history is not available"

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_rename_conversation_missing_conversation_id(self, mock_logger, mock_auth, mock_config_helper, client):
        """Test conversation renaming with missing conversation_id."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {"title": "New Title"}  # Missing conversation_id
        
        response = client.post('/history/rename',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "conversation_id is required"

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_rename_conversation_empty_title(self, mock_logger, mock_auth, mock_config_helper, client):
        """Test conversation renaming with empty title."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {"conversation_id": "conv1", "title": ""}
        
        response = client.post('/history/rename',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "A non-empty title is required"

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_rename_conversation_not_found(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test conversation renaming when conversation is not found."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversation = AsyncMock(return_value=None)
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {"conversation_id": "nonexistent", "title": "New Title"}
        
        response = client.post('/history/rename',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Conversation nonexistent was not found" in data["error"]


class TestGetConversationEndpoint:
    """Test /history/read endpoint."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_get_conversation_success(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test successful conversation retrieval."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        conversation = {
            "id": "conv1",
            "title": "Test Conversation",
            "user_id": "test-user-id"
        }
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversation = AsyncMock(return_value=conversation)
        mock_db_client.get_messages = AsyncMock(return_value=messages)
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {"conversation_id": "conv1"}
        
        response = client.post('/history/read',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["conversation_data"]["id"] == "conv1"
        assert len(data["messages"]) == 2

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_get_conversation_missing_id(self, mock_logger, mock_auth, mock_config_helper, client):
        """Test conversation retrieval with missing conversation_id."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {}  # Missing conversation_id
        
        response = client.post('/history/read',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "conversation_id is required"


class TestDeleteConversationEndpoint:
    """Test /history/delete endpoint."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_delete_conversation_success(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test successful conversation deletion."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        conversation = {
            "id": "conv1",
            "title": "Test Conversation",
            "user_id": "test-user-id"
        }
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversation = AsyncMock(return_value=conversation)
        mock_db_client.delete_conversation = AsyncMock(return_value=True)
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {"conversation_id": "conv1"}
        
        response = client.delete('/history/delete',
                               data=json.dumps(request_data),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Successfully deleted conversation and messages"
        
        mock_db_client.delete_conversation.assert_called_once_with("test-user-id", "conv1")


class TestDeleteAllConversationsEndpoint:
    """Test /history/delete_all endpoint."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_delete_all_conversations_success(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test successful deletion of all conversations."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.delete_all_conversations = AsyncMock(return_value=True)
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        response = client.delete('/history/delete_all')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Successfully deleted conversation and messages"
        
        mock_db_client.delete_all_conversations.assert_called_once_with("test-user-id")


class TestUpdateConversationEndpoint:
    """Test /history/update endpoint."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_update_conversation_success(self, mock_logger, mock_init_db, mock_auth, mock_config_helper, client):
        """Test successful conversation update."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user-id"}
        
        updated_conversation = {
            "id": "conv1",
            "title": "Updated Conversation",
            "user_id": "test-user-id"
        }
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.upsert_conversation = AsyncMock(return_value=updated_conversation)
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        request_data = {
            "conversation": {
                "id": "conv1",
                "title": "Updated Conversation",
                "user_id": "test-user-id"
            },
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        response = client.post('/history/update',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == "conv1"


class TestGetFrontendSettingsEndpoint:
    """Test /history/frontend_settings endpoint."""

    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.logger')
    def test_get_frontend_settings_success(self, mock_logger, mock_config_helper, client):
        """Test successful frontend settings retrieval."""
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        response = client.get('/history/frontend_settings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["enable_chat_history"] is True

    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.logger')
    def test_get_frontend_settings_disabled(self, mock_logger, mock_config_helper, client):
        """Test frontend settings when chat history is disabled."""
        mock_config = Mock()
        mock_config.enable_chat_history = False
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        response = client.get('/history/frontend_settings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["enable_chat_history"] is False


class TestGenerateTitleFunction:
    """Test generate_title function."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.init_openai_client')
    async def test_generate_title_success(self, mock_init_openai):
        """Test successful title generation."""
        mock_openai_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Generated Title"
        
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_init_openai.return_value = mock_openai_client
        
        messages = [
            {"role": "user", "content": "What is AI?"},
            {"role": "assistant", "content": "AI is artificial intelligence."}
        ]
        
        result = await generate_title(messages)
        
        assert result == "Generated Title"
        mock_openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.init_openai_client')
    async def test_generate_title_exception(self, mock_init_openai):
        """Test title generation with exception."""
        mock_openai_client = AsyncMock()
        mock_openai_client.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI error"))
        mock_init_openai.return_value = mock_openai_client
        
        messages = [{"role": "user", "content": "Test"}]
        
        result = await generate_title(messages)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_title_empty_messages(self):
        """Test title generation with empty messages."""
        messages = []
        
        result = await generate_title(messages)
        
        assert result is None 