""" Proxy handler specific settings
including encoding, overwrite handling, etc. """

from resolvebridge.handlers.proxies.handle_proxies import handle_already_linked, handle_existing_unlinked, handle_offline_proxies, handle_orphaned_proxies


encode_settings = dict(

  vid_codec = "dnxhd",
  h_res = 1280,
  v_res = 720,
  vid_profile = "dnxhr_sq",
  pix_fmt = "yuv422p",
  misc_args = ["-hide_banner", "-stats", "-loglevel error"],
  ext = ".mxf",
  overwrite_mode = "increment", #keep, skip

  audio = dict(
    audio_codec = "pcm_s16le",
    audio_samplerate = 48000,
  )
)

handler_settings = dict(
    handle_orphans = False,
    handle_already_linked = True,
    handle_existing_unlinked = True,
    handle_offline = True, 
)
