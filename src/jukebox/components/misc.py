"""
Miscellaneous function package
"""
import os
import time
import logging.handlers
import jukebox
import jukebox.plugs as plugin
from jukebox.daemon import get_jukebox_daemon

logger = logging.getLogger('jb.misc')


@plugin.register
def rpc_cmd_help():
    """Return all commands for RPC"""
    return plugin.summarize()


@plugin.register
def get_all_loaded_packages():
    """Get all successfully loaded plugins"""
    return plugin.get_all_loaded_packages()


@plugin.register
def get_all_failed_packages():
    """Get all plugins with error during load or initialization"""
    return plugin.get_all_failed_packages()


@plugin.register
def get_start_time():
    """Time when JukeBox has been started"""
    return time.ctime(get_jukebox_daemon().start_time)


def get_log(handler_name: str):
    """Get the log file from the loggers (debug_file_handler, error_file_handler)"""
    # With the correct logger.yaml, there is up to two RotatingFileHandler attached
    content = "No file handles configured"
    for h in logging.getLogger('jb').handlers:
        if isinstance(h, logging.handlers.RotatingFileHandler):
            content = f"No file handler with name {handler_name} configured"
            if h.name == handler_name:
                try:
                    size = os.path.getsize(h.baseFilename)
                    if size == 0:
                        content = f"Log file {h.baseFilename} is empty. (Could be good or bad: " \
                                  "Is the RotatingFileHandler configured as handler sink for jb in logger.yaml?)"
                        break
                    mtime = os.path.getmtime(h.baseFilename)
                    stime = get_jukebox_daemon().start_time
                    logger.debug(f"Accessing log file {h.baseFilename} modified time {time.ctime(mtime)} "
                                 f"(JB start time {time.ctime(stime)})")
                    # Generous 3 second tolerance between file creation and jukebox start time recording
                    if mtime - stime < -3:
                        content = (f"Log file {h.baseFilename} too old for this Jukebox start! "
                                   f"Is the RotatingFileHandler configured as handler sink for jb in logger.yaml?")
                        break
                    with open(h.baseFilename) as stream:
                        content = stream.read()
                except Exception as e:
                    content = f"{e.__class__.__name__}: {e}"
                    logger.error(content)
                break
    return content


@plugin.register
def get_log_debug():
    """Get the log file (from the debug_file_handler)"""
    return get_log('debug_file_handler')


@plugin.register
def get_log_error():
    """Get the log file (from the error_file_handler)"""
    return get_log('error_file_handler')


@plugin.register
def get_version():
    return jukebox.version()
