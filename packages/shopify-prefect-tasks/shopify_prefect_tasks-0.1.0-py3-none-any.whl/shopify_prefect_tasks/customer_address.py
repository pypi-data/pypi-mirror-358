import json

import shopify

from prefect import Task
from prefect.utilities.tasks import defaults_from_attrs
from typing import *


class CreateCustomerAddress(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            customer_address_data: dict = None, **task_kwargs) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if not 'customer_id' in customer_address_data:
                raise ValueError('A Customer ID must be provided')

            if customer_address_data is None:
                raise ValueError("Data for an Address must be provided")

            address_data = dict()
            address_data.update({'customer_address': customer_address_data})

            customer_address = shopify.Customer.find(id_=customer_address_data.get('customer_id')).post('addresses',
                                                                                                        json.dumps(
                                                                                                            address_data,
                                                                                                            indent=2).encode(
                                                                                                            'utf-8'),
                                                                                                        **task_kwargs)

        return customer_address


class FetchCustomerAddress(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            customer_address_data: dict = None, from_url: str = None, **task_kwargs) -> dict:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if customer_address_data is None:
                raise ValueError("Data for an Address must be provided")
            else:
                if not 'customer_id' in customer_address_data:
                    raise ValueError('A Customer ID must be provided')

                address_data = dict()
                address_data.update({'customer_address': customer_address_data})

                if not 'address_id' in customer_address_data:
                    customer_address = shopify.Customer.find(id_=customer_address_data.get('customer_id')).get(
                        'addresses', **task_kwargs)
                else:
                    customer_address = shopify.Customer.find(id_=customer_address_data.get('customer_id')).get(
                        'addresses/' + customer_address_data.get('address_id'), **task_kwargs)

        return customer_address


class UpdateCustomerAddress(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            customer_address_data: dict = None, from_url: str = None, **task_kwargs) -> Any:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if customer_address_data is None:
                raise ValueError("Data for an Address must be provided")
            else:
                if not 'customer_id' in customer_address_data:
                    raise ValueError('A Customer ID must be provided')

                address_data = dict()
                address_data.update({'customer_address': customer_address_data})

                if not 'address_id' in customer_address_data:
                    raise ValueError('An Address ID must be provided')

                customer_address = shopify.Customer.find(id_=customer_address_data.get('customer_id')).put(
                    'addresses/' + customer_address_data.get('address_id'),
                    json.dumps(address_data, indent=2).encode('utf-8'), **task_kwargs)

            return customer_address


class DeleteCustomerAddress(Task):
    def __init__(self, shop_url: str = None, api_version: str = None, **kwargs: Any):
        self.shop_url = shop_url
        self.api_version = api_version
        super().__init__(**kwargs)

    @defaults_from_attrs("shop_url", "api_version")
    def run(self, shop_url: str = None, api_version: str = None, private_app_password: str = "SHOPIFY_APP_PASSWORD",
            customer_address_data: dict = None, from_url: str = None, **task_kwargs) -> None:
        if shop_url is None:
            raise ValueError("A Shop URL must be provided.")

        if api_version is None:
            raise ValueError("An API version must be provided")

        if private_app_password is None:
            raise ValueError("A private app password must be provided")

        with shopify.Session.temp(shop_url, api_version, private_app_password):
            if customer_address_data is None:
                raise ValueError("Data for an Address must be provided")
            else:
                if not 'customer_id' in customer_address_data:
                    raise ValueError('A Customer ID must be provided')

                address_data = dict()
                address_data.update({'customer_address': customer_address_data})

                if not 'address_id' in customer_address_data:
                    raise ValueError('An Address ID must be provided')

                customer_address = shopify.Customer.find(id_=customer_address_data.get('customer_id')).delete(
                    'addresses/' + customer_address_data.get('address_id'), **task_kwargs)

            return customer_address
