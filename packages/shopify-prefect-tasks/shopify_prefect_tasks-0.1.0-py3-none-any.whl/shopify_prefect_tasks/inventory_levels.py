import shopify

from prefect import Task
from prefect.utilities.tasks import defaults_from_attrs
from typing import Any


class FetchInventoryLevels(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            inventory_level_data: dict = None, **task_kwargs: Any) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            inventory_levels = shopify.InventoryLevel.find(id_=None, from_=None, **inventory_level_data)

        return inventory_levels


class LinkInventoryLevel(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            inventory_level_data: dict = None, **task_kwargs: Any) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        if inventory_level_data is None:
            raise ValueError("InventoryLevel data must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            inventory_level = shopify.InventoryLevel.connect(**inventory_level_data)

            return inventory_level


class SetInventoryLevel(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            inventory_level_data: dict = None, **task_kwargs: Any) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        if inventory_level_data is None:
            raise ValueError("InventoryLevel data must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            inventory_level = shopify.InventoryLevel.set(**inventory_level_data)

            return inventory_level


class AdjustInventoryLevel(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            inventory_level_data: dict = None, **task_kwargs: Any) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        if inventory_level_data is None:
            raise ValueError("InventoryLevel data must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            inventory_level = shopify.InventoryLevel.adjust(**inventory_level_data)

            return inventory_level


class DeleteInventoryLevel(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            inventory_level_data: dict = None, **task_kwargs: Any) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        if inventory_level_data is None:
            raise ValueError("InventoryLevel Data must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            inventory_level = shopify.InventoryLevel.find(**inventory_level_data)

            return inventory_level.destroy()

