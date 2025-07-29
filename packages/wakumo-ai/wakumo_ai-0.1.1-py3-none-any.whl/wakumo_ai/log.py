VERBOSE_MODE = False

def set_verbose(enabled: bool):
    global VERBOSE_MODE
    VERBOSE_MODE = enabled

def vprint(*args, **kwargs):
    if VERBOSE_MODE:
        print(*args, **kwargs)