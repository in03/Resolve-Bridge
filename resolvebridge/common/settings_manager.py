""" Settings manager module for Resolve Bridge.
Other modules register their defaults with the .update() function, but
can be overriden using the .ini preferences file in user's home,
or by an environment variables in the format "RESOLVEBRIDGE-{section}-{key}."
"""
from attrdict import AttrDict
import configparser
import logging
import os

from resolvebridge.common import constants, helpers

MANAGER_DEBUG = False

if MANAGER_DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARN)
print()


class SettingsManager():

    def __init__(self, source:dict):
        """ Create a new settings instance, automatically
        creating the necessary folder structure
        """

        self.logger = helpers.get_module_logger()
        self.settings_dir = constants.LOCAL_STORAGE
        self.user_pref = os.path.join(self.settings_dir, "settings.ini")
        self.settings = {}

        # Ensure settings directory
        if not os.path.exists(self.settings_dir):
            self.logger.warning("Settings folder is missing. Creating.")
            os.makedirs(self.settings_dir)

        helpers.write_if_not_exist(self.user_pref)
        self.initialise_settings(source)

    def get_settings(self):
        """ Return settings as namespace obj """
        attrdict = AttrDict(**self.settings)
        return attrdict

    def initialise_settings(self, source):
        """ Reload all settings with provided sources """

        if source is None:
            self.logger.warning("No sources passed to initialize_settings.")
            return None

            # Reorder code blocks here to change load priority

        if isinstance(source, dict):
            dict_source = self._load_dict(source)
            self.settings.update(**dict_source)

        elif os.path.splitext(source)[1] == ".ini":
            config_source = self._load_config(source)
            self.settings.update(**config_source)

        else:
            self.logger.warning("Unsupported source! Ignoring: %s", source)

        return self.settings

    def _load_config(self, user_pref):
        """ Load an ini config file """
        config = configparser.ConfigParser()
        config.read(user_pref)
        parsed_config = {s:dict(config.items(s)) for s in config.sections()}
        self.logger.debug("Registered config source, %s", os.path.basename(user_pref))
        return parsed_config

    def _load_dict(self, dict_):
        """ Load a dictionary """
        # Make sure we have a dict
        if not isinstance(dict_, dict):
            type_ = type(dict_)
            self.logger.error("Update method requires a dictionary, not %s", type_)

        # Make sure it's at least one level deep, since we need sections AND keys.
        depth = helpers.get_dict_depth(dict_)

        self.logger.debug("Dict depth: %s", depth)

        if depth < 2:
            self.logger.warning(
                "Dictionary source: %s, is too shallow to contain section and key."
                "It will be ignored!", dict_
            )
        self.logger.debug("Registered dict source, %s", dict_)
        return dict_

    def ingest(self, sources):
        """ Add or update a setting for the SettingsManager instance.
        Multiple modules can consolidate their settings into one callable.
        DOES NOT write updates to file. .ini config file always overrides
        settings that are set using this update method.
        """
        self.logger.debug("Ingest provided: %s", sources)

        # TODO: Check merge operator works in 3.6.8
        settings = self.settings
        settings = dict(**settings, **sources)

        self.initialise_settings(settings)