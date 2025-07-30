"""
Tasks for interacting with Shopify.
"""
try:
    from .customer import FetchCustomer, CreateCustomer, UpdateCustomer, DeleteCustomer, SearchCustomer
    from .customer_address import FetchCustomerAddress, CreateCustomerAddress, UpdateCustomerAddress
    from .product import FetchProduct, CreateProduct, UpdateProduct, CountProducts, DeleteProduct
    from .variant import FetchVariant, CreateVariant, UpdateVariant, CountVariants, DeleteVariant
    from .locations import FetchLocations
    from .order import FetchOrder, CreateOrder, UpdateOrder, DeleteOrder, SearchOrder
    from .inventory_items import FetchInventoryItem, UpdateInventoryItem
    from .inventory_levels import FetchInventoryLevels, LinkInventoryLevel, SetInventoryLevel, AdjustInventoryLevel, \
        DeleteInventoryLevel
    from .graphql import ExecuteGraphQL
except ImportError:
    raise ImportError(
        'Using `prefect.tasks.shopify` requires Prefect to be installed with the "shopify" extra.'
    )
