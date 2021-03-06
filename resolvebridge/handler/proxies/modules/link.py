
#!/usr/bin/env python3.6
# Link proxies

import os
import re
import tkinter
import tkinter.messagebox
import traceback
from inspect import Attribute
from tkinter import filedialog

import yaml
from colorama import Fore, Style, init

from python_get_resolve import GetResolve

# Get environment variables #########################################
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "proxy_encoder", "config.yml")) as file: 
    config = yaml.safe_load(file)
    
proxy_path_root = config['paths']['proxy_path_root']
acceptable_exts = config['filters']['acceptable_exts']

#####################################################################

debug = False
      
# Get global variables
resolve = GetResolve()
project = resolve.GetProjectManager().GetCurrentProject()
media_pool = project.GetMediaPool()

def debug_print(variable):
    print(variable, '=', repr(eval(variable)))
    return

def get_proxy_path():
    root = tkinter.Tk()
    root.withdraw()
    f = filedialog.askdirectory(initialdir = proxy_path_root, title = "Link proxies")
    if f is None:
        print("User cancelled dialog. Exiting.")
        exit(0)
    return f

def recurse_dir(root):
    """Recursively search given directory for files
    and return full filepaths
    """

    all_files = [os.path.join(root, f) for root, dirs, files in os.walk(root) for f in files]
    return all_files

def filter_files(dir_, acceptable_exts):
    """Filter files by allowed filetype
    """

    allowed = [x for x in dir_ if os.path.splitext(x) in acceptable_exts]
    return allowed


    print(f"{Fore.CYAN}{timeline.GetName()} - Video track count: {track_len}")

def get_track_items(timeline, track_type="video"):
    """Retrieve all video track items from a given timeline object"""

    track_len = timeline.GetTrackCount("video") 
    if debug: print(f"{Fore.CYAN}{timeline.GetName()} - Video track count: {track_len}")

    items = []
    
    for i in range(track_len):
        i += 1 # Track index starts at one...
        items.extend(timeline.GetItemListInTrack(track_type, i))
        
    return items

def get_resolve_timelines(active_timeline_first=True):
    """ Return a list of all Resolve timeline objects in current project. """

    timelines = []

    timeline_len = project.GetTimelineCount()
    if timeline_len > 0:

        for i in range(1, timeline_len + 1):
            timeline = project.GetTimelineByIndex(i)
            timelines.append(timeline)

        if active_timeline_first:
            active = project.GetCurrentTimeline().GetName()                     # Get active timeline
            timeline_names = [x.GetName() for x in timelines]
            active_i = timeline_names.index(active)                             # It's already in the list, find it's index
            timelines.insert(0, timelines.pop(active_i))            # Move it to the front, indexing should be the same as name list
    else:
         return False

    return timelines

def get_timeline_data(timeline):
    """ Return a dictionary containing timeline names, 
    their tracks, clips media paths, etc.
    """

    clips = get_track_items(timeline, track_type="video")
    data = {
        'timeline': timeline,
        'name': timeline.GetName(), 
        'track count': timeline.GetTrackCount(),
        'clips': clips,
    }
    
    return data

def __link_proxies(proxy_files, clips):
    """ Actual linking function.
    Matches filenames between lists of paths.
    'clips' actually needs to be a Resolve timeline item object.
    """

    linked_proxies = []
    failed_proxies = []
    linked_clips = []

    for proxy in proxy_files:
        for clip in clips:

            proxy_name = os.path.splitext(os.path.basename(proxy))[0]
            if proxy in failed_proxies:
                if debug: print(f"{Fore.YELLOW}Skipping {proxy_name}, already failed.")
                break

            try:
                media_pool_item = clip.GetMediaPoolItem()
                path = media_pool_item.GetClipProperty("File Path")
                filename = os.path.splitext(os.path.basename(path))[0]

                if proxy_name.lower() in filename.lower():

                    print(f"{Fore.GREEN}Found match:")
                    print(f"{proxy} &\n{path}")

                    if media_pool_item.LinkProxyMedia(proxy):

                        print(f"{Fore.GREEN}Linked\n")
                        linked_proxies.append(proxy)
                        linked_clips.append(clip)

                    else:
                        print(f"{Fore.RED}Failed link.\n")
                        failed_proxies.append(proxy)

            except AttributeError:

                if debug: 
                    print(f"{Fore.YELLOW}{clip.GetName()} has no 'file path' attribute," + 
                    " probably Resolve internal media.")

    
    return linked_proxies, failed_proxies

def link_proxies(proxy_files):
    """ Attempts to match source media in active Resolve project
     with a list of filepaths to proxy files."""

    linked = []
    failed = []

    timelines = get_resolve_timelines()
    if not timelines:
        raise Exception("No timelines exist in current project.")

    # Get clips from all timelines.
    for timeline in timelines:
        
        timeline_data = get_timeline_data(timeline)
        clips = timeline_data['clips']
        unlinked_source = [x for x in clips if x not in linked]

        if len(unlinked_source) == 0:
            if debug: print(f"{Fore.YELLOW}No more clips to link in {timeline_data['name']}")
            continue
        else:
            print(f"{Fore.CYAN}Searching timeline {timeline_data['name']}")
        
        unlinked_proxies = [x for x in proxy_files if x not in linked]
        print(f"Unlinked source count: {len(unlinked_source)}")
        print(f"Unlinked proxies count: {len(unlinked_proxies)}")


        if len(unlinked_proxies) == 0:
            print(f"{Fore.YELLOW}No more proxies to link in {timeline_data['name']}")
            return
  
        linked_, failed_ = (__link_proxies(proxy_files, clips))

        linked.extend(linked_)
        failed.extend(failed_)

        if debug: print(f"Linked: {linked}, Failed: {failed}")

    if len(failed) > 0:
        print(f"{Fore.RED}The following files matched, but couldn't be linked. Suggest rerendering them:")
        [print(os.path.basename(x)) for x in failed]
        print()

    return linked

if __name__ == "__main__":

    try:
        init(autoreset=True)

        proxy_dir = get_proxy_path()
        print(f"Passed directory: '{proxy_dir}'\n")

        all_files = recurse_dir(proxy_dir)
        proxy_files = filter_files(all_files, acceptable_exts)
        linked = link_proxies(proxy_files)

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        tkinter.messagebox.showinfo("ERROR", tb)
        print("ERROR - " + str(e))