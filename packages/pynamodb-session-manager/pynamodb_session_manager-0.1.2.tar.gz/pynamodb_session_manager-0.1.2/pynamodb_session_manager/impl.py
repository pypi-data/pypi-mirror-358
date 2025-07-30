# -*- coding: utf-8 -*-

"""
PynamoDB Context Manager for Using Specific Boto3 Sessions

This module provides a context manager that allows PynamoDB models to temporarily
use different AWS credentials/sessions without modifying the model definition.
This is particularly useful for:

- Multi-account operations
- Different AWS profiles for different environments
- Temporary credential switching
- Cross-account DynamoDB operations
"""

import typing as T
import contextlib

import botocore.exceptions
from pynamodb.connection import Connection
from pynamodb.exceptions import PynamoDBException

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    from pynamodb.models import Model


@contextlib.contextmanager
def use_boto_session(
    table: T.Type["Model"],
    bsm: T.Optional["BotoSesManager"] = None,
    restore_on_exit: bool = True,
):
    """
    Context manager to temporarily switch PynamoDB model to use different AWS credentials.

    This context manager allows a PynamoDB model to temporarily use different AWS
    credentials by leveraging the boto-session-manager's awscli() context manager
    and manipulating the model's connection and region settings.

    :param table: The PynamoDB model class that will use the new credentials.
    :param bsm: The boto session manager instance containing the
        target AWS credentials/profile to use. If None, the context manager
        has no effect, providing a clean API where users can conditionally
        switch credentials without separate if/else logic.
        See https://pypi.org/project/boto-session-manager/
    :param restore_on_exit: If True, restore original connection on exit
        if False, keep current connection for subsequent operations.
        See also :func:`reset_connection`.

    :yields: None, This is a context manager that doesn't return a value

    Usage::

        # Define your model
        class MyModel(Model):
            class Meta:
                table_name = "my_table"
                region = "us-east-1"

            id = NumberAttribute(hash_key=True)

        # Use different credentials temporarily
        target_bsm = BotoSesManager(profile_name="target_profile")

        with target_aws_cred(target_bsm, MyModel):
            # All operations here use the target_profile credentials
            MyModel.create_table()
            item = MyModel(id=1)
            item.save()

        # Back to original credentials
        items = MyModel.scan()  # This uses default credentials

    How it works:

    1. Saves the current region setting from the model's Meta class
    2. Enters the boto session manager's awscli() context (sets env vars)
    3. Clears the model's cached connection to force recreation
    4. Updates the model's region to match the session manager's region
    5. Creates a new Connection object with the new region
    6. On exit, restores the original region and clears connection again

    .. note::

        - The model's _connection attribute is set to None to force PynamoDB
            to create a new connection with the current environment variables
        - The region is temporarily changed to ensure consistency with the session
        - All changes are reverted when exiting the context manager when restore_on_exit is True
    """
    # Store the current region setting to restore it later
    current_aws_region = table.Meta.region
    try:
        if bsm is None:
            # if BotoSesManager is not provided, we do nothing
            yield None
        else:
            # Enter the boto session manager's context
            # This typically sets AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc. as env vars
            with bsm.awscli():
                # Clear the existing connection to force PynamoDB to create a new one
                # with the current environment variables (which are now set by bsm.awscli())
                table._connection = None
                # Update the model's region to match the session manager's region
                # This ensures consistency between the session and the model configuration
                table.Meta.region = bsm.aws_region
                # Create a new connection object with the new region
                # This connection will inherit the AWS credentials from environment variables
                Connection(region=bsm.aws_region)
                # Yield control back to the caller
                # All PynamoDB operations within this context will use the new credentials
                yield None
    finally:
        if restore_on_exit and (bsm is not None):
            # Cleanup: Restore the original state regardless of success or failure
            # Clear the connection again to ensure clean state
            table._connection = None
            # Restore the original region setting
            table.Meta.region = current_aws_region
            # Create a new connection with the original region
            # When the bsm.awscli() context exits, the environment variables
            # will be restored, so this connection will use the original credentials
            Connection(region=current_aws_region)


def reset_connection(
    table: T.Type["Model"],
):
    """
    Reset the PynamoDB model's connection to use the default AWS connection.

    This is useful when you have changed AWS credentials using
    :func:`use_boto_session` context manager, and then want to revert back
    to the default PynamoDB behavior.

    :param table: The PynamoDB model class whose connection should be reset.

    Usage::

        # Define your model
        class MyModel(Model):
            ...

        # Use different credentials and keep the connection
        with use_boto_session(target_bsm, MyModel, restore_on_exit=False):
            ...

        # Reset the connection to use the default AWS credentials
        reset_connection(MyModel)
    """
    # Clear the existing connection then make an test API call to force
    # PynamoDB to create a new one
    table._connection = None
    try:
        table.describe_table()
    except PynamoDBException:  # pragma: no cover
        pass
    except botocore.exceptions.ClientError:  # pragma: no cover
        pass
