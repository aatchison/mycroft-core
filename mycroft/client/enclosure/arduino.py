# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


from mycroft.util.log import getLogger

__author__ = 'jdorleans'

LOGGER = getLogger(__name__)


class EnclosureArduino:
    """
    Listens to enclosure commands for Mycroft's Arduino.

    Performs the associated command on Arduino by writing on the Serial port.
    """

    def __init__(self, ws, writer):
        """Enclosure class init
            Args:
                ws (obj): websocket to connect to
                writer (obj): serial port writer
        """
        self.ws = ws
        self.writer = writer
        self.__init_events()

    def __init_events(self):
        """Enclosure event init
        """
        self.ws.on('enclosure.system.reset', self.reset)
        self.ws.on('enclosure.system.mute', self.mute)
        self.ws.on('enclosure.system.unmute', self.unmute)
        self.ws.on('enclosure.system.blink', self.blink)

    def reset(self, event=None):
        """Arduino system reset event
        """
        self.writer.write("system.reset")

    def mute(self, event=None):
        """Arduino speaker hard mute event
        """
        self.writer.write("system.mute")

    def unmute(self, event=None):
        """Arduino speaker hard unmute envent
        """
        self.writer.write("system.unmute")

    def blink(self, event=None):
        """Arduino eyes blink event
        """
        times = 1
        if event and event.data:
            times = event.data.get("times", times)
        self.writer.write("system.blink=" + str(times))
