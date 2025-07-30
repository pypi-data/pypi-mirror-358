"""
Tests for EnvHelper module.
"""
import sys
from unittest.mock import Mock

if 'cwyodmodules.batch.utilities.helpers.env_helper' in sys.modules:
    del sys.modules['cwyodmodules.batch.utilities.helpers.env_helper']
if 'cwyodmodules.batch.utilities.helpers' in sys.modules:
    del sys.modules['cwyodmodules.batch.utilities.helpers']

# The mgmt_config module is mocked by pytest_plugins.py.
# The mock is missing some attributes that env_helper needs for import.
if 'mgmt_config' in sys.modules:
    mgmt_config_mock = sys.modules['mgmt_config']
    if not hasattr(mgmt_config_mock, 'head_keyvault'):
        mgmt_config_mock.head_keyvault = Mock()

import pytest
import os
import threading
from unittest.mock import Mock, patch, MagicMock
from cwyodmodules.batch.utilities.helpers.env_helper import EnvHelper


class TestEnvHelperInitialization:
    """Test EnvHelper initialization and singleton behavior."""

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "key_vault_uri": "https://test-kv.vault.azure.net/",
        "head_key_vault_uri": "https://test-head-kv.vault.azure.net/"
    })
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.identity')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.logger')
    def test_init_with_valid_config(self, mock_logger, mock_identity, mock_head_keyvault, mock_keyvault):
        """Test EnvHelper initializes with valid configuration."""
        # Setup mocks
        mock_keyvault.get_secret.side_effect = self._mock_keyvault_secrets
        mock_head_keyvault.get_secret.side_effect = self._mock_head_keyvault_secrets
        mock_identity.get_token_provider.return_value = "mock_token_provider"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.info = Mock()
        
        # Clear singleton
        EnvHelper.clear_instance()
        
        # Create instance
        env_helper = EnvHelper()
        
        # Verify initialization
        assert env_helper.AZURE_CLIENT_ID == "test-client-id"
        assert env_helper.PROJECT_CODE == "mock_project_code"
        assert env_helper.AZURE_RESOURCE_GROUP == "mock_resource_group_name"
        assert env_helper.AZURE_OPENAI_MODEL == "gpt-4o-default"
        assert env_helper.AZURE_AUTH_TYPE == "rbac"
        assert env_helper.LOG_EXECUTION is True
        assert env_helper.LOG_ARGS is True
        assert env_helper.LOG_RESULT is True
        
        # Verify keyvault calls
        mock_keyvault.get_secret.assert_any_call("logging-level")
        mock_keyvault.get_secret.assert_any_call("subscription-id")
        mock_keyvault.get_secret.assert_any_call("resource-group-name")
        
        # Verify head keyvault calls
        mock_head_keyvault.get_secret.assert_any_call("resource-group-name")
        mock_head_keyvault.get_secret.assert_any_call("cognitive-kind-AIServices")

    def test_singleton_behavior(self):
        """Test that EnvHelper follows singleton pattern."""
        # Clear singleton
        EnvHelper.clear_instance()
        
        with patch.dict(os.environ, {
            "AZURE_CLIENT_ID": "test-client-id",
            "key_vault_uri": "https://test-kv.vault.azure.net/",
            "head_key_vault_uri": "https://test-head-kv.vault.azure.net/"
        }):
            with patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault'):
                with patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault'):
                    with patch('cwyodmodules.batch.utilities.helpers.env_helper.identity'):
                        with patch('cwyodmodules.batch.utilities.helpers.env_helper.logger') as mock_logger:
                            mock_logger.trace_function = lambda **kwargs: lambda func: func
                            mock_logger.info = Mock()
                            
                            instance1 = EnvHelper()
                            instance2 = EnvHelper()
                            
                            assert instance1 is instance2

    def test_thread_safety(self):
        """Test that EnvHelper singleton is thread-safe."""
        # Clear singleton
        EnvHelper.clear_instance()
        
        instances = []
        
        def create_instance():
            with patch.dict(os.environ, {
                "AZURE_CLIENT_ID": "test-client-id",
                "key_vault_uri": "https://test-kv.vault.azure.net/",
                "head_key_vault_uri": "https://test-head-kv.vault.azure.net/"
            }):
                with patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault'):
                    with patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault'):
                        with patch('cwyodmodules.batch.utilities.helpers.env_helper.identity'):
                            with patch('cwyodmodules.batch.utilities.helpers.env_helper.logger') as mock_logger:
                                mock_logger.trace_function = lambda **kwargs: lambda func: func
                                mock_logger.info = Mock()
                                instances.append(EnvHelper())
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        for instance in instances[1:]:
            assert instance is instances[0]

    @patch.dict(os.environ, {}, clear=True)
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault', None)
    def test_init_missing_keyvault(self):
        """Test proper error handling when keyvault is not configured."""
        EnvHelper.clear_instance()
        
        with pytest.raises(ValueError, match="keyvault is not configured"):
            EnvHelper()

    @patch.dict(os.environ, {
        "key_vault_uri": "https://test-kv.vault.azure.net/"
    })
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault', Mock())
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault', None)
    def test_init_missing_head_keyvault(self):
        """Test proper error handling when head_keyvault is not configured."""
        EnvHelper.clear_instance()
        
        with pytest.raises(ValueError, match="head_keyvault is not configured"):
            EnvHelper()

    def _mock_keyvault_secrets(self, key):
        """Mock keyvault secret responses."""
        secrets = {
            "logging-level": "INFO",
            "subscription-id": "mock-subscription-id",
            "resource-group-name": "mock_resource_group_name",
            "resource-group-environment": "dev",
            "run-private-endpoint": "false",
            "project-code": "mock_project_code",
            "cognitive-kind-FormRecognizer": "mock-form-recognizer",
            "mock-form-recognizer-endpoint": "https://mock-fr.cognitiveservices.azure.com/"
        }
        return secrets.get(key, f"mock_{key.replace('-', '_')}")

    def _mock_head_keyvault_secrets(self, key):
        """Mock head keyvault secret responses."""
        secrets = {
            "resource-group-name": "mock-head-resource-group",
            "cognitive-kind-AIServices": "mock-ai-services",
            "cognitive-kind-ComputerVision": "mock-computer-vision",
            "cognitive-kind-ContentSafety": "mock-content-safety"
        }
        return secrets.get(key, f"mock_head_{key.replace('-', '_')}")


class TestEnvHelperMethods:
    """Test EnvHelper utility methods."""

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "key_vault_uri": "https://test-kv.vault.azure.net/",
        "head_key_vault_uri": "https://test-head-kv.vault.azure.net/"
    })
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.identity')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.logger')
    def setup_method(self, method, mock_logger, mock_identity, mock_head_keyvault, mock_keyvault):
        """Set up test environment."""
        mock_keyvault.get_secret.side_effect = lambda key: f"mock_{key.replace('-', '_')}"
        mock_head_keyvault.get_secret.side_effect = lambda key: f"mock_head_{key.replace('-', '_')}"
        mock_identity.get_token_provider.return_value = "mock_token_provider"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.info = Mock()
        
        EnvHelper.clear_instance()
        self.env_helper = EnvHelper()

    def test_is_chat_model(self):
        """Test is_chat_model method."""
        result = self.env_helper.is_chat_model()
        assert isinstance(result, bool)

    def test_get_env_var_bool_true(self):
        """Test get_env_var_bool with true values."""
        with patch.dict(os.environ, {"TEST_BOOL": "true"}):
            assert self.env_helper.get_env_var_bool("TEST_BOOL") is True
        
        with patch.dict(os.environ, {"TEST_BOOL": "True"}):
            assert self.env_helper.get_env_var_bool("TEST_BOOL") is True
        
        with patch.dict(os.environ, {"TEST_BOOL": "TRUE"}):
            assert self.env_helper.get_env_var_bool("TEST_BOOL") is True

    def test_get_env_var_bool_false(self):
        """Test get_env_var_bool with false values."""
        with patch.dict(os.environ, {"TEST_BOOL": "false"}):
            assert self.env_helper.get_env_var_bool("TEST_BOOL") is False
        
        with patch.dict(os.environ, {"TEST_BOOL": "False"}):
            assert self.env_helper.get_env_var_bool("TEST_BOOL") is False
        
        with patch.dict(os.environ, {"TEST_BOOL": "anything"}):
            assert self.env_helper.get_env_var_bool("TEST_BOOL") is False

    def test_get_env_var_bool_default(self):
        """Test get_env_var_bool with default values."""
        with patch.dict(os.environ, {}, clear=True):
            assert self.env_helper.get_env_var_bool("NONEXISTENT", "True") is True
            assert self.env_helper.get_env_var_bool("NONEXISTENT", "False") is False

    def test_get_env_var_array(self):
        """Test get_env_var_array method."""
        with patch.dict(os.environ, {"TEST_ARRAY": "item1,item2,item3"}):
            result = self.env_helper.get_env_var_array("TEST_ARRAY")
            assert result == ["item1", "item2", "item3"]
        
        with patch.dict(os.environ, {"TEST_ARRAY": "single_item"}):
            result = self.env_helper.get_env_var_array("TEST_ARRAY")
            assert result == ["single_item"]
        
        with patch.dict(os.environ, {}, clear=True):
            result = self.env_helper.get_env_var_array("NONEXISTENT", "default1,default2")
            assert result == ["default1", "default2"]

    def test_get_env_var_int(self):
        """Test get_env_var_int method."""
        with patch.dict(os.environ, {"TEST_INT": "42"}):
            result = self.env_helper.get_env_var_int("TEST_INT", 0)
            assert result == 42
        
        with patch.dict(os.environ, {"TEST_INT": "invalid"}):
            result = self.env_helper.get_env_var_int("TEST_INT", 10)
            assert result == 10
        
        with patch.dict(os.environ, {}, clear=True):
            result = self.env_helper.get_env_var_int("NONEXISTENT", 5)
            assert result == 5

    def test_get_env_var_float(self):
        """Test get_env_var_float method."""
        with patch.dict(os.environ, {"TEST_FLOAT": "3.14"}):
            result = self.env_helper.get_env_var_float("TEST_FLOAT", 0.0)
            assert result == 3.14
        
        with patch.dict(os.environ, {"TEST_FLOAT": "invalid"}):
            result = self.env_helper.get_env_var_float("TEST_FLOAT", 1.0)
            assert result == 1.0
        
        with patch.dict(os.environ, {}, clear=True):
            result = self.env_helper.get_env_var_float("NONEXISTENT", 2.5)
            assert result == 2.5

    def test_is_auth_type_keys(self):
        """Test is_auth_type_keys method."""
        self.env_helper.AZURE_AUTH_TYPE = "keys"
        assert self.env_helper.is_auth_type_keys() is True
        
        self.env_helper.AZURE_AUTH_TYPE = "rbac"
        assert self.env_helper.is_auth_type_keys() is False

    def test_get_info_from_env_valid_json(self):
        """Test get_info_from_env with valid JSON."""
        test_json = '{"key1": "value1", "key2": "value2"}'
        with patch.dict(os.environ, {"TEST_INFO": test_json}):
            result = self.env_helper.get_info_from_env("TEST_INFO", "{}")
            assert result == {"key1": "value1", "key2": "value2"}

    def test_get_info_from_env_invalid_json(self):
        """Test get_info_from_env with invalid JSON."""
        with patch.dict(os.environ, {"TEST_INFO": "invalid json"}):
            result = self.env_helper.get_info_from_env("TEST_INFO", '{"default": "value"}')
            assert result == {"default": "value"}

    def test_get_info_from_env_missing_var(self):
        """Test get_info_from_env with missing environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            result = self.env_helper.get_info_from_env("NONEXISTENT", '{"default": "value"}')
            assert result == {"default": "value"}

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "key_vault_uri": "https://test-kv.vault.azure.net/",
        "head_key_vault_uri": "https://test-head-kv.vault.azure.net/"
    })
    def test_check_env(self):
        """Test check_env static method."""
        result = EnvHelper.check_env()
        # check_env should return without error
        assert result is None

    def test_clear_instance(self):
        """Test clear_instance class method."""
        EnvHelper.clear_instance()
        assert EnvHelper._instance is None


class TestEnvHelperConfigurationProperties:
    """Test EnvHelper configuration property setting."""

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "key_vault_uri": "https://test-kv.vault.azure.net/",
        "head_key_vault_uri": "https://test-head-kv.vault.azure.net/",
        "REFLECTION_NAME": "CustomApp"
    })
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.identity')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.logger')
    def test_custom_app_name(self, mock_logger, mock_identity, mock_head_keyvault, mock_keyvault):
        """Test custom app name configuration."""
        mock_keyvault.get_secret.side_effect = lambda key: f"mock_{key.replace('-', '_')}"
        mock_head_keyvault.get_secret.side_effect = lambda key: f"mock_head_{key.replace('-', '_')}"
        mock_identity.get_token_provider.return_value = "mock_token_provider"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.info = Mock()
        
        EnvHelper.clear_instance()
        env_helper = EnvHelper()
        
        assert env_helper.APP_NAME == "CustomApp"

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "key_vault_uri": "https://test-kv.vault.azure.net/",
        "head_key_vault_uri": "https://test-head-kv.vault.azure.net/",
        "AZURE_POSTGRESQL_INFO": '{"user": "custom_user", "dbname": "custom_db", "host": "custom_host"}'
    })
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.identity')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.logger')
    def test_custom_postgresql_config(self, mock_logger, mock_identity, mock_head_keyvault, mock_keyvault):
        """Test custom PostgreSQL configuration."""
        mock_keyvault.get_secret.side_effect = lambda key: f"mock_{key.replace('-', '_')}"
        mock_head_keyvault.get_secret.side_effect = lambda key: f"mock_head_{key.replace('-', '_')}"
        mock_identity.get_token_provider.return_value = "mock_token_provider"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.info = Mock()
        
        EnvHelper.clear_instance()
        env_helper = EnvHelper()
        
        assert env_helper.POSTGRESQL_USER == "custom_user"
        assert env_helper.POSTGRESQL_DATABASE == "custom_db"
        assert env_helper.POSTGRESQL_HOST == "custom_host"


class TestEnvHelperEdgeCases:
    """Test EnvHelper edge cases and error handling."""

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "key_vault_uri": "https://test-kv.vault.azure.net/",
        "head_key_vault_uri": "https://test-head-kv.vault.azure.net/"
    })
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.identity')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.logger')
    def test_keyvault_secret_exception(self, mock_logger, mock_identity, mock_head_keyvault, mock_keyvault):
        """Test handling of keyvault secret retrieval exceptions."""
        mock_keyvault.get_secret.side_effect = Exception("KeyVault error")
        mock_head_keyvault.get_secret.side_effect = lambda key: f"mock_head_{key.replace('-', '_')}"
        mock_identity.get_token_provider.return_value = "mock_token_provider"
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.info = Mock()
        
        EnvHelper.clear_instance()
        
        with pytest.raises(Exception, match="KeyVault error"):
            EnvHelper()

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "key_vault_uri": "https://test-kv.vault.azure.net/",
        "head_key_vault_uri": "https://test-head-kv.vault.azure.net/"
    })
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.identity')
    @patch('cwyodmodules.batch.utilities.helpers.env_helper.logger')
    def test_identity_token_provider_exception(self, mock_logger, mock_identity, mock_head_keyvault, mock_keyvault):
        """Test handling of identity token provider exceptions."""
        mock_keyvault.get_secret.side_effect = lambda key: f"mock_{key.replace('-', '_')}"
        mock_head_keyvault.get_secret.side_effect = lambda key: f"mock_head_{key.replace('-', '_')}"
        mock_identity.get_token_provider.side_effect = Exception("Identity error")
        mock_logger.trace_function = lambda **kwargs: lambda func: func
        mock_logger.info = Mock()
        
        EnvHelper.clear_instance()
        
        with pytest.raises(Exception, match="Identity error"):
            EnvHelper()

    def test_concurrent_initialization(self):
        """Test concurrent initialization doesn't cause issues."""
        import concurrent.futures
        
        EnvHelper.clear_instance()
        
        def init_env_helper():
            with patch.dict(os.environ, {
                "AZURE_CLIENT_ID": "test-client-id",
                "key_vault_uri": "https://test-kv.vault.azure.net/",
                "head_key_vault_uri": "https://test-head-kv.vault.azure.net/"
            }):
                with patch('cwyodmodules.batch.utilities.helpers.env_helper.keyvault'):
                    with patch('cwyodmodules.batch.utilities.helpers.env_helper.head_keyvault'):
                        with patch('cwyodmodules.batch.utilities.helpers.env_helper.identity'):
                            with patch('cwyodmodules.batch.utilities.helpers.env_helper.logger') as mock_logger:
                                mock_logger.trace_function = lambda **kwargs: lambda func: func
                                mock_logger.info = Mock()
                                return EnvHelper()
        
        # Test concurrent initialization
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(init_env_helper) for _ in range(10)]
            instances = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All instances should be the same
        for instance in instances[1:]:
            assert instance is instances[0] 