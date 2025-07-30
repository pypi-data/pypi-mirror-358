import shopify

from prefect import Task
from prefect.utilities.tasks import defaults_from_attrs
from typing import Any


class CreateVariant(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            variant_data: dict = None, **task_kwargs: Any) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if variant_data is None:
                raise ValueError("Data for a Variant must be provided")

            return shopify.Variant.create(variant_data)


class FetchVariant(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            variant_data: dict = None, **task_kwargs: Any) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            variant = shopify.Variant.find(**variant_data)

        return variant


class UpdateVariant(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            variant_id: str = None, variant_data: dict = None, **task_kwargs: Any) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        if variant_data is None:
            raise ValueError("Variant data must be provided")
        with shopify.Session.temp(shop_url, api_version, private_app_password):
            variant = shopify.Variant(variant_data)
            if variant.save():
                return variant
            else:
                return None


class DeleteVariant(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            variant_id: str = None, **task_kwargs: Any) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if variant_id is None:
                raise ValueError("A Variant ID must be provided")
            else:
                variant_exists = shopify.Variant.exists(variant_id)
                if not variant_exists:
                    raise ValueError("There is no Variant with the given ID")
                variant = shopify.Variant.find(id_=variant_id, from_=None, **task_kwargs)

            return variant.destroy()


class CountVariants(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            options: dict = None, **task_kwargs: Any) -> int:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            count = shopify.Variant.count(_options=options, **task_kwargs)

        return count
