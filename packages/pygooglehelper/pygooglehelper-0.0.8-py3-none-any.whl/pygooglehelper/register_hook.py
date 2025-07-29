""" register_hook.py """

from pytconf import register_function
from pygooglehelper.configs import ConfigAuth, ConfigRequest
from pygooglehelper.auth import get_credentials


def register_functions():
    register_function(
        function=get_credentials,
        description="Do the authentication procedure and get token for your app",
        name="auth",
        configs=[ConfigAuth, ConfigRequest],
    )
