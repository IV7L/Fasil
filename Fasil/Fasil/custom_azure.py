from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'fasilaccountstorage' # Must be replaced by your <storage_account_name>
    account_key = 'wtY023635hc9hZhspCqEt80Wuw4RcEANvsa8iwWoADIO+C7qTqOx5osus+QLJQi+IePVblcHK59++AStF5v9sQ==' # Must be replaced by your <storage_account_key>
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = 'fasilaccountstorage' # Must be replaced by your storage_account_name
    account_key = 'wtY023635hc9hZhspCqEt80Wuw4RcEANvsa8iwWoADIO+C7qTqOx5osus+QLJQi+IePVblcHK59++AStF5v9sQ==' # Must be replaced by your <storage_account_key>
    azure_container = 'static'
    expiration_secs = None