""" Proxies handler settings.
Submodules have their own adjacent settings files.
"""
# Always need an outer dict
defaults = dict(

    proxies = dict(
        vid_codec = "dnxhd",
        h_res = 1280,
        v_res = 720,
        vid_profile = "dnxhr_sq",
        pix_fmt = "yuv422p",
        misc_args = ["-hide_banner", "-stats", "-loglevel error"],
        ext = ".mxf",
        overwrite_mode = "increment", #keep, skip
        audio_codec = "pcm_s16le",
        audio_samplerate = 48000,
        handle_orphans = False,
        handle_already_linked = True,
        handle_existing_unlinked = True,
        handle_offline = True,
    )

)
