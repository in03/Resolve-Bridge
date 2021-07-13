""" Settings manager module for Resolve Bridge.
"""
import configparser
import logging
import os

# from typing import Union
from attrdict import AttrDict

from resolvebridge.common import constants, helpers

# TODO: Debug logging is messy.
# There's probably a quicker way to ingest new settings.
# Consider iterating through settings by config 'section'
# or by ingest, since it's unlikely users will ingest conflicting values
# or if they do it will be on purpose.

MANAGER_DEBUG = False
if MANAGER_DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARN)
print()


class SettingsManager():
    """ Settings Manager takes multiple dictionary sources of application settings,
    finds their overriding preferences set in a central config file and returns them all
    as a dictionary or namespace / atrribute object.
    """

    def __init__(self, preference_directory, results_as_attr:bool=False):
        """ Create a new settings instance with a config preference file in the provided directory.
        Choose to return settings as a namespace object or dictionary with 'results_as_attr'.
        """

        # Get Logger
        self.logger = helpers.get_module_logger()

        # Return results as namespace / attributes?
        # Pass arg in class
        self.results_as_attr = results_as_attr

        # If no preference directory passed as arg, default to home
        if not preference_directory:
            self.conf_path = os.path.join(constants.LOCAL_STORAGE, "settings.ini")

        else:
            self.conf_path = preference_directory

        # Parent directory
        self.dirname = os.path.dirname(self.conf_path)

        # Init settings var
        self.settings = {}

        # Ensure settings directory exists
        if not os.path.exists(self.dirname):
            self.logger.warning("Settings folder is missing. Creating.")
            os.makedirs(self.dirname)

    def _read_prefs(self) -> dict:
        config = configparser.ConfigParser()
        config.read(self.conf_path)

        # Get dictionary of every item from every section
        prefs = {s:dict(config.items(s)) for s in config.sections()}

        self.logger.debug("Read config file: %s \nData: %s", self.conf_path, prefs)
        return prefs

    def _update_settings(self):

        prefs = self._read_prefs()

        # For each k:v pair in preferences
        for pref_k, pref_v in prefs.items():

            # If key matches, update setting
            if pref_k in self.settings.keys():
                self.settings.update({pref_k: pref_v})

                self.logger.debug(
                    "Found matching key: %s in config file."
                    "Using preferred value: %s", pref_k, pref_v
                )

        return self._write_prefs()

    def _write_prefs(self):
        """ Rewrite updated preferences to file """

        try:

            # Convert dict to config
            parser = configparser.ConfigParser()
            parser.read_dict(self.settings)

            self.logger.debug("Attempting rewrite config file: %s", self.conf_path)

            # Rewrite config to file
            with open(self.conf_path, "w") as config_file:
                parser.write(config_file)

        except Exception as error:
            self.logger.error("Something went wrong! Couldn't write config file: %s", error)
            return False

        return True

    def _update_config(self, dict_source: dict) -> dict:
        """ Load an ini config file """

        conf_path = self.conf_path

        config = configparser.ConfigParser()

        # Write whole section if necessary
        for dict_sub in dict_source:

            # First element of outer dict should be 'Section'
            if isinstance(dict_sub, str):

                dict_section = str(dict_sub)
                config.add_section(dict_section)

                new_settings = {

                    k:v for (k,v) in dict_source[dict_section].items()
                    if k not in config[dict_section].keys()

                }


                logging.debug("New Settings: %s", new_settings)

                # TODO: Get this part to work!
                config[dict_section] = new_settings
                print(config)

        with open(conf_path, "a") as config_file:
            config.write(config_file)
        exit()

        self.logger.debug("Updated config %s", os.path.basename(self.conf_path))

        with open(conf_path, "r") as config_file:
            config.read(config_file)

        parsed_config = {s:dict(config.items(s)) for s in config.sections()}

        return parsed_config

    def _check_dict(self, dict_: dict) -> bool:
        """ Check dictionary meets criteria for source.
        Needs to be nested at least once, since we need sections and keys.
        """

        depth = helpers.get_dict_depth(dict_)
        self.logger.debug("Dict depth: %s", depth)

        if depth < 2:
            self.logger.warning(
                "Dictionary source: %s, is too shallow to contain section and key."
                "It will be ignored!", dict_
            )
            return False

        self.logger.debug("Registered dict source, %s", dict_)
        return True

    def get(self):
        """ Return settings as namespace obj """

        results = self.settings

        # Convert to namespace / attribute type
        if self.results_as_attr:
            results = AttrDict(**self.settings)

        return results

    def ingest(self, source: dict):
        """ Register provided settings. Any keys that don't exist in the config
        will have their defaults written.
        """

        self.logger.debug("Source provided: %s", source)

        # Check source is valid
        if not isinstance(source, dict):
            self.logger.warning("Invalid source type passed! Ignoring")
            return None

        if not self._check_dict(source):
            self.logger.warning("Invalid dict passed! Ignoring")
            return None

        # Merge current settings with new source
        self.settings = dict(**self.settings, **source)
        self.logger.debug("Self settings: %s", self.settings)

        # Add default settings to config if missing,
        # Pull preferred settings from config if present
        self._update_settings()

        return self.settings
