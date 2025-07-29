"""
Azure Project Management Configuration Template

This template provides standardized configuration for Azure logging and identity
management across projects. It creates singleton instances of AzureLogger and
AzureIdentity that can be imported and used throughout your application.

Usage:
    from mgmt_config import logger, identity
    
    logger.info("Application started")
    credential = identity.get_credential()
"""

import os
from typing import Optional, Dict, Any
from azpaddypy.mgmt.logging import create_app_logger, create_function_logger
from azpaddypy.mgmt.identity import create_azure_identity
from azpaddypy.resources.keyvault import create_azure_keyvault
from azpaddypy.mgmt.local_env_manager import create_local_env_manager

# Alias for import in other packages

# =============================================================================
# SERVICE CONFIGURATION
# =============================================================================

# Service identity - customize these for your project
REFLECTION_NAME = os.getenv("REFLECTION_NAME")
REFLECTION_KIND = os.getenv("REFLECTION_KIND")
SERVICE_NAME = REFLECTION_NAME or str(__name__)
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")

def is_running_in_docker():
    """
    Checks if the current process is running inside a Docker container.

    Returns:
        bool: True if running in Docker, False otherwise.
    """
    # Method 1: Check for /.dockerenv file
    if os.path.exists('/.dockerenv'):
        return True

    # Method 2: Check cgroup for "docker"
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            cgroup_content = f.read()
            if 'docker' in cgroup_content or 'kubepods' in cgroup_content:
                return True
    except FileNotFoundError:
        # /proc/1/cgroup does not exist, not a Linux-like environment
        pass
    except Exception:
        # Handle other potential exceptions, e.g., permissions
        pass

    return False

running_in_docker = is_running_in_docker()
print("is_running_in_docker: " + str(running_in_docker))


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Enable console output (useful for local development)
LOGGER_ENABLE_CONSOLE = os.getenv("LOGGER_ENABLE_CONSOLE", "true").lower() == "true"

# Application Insights connection string (optional, will use environment variable if not set)
LOGGER_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

# Local development settings
if running_in_docker:
    LOCAL_SETTINGS = {
        "AZURE_CLIENT_ID": "aa73da4a-2888-4cb7-896e-5d51125f11f0",
        "AZURE_TENANT_ID": "e5590d5d-336c-4cf5-b0ac-b79a598ec797",
        "AZURE_CLIENT_SECRET": "IQ08Q~4uCfc4B~p2F95D2737GzYvvrtIjursFbCf"
    }
else:
    LOCAL_SETTINGS = {
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "AzureWebJobsDashboard": "UseDevelopmentStorage=true",
        "input_queue_connection__queueServiceUri":  "UseDevelopmentStorage=true",
        "AzureWebJobsStorage__accountName":  "UseDevelopmentStorage=true",
        "AzureWebJobsStorage__blobServiceUri":  "UseDevelopmentStorage=true",
    }

# Configure which Azure SDK components to instrument
LOGGER_INSTRUMENTATION_OPTIONS = {
    "azure_sdk": {"enabled": True},
    "django": {"enabled": False},
    "fastapi": {"enabled": False},
    "flask": {"enabled": True},
    "psycopg2": {"enabled": True},
    "requests": {"enabled": True},
    "urllib": {"enabled": True},
    "urllib3": {"enabled": True},
}

# =============================================================================
# IDENTITY CONFIGURATION
# =============================================================================

# Token caching settings
IDENTITY_ENABLE_TOKEN_CACHE = os.getenv("IDENTITY_ENABLE_TOKEN_CACHE", "true").lower() == "true"
IDENTITY_ALLOW_UNENCRYPTED_STORAGE = os.getenv("IDENTITY_ALLOW_UNENCRYPTED_STORAGE", "true").lower() == "true"

# Custom credential options (None means use defaults)
IDENTITY_CUSTOM_CREDENTIAL_OPTIONS: Optional[Dict[str, Any]] = None

# Connection string for identity logging (uses same as logger by default)
IDENTITY_CONNECTION_STRING = LOGGER_CONNECTION_STRING

# =============================================================================
# KEYVAULT CONFIGURATION
# =============================================================================

# Enable specific Key Vault client types
KEYVAULT_ENABLE_SECRETS = os.getenv("KEYVAULT_ENABLE_SECRETS", "true").lower() == "true"
KEYVAULT_ENABLE_KEYS = os.getenv("KEYVAULT_ENABLE_KEYS", "false").lower() == "true"
KEYVAULT_ENABLE_CERTIFICATES = os.getenv("KEYVAULT_ENABLE_CERTIFICATES", "false").lower() == "true"

# Connection string for keyvault logging (uses same as logger by default)
KEYVAULT_CONNECTION_STRING = LOGGER_CONNECTION_STRING

# =============================================================================
# INITIALIZE SERVICES
# =============================================================================

# Create logger instance
if "functionapp" in os.getenv("REFLECTION_KIND", "app"):
    logger = create_function_logger(
        function_app_name=REFLECTION_NAME,
        function_name=REFLECTION_KIND,
        service_version=SERVICE_VERSION,
        connection_string=LOGGER_CONNECTION_STRING,
        instrumentation_options=LOGGER_INSTRUMENTATION_OPTIONS,
    )
    logger.info("Function logger: " + str(REFLECTION_KIND) + " " + str(REFLECTION_NAME) + " initialized")
else:
    logger = create_app_logger(
        service_name=SERVICE_NAME,
        service_version=SERVICE_VERSION,
        connection_string=LOGGER_CONNECTION_STRING,
        enable_console_logging=LOGGER_ENABLE_CONSOLE,
        instrumentation_options=LOGGER_INSTRUMENTATION_OPTIONS,
    )
    logger.info("App logger: " + str(REFLECTION_KIND) + " " + str(REFLECTION_NAME) + " initialized")

# Create local development settings instance
local_env_manager = create_local_env_manager(
    file_path=".env",
    settings=LOCAL_SETTINGS,
    logger=logger,
    override_json=True,
    override_dotenv=True,
    override_settings=True,
)

# Create identity instance with shared logger
identity = create_azure_identity(
    service_name=SERVICE_NAME,
    service_version=SERVICE_VERSION,
    enable_token_cache=IDENTITY_ENABLE_TOKEN_CACHE,
    allow_unencrypted_storage=IDENTITY_ALLOW_UNENCRYPTED_STORAGE,
    custom_credential_options=IDENTITY_CUSTOM_CREDENTIAL_OPTIONS,
    connection_string=IDENTITY_CONNECTION_STRING,
    logger=logger,
)

# Azure Key Vault URL (required for Key Vault operations)
KEYVAULT_URL = os.getenv("key_vault_uri")
HEAD_KEYVAULT_URL = os.getenv("head_key_vault_uri")

# Create keyvault instance with shared logger and identity (if URL is configured)
keyvault = None
if KEYVAULT_URL:
    keyvault = create_azure_keyvault(
        vault_url=KEYVAULT_URL,
        azure_identity=identity,
        service_name=SERVICE_NAME,
        service_version=SERVICE_VERSION,
        logger=logger,
        connection_string=KEYVAULT_CONNECTION_STRING,
        enable_secrets=KEYVAULT_ENABLE_SECRETS,
        enable_keys=KEYVAULT_ENABLE_KEYS,
        enable_certificates=KEYVAULT_ENABLE_CERTIFICATES,
    )

head_keyvault = None
if HEAD_KEYVAULT_URL:
    head_keyvault = create_azure_keyvault(
        vault_url=HEAD_KEYVAULT_URL,
        azure_identity=identity,
        service_name=SERVICE_NAME,
        service_version=SERVICE_VERSION,
        logger=logger,
        connection_string=KEYVAULT_CONNECTION_STRING,
        enable_secrets=KEYVAULT_ENABLE_SECRETS,
        enable_keys=KEYVAULT_ENABLE_KEYS,
        enable_certificates=KEYVAULT_ENABLE_CERTIFICATES,
    )

# =============================================================================
# VALIDATION & STARTUP
# =============================================================================

# Validate critical configuration
if SERVICE_NAME == __name__:
    logger.warning(
        "SERVICE_NAME is not configured. Please set SERVICE_NAME environment variable or update this template.",
        extra={"configuration_issue": "service_name_not_set"}
    )

if not LOGGER_CONNECTION_STRING:
    logger.info(
        "No Application Insights connection string configured. Telemetry will be disabled.",
        extra={"telemetry_status": "disabled"}
    )

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

# Log successful initialization
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
        "running_in_docker": running_in_docker,
    }
)

# =============================================================================
# EXPORTS
# =============================================================================

# Export logger, identity, and keyvault for use in applications
__all__ = ["logger", "local_env_manager", "identity", "keyvault", "head_keyvault"]
