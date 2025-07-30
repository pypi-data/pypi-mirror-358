"""Azure configuration directors.

This module provides director patterns for common Azure configuration setups.
Directors orchestrate builders to create pre-configured combinations of Azure services.
"""

from .configuration import (
    ConfigurationSetupBuilder,
    AzureManagementBuilder,
    AzureResourceBuilder,
    AzureManagementConfiguration,
    AzureResourceConfiguration,
    AzureConfiguration,
)


class ConfigurationSetupDirector:
    """Director for common setup configurations."""
    
    @staticmethod
    def build_default_setup():
        """Build default environment configuration.
        
        Note: This method does not set any Azure credentials directly.
        Azure credentials should be configured through:
        1. Environment variables (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET)
        2. Azure CLI authentication
        3. Managed Identity when running in Azure
        4. Visual Studio Code/Azure Developer CLI authentication
        
        For local development, use Azure CLI 'az login' or set environment variables.
        """
        return (ConfigurationSetupBuilder()
                .with_local_env_management()  # FIRST: Load .env files and environment variables
                .with_environment_detection()
                .with_environment_variables({
                    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
                    "AzureWebJobsDashboard": "UseDevelopmentStorage=true",
                    "input_queue_connection__queueServiceUri": "UseDevelopmentStorage=true",
                    "AzureWebJobsStorage__accountName": "UseDevelopmentStorage=true",
                    "AzureWebJobsStorage__blobServiceUri": "UseDevelopmentStorage=true"
                }, in_docker=False, in_machine=True)  # Development storage only for local machine
                .with_service_configuration()
                .with_logging_configuration()
                .with_identity_configuration()
                .build())  # keyvault/storage configs removed - now handled directly in service creation


class AzureManagementDirector:
    """Director for common management configurations."""
    
    @staticmethod
    def build_default_management() -> AzureManagementConfiguration:
        """Build default management configuration."""
        env_config = ConfigurationSetupDirector.build_default_setup()
        return (AzureManagementBuilder(env_config)
                .with_logger()
                .with_identity()
                .with_keyvault()
                .build())


class AzureResourceDirector:
    """Director for common combined configurations."""
    
    @staticmethod
    def build_default_config() -> AzureConfiguration:
        """Build default configuration."""
        env_config = ConfigurationSetupDirector.build_default_setup()
        mgmt_config = AzureManagementDirector.build_default_management()
        resource_config = AzureResourceBuilder(mgmt_config, env_config).with_storage().build()
        return AzureConfiguration(management=mgmt_config, resources=resource_config)


__all__ = [
    "ConfigurationSetupDirector",
    "AzureManagementDirector", 
    "AzureResourceDirector"] 