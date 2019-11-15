from PyQt5.QtGui import QColor


class EMColorModel:
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
