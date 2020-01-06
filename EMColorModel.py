"""
Encounter Mapper is a tile-based encounter map creator for tabletop RPGs.
Copyright 2019, 2020 Eric Symmank

This file is part of Encounter Mapper.

Encounter Mapper is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

Encounter Mapper is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Encounter Mapper.
If not, see <https://www.gnu.org/licenses/>.
"""

from PyQt5.QtGui import QColor


class EMColorModel:
    """
    Contains an array of colors used for painting the bg and FG of tiles.

    This class will be added to EMModel.py in the future, and updated to
    match the existing model classes.
    """

    def __init__(self, name, r, g, b):
        self.name = name
        self.color = QColor(r, g, b)

    def setColor(self, r, g, b):
        self.color = QColor(r, g, b)

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def getColor(self):
        return self.color

    def jsonObj(self):

        return {
            "name": self.name,
            "r": self.color.red(),
            "g": self.color.green(),
            "b": self.color.blue(),
        }
