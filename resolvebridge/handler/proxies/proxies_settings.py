""" Proxies handler settings.
Submodules have their own adjacent settings files.
"""
# Always need an outer dict
defaults = dict(

    encode_settings = dict(

        vid_codec = "dnxhd",
        h_res = 1280,
        v_res = 720,
        vid_profile = "dnxhr_sq",
        pix_fmt = "yuv422p",
        misc_args = ["-y", "-hide_banner", "-stats", "-loglevel error"],
        ext = ".mxf",

        audio_codec = "pcm_s16le",
        audio_samplerate = 48000,
    ),

    handler_settings = dict(
        handle_orphans = False,
        handle_already_linked = True,
        handle_existing_unlinked = True,
        handle_offline = True,
    )

)
