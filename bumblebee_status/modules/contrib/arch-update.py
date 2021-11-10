"""Check updates to Arch Linux.

Requires the following executable:
    * checkupdates (from pacman-contrib)

contributed by `lucassouto <https://github.com/lucassouto>`_ - many thanks!
"""

import logging
from time import sleep

import core.module
import core.widget
import core.decorators

import util.cli


class Module(core.module.Module):
    @core.decorators.every(minutes=60)
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.utilization))
        self.background = True
        self.__packages = 0
        self.__error = False
        self.__connection_err = False

    @property
    def __format(self):
        return self.parameter("format", "Update Arch: {}")

    def utilization(self, widget):
        if self.__connection_err:
            return "Arch: No IP"
        else:
            return self.__format.format(self.__packages)


    def hidden(self):
        return self.__packages == 0 and not self.__error

    def update(self):
        self.__error = False
        sleep(1)
        code, result = util.cli.execute(
            "checkupdates", ignore_errors=True, return_exitcode=True
        )

        self.__connection_err = code == 1
        if code == 0:
            self.__packages = len(result.strip().split("\n"))
        elif code == 2:
            self.__packages = 0
        else:
            self.__error = True
            logging.error("checkupdates exited with {}: {}".format(code, result))

    def state(self, widget):
        if self.__connection_err:
            return None
        elif self.__error:
            return "warning"
        warn = 1
        not_connected = True
        if not_connected:
            warn = 100
        return self.threshold_state(self.__packages, warn, 100)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
