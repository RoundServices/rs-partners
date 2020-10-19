# rs-partners is available under the MIT License. https://gitlab.com/roundservices/rs-partners/
# Copyright (c) 2020, Round Services LLC - https://roundservices.biz/
#
# Author: Ezequiel Sandoval - esandoval@roundservices.biz
#
import sys
from org.gluu.service import PythonService
from org.slf4j import Logger, LoggerFactory


class Logger(object):
    """ Logger is an auxiliary class for granular logging and pretty printing. Log level is set on Gluu Config.

        Args:
            name (str): Script that invokes Logger instance

        Attributes:
            _name: name of the Logger instance
        """

    def __init__(self, name):
        self._name = name
        self._logger = LoggerFactory.getLogger(PythonService)

    def trace(self, msg, *args):
        """ TRACE log

        :param msg: msg to log
        """
        self._doLog(self._logger.trace, msg, *args)

    def debug(self, msg, *args):
        """ DEBUG log

        :param msg: msg to log
        """
        self._doLog(self._logger.debug, msg, *args)

    def info(self, msg, *args):
        """ INFO log

        :param msg: msg to log
        """
        self._doLog(self._logger.info, msg, *args)

    def warn(self, msg, *args):
        """ WARN log

        :param msg: msg to log
        """
        self._doLog(self._logger.warn, msg, *args)

    def error(self, msg, *args):
        """ ERROR log

        :param msg: msg to log
        """
        self._doLog(self._logger.error, msg, *args)

    def _doLog(self, log_level_function, msg, *args):
        """ logs according level set

        :param function_log_level: log level
        :param msg: msg to log
        """
        log_level_function("{} || {} || {}".format(self._name, sys._getframe(2).f_code.co_name, self.encodeString(msg, *args)))

    def encodeString(self, msg, *args):
        msg = msg.encode('utf-8')
        if len(args) > 0:
            encoded_args = []
            for arg in args:
                encoded_args.append(
                    arg if not isinstance(arg, str) else arg.encode('utf-8')
                )
            msg = msg.format(*encoded_args)
        return msg
