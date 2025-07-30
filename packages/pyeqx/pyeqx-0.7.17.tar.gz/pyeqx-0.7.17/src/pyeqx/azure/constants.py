AZURE_STORAGE_CONTAINER_PATTERN = r"abfss://(.*?)@(.*?)\.dfs\.core\.windows\.net"
AZURE_SPARK_OPTION_PATTERN = r"fs\.azure\.account\.key\.(.*?)\.dfs\.core\.windows\.net"

AZURE_STORAGE_INFO_ACCOUNT_KEY = "accountKey"
AZURE_STORAGE_INFO_ACCOUNT_NAME = "accountName"
AZURE_STORAGE_INFO_CONTAINER_NAME = "containerName"

AZURE_STORAGE_EXCEPTION_ACCOUNT_KEY_OR_NAME_NOT_FOUND = (
    "Account key or account name not found."
)
AZURE_STORAGE_EXCEPTION_CONTAINER_NOT_FOUND = "Container not found."
