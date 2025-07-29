"""
Functional accounts module, all the logic to manage functional accounts from PS API
"""

import logging
from typing import Tuple

from secrets_safe_library import exceptions, utils
from secrets_safe_library.authentication import Authentication
from secrets_safe_library.constants.endpoints import POST_FUNCTIONAL_ACCOUNTS
from secrets_safe_library.constants.versions import Version
from secrets_safe_library.core import APIObject
from secrets_safe_library.data_classes import SSHConfig
from secrets_safe_library.mapping.functional_accounts import (
    fields as functional_accounts_fields,
)
from secrets_safe_library.mixins import DeleteByIdMixin, GetByIdMixin, ListMixin
from secrets_safe_library.validators import CustomValidator


class _FunctionalAccountValidator:
    common_schema = {}

    def get_create_schema(self):
        """
        Returns the schema for creating a functional account.
        """
        return {
            **self.common_schema,
            "platform_id": {"type": "integer", "nullable": False},
            "domain_name": {"type": "string", "maxlength": 500, "nullable": True},
            "account_name": {
                "type": "string",
                "maxlength": 245,
                "nullable": False,
            },
            "display_name": {
                "type": "string",
                "maxlength": 100,
                "nullable": True,
            },
            "password": {
                "type": "string",
                "maxlength": 1000,
                "nullable": True,
                "is_required_if": {
                    "field": "requires_secret",
                    "value": False,
                },
            },
            "private_key": {  # Comes from SSHConfig
                "type": "string",
                "nullable": True,
            },
            "passphrase": {  # Comes from SSHConfig
                "type": "string",
                "nullable": True,
            },
            "description": {
                "type": "string",
                "maxlength": 1000,
                "nullable": True,
            },
            "elevation_command": {  # Comes from SSHConfig
                "type": "string",
                "maxlength": 80,
                "nullable": True,
            },
            "tenant_id": {
                "type": "string",
                "maxlength": 36,
                "nullable": True,
            },
            "object_id": {
                "type": "string",
                "maxlength": 36,
                "nullable": True,
            },
            "secret": {
                "type": "string",
                "maxlength": 255,
                "nullable": True,
            },
            "service_account_email": {
                "type": "string",
                "maxlength": 255,
                "nullable": True,
            },
            "azure_instance": {
                "type": "string",
                "allowed": ["AzurePublic", "AzureUsGovernment"],
                "nullable": True,
            },
        }

    def validate(
        self,
        data: dict,
        operation: str,
        allow_unknown: bool = False,
        update: bool = False,
    ) -> None:
        """
        Validate data using the schema for given operation.

        Args:
            data (dict): Data to validate.
            operation (str): Operation type, e.g., 'create', 'update'.
            allow_unknown (bool): Whether to allow unknown fields in the data.
            update (bool): Whether the operation is an update.
        """

        match operation:
            case "create":
                schema = self.get_create_schema()
            case _:
                raise ValueError(f"Unsupported operation: {operation}")

        validator = CustomValidator(schema, allow_unknown=allow_unknown)

        if not validator.validate(data, update=update):
            utils.print_log(
                self._logger,
                f"Validation failed for {operation} operation: {validator.errors}",
                logging.ERROR,
            )
            raise exceptions.OptionsError(f"Please check: {validator.errors}")


class FunctionalAccount(
    APIObject, GetByIdMixin, DeleteByIdMixin, ListMixin, _FunctionalAccountValidator
):
    """
    FunctionalAccount class to manage functional accounts in Password Safe.
    """

    def __init__(self, authentication: Authentication, logger: logging.Logger = None):
        super().__init__(authentication, logger, endpoint="/functionalaccounts")

    def create_functional_account(
        self,
        *,
        platform_id: int,
        account_name: str,
        display_name: str = "",
        description: str = "",
        domain_name: str = "",
        password: str = "",
        ssh_config: SSHConfig = None,
        tenant_id: str = "",
        object_id: str = "",
        secret: str = "",
        service_account_email: str = "",
        azure_instance: str = "AzurePublic",
    ) -> Tuple[dict, int]:
        """
        Creates a new functional account.

        Args:
            platform_id (int): ID of the platform to which the account belongs.
            account_name (str): Name of the account.
            display_name (str, optional): Display name or alias for the account.
            description (str, optional): Description of the account.
            domain_name (str, optional): Domain name of the account.
            password (str, optional): Current account password.
            ssh_config (SSHConfig, optional): SSH configuration details if applicable.
            tenant_id (str, optional): Tenant ID if required by platform.
            object_id (str, optional): Object ID if required by platform.
            secret (str, optional): Secret if required by platform.
            service_account_email (str, optional): Service account email for Google
                accounts.
            azure_instance (str, optional): Azure instance type.

        Returns:
            Tuple[dict, int]: A tuple containing the created functional account object
                and the HTTP status code.
        """

        attributes = {
            "platform_id": platform_id,
            "account_name": account_name,
            "display_name": display_name,
            "description": description,
            "domain_name": domain_name,
            "password": password,
            "tenant_id": tenant_id,
            "object_id": object_id,
            "secret": secret,
            "service_account_email": service_account_email,
            "azure_instance": azure_instance,
        }

        if ssh_config and not isinstance(ssh_config, SSHConfig):
            raise exceptions.OptionsError(
                "ssh_config must be an instance of SSHConfig or None"
            )

        if ssh_config:
            attributes.update(ssh_config.__dict__)

        self.validate(attributes, operation="create", allow_unknown=False)

        req_structure = self.get_request_body_version(
            functional_accounts_fields, POST_FUNCTIONAL_ACCOUNTS, Version.DEFAULT
        )

        req_body = self.generate_request_body(req_structure, **attributes)
        utils.print_log(
            self._logger, "Calling create functional account endpoint", logging.DEBUG
        )
        response = self._run_post_request(
            endpoint=self.endpoint,
            payload=req_body,
            include_api_version=False,
        )
        return response.json(), response.status_code
