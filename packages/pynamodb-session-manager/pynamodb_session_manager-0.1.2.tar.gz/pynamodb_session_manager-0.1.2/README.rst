
.. image:: https://readthedocs.org/projects/pynamodb-session-manager/badge/?version=latest
    :target: https://pynamodb-session-manager.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/pynamodb_session_manager-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/pynamodb_session_manager-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/pynamodb_session_manager-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/pynamodb_session_manager-project

.. image:: https://img.shields.io/pypi/v/pynamodb-session-manager.svg
    :target: https://pypi.python.org/pypi/pynamodb-session-manager

.. image:: https://img.shields.io/pypi/l/pynamodb-session-manager.svg
    :target: https://pypi.python.org/pypi/pynamodb-session-manager

.. image:: https://img.shields.io/pypi/pyversions/pynamodb-session-manager.svg
    :target: https://pypi.python.org/pypi/pynamodb-session-manager

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/pynamodb_session_manager-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/pynamodb_session_manager-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://pynamodb-session-manager.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/pynamodb_session_manager-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/pynamodb_session_manager-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/pynamodb_session_manager-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/pynamodb-session-manager#files


Welcome to ``pynamodb_session_manager`` Documentation
==============================================================================
.. image:: https://pynamodb-session-manager.readthedocs.io/en/latest/_static/pynamodb_session_manager-logo.png
    :target: https://pynamodb-session-manager.readthedocs.io/en/latest/

``pynamodb_session_manager`` enables PynamoDB models to dynamically switch AWS credentials at runtime without modifying model definitions.

**Problem Background**

PynamoDB 6.0.0+ allows setting table-level connections by explicitly providing credentials, but this approach is not flexible or elegant for dynamic credential switching. Each PynamoDB model stores AWS session information in a ``_connection`` attribute. When you first use an ORM class to send a DynamoDB request, PynamoDB checks the model's ``Meta`` class for AWS credentials. If none are found, it uses the default AWS profile and creates a connection stored in ``_connection``, and then use it for all subsequent requests. This means that once a model's connection is established, it cannot be changed without modifying the model's definition or using a different model class.

As the author of `boto-session-manager <https://pypi.org/project/boto-session-manager/>`_, an advanced boto3 session manager that can temporarily change the "Default AWS Profile" using context managers, I created this library to solve PynamoDB's dynamic credential switching limitation.

**How It Works**

The ``use_boto_session`` context manager temporarily stores the current ORM class configuration, resets the ``_connection`` using the provided boto session manager, and conditionally reverts it back (depending on ``restore_on_exit`` parameter).

**Quick Start**

.. code-block:: python

    from pynamodb.models import Model
    from pynamodb.attributes import UnicodeAttribute
    from boto_session_manager import BotoSesManager

    from pynamodb_session_manager import use_boto_session

    # Define your PynamoDB model
    class User(Model):
        class Meta:
            table_name = "users"
            region = "us-east-1"
        
        id = UnicodeAttribute(hash_key=True)

    # Create session manager for different AWS account/profile
    target_bsm = BotoSesManager(profile_name="target_profile")

    # Use different credentials temporarily
    with use_boto_session(User, target_bsm):
        # All operations here use target_profile credentials
        User.create_table(wait=True)
        user = User(id="123")
        user.save()

    # Back to default credentials
    # This will fail if table doesn't exist in default account
    try:
        user = User.get("123")  # Uses default credentials
    except Exception:
        print("Table not found in default account")

**Advanced Usage**

.. code-block:: python

    from pynamodb_session_manager import reset_connection

    # Keep connection after context exits
    with use_boto_session(User, target_bsm, restore_on_exit=False):
        user = User(id="456")
        user.save()
    
    # Connection still uses target_profile
    user = User.get("456")  # Still uses target_profile
    
    # Manually reset to default credentials
    reset_connection(User)
    # Now uses default credentials again

**Multiple Account Operations**

.. code-block:: python

    default_bsm = BotoSesManager()  # Default profile
    staging_bsm = BotoSesManager(profile_name="staging")
    prod_bsm = BotoSesManager(profile_name="production")

    # Create table in staging
    with use_boto_session(User, staging_bsm):
        User.create_table(wait=True)
    
    # Copy data from staging to production
    with use_boto_session(User, staging_bsm):
        staging_users = list(User.scan())
    
    with use_boto_session(User, prod_bsm):
        User.create_table(wait=True)
        for user in staging_users:
            user.save()

For comprehensive examples and advanced usage patterns, see the `complete test suite <https://github.com/MacHu-GWU/pynamodb_session_manager-project/blob/main/tests_manual/test_impl.py>`_.


.. _install:

Install
------------------------------------------------------------------------------

``pynamodb_session_manager`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install pynamodb-session-manager

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pynamodb-session-manager
