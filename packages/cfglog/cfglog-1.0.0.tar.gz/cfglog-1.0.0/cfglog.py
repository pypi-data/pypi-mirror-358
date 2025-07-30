import io
from logging import FileHandler, Formatter, StreamHandler, getLogger
import sys
import time


class TimeoffsetFormatter(Formatter):
    """TimeoffsetFormatter

    Parameters:
        *args (tuple, Optional): arguments for Formatter, including fmt, datefmt, [style].
        datetime (datetime.datetime, Optional): Specify the datetime to reset.
        **kwargs (dict, Optional): keyword arguments for Formatter, including fmt, datefmt, [style], validate, defaults.

    See also:
        https://docs.python.org/3/library/logging.html#logging.Formatter
    """
    def __init__(self, *args, datetime=None, **kwargs):
        super().__init__(*args, **kwargs)
        if datetime:
            self.timeoffset = datetime.timestamp() - time.time()
        else:
            self.timeoffset = 0

    def formatTime(self, record, datefmt=None):
        """formatTime

        See also:
            https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime
        """
        timestamp = record.created + self.timeoffset
        ct = self.converter(timestamp)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime(self.default_time_format, ct)
            if self.default_msec_format:
                s = self.default_msec_format % (s, record.msecs)
        return s


root = getLogger()


def basicConfig(**kwargs):
    """
    Extended version of logging.basicConfig() to do basic configuration.

    This function does nothing if the root logger already has handlers
    configured, unless the keyword argument *force* is set to ``True``.
    It is a convenience method intended for use by simple scripts
    to do one-shot configuration of the logging package.

    The default behaviour is to create a StreamHandler which writes to
    sys.stderr, set a formatter using the BASIC_FORMAT format string, and
    add the handler to the root logger.

    A number of optional keyword arguments may be specified, which can alter
    the default behaviour.

    Parameters:
        datetime (datetime.datetime, Optional): Overwrite current datetime of logging.
        style (str, Optional): It should not be specified for Python version<3.2.
        errors (str, Optional): It should not be specified for Python version<3.8.
        **kwargs (dict, Optional): keyword arguments for logging.basicConfig(),
                including 'handlers', 'force', and 'encoding'.

    See also:
        https://docs.python.org/3/library/logging.html#logging.basicConfig
        https://github.com/python/cpython/blob/main/Lib/logging/__init__.py
    """
    force = kwargs.pop('force', False)
    if force:
        root.handlers.clear()

    force = kwargs.pop('force', False)
    encoding = kwargs.pop('encoding', None)
    errors = kwargs.pop('errors', 'backslashreplace')
    if force:
        for h in root.handlers[:]:
            root.removeHandler(h)
            h.close()
    if len(root.handlers) == 0:
        handlers = kwargs.pop("handlers", None)
        if handlers is None:
            if "stream" in kwargs and "filename" in kwargs:
                raise ValueError("'stream' and 'filename' should not be specified together")
        else:
            if "stream" in kwargs or "filename" in kwargs:
                raise ValueError("'stream' or 'filename' should not be specified together with 'handlers'")
        if handlers is None:
            filename = kwargs.pop("filename", None)
            mode = kwargs.pop("filemode", 'a')
            if filename:
                if 'b' in mode:
                    errors = None
                else:
                    encoding = io.text_encoding(encoding)
                if sys.version_info < (3, 8):
                    if errors is not None:
                        raise ValueError("errors argument not supported in Python < 3.8")
                        h = FileHandler(filename, mode, encoding=encoding)
                else:
                    h = FileHandler(filename, mode, encoding=encoding, errors=errors)
            else:
                stream = kwargs.pop("stream", None)
                h = StreamHandler(stream)
            handlers = [h]
        fmt = kwargs.pop("formatter", None)
        if fmt is None:
            dfs = kwargs.pop("datefmt", None)
            style = kwargs.pop("style", '%')
            default_formats = {
                '%': "%(levelname)s:%(name)s:%(message)s",
                '{': '{levelname}:{name}:{message}',
                '$': '${levelname}:${name}:${message}',
            }
            if style not in default_formats:
                raise ValueError('Style must be one of: %s' % ','.join(
                                default_formats.keys()))
            if sys.version_info < (3, 2):
                if style != '%':
                    raise ValueError('Style must be "%" on Python < 3.2')
                style = None
            fs = kwargs.pop("format", default_formats[style])
            datetime = kwargs.pop("datetime", None)
            if style == '%':
                fmt = TimeoffsetFormatter(fmt=fs, datefmt=dfs, style=style, datetime=datetime)
            else:
                fmt = TimeoffsetFormatter(fmt=fs, datefmt=dfs, datetime=datetime)
        else:
            for forbidden_key in ("datefmt", "format", "style", "datetime"):
                if forbidden_key in kwargs:
                    raise ValueError(f"{forbidden_key!r} should not be specified together with 'formatter'")
        for h in handlers:
            if h.formatter is None:
                h.setFormatter(fmt)
            root.addHandler(h)
        level = kwargs.pop("level", None)
        if level is not None:
            root.setLevel(level)
        if kwargs:
            keys = ', '.join(kwargs.keys())
            raise ValueError('Unrecognised argument(s): %s' % keys)
