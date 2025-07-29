"""Azure resources package for azpaddypy.

This package contains modules for interacting with various Azure resources
including Key Vault, Storage, and other Azure services.
"""

from .keyvault import AzureKeyVault, create_azure_keyvault

__all__ = [
    "AzureKeyVault",
    "create_azure_keyvault",
] 