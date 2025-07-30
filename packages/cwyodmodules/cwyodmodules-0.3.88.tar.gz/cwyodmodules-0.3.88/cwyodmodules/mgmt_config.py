"""Azure Project Management Configuration Template.

This module provides standardized configuration for Azure logging, identity management,
and Key Vault access across projects. It creates singleton instances that can be
imported and used throughout your application.

The configuration is driven by environment variables with sensible defaults, allowing
for flexible deployment across different environments (local development, staging,
production) without code changes.

Features:
    - Automatic service detection (app vs function app)
    - Configurable logging with Application Insights integration
    - Azure identity management with token caching
    - Key Vault integration for secrets, keys, and certificates
    - Docker environment detection
    - Local development environment setup

Usage:
    Basic usage::
    
        from mgmt_config import logger, identity
        
        logger.info("Application started")
        credential = identity.get_credential()
    
    With Key Vault::
    
        from mgmt_config import keyvault
        
        if keyvault:
            secret_value = keyvault.get_secret("my-secret")

Environment Variables:
    Service Configuration:
        REFLECTION_NAME: Service name for identification
        REFLECTION_KIND: Service type (app, functionapp, etc.)
        SERVICE_VERSION: Version of the service (default: "1.0.0")
    
    Logging Configuration:
        LOGGER_ENABLE_CONSOLE: Enable console logging (default: "true")
        APPLICATIONINSIGHTS_CONNECTION_STRING: App Insights connection string
    
    Identity Configuration:
        IDENTITY_ENABLE_TOKEN_CACHE: Enable token caching (default: "true")
        IDENTITY_ALLOW_UNENCRYPTED_STORAGE: Allow unencrypted token storage (default: "true")
    
    Key Vault Configuration:
        key_vault_uri: Primary Key Vault URL
        head_key_vault_uri: Secondary Key Vault URL
        KEYVAULT_ENABLE_SECRETS: Enable secrets client (default: "true")
        KEYVAULT_ENABLE_KEYS: Enable keys client (default: "false")
        KEYVAULT_ENABLE_CERTIFICATES: Enable certificates client (default: "false")

Examples:
    Local Development:
        Set REFLECTION_NAME and ensure .env file exists for local settings.
    
    Azure Function App:
        Set REFLECTION_KIND="functionapp" and REFLECTION_NAME to your function app name.
    
    Web Application:
        Set REFLECTION_KIND="app" (or leave default) and configure App Insights.
"""

import os
from typing import Any, Dict, Optional

from azpaddypy.mgmt.identity import create_azure_identity
from azpaddypy.mgmt.local_env_manager import create_local_env_manager
from azpaddypy.mgmt.logging import create_app_logger, create_function_logger
from azpaddypy.resources.keyvault import create_azure_keyvault


# =============================================================================
# DOCKER ENVIRONMENT DETECTION
# =============================================================================

def is_running_in_docker() -> bool:
    """Check if the current process is running inside a Docker container.

    This function uses multiple detection methods to reliably identify
    Docker environments across different container runtimes and orchestrators.

    Returns:
        True if running in Docker/container, False otherwise.
        
    Detection Methods:
        1. Check for /.dockerenv file (standard Docker indicator)
        2. Check /proc/1/cgroup for container-specific entries
        3. Handles various container runtimes (Docker, Kubernetes, etc.)
    """
    # Method 1: Check for Docker environment file
    if os.path.exists('/.dockerenv'):
        return True

    # Method 2: Check process control groups for container indicators
    try:
        with open('/proc/1/cgroup', 'rt', encoding='utf-8') as f:
            cgroup_content = f.read()
            return any(indicator in cgroup_content 
                      for indicator in ['docker', 'kubepods', 'containerd'])
    except (FileNotFoundError, PermissionError, OSError):
        # /proc filesystem not available or accessible (e.g., Windows, macOS)
        pass

    return False


RUNNING_IN_DOCKER = is_running_in_docker()
print(f"is_running_in_docker: {RUNNING_IN_DOCKER}")

# =============================================================================
# LOCAL DEVELOPMENT CONFIGURATION
# =============================================================================

def _get_local_settings() -> Dict[str, str]:
    """Get local development settings based on environment.
    
    Returns:
        Dictionary of local development settings appropriate for the environment.
        
    Note:
        Docker environments get Azure service principal settings,
        while local environments get Azure Storage Emulator settings.
    """
    if RUNNING_IN_DOCKER:
        return {
            "AZURE_CLIENT_ID": "aa73da4a-2888-4cb7-896e-5d51125f11f0",
            "AZURE_TENANT_ID": "e5590d5d-336c-4cf5-b0ac-b79a598ec797",
            "AZURE_CLIENT_SECRET": "IQ08Q~4uCfc4B~p2F95D2737GzYvvrtIjursFbCf"
        }
    else:
        return {
            "AzureWebJobsStorage": "UseDevelopmentStorage=true",
            "AzureWebJobsDashboard": "UseDevelopmentStorage=true",
            "input_queue_connection__queueServiceUri": "UseDevelopmentStorage=true",
            "AzureWebJobsStorage__accountName": "UseDevelopmentStorage=true",
            "AzureWebJobsStorage__blobServiceUri": "UseDevelopmentStorage=true",
            "AZURE_CLIENT_ID": "aa73da4a-2888-4cb7-896e-5d51125f11f0",
            "AZURE_TENANT_ID": "e5590d5d-336c-4cf5-b0ac-b79a598ec797",
            "AZURE_CLIENT_SECRET": "IQ08Q~4uCfc4B~p2F95D2737GzYvvrtIjursFbCf"
        }

# Initialize local environment manager
local_env_manager = create_local_env_manager(
    file_path=".env",
    settings=_get_local_settings(),
    override_json=True,
    override_dotenv=True,
    override_settings=True,
)

# =============================================================================
# SERVICE CONFIGURATION
# =============================================================================

def _get_service_configuration() -> tuple[str, str, str]:
    """Get service configuration from environment variables.
    
    Returns:
        A tuple containing (service_name, service_version, service_kind).
        
    Note:
        REFLECTION_KIND has commas replaced with hyphens for compatibility.
    """
    reflection_name = os.getenv("REFLECTION_NAME")
    reflection_kind = os.getenv("REFLECTION_KIND", "").replace(",", "-")
    service_name = reflection_name or str(__name__)
    service_version = os.getenv("SERVICE_VERSION", "1.0.0")
    
    return service_name, service_version, reflection_kind


SERVICE_NAME, SERVICE_VERSION, REFLECTION_KIND = _get_service_configuration()

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def _get_logging_configuration() -> tuple[bool, Optional[str], Dict[str, Dict[str, bool]]]:
    """Get logging configuration from environment variables.
    
    Returns:
        A tuple containing (console_enabled, connection_string, instrumentation_options).
    """
    console_enabled = os.getenv("LOGGER_ENABLE_CONSOLE", "true").lower() == "true"
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    log_level = os.getenv("LOGGER_LOG_LEVEL", "INFO")
    enable_console_logging = os.getenv("LOGGER_ENABLE_CONSOLE", "true").lower() == "true"
    
    instrumentation_options = {
        "azure_sdk": {"enabled": True},
        "django": {"enabled": False},
        "fastapi": {"enabled": False},
        "flask": {"enabled": True},
        "psycopg2": {"enabled": True},
        "requests": {"enabled": True},
        "urllib": {"enabled": True},
        "urllib3": {"enabled": True},
    }
    
    return console_enabled, connection_string, instrumentation_options, log_level


LOGGER_ENABLE_CONSOLE, LOGGER_CONNECTION_STRING, LOGGER_INSTRUMENTATION_OPTIONS, LOGGER_LOG_LEVEL = _get_logging_configuration()

# =============================================================================
# IDENTITY CONFIGURATION
# =============================================================================

def _get_identity_configuration() -> tuple[bool, bool, Optional[Dict[str, Any]], Optional[str]]:
    """Get identity configuration from environment variables.
    
    Returns:
        A tuple containing (token_cache_enabled, unencrypted_storage_allowed, 
        custom_options, connection_string).
    """
    token_cache_enabled = os.getenv("IDENTITY_ENABLE_TOKEN_CACHE", "true").lower() == "true"
    unencrypted_storage_allowed = os.getenv("IDENTITY_ALLOW_UNENCRYPTED_STORAGE", "true").lower() == "true"
    custom_options = None  # Reserved for future custom credential configuration
    connection_string = LOGGER_CONNECTION_STRING  # Share with logger by default
    
    return token_cache_enabled, unencrypted_storage_allowed, custom_options, connection_string


(IDENTITY_ENABLE_TOKEN_CACHE, 
 IDENTITY_ALLOW_UNENCRYPTED_STORAGE, 
 IDENTITY_CUSTOM_CREDENTIAL_OPTIONS, 
 IDENTITY_CONNECTION_STRING) = _get_identity_configuration()

# =============================================================================
# KEY VAULT CONFIGURATION
# =============================================================================

def _get_keyvault_configuration() -> tuple[Optional[str], Optional[str], bool, bool, bool, Optional[str]]:
    """Get Key Vault configuration from environment variables.
    
    Returns:
        A tuple containing (vault_url, head_vault_url, secrets_enabled, 
        keys_enabled, certificates_enabled, connection_string).
    """
    vault_url = os.getenv("key_vault_uri")
    head_vault_url = os.getenv("head_key_vault_uri")
    secrets_enabled = os.getenv("KEYVAULT_ENABLE_SECRETS", "true").lower() == "true"
    keys_enabled = os.getenv("KEYVAULT_ENABLE_KEYS", "false").lower() == "true"
    certificates_enabled = os.getenv("KEYVAULT_ENABLE_CERTIFICATES", "false").lower() == "true"
    connection_string = LOGGER_CONNECTION_STRING  # Share with logger by default
    
    return vault_url, head_vault_url, secrets_enabled, keys_enabled, certificates_enabled, connection_string


(KEYVAULT_URL, 
 HEAD_KEYVAULT_URL, 
 KEYVAULT_ENABLE_SECRETS, 
 KEYVAULT_ENABLE_KEYS, 
 KEYVAULT_ENABLE_CERTIFICATES, 
 KEYVAULT_CONNECTION_STRING) = _get_keyvault_configuration()

# =============================================================================
# SERVICE INITIALIZATION
# =============================================================================

def _create_logger():
    """Create and configure the appropriate logger instance.
    
    Returns:
        Configured AzureLogger instance (either app or function logger).
        
    Note:
        Logger type is determined by REFLECTION_KIND environment variable.
        Function apps get specialized function loggers with additional context.
    """
    if "functionapp" in REFLECTION_KIND:
        logger_instance = create_function_logger(
            function_app_name=SERVICE_NAME,
            function_name=REFLECTION_KIND,
            service_version=SERVICE_VERSION,
            connection_string=LOGGER_CONNECTION_STRING,
            log_level=LOGGER_LOG_LEVEL,
            instrumentation_options=LOGGER_INSTRUMENTATION_OPTIONS, 
        )
        logger_instance.info(
            f"Function logger initialized: {REFLECTION_KIND} {SERVICE_NAME}",
            extra={"logger_type": "function", "function_name": REFLECTION_KIND}
        )
    else:
        logger_instance = create_app_logger(
            service_name=SERVICE_NAME,
            service_version=SERVICE_VERSION,
            connection_string=LOGGER_CONNECTION_STRING,
            log_level=LOGGER_LOG_LEVEL,
            enable_console_logging=LOGGER_ENABLE_CONSOLE,
            instrumentation_options=LOGGER_INSTRUMENTATION_OPTIONS,
        )
        logger_instance.info(
            f"App logger initialized: {REFLECTION_KIND} {SERVICE_NAME}",
            extra={"logger_type": "app", "service_kind": REFLECTION_KIND}
        )
    
    return logger_instance


def _create_identity_manager(logger_instance):
    """Create and configure the Azure identity manager.
    
    Args:
        logger_instance: Shared logger instance for identity operations.
        
    Returns:
        Configured AzureIdentity instance.
    """
    return create_azure_identity(
        service_name=SERVICE_NAME,
        service_version=SERVICE_VERSION,
        enable_token_cache=IDENTITY_ENABLE_TOKEN_CACHE,
        allow_unencrypted_storage=IDENTITY_ALLOW_UNENCRYPTED_STORAGE,
        custom_credential_options=IDENTITY_CUSTOM_CREDENTIAL_OPTIONS,
        connection_string=IDENTITY_CONNECTION_STRING,
        logger=logger_instance,
    )


def _create_keyvault_client(vault_url: str, identity_instance, logger_instance):
    """Create a Key Vault client for the specified vault.
    
    Args:
        vault_url: Azure Key Vault URL.
        identity_instance: Shared identity manager.
        logger_instance: Shared logger instance.
        
    Returns:
        Configured AzureKeyVault instance or None if creation fails.
    """
    if not vault_url:
        return None
        
    return create_azure_keyvault(
        vault_url=vault_url,
        azure_identity=identity_instance,
        service_name=SERVICE_NAME,
        service_version=SERVICE_VERSION,
        logger=logger_instance,
        connection_string=KEYVAULT_CONNECTION_STRING,
        enable_secrets=KEYVAULT_ENABLE_SECRETS,
        enable_keys=KEYVAULT_ENABLE_KEYS,
        enable_certificates=KEYVAULT_ENABLE_CERTIFICATES,
    )


# Initialize core services
logger = _create_logger()
identity = _create_identity_manager(logger)

# Initialize Key Vault clients (if URLs are configured)
keyvault = _create_keyvault_client(KEYVAULT_URL, identity, logger)
head_keyvault = _create_keyvault_client(HEAD_KEYVAULT_URL, identity, logger)

# =============================================================================
# CONFIGURATION VALIDATION & STARTUP LOGGING
# =============================================================================

def _validate_and_log_configuration():
    """Validate configuration and log startup information.
    
    This function performs validation checks and logs important configuration
    status information for debugging and monitoring purposes.
    """
    # Validate critical configuration
    if SERVICE_NAME == __name__:
        logger.warning(
            "SERVICE_NAME is using module name. Consider setting REFLECTION_NAME environment variable.",
            extra={"configuration_issue": "service_name_not_set", "current_name": SERVICE_NAME}
        )

    # Log telemetry status
    if not LOGGER_CONNECTION_STRING:
        logger.info(
            "No Application Insights connection string configured. Telemetry will be disabled.",
            extra={"telemetry_status": "disabled"}
        )

    # Log Key Vault status
    if not KEYVAULT_URL:
        logger.info(
            "No Key Vault URL configured. Key Vault operations will be disabled.",
            extra={"keyvault_status": "disabled"}
        )

    if not HEAD_KEYVAULT_URL:
        logger.info(
            "No Head Key Vault URL configured. Head Key Vault operations will be disabled.",
            extra={"head_keyvault_status": "disabled"}
        )

    # Log successful initialization with comprehensive metadata
    logger.info(
        f"Management configuration initialized for service '{SERVICE_NAME}' v{SERVICE_VERSION}",
        extra={
            "service_name": SERVICE_NAME,
            "service_version": SERVICE_VERSION,
            "console_logging": LOGGER_ENABLE_CONSOLE,
            "token_cache_enabled": IDENTITY_ENABLE_TOKEN_CACHE,
            "telemetry_enabled": bool(LOGGER_CONNECTION_STRING),
            "keyvault_enabled": bool(KEYVAULT_URL),
            "head_keyvault_enabled": bool(HEAD_KEYVAULT_URL),
            "keyvault_secrets_enabled": KEYVAULT_ENABLE_SECRETS if KEYVAULT_URL else False,
            "keyvault_keys_enabled": KEYVAULT_ENABLE_KEYS if KEYVAULT_URL else False,
            "keyvault_certificates_enabled": KEYVAULT_ENABLE_CERTIFICATES if KEYVAULT_URL else False,
            "running_in_docker": RUNNING_IN_DOCKER,
        }
    )


# Perform validation and startup logging
_validate_and_log_configuration()

# =============================================================================
# MODULE EXPORTS
# =============================================================================

# Export primary service instances for application use
__all__ = ["logger", "local_env_manager", "identity", "keyvault", "head_keyvault"]
