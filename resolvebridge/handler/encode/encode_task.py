#!/usr/bin/env python

import logging
import os
import time

from ffmpy import FFmpeg, FFRuntimeError
from resolvebridge import app_settings
from resolvebridge.celery_worker import celery_settings
from resolvebridge.celery_worker.celery import app
from resolvebridge.common import constants
from resolvebridge.handlers.proxies import proxies_settings
from resolvebridge.common.settings_manager import SettingsManager

settings = SettingsManager(constants.USER_PREFS_PATH)

settings.ingest(celery_settings.defaults)
settings.ingest(app_settings.defaults)
settings.ingest(proxies_settings.defaults)

preferences = settings.get()

celery_worker = preferences['celery_worker']
celery_general = preferences['celery_general']
encode_settings = preferences['proxies_settings']

log_level = eval("logging." + celery_general['log_level'])
logging.basicConfig(level=log_level)


def encode(job):
    """ Send job for encoding according to
    passed job arguments
    """

    # Create path for proxy first
    os.makedirs(
        job['Expected Proxy Path'],
        exist_ok=True,
    )

    # Paths
    source_file = job['File Path']

    output_file = os.path.join(
        job['Expected Proxy Path'],
        os.path.splitext(job['Clip Name'])[0] +
        encode_settings['ext'],
    )

    # Video
    h_res = encode_settings['h_res']
    v_res = encode_settings['v_res']
    fps = job['FPS']


    # Flip logic:
    # If any flip args were sent with the job from Resolve, flip the clip accordingly.
    # Flipping should be applied to clip attributes, not through the inspector panel

    flippage = ''
    if job['H-FLIP'] == "On":
        flippage += ' hflip, '
    if job['V-FLIP'] == "On":
        flippage += 'vflip, '

    ffmpeg = FFmpeg(
        global_options = [
            '-y',
            '-hide_banner',
            '-stats',
            '-loglevel error',
        ],

        inputs = {source_file: None},
        outputs = {
            output_file:
                ['-c:v',
                    'dnxhd',
                    '-profile:v',
                    encode_settings["vid_profile"],
                    '-vf',
                    f'scale={h_res}:{v_res},{flippage}' +
                    f'fps={fps},' +
                    f'format={encode_settings["pix_fmt"]}',
                    '-c:a',
                    encode_settings['audio_codec'],
                    '-ar',
                    encode_settings['audio_samplerate'],
                ]
        },
    )



    print(ffmpeg.cmd)

    try:

        ffmpeg.run()

    except FFRuntimeError as error:

        logging.warning(error)
        return False

    else:

        return job
