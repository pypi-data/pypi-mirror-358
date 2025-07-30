# cfglog: Configurate Logging Easily

`cfglog` provides an easy way to setup logging. It supports the configuration of datetime in the logging system, which is useful when you want to share the time spent on the program's execution without revealing when the program was run.


## Installation

```bash
pip install --upgrade cfglog
```

## Usage Example

```python
>>> import datetime as dt
>>> import logging
>>> import sys
>>> import cfglog
>>> cfglog.basicConfig(
...     level=logging.DEBUG,  # logging when level >= DEBUG
...     format="%(asctime)s [%(levelname)s] %(message)s",
...     datefmt="%H:%M:%S",
...     datetime=dt.datetime(2000, 1, 1),  # set current datetime in logging system as 2000-01-01T00:00:00
...     stream=sys.stdout,  # write to stdout rather than stderr
...     force=True,  # overwrite existing configuration
... )
>>> logging.debug("This is a debug message.")
00:00:00 [DEBUG] This is a debug message.
>>> logging.info("This is an info message.")
00:00:00 [INFO] This is an info message.
>>> logging.warning("This is a warning message.")
00:00:00 [WARNING] This is a warning message.
>>> logging.error("This is an error message.")
00:00:00 [ERROR] This is an error message.
>>> logging.critical("This is a critical message.")
00:00:00 [CRITICAL] This is a critical message.
```

## APIs

class `TimeoffsetFormatter`: An extended version of `logging.Formatter` that supports datetime configuration via the parameter `datetime`.

Function `basicConfig()`: An extended version of `logging.basicConfig()` that supports datetime configuration via the parameter `datetime`, and some features in newer/future version of Python such as `style`, `handlers`, `force`, `encoding`, and `errors`.
