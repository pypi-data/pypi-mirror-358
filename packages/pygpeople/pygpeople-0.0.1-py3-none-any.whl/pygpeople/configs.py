"""
All configurations for pygpeople
"""

from pytconf import Config, ParamCreator


class ConfigEmpty(Config):
    """
    Dummy config
    """

    doit = ParamCreator.create_bool(help_string="Really fix the source?", default=True,)
