"""
Integration tests for cwyodmodules.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestIntegrationWorkflows:
    """Test key integration workflows."""

    @pytest.mark.asyncio
    @patch('cwyodmodules.api.chat_history.ConfigHelper')
    @patch('cwyodmodules.api.chat_history.get_authenticated_user_details')
    @patch('cwyodmodules.api.chat_history.init_database_client')
    @patch('cwyodmodules.api.chat_history.logger')
    async def test_chat_history_workflow(self, mock_logger, mock_init_db, mock_auth, mock_config_helper):
        """Test complete chat history workflow."""
        # Setup mocks
        mock_config = Mock()
        mock_config.enable_chat_history = True
        mock_config_helper.get_active_config_or_default.return_value = mock_config
        
        mock_auth.return_value = {"user_principal_id": "test-user"}
        
        mock_db_client = AsyncMock()
        mock_db_client.connect = AsyncMock()
        mock_db_client.close = AsyncMock()
        mock_db_client.get_conversations = AsyncMock(return_value=[{"id": "conv1"}])
        mock_db_client.get_conversation = AsyncMock(return_value={"id": "conv1", "title": "Test"})
        mock_db_client.upsert_conversation = AsyncMock(return_value={"id": "conv1", "title": "Updated"})
        mock_init_db.return_value = mock_db_client
        
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        
        # Import after mocking
        from cwyodmodules.api.chat_history import list_conversations, rename_conversation
        
        # Test list conversations
        conversations = await list_conversations()
        assert conversations is not None
        
        # Test rename conversation - need to mock request context
        with patch('cwyodmodules.api.chat_history.request') as mock_request:
            mock_request.get_json.return_value = {"conversation_id": "conv1", "title": "Updated"}
            mock_request.headers = {}
            
            result = await rename_conversation()
            assert result is not None

    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.identity')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.logger')
    def test_env_helper_integration(self, mock_logger, mock_identity, mock_head_keyvault, mock_keyvault):
        """Test EnvHelper integration with dependencies."""
        import os
        from cwyodmodules.batch.utilities.helpers.env_helper import EnvHelper
        
        # Setup mocks
        mock_keyvault.get_secret.side_effect = lambda key: f"mock_{key.replace('-', '_')}"
        mock_head_keyvault.get_secret.side_effect = lambda key: f"head_{key.replace('-', '_')}"
        mock_identity.get_token_provider.return_value = "mock_token"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.info = Mock()
        
        with patch.dict(os.environ, {
            "AZURE_CLIENT_ID": "test-client",
            "key_vault_uri": "https://test.vault.azure.net/",
            "head_key_vault_uri": "https://test-head.vault.azure.net/"
        }):
            EnvHelper.clear_instance()
            env_helper = EnvHelper()
            
            # Test configuration loaded correctly
            assert env_helper.AZURE_AUTH_TYPE == "rbac"
            assert env_helper.PROJECT_CODE == "mock_project_code"
            assert env_helper.AZURE_TOKEN_PROVIDER == "mock_token"

    def test_answer_and_source_document_integration(self):
        """Test Answer and SourceDocument integration."""
        from cwyodmodules.batch.utilities.common.answer import Answer
        from cwyodmodules.batch.utilities.common.source_document import SourceDocument
        
        # Create source documents
        source1 = SourceDocument(
            id="doc1",
            content="Content 1",
            title="Document 1",
            source="https://example.com/doc1"
        )
        
        source2 = SourceDocument(
            id="doc2", 
            content="Content 2",
            title="Document 2",
            source="https://example.com/doc2"
        )
        
        # Create answer with sources
        answer = Answer(
            question="Test question?",
            answer="Test answer",
            source_documents=[source1, source2],
            prompt_tokens=10,
            completion_tokens=20
        )
        
        # Test serialization
        json_str = answer.to_json()
        assert json_str is not None
        
        # Test string representation
        str_repr = str(answer)
        assert "Test answer" in str_repr
        assert "Sources:" in str_repr
        assert "Document 1" in str_repr
        assert "Document 2" in str_repr


class TestErrorScenarios:
    """Test error handling across modules."""

    def test_env_helper_missing_keyvault(self):
        """Test EnvHelper with missing keyvault configuration."""
        import os
        from cwyodmodules.batch.utilities.helpers.env_helper import EnvHelper
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault', None):
                EnvHelper.clear_instance()
                
                with pytest.raises(ValueError, match="keyvault is not configured"):
                    EnvHelper()

    def test_answer_equality_edge_cases(self):
        """Test Answer equality with edge cases."""
        from cwyodmodules.batch.utilities.common.answer import Answer
        
        answer1 = Answer("Q1", "A1")
        answer2 = Answer("Q1", "A1")
        answer3 = Answer("Q1", "A2")
        
        assert answer1 == answer2
        assert answer1 != answer3
        assert answer1 != "not an answer"
        assert answer1 != None

    def test_source_document_serialization_edge_cases(self):
        """Test SourceDocument serialization with edge cases."""
        from cwyodmodules.batch.utilities.common.source_document import SourceDocument
        import json
        
        # Test with None values
        doc = SourceDocument(
            id="test",
            content="test content",
            title=None,
            source="test source",
            metadata=None
        )
        
        json_str = doc.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["title"] is None
        assert parsed["metadata"] is None
        
        # Test round-trip
        restored = SourceDocument.from_json(json_str)
        assert restored == doc


class TestPerformanceIntegration:
    """Test performance aspects of integration."""

    def test_large_answer_with_many_sources(self):
        """Test Answer with many source documents."""
        from cwyodmodules.batch.utilities.common.answer import Answer
        from cwyodmodules.batch.utilities.common.source_document import SourceDocument
        
        # Create many source documents
        sources = []
        for i in range(100):
            source = SourceDocument(
                id=f"doc{i}",
                content=f"Content {i}",
                title=f"Document {i}",
                source=f"https://example.com/doc{i}"
            )
            sources.append(source)
        
        answer = Answer(
            question="Complex question with many sources?",
            answer="Complex answer with comprehensive sourcing.",
            source_documents=sources
        )
        
        # Test string representation performance
        str_repr = str(answer)
        assert len(str_repr) > 1000
        assert "Document 0" in str_repr
        assert "Document 99" in str_repr
        
        # Test serialization performance
        json_str = answer.to_json()
        assert len(json_str) > 5000

    def test_env_helper_concurrent_access(self):
        """Test EnvHelper singleton with concurrent access."""
        import threading
        import os
        from cwyodmodules.batch.utilities.helpers.env_helper import EnvHelper
        
        instances = []
        
        def create_instance():
            with patch.dict(os.environ, {
                "AZURE_CLIENT_ID": "test-client",
                "key_vault_uri": "https://test.vault.azure.net/",
                "head_key_vault_uri": "https://test-head.vault.azure.net/"
            }):
                with patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault'):
                    with patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault'):
                        with patch('cwyodmodules.batch.utilities.helpers.env_helper.identity'):
                            with patch('cwyodmodules.batch.utilities.helpers.env_helper.logger') as mock_logger:
                                mock_logger.trace_function = lambda **kwargs: lambda func: func
                                mock_logger.info = Mock()
                                instances.append(EnvHelper())
        
        EnvHelper.clear_instance()
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        assert len(instances) == 10
        for instance in instances[1:]:
            assert instance is instances[0] 