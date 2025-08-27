#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99


__author__ = 'Dieter Vansteenwegen'
__project__ = 'Turing display driver'
__project_link__ = 'https://www.boxfish.be'

# import logging

# import datetime as dt
# import logging.handlers
# from pathlib import Path

# LOG_FMT = (
# '%(asctime)s|%(levelname)-8.8s|%(module)-15.15s|%(lineno)-0.4d|'
# '%(funcName)-20.20s|%(message)s|'
# )
# DATEFMT = '%d/%m/%Y %H:%M:%S'
# LOGFILE = Path(Path.home(), 'logs', 'turing_display.log')
# LOG_FILE_MAX_BYTES = 1000000
# LOG_BACKUP_COUNT = 10
# TZ_UTC = dt.timezone.utc
# CONSOLE_LOG_LEVEL = logging.INFO


# class MilliSecondsFormatter(logging.Formatter):
#     """Formats timestamp of log messages, keeping first three digits of milliseconds.


#     Args:
#         logging (logging.Formatter): formatter to add timestamp formatter to.
#     """

#     def formatTime(self, record: logging.LogRecord, datefmt: Union[str, None] = None)
# -> str:  # noqa: N802
#         """Formats timestamp of log messages, keeping first three digits of milliseconds.

#         Args:
#             record (logging.LogRecord): LogRecord to apply formatting to.
#             datefmt (Union[str, None], optional): datefmt for formatter. Uses DATEFMT is None.
#                                                     Defaults to None.

#         Returns:
#             str: formatted timestamp for LogRecord
#         """
#         ct = dt.datetime.fromtimestamp(record.created).astimezone(TZ_UTC)
#         if datefmt:
#             s = ct.strftime(datefmt)
#         else:
#             t = ct.strftime(DATEFMT)
#             s = f'{t}.{int(record.msecs):03}'
#         return s


# def setup_logger() -> logging.Logger:
#     """Setup logging.

#     Returns logging.Logger object with  1 streamhandler (to stdout).
#     This handler has a level of CONSOLE_LOG_LEVEL uses MilliSecondsFormatter(LOG_FMT).

#     Returns:
#         logging.Logger: configured logger object
#     """
#     logger = logging.getLogger(__name__)  # Specifiy name so we don't touch the root logger
#     logger.setLevel(logging.DEBUG)
#     # add_console_handler(logger)  # Don't add log handlers to modules
#     return logger


# def add_console_handler(logger: logging.Logger) -> None:
#     """Add consolehandler to logger.


#     Args:
#         logger (logging.Logger): Logger to add handler to.
#     """
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(CONSOLE_LOG_LEVEL)
#     console_handler.setFormatter(MilliSecondsFormatter(LOG_FMT))
#     logger.addHandler(console_handler)


# def add_rotating_file(logger: logging.Logger) -> None:
#     """Add rotating file handler to Logger instance.

#     Logfile used: LOGFILE
#     Maximum log size: LOGMAXBYTES.
#     Logging level set to DEBUG.
#     Format set to LOG_FMT.
#     Creates directory for logfiles if non-existent.

#     Args:
#         logger (logging.Logger): Logger to add handler to.
#     """
#     base = Path(LOGFILE).parent
#     if not base.is_dir():
#         logger.debug(f'Logging directory {base} does not exist. Creating...')
#         base.mkdir(parents=True, exist_ok=True)
#         logger.debug(f'Created logging directory {base}')
#     rot_fil_handler = logging.handlers.RotatingFileHandler(
#         LOGFILE,
#         maxBytes=LOG_FILE_MAX_BYTES,
#         backupCount=LOG_BACKUP_COUNT,
#     )
#     rot_fil_handler.doRollover()
#     rot_fil_handler.setLevel(logging.DEBUG)
#     rot_fil_handler.setFormatter(MilliSecondsFormatter(LOG_FMT))
#     logger.addHandler(rot_fil_handler)
