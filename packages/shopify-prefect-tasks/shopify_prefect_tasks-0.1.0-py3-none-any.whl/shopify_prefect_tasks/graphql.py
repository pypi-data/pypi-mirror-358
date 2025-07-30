import shopify

from prefect import Task
from prefect.utilities.tasks import defaults_from_attrs
from typing import Any


class ExecuteGraphQL(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            graphql_data: dict = None, **task_kwargs: Any) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if graphql_data is None:
                raise ValueError("Data for a Variant must be provided")

            return shopify.GraphQL().execute(**graphql_data)

