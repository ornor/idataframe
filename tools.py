import signal
from contextlib import contextmanager


__all__ = ['in_notebook', 'display_auto', 'display_ipython', 'display_text', 'display_hide']


def in_notebook():
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


def display_auto(obj=None, *args, **kwargs):
    if in_notebook:
        display_ipython(obj, *args, **kwargs)
    else:
        display_text(obj, *args, **kwargs)


def display_ipython(obj=None, *args, **kwargs):
    from IPython.display import display, HTML
    import warnings
    warnings.filterwarnings('ignore')
    
    if obj is None:
        obj = ''
    if isinstance(obj, str):
        if len(obj) > 1 and obj[0] == '<':  # HTML string
            display(HTML(obj, *args, **kwargs))
        else:  # normal string
            print(obj, *args, **kwargs)
    else:
        display(obj, *args, **kwargs)


def display_text(obj=None, *args, **kwargs):
    if obj is None:
        obj = ''
    if isinstance(obj, str):
        print(obj, *args, **kwargs)
    else:
        print()
        print(str(type(obj)))
        print()


def display_hide(*args, **kwargs):
    pass

