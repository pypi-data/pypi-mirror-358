# Copyright 2023 LucidInvestor <https://lucidinvestor.ca/>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging as log


class Analytics:
    """
    Format Logging across classes and modules
    """
    def __init__(self, analytics_name, **kwargs):
        self.analytics_name = analytics_name
        # create logger object
        self.__logger = None
        self.__log_state = False
        return

    def level_logbook2logging(self, level):
        if level == 6:
            return log.CRITICAL
        elif level == 5:
            return log.ERROR
        elif level == 4:
            return log.ERROR
        elif level == 3:
            return log.WARNING
        elif level == 2:
            return log.INFO
        elif level == 1:
            return log.DEBUG
        else:
            return log.DEBUG

    def set_log_option(self, logconsole=False, level=3):

        self.__log_state = logconsole
        level = self.level_logbook2logging(level)

        # create logger object
        if self.__logger is None:
            self.__logger = log.getLogger(self.analytics_name)
            # clearing any existing handlers : not pretty but efficient, and
            # associating handlers based on user-configuration input param.
            self.__logger.handlers = []

        # create logger with 'spam_application'
        self.__logger.setLevel(level)
        # don't propagate with the main logger as we create custom handler (console, file, db)
        self.__logger.propagate = False

        msg = ""
        if self.__log_state:
            msg = msg + self.set_log_console(level)
        return msg

    def set_log_console(self, level):
        """
        level is adjusted in set_log_option()
        """

        # do we already have a StreamHandler attached to the logger for the console (no other use in our case)
        if any(isinstance(x, log.StreamHandler) for x in log.getLogger(self.analytics_name).handlers):
            msg = ""
            return msg

        # creating handler to write log on console/terminal
        ch = log.StreamHandler()

        # set level and format
        ch.setLevel(level)
        formatter = log.Formatter('\n' + self.analytics_name + '/AnalyticsManager -> %(asctime)s %(module)s %(name)s.%('
                                                               'funcName)s +%(lineno)s: %(''levelname)-8s [%(process)d]'
                                                               ' %(message)s')
        ch.setFormatter(formatter)
        self.__logger.addHandler(ch)
        self.__logger.propagate = False

        msg = "logging mode: " + str(self.__logger.level) + " activated in console"
        return msg

    def add_log(self, logtype, msg, data=None, broker_msg=" | Backtesting Session."):
        if not self.__log_state or len(msg) == 0:
            return
        timestamped_msg = "\nbacktrader time: "
        if data is None:
            timestamped_msg = timestamped_msg + "Not provided. "
        else:
            try:
                timestamped_msg = timestamped_msg + str(data.num2date())
            except IndexError:
                timestamped_msg = timestamped_msg + "N/A - if live data is probably being accrued. "

        timestamped_msg = timestamped_msg + broker_msg + msg + "\n<end of msg>"

        if logtype == 'critical':
            self.__logger.critical(timestamped_msg)
        elif logtype == 'error':
            self.__logger.error(timestamped_msg)
        elif logtype == 'warning':
            self.__logger.warning(timestamped_msg)
        elif logtype == 'info':
            self.__logger.info(timestamped_msg)
        elif logtype == 'debug':
            self.__logger.debug(timestamped_msg)

        return timestamped_msg
