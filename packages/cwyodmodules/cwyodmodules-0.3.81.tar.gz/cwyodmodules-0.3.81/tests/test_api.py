"""
Tests for the API module, specifically chat_history functionality.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from flask import Flask
import json
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
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(bp_chat_history_response)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestChatHistoryAPI:
    """Test class for chat history API endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_init_database_client_success(self, mock_logger):
        """Test successful database client initialization."""
        with patch('cwyodmodules.api.chat_history.DatabaseFactory') as mock_factory:
            mock_client = AsyncMock()
            mock_factory.get_conversation_client.return_value = mock_client

            result = init_database_client()

            assert result == mock_client
            mock_factory.get_conversation_client.assert_called_once()

    @pytest.mark.api
    @pytest.mark.unit
    def test_init_database_client_exception(self, mock_logger):
        """Test database client initialization with exception."""
        with patch('cwyodmodules.api.chat_history.DatabaseFactory') as mock_factory:
            mock_factory.get_conversation_client.side_effect = Exception("Database error")

            with pytest.raises(Exception, match="Database error"):
                init_database_client()

    @pytest.mark.api
    @pytest.mark.unit
    def test_init_openai_client_with_keys(self, mock_logger):
        """Test OpenAI client initialization with API keys."""
        with patch('cwyodmodules.api.chat_history.AsyncAzureOpenAI') as mock_openai:
            with patch('cwyodmodules.api.chat_history.env_helper') as mock_env:
                mock_env.is_auth_type_keys.return_value = True
                mock_env.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
                mock_env.AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
                mock_env.AZURE_OPENAI_API_KEY = "test-key"

                mock_client = AsyncMock()
                mock_openai.return_value = mock_client

                result = init_openai_client()

                assert result == mock_client
                mock_openai.assert_called_once_with(
                    azure_endpoint="https://test.openai.azure.com/",
                    api_version="2024-02-15-preview",
                    api_key="test-key"
                )

    @pytest.mark.api
    @pytest.mark.unit
    def test_init_openai_client_with_token(self, mock_logger):
        """Test OpenAI client initialization with token provider."""
        with patch('cwyodmodules.api.chat_history.AsyncAzureOpenAI') as mock_openai:
            with patch('cwyodmodules.api.chat_history.env_helper') as mock_env:
                mock_env.is_auth_type_keys.return_value = False
                mock_env.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
                mock_env.AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
                mock_env.AZURE_TOKEN_PROVIDER = Mock()

                mock_client = AsyncMock()
                mock_openai.return_value = mock_client

                result = init_openai_client()

                assert result == mock_client
                mock_openai.assert_called_once_with(
                    azure_endpoint="https://test.openai.azure.com/",
                    api_version="2024-02-15-preview",
                    azure_ad_token_provider=mock_env.AZURE_TOKEN_PROVIDER
                )

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_list_conversations_success(self, client, mock_logger):
        """Test successful conversation listing."""
        with patch('cwyodmodules.api.chat_history.ConfigHelper') as mock_config_helper:
            with patch('cwyodmodules.api.chat_history.get_authenticated_user_details') as mock_auth:
                with patch('cwyodmodules.api.chat_history.init_database_client') as mock_init_db:
                    with patch('cwyodmodules.api.chat_history.request') as mock_request:
                        # Setup mocks
                        mock_config = Mock()
                        mock_config.enable_chat_history = True
                        mock_config_helper.get_active_config_or_default.return_value = mock_config

                        mock_auth.return_value = {"user_principal_id": "test-user"}

                        mock_db_client = AsyncMock()
                        mock_init_db.return_value = mock_db_client
                        mock_db_client.get_conversations.return_value = [
                            {"id": "conv1", "title": "Test Conversation"}
                        ]

                        mock_request.args = {"offset": "0"}
                        mock_request.headers = {"Authorization": "Bearer test-token"}

                        # Execute
                        response = await list_conversations()

                        # Assert
                        assert response[1] == 200
                        data = json.loads(response[0].get_data(as_text=True))
                        assert len(data) == 1
                        assert data[0]["id"] == "conv1"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_list_conversations_disabled(self, client, mock_logger):
        """Test conversation listing when chat history is disabled."""
        with patch('cwyodmodules.api.chat_history.ConfigHelper') as mock_config_helper:
            mock_config = Mock()
            mock_config.enable_chat_history = False
            mock_config_helper.get_active_config_or_default.return_value = mock_config

            response = await list_conversations()

            assert response[1] == 400
            data = json.loads(response[0].get_data(as_text=True))
            assert data["error"] == "Chat history is not available"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_rename_conversation_success(self, client, mock_logger):
        """Test successful conversation renaming."""
        with patch('cwyodmodules.api.chat_history.ConfigHelper') as mock_config_helper:
            with patch('cwyodmodules.api.chat_history.get_authenticated_user_details') as mock_auth:
                with patch('cwyodmodules.api.chat_history.init_database_client') as mock_init_db:
                    with patch('cwyodmodules.api.chat_history.request') as mock_request:
                        # Setup mocks
                        mock_config = Mock()
                        mock_config.enable_chat_history = True
                        mock_config_helper.get_active_config_or_default.return_value = mock_config

                        mock_auth.return_value = {"user_principal_id": "test-user"}

                        mock_db_client = AsyncMock()
                        mock_init_db.return_value = mock_db_client

                        existing_conversation = {
                            "id": "conv1",
                            "title": "Old Title",
                            "user_id": "test-user"
                        }
                        updated_conversation = {
                            "id": "conv1",
                            "title": "New Title",
                            "user_id": "test-user"
                        }

                        mock_db_client.get_conversation.return_value = existing_conversation
                        mock_db_client.upsert_conversation.return_value = updated_conversation

                        mock_request.get_json.return_value = {
                            "conversation_id": "conv1",
                            "title": "New Title"
                        }
                        mock_request.headers = {"Authorization": "Bearer test-token"}

                        # Execute
                        response = await rename_conversation()

                        # Assert
                        assert response[1] == 200
                        data = json.loads(response[0].get_data(as_text=True))
                        assert data["title"] == "New Title"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_rename_conversation_missing_id(self, client, mock_logger):
        """Test conversation renaming with missing conversation ID."""
        with patch('cwyodmodules.api.chat_history.ConfigHelper') as mock_config_helper:
            with patch('cwyodmodules.api.chat_history.get_authenticated_user_details') as mock_auth:
                with patch('cwyodmodules.api.chat_history.request') as mock_request:
                    # Setup mocks
                    mock_config = Mock()
                    mock_config.enable_chat_history = True
                    mock_config_helper.get_active_config_or_default.return_value = mock_config

                    mock_auth.return_value = {"user_principal_id": "test-user"}

                    mock_request.get_json.return_value = {"title": "New Title"}
                    mock_request.headers = {"Authorization": "Bearer test-token"}

                    # Execute
                    response = await rename_conversation()

                    # Assert
                    assert response[1] == 400
                    data = json.loads(response[0].get_data(as_text=True))
                    assert data["error"] == "conversation_id is required"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_conversation_success(self, client, mock_logger):
        """Test successful conversation retrieval."""
        with patch('cwyodmodules.api.chat_history.ConfigHelper') as mock_config_helper:
            with patch('cwyodmodules.api.chat_history.get_authenticated_user_details') as mock_auth:
                with patch('cwyodmodules.api.chat_history.init_database_client') as mock_init_db:
                    with patch('cwyodmodules.api.chat_history.request') as mock_request:
                        # Setup mocks
                        mock_config = Mock()
                        mock_config.enable_chat_history = True
                        mock_config_helper.get_active_config_or_default.return_value = mock_config

                        mock_auth.return_value = {"user_principal_id": "test-user"}

                        mock_db_client = AsyncMock()
                        mock_init_db.return_value = mock_db_client

                        conversation = {
                            "id": "conv1",
                            "title": "Test Conversation",
                            "user_id": "test-user"
                        }
                        messages = [
                            {"id": "msg1", "content": "Hello", "role": "user"}
                        ]

                        mock_db_client.get_conversation.return_value = conversation
                        mock_db_client.get_messages.return_value = messages

                        mock_request.get_json.return_value = {"conversation_id": "conv1"}
                        mock_request.headers = {"Authorization": "Bearer test-token"}

                        # Execute
                        response = await get_conversation()

                        # Assert
                        assert response[1] == 200
                        data = json.loads(response[0].get_data(as_text=True))
                        assert data["conversation"]["id"] == "conv1"
                        assert len(data["messages"]) == 1

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_delete_conversation_success(self, client, mock_logger):
        """Test successful conversation deletion."""
        with patch('cwyodmodules.api.chat_history.ConfigHelper') as mock_config_helper:
            with patch('cwyodmodules.api.chat_history.get_authenticated_user_details') as mock_auth:
                with patch('cwyodmodules.api.chat_history.init_database_client') as mock_init_db:
                    with patch('cwyodmodules.api.chat_history.request') as mock_request:
                        # Setup mocks
                        mock_config = Mock()
                        mock_config.enable_chat_history = True
                        mock_config_helper.get_active_config_or_default.return_value = mock_config

                        mock_auth.return_value = {"user_principal_id": "test-user"}

                        mock_db_client = AsyncMock()
                        mock_init_db.return_value = mock_db_client
                        mock_db_client.delete_conversation.return_value = True

                        mock_request.get_json.return_value = {"conversation_id": "conv1"}
                        mock_request.headers = {"Authorization": "Bearer test-token"}

                        # Execute
                        response = await delete_conversation()

                        # Assert
                        assert response[1] == 200
                        data = json.loads(response[0].get_data(as_text=True))
                        assert data["message"] == "Conversation deleted successfully"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_delete_all_conversations_success(self, client, mock_logger):
        """Test successful deletion of all conversations."""
        with patch('cwyodmodules.api.chat_history.ConfigHelper') as mock_config_helper:
            with patch('cwyodmodules.api.chat_history.get_authenticated_user_details') as mock_auth:
                with patch('cwyodmodules.api.chat_history.init_database_client') as mock_init_db:
                    with patch('cwyodmodules.api.chat_history.request') as mock_request:
                        # Setup mocks
                        mock_config = Mock()
                        mock_config.enable_chat_history = True
                        mock_config_helper.get_active_config_or_default.return_value = mock_config

                        mock_auth.return_value = {"user_principal_id": "test-user"}

                        mock_db_client = AsyncMock()
                        mock_init_db.return_value = mock_db_client
                        mock_db_client.delete_all_conversations.return_value = 5

                        mock_request.headers = {"Authorization": "Bearer test-token"}

                        # Execute
                        response = await delete_all_conversations()

                        # Assert
                        assert response[1] == 200
                        data = json.loads(response[0].get_data(as_text=True))
                        assert data["message"] == "All conversations deleted successfully"
                        assert data["deleted_count"] == 5

    @pytest.mark.api
    @pytest.mark.unit
    def test_get_frontend_settings(self, client, mock_logger):
        """Test frontend settings endpoint."""
        with patch('cwyodmodules.api.chat_history.ConfigHelper') as mock_config_helper:
            mock_config = Mock()
            mock_config.enable_chat_history = True
            mock_config_helper.get_active_config_or_default.return_value = mock_config

            response = get_frontend_settings()

            assert response[1] == 200
            data = json.loads(response[0].get_data(as_text=True))
            assert data["enable_chat_history"] is True

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_generate_title_success(self, mock_logger):
        """Test successful title generation."""
        with patch('cwyodmodules.api.chat_history.init_openai_client') as mock_init_openai:
            with patch('cwyodmodules.api.chat_history.env_helper') as mock_env:
                mock_client = AsyncMock()
                mock_init_openai.return_value = mock_client

                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "Generated Title"
                mock_client.chat.completions.create.return_value = mock_response

                conversation_messages = [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ]

                title = await generate_title(conversation_messages)

                assert title == "Generated Title"
                mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_generate_title_exception(self, mock_logger):
        """Test title generation with exception."""
        with patch('cwyodmodules.api.chat_history.init_openai_client') as mock_init_openai:
            mock_client = AsyncMock()
            mock_init_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("OpenAI error")

            conversation_messages = [
                {"role": "user", "content": "Hello"}
            ]

            title = await generate_title(conversation_messages)

            assert title == "New Conversation" 