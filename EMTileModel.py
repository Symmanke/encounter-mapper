from PyQt5.QtCore import (Qt, QPoint)
from PyQt5.QtGui import QColor


class EMTileModel():
    def __init__(self, name):
        self.name = name
        self.size = (1, 1)
        self.backgroundColor = QColor(105, 141, 85)
        self.foregroundColor = QColor(101, 101, 102)
        self.fgPoints = [
            QPoint(0, 0),
            QPoint(0, 10),
            QPoint(100, 10),
            QPoint(100, 0)
        ]

    # def __init__(name, size, bc, fc, points):
    #     self.name = name
    #     self.size = size
    #     self.backgroundColor = bc
    #     self.foregroundColor = fc
    #     self.fgPoints = points

    def setName(self, name):
        self.name = names

    def setFgPoints(self, points):
        self.fgPoints = points

    def generatePointOffset(self, xOff, yOff, scale):
        tempPoints = []
        scaleX = xOff * scale
        scaleY = yOff * scale
        pointScale = scale/100
        for point in self.fgPoints:
            tempPoints.append(QPoint(point.x() * pointScale + scaleX,
                                     point.y() * pointScale + scaleY))

        return tempPoints
