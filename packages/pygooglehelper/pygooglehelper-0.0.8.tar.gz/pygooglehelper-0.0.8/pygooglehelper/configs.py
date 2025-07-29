""" configs.py """

from pytconf import Config, ParamCreator


class ConfigAuth(Config):
    """
    Configuration parameters for doing the authentication to google
    """
    force = ParamCreator.create_bool(
        help_string="Should we force creation of a new auth token",
        default=False,
    )
    host = ParamCreator.create_str(
        help_string="The hostname for local redirect. This is http, not https. Passed to run_local_server",
        default="localhost",
    )
    port = ParamCreator.create_int(
        help_string="The port for the local redirect server, passed to run_local_server",
        default=0,
    )
    authorization_prompt_message = ParamCreator.create_str(
        help_string="The message to display to tell the user to navigate to the authorization URL",
        default="navigate to that URL",
    )


class ConfigRequest(Config):
    """
    Configuration of the specific request
    """
    scopes = ParamCreator.create_list_str(
        help_string="List of security scopes requested",
        default=[],
    )
    location = ParamCreator.create_str_or_none(
        help_string="Where is the location of the client_secret.json",
        default=None,
    )
