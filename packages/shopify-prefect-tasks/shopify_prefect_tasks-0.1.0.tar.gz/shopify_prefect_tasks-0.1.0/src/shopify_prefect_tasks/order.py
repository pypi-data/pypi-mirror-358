import shopify

from prefect import Task
from prefect.utilities.tasks import defaults_from_attrs
from typing import Any


class FetchOrder(Task):
    """
    Fetch an order task from Shopify

    Attributes:
        shop_url (str): The URL of the Shopify store
        api_version (str): The API version to use

    Returns:
        dict: The order
    """
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            order_id: str = None, from_url: str = None, **task_kwargs) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if order_id is None:
                order = shopify.Order.find()
            else:
                order = shopify.Order.find(id_=order_id, from_=from_url, **task_kwargs)

        return order


class CreateOrder(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            order_data: dict = None) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if order_data is None:
                raise ValueError("Data for an Order must be provided")

            return shopify.Order.create(order_data)


class SearchOrder(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            order_id: str = None) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if order_id is None:
                return shopify.Order.find()
            else:
                return shopify.Order.find(order_id)


class UpdateOrder(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            order_id: str = None, order_data: dict = None) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if order_data is None:
                raise ValueError("Data for Order update must be provided")
            if order_id is None:
                raise ValueError("An Order ID must be provided")

            order = shopify.Order.find(order_id)
            order.update(order_data)
            return order.save()


class DeleteOrder(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            order_id: str = None) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            order_exists = shopify.Order.exists(order_id)
            if not order_exists:
                raise ValueError("There is no Order with the given ID")

            order = shopify.Order.find(order_id)
            return order.destroy()
