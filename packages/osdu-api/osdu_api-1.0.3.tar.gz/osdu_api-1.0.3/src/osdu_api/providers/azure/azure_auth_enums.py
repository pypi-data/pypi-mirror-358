from enum import Enum


class AzureAuthType(Enum):
    MSI = 1
    CLIENT_SECRET = 2
    CLIENT_CERTIFICATE = 3


class ClientSecretFetchType(Enum):
    PLAIN_TEXT = 1
    ENVIRONMENT_VARIABLE = 2
    KEYVAULT = 3
