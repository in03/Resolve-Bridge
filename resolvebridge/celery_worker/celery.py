#!/usr/bin/env python
""" Celery worker instance. Runs on machines that receive tasks to work on.
Should be configured either with environment variables or configuration object
"""


from __future__ import absolute_import

import os
import sys

from celery import Celery
# TODO: Get this to work
# from celery.task.control import inspect

from resolvebridge.common import constants
from resolvebridge.common.settings_manager import SettingsManager
from . import celery_settings

# Load Settings
settings = SettingsManager(constants.USER_PREFS_PATH)
settings.ingest(celery_settings.defaults)
preferences = settings.get()
celery_worker = preferences['celery_worker']

# Windows can't fork processes.
if sys.platform == "win32":
    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')


    

def find_supported_tasks():
    """ Gather a list of Celery tasks from all supported handlers.
    Must be installed in tasks subfolder with 'task_' prefix to be found.
    """

    # TODO: Make this work!
    # Subfolder part is easy enough, need to decide how to register
    # additional handlers. Can they be installed to the same directory?
    # Or must we search all packages on path?


# Start Celery worker
app = Celery(constants.APP_NAME)
app.config_from_object(celery_worker)
app.autodiscover_tasks(find_supported_tasks(), force=True)

# Print discovered worker tasks
# TODO: Get this to work
# i = inspect().registered_tasks()
# if i > 0:
#     print("Discovered worker tasks:")
#     for task in i:
#         print(task)
