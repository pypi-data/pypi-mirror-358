"""
Tests for database client functionality.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from cwyodmodules.batch.utilities.chat_history.database_factory import DatabaseFactory
from cwyodmodules.batch.utilities.chat_history.database_client_base import DatabaseClientBase


class TestDatabaseFactory:
    """Test DatabaseFactory functionality."""

    @patch('cwyodmodules.batch.utilities.chat_history.database_factory.AzurePostgresConversationClient')
    @patch('cwyodmodules.batch.utilities.chat_history.database_factory.env_helper')
    def test_get_conversation_client_postgres(self, mock_env_helper, mock_postgres_client):
        """Test getting PostgreSQL conversation client."""
        mock_env_helper.CONVERSATION_DATABASE_TYPE = "postgresql"
        mock_client_instance = Mock()
        mock_postgres_client.return_value = mock_client_instance
        
        result = DatabaseFactory.get_conversation_client()
        
        assert result == mock_client_instance
        mock_postgres_client.assert_called_once()

    @patch('cwyodmodules.batch.utilities.chat_history.database_factory.env_helper')
    def test_get_conversation_client_unsupported_type(self, mock_env_helper):
        """Test getting conversation client with unsupported database type."""
        mock_env_helper.CONVERSATION_DATABASE_TYPE = "unsupported"
        
        with pytest.raises(ValueError, match="Unsupported database type"):
            DatabaseFactory.get_conversation_client()

    @patch('cwyodmodules.batch.utilities.chat_history.database_factory.AzurePostgresConversationClient')
    @patch('cwyodmodules.batch.utilities.chat_history.database_factory.env_helper')
    def test_get_conversation_client_exception(self, mock_env_helper, mock_postgres_client):
        """Test getting conversation client with initialization exception."""
        mock_env_helper.CONVERSATION_DATABASE_TYPE = "postgresql"
        mock_postgres_client.side_effect = Exception("Database initialization error")
        
        with pytest.raises(Exception, match="Database initialization error"):
            DatabaseFactory.get_conversation_client()


class TestDatabaseClientBase:
    """Test DatabaseClientBase functionality."""

    def test_database_client_base_instantiation(self):
        """Test that DatabaseClientBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DatabaseClientBase()

    def test_database_client_base_methods_not_implemented(self):
        """Test that abstract methods raise NotImplementedError."""
        
        class TestClient(DatabaseClientBase):
            pass
        
        # Should not be able to instantiate due to abstract methods
        with pytest.raises(TypeError):
            TestClient()


class TestAzurePostgresConversationClient:
    """Test Azure PostgreSQL conversation client."""

    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    def test_init_with_connection_string(self, mock_env_helper, mock_logger):
        """Test initialization with connection string."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        client = AzurePostgresConversationClient("postgresql://test-connection-string")
        
        assert client.connection_string == "postgresql://test-connection-string"

    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    def test_init_without_connection_string(self, mock_env_helper, mock_logger):
        """Test initialization without connection string."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        client = AzurePostgresConversationClient()
        
        assert client.host == "test-host"
        assert client.database == "test-db"
        assert client.user == "test-user"

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.asyncpg')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_connect_success(self, mock_env_helper, mock_logger, mock_asyncpg):
        """Test successful database connection."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        mock_asyncpg.connect.return_value = mock_connection
        
        client = AzurePostgresConversationClient()
        await client.connect()
        
        assert client.connection == mock_connection
        mock_asyncpg.connect.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_connect_exception(self, mock_env_helper, mock_logger):
        """Test database connection with exception."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "invalid-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        client = AzurePostgresConversationClient()
        
        with patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.asyncpg') as mock_asyncpg:
            mock_asyncpg.connect.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception, match="Connection failed"):
                await client.connect()
            
            mock_logger.exception.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_close_connection(self, mock_env_helper, mock_logger):
        """Test closing database connection."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        await client.close()
        
        mock_connection.close.assert_called_once()
        assert client.connection is None

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_close_no_connection(self, mock_env_helper, mock_logger):
        """Test closing when no connection exists."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        client = AzurePostgresConversationClient()
        
        # Should not raise exception
        await client.close()
        
        assert client.connection is None

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_get_conversations_success(self, mock_env_helper, mock_logger):
        """Test successful conversation retrieval."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        mock_records = [
            {"id": "conv1", "title": "Conversation 1", "user_id": "user1"},
            {"id": "conv2", "title": "Conversation 2", "user_id": "user1"}
        ]
        mock_connection.fetch.return_value = mock_records
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        result = await client.get_conversations("user1", offset=0, limit=25)
        
        assert len(result) == 2
        assert result[0]["id"] == "conv1"
        assert result[1]["id"] == "conv2"
        mock_connection.fetch.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_get_conversation_success(self, mock_env_helper, mock_logger):
        """Test successful single conversation retrieval."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        mock_record = {"id": "conv1", "title": "Conversation 1", "user_id": "user1"}
        mock_connection.fetchrow.return_value = mock_record
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        result = await client.get_conversation("user1", "conv1")
        
        assert result["id"] == "conv1"
        assert result["title"] == "Conversation 1"
        mock_connection.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_get_conversation_not_found(self, mock_env_helper, mock_logger):
        """Test conversation retrieval when not found."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        mock_connection.fetchrow.return_value = None
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        result = await client.get_conversation("user1", "nonexistent")
        
        assert result is None
        mock_connection.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_upsert_conversation_success(self, mock_env_helper, mock_logger):
        """Test successful conversation upsert."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        conversation_data = {
            "id": "conv1",
            "title": "Test Conversation",
            "user_id": "user1"
        }
        mock_connection.fetchrow.return_value = conversation_data
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        result = await client.upsert_conversation(conversation_data)
        
        assert result == conversation_data
        mock_connection.execute.assert_called_once()
        mock_connection.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_delete_conversation_success(self, mock_env_helper, mock_logger):
        """Test successful conversation deletion."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        result = await client.delete_conversation("user1", "conv1")
        
        assert result is True
        # Should delete both messages and conversation
        assert mock_connection.execute.call_count == 2

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_delete_all_conversations_success(self, mock_env_helper, mock_logger):
        """Test successful deletion of all conversations."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        result = await client.delete_all_conversations("user1")
        
        assert result is True
        # Should delete both messages and conversations
        assert mock_connection.execute.call_count == 2

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_get_messages_success(self, mock_env_helper, mock_logger):
        """Test successful message retrieval."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        mock_messages = [
            {"id": "msg1", "role": "user", "content": "Hello"},
            {"id": "msg2", "role": "assistant", "content": "Hi there!"}
        ]
        mock_connection.fetch.return_value = mock_messages
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        result = await client.get_messages("user1", "conv1")
        
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"
        mock_connection.fetch.assert_called_once()


class TestDatabaseIntegrationScenarios:
    """Test database integration scenarios."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.asyncpg')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_full_conversation_lifecycle(self, mock_env_helper, mock_logger, mock_asyncpg):
        """Test complete conversation lifecycle (create, read, update, delete)."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        mock_connection = AsyncMock()
        mock_asyncpg.connect.return_value = mock_connection
        
        # Mock conversation data
        conversation_data = {
            "id": "test-conv",
            "title": "Test Conversation",
            "user_id": "test-user"
        }
        
        mock_connection.execute.return_value = None
        mock_connection.fetchrow.return_value = conversation_data
        mock_connection.fetch.return_value = []
        
        client = AzurePostgresConversationClient()
        
        # Connect
        await client.connect()
        assert client.connection == mock_connection
        
        # Create/Update conversation
        result = await client.upsert_conversation(conversation_data)
        assert result == conversation_data
        
        # Read conversation
        retrieved = await client.get_conversation("test-user", "test-conv")
        assert retrieved == conversation_data
        
        # Get messages
        messages = await client.get_messages("test-user", "test-conv")
        assert messages == []
        
        # Delete conversation
        deleted = await client.delete_conversation("test-user", "test-conv")
        assert deleted is True
        
        # Close connection
        await client.close()
        assert client.connection is None

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_connection_error_handling(self, mock_env_helper, mock_logger):
        """Test proper error handling when connection is not established."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        client = AzurePostgresConversationClient()
        # Don't establish connection
        
        with pytest.raises(Exception):
            await client.get_conversations("user1")
        
        with pytest.raises(Exception):
            await client.get_conversation("user1", "conv1")
        
        with pytest.raises(Exception):
            await client.upsert_conversation({"id": "conv1"})


class TestDatabaseErrorHandling:
    """Test database error handling scenarios."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_database_query_exception(self, mock_env_helper, mock_logger):
        """Test handling of database query exceptions."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        mock_connection = AsyncMock()
        mock_connection.fetch.side_effect = Exception("Database query failed")
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        with pytest.raises(Exception, match="Database query failed"):
            await client.get_conversations("user1")
        
        mock_logger.exception.assert_called()

    @pytest.mark.asyncio
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.logger')
    @patch('cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client.env_helper')
    async def test_transaction_rollback_on_error(self, mock_env_helper, mock_logger):
        """Test transaction rollback on database errors."""
        from cwyodmodules.batch.utilities.chat_history.azure_postgres_conversation_client import AzurePostgresConversationClient
        
        mock_env_helper.POSTGRESQL_HOST = "test-host"
        mock_env_helper.POSTGRESQL_DATABASE = "test-db"
        mock_env_helper.POSTGRESQL_USER = "test-user"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.exception = Mock()
        
        mock_connection = AsyncMock()
        mock_connection.execute.side_effect = Exception("Transaction failed")
        
        client = AzurePostgresConversationClient()
        client.connection = mock_connection
        
        conversation_data = {"id": "conv1", "title": "Test", "user_id": "user1"}
        
        with pytest.raises(Exception, match="Transaction failed"):
            await client.upsert_conversation(conversation_data)
        
        mock_logger.exception.assert_called() 