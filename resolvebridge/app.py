#!/usr/bin/env python

import os
import pathlib
import sys
import time
import tkinter
import tkinter.messagebox
import traceback

from celery import group
from colorama import Fore, init
from pyfiglet import Figlet
from win10toast import ToastNotifier

from resolvebridge.common import constants, python_get_resolve
from resolvebridge.common.settings_manager import SettingsManager
from resolvebridge.handlers.proxies import proxies_settings

from resolvebridge import app_settings

from resolvebridge.celery_worker import tasks as do
from resolvebridge.celery_worker import celery_settings
# from resolvebridge.common import constants
# from resolvebridge.common.python_get_resolve import get_resolve
# from resolvebridge.handlers.proxies import link
settings = SettingsManager(app_settings.defaults)
settings.ingest(proxies_settings.defaults)
settings.ingest(celery_settings.defaults)
prefs = settings.get_settings()

debugmode = prefs.app.debug
some_action_taken = False

def app_exit(level, force_explicit_exit=True):
    ''' Standard exitcodes for 'level' '''
    print(f.renderText("Done!"))

    if settings.get("app", "debug") or force_explicit_exit or level > 1:
        input("Press ENTER to exit.")

    else: exit_in_seconds(seconds = 5)

def toast(message, threaded = True):
    """ Show a windows 10 notification toast """
    toaster.show_toast(
        constants.APP_NAME, 
        message,
        threaded = threaded,
    )

def exit_in_seconds(seconds=5, level=0):
    ''' Allow time to read console before exit '''

    ansi_colour = Fore.CYAN
    if level > 0: 
        ansi_colour = Fore.RED

    for i in range(seconds, -1, -1):
        sys.stdout.write(f"{ansi_colour}\rExiting in " + str(i))
        time.sleep(1)

    erase_line = '\x1b[2K' 
    sys.stdout.write(f"\r{erase_line}")
    print()
    sys.exit(level)

def create_tasks(clips, **kwargs):
    ''' Create metadata dictionaries to send as Celery tasks' '''

    # Append project details to each clip
    tasks = [dict(item, **kwargs) for item in clips]
    return tasks

def queue_job(tasks):
    ''' Send tasks as a celery job 'group' '''

    # Wrap job object in task function
    callable_tasks = [do.encode.s(x) for x in tasks]

    if settings.get("app", "debug"):
        print(callable_tasks)


    # Create job group to retrieve job results as batch
    job = group(callable_tasks)

    # Queue job
    print(f"{Fore.CYAN}Sending job.")
    return job.apply_async()

def parse_for_link(media_list):

    print(f"{Fore.CYAN}Linking {len(media_list)} proxies.")
    existing_proxies = []

    for media in media_list:
        proxy = media.get('Unlinked Proxy', None)
        if proxy is None:
            continue

        existing_proxies.append(proxy)

        if not os.path.exists(proxy):
            tkinter.messagebox.showerror(title = "Error linking proxy", message = f"Proxy media not found at '{proxy}'")
            print(f"{Fore.RED}Error linking proxy: Proxy media not found at '{proxy}'")
            continue

        else:
            media.update({'Unlinked Proxy': None}) # Set existing to none once linked

        media.update({'Proxy':"1280x720"})

        
    link(existing_proxies)    

    print()

    pre_len = len(media_list)
    media_list = [x for x in media_list if 'Unlinked Proxy' not in x]
    post_len = len(media_list)
    print(f"{pre_len - post_len} proxy(s) linked, will not be queued.")
    print(f"{Fore.MAGENTA}Queueing {post_len}")
    print()

    return media_list

def confirm(title, message):
    '''General tkinter confirmation prompt using ok/cancel.
    Keeps things tidy'''

    answer = tkinter.messagebox.askokcancel(
        title = title, 
        message = message,
    )

    some_action_taken = True
    return answer

def get_expected_proxy_path(media_list):
    '''Retrieves the current expected proxy path using the source media path.
    Useful if you need to handle any matching without 'Proxy Media Path' values from Resolve.'''

    for media in media_list:

        proxy_dir = prefs.paths.proxy_dir

        file_path = media['File Path']
        p = pathlib.Path(file_path)

        # Tack the source media relative path onto the proxy media path
        expected_proxy_path = os.path.join(proxy_dir, os.path.dirname(p.relative_to(*p.parts[:1])))
        media.update({'Expected Proxy Path': expected_proxy_path})

    return media_list

def get_safe_track_count(timeline):
    """ Resolve API won't retrieve track items if less than 2 tracks. 
    Warn if less than two, otherwise return track length 
    """

    track_len = timeline.GetTrackCount("video")
    if track_len == 1: 
        # Really not sure why, but Resolve returns no clips if only one vid timeline
        message = "Not enough tracks on timeline to get clips.\nPlease create another empty track"
        print(f"\nERROR:\n{message}")
        tkinter.messagebox.showinfo("ERROR", message)
        sys.exit(1)

    if settings.get("app", "debug"):
        print(f"{Fore.GREEN}Video track count: {track_len}")
    return track_len

def get_all_clip_properties_from_timeline(timeline, media_type):
    """ Retrieve clip properties from each track item with unique source media.
    """

    track_len = get_safe_track_count(timeline)  

    all_clips = []
    for i in range(1, track_len):
        items = timeline.GetItemListInTrack("video", i)
        
        if items is None:
            print(f"{Fore.YELLOW}No items found in track {i}")
            continue

        for item in items:
            try:
                media_item = item.GetMediaPoolItem()
                attributes = media_item.GetClipProperty()
                all_clips.append(attributes)

            except TypeError:
                if settings.get("app", "debug"):
                    print(f"{Fore.MAGENTA}Skipping {item.GetName()}, no linked media pool item.")    
                continue

    # Get unique source media from clips on timeline
    unique_sets = set(frozenset(d.items()) for d in all_clips)
    return [dict(s) for s in unique_sets]

def get_active_clip_properties_from_timeline(timeline, media_type):
    """ Get clip properties for the clip directly underneath 
    the playhead """

    track_len = get_safe_track_count(timeline)  

    print("Need to work on this!!")
    sys.exit(1)
    return


# TODO: flesh this out! We need to generalise everything proxy related,
# and make these functions useful as imports for a 'stabilise' module
# or any other future module.

def get_timeline_items(timeline, item_type="all", media_type="video"):
    """ Retrieve clip properties dictionary for track items """ 

    if item_type == "all":
        media_list = get_all_clip_properties_from_timeline(timeline, media_type)

    elif item_type =="active":
        media_list = get_active_clip_properties_from_timeline(timeline, media_type)

    else:
        raise ValueError(f"'{item_type}' is not a supported item_type!")

    return media_list

if __name__ == "__main__":

    init(autoreset=True)
    toaster = ToastNotifier()

    root = tkinter.Tk()
    root.withdraw()



    f = Figlet()
    print(f.renderText("Queue/Link Proxies"))
    print()

    try:       
        # Get global variables
        resolve = python_get_resolve.get_resolve()
        project = resolve.GetProjectManager().GetCurrentProject()
        timeline = project.GetCurrentTimeline()
        resolve_job_name = f"{project.GetName().upper()} - {timeline.GetName().upper()}"

        print(f"{Fore.CYAN}Working on: {resolve_job_name}") 


        print()
        # HEAVY LIFTING HERE
        clips = get_timeline_items(timeline, item_type="all", media_type="video")

        # clips = handle_orphaned_proxies(clips)
        clips = handle_already_linked(clips)
        clips = handle_offline_proxies(clips)
        clips = handle_existing_unlinked(clips)

        if len(clips) == 0:
            if not some_action_taken:
                print(f"{Fore.RED}No clips to queue.")
                tkinter.messagebox.showwarning("No clip to queue", "There is no new media to queue for proxies.\n" +
                                            "If you want to re-rerender some proxies, unlink those existing proxies within Resolve and try again.")
                sys.exit(1)
            else:
                print(f"{Fore.GREEN}All clips linked now. No encoding necessary.")

        # Final Prompt confirm
        if not confirm(
            "Go time!", 
            f"{len(clips)} clip(s) are ready to queue!\n" +
            "Continue?"
        ):
            sys.exit(0)

        tasks = create_tasks(
            clips,
            project = project.GetName(), 
            timeline = timeline.GetName(),
        )

        job = queue_job(tasks)

        toast('Started encoding job')
        print(f"{Fore.YELLOW}Waiting for job to finish. Feel free to minimize.")
        
        job_metadata = job.join()

        # Notify failed
        if job.failed():
            fail_message = f"Some videos failed to encode! Check dashboard @ 192.168.1.19:5555."
            print(Fore.RED + fail_message)
            toast(fail_message)

        # Notify complete
        complete_message = f"Completed encoding {job.completed_count()} videos."
        print(Fore.GREEN + complete_message)
        print()

        toast(complete_message)

        # ATTEMPT POST ENCODE LINK
        active_project = resolve.GetProjectManager().GetCurrentProject().GetName()
        linkable = [x for x in job_metadata if x['project'] == active_project]

        if len(linkable) == 0:
            print(
                f"{Fore.YELLOW}\nNo proxies to link post-encode.\n" +
                "Resolve project may have changed.\n" +
                "Skipping."
            )

        else: 
            parse_for_link(linkable)

        app_exit(0)

    
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        
        tkinter.messagebox.showerror("ERROR", tb)
        print("ERROR - " + str(e))

        app_exit(1)
