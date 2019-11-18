from PyQt5.QtGui import QColor
from PyQt5.QtCore import (QObject, pyqtSignal, QPoint)


class EMTileGroupModel(QObject):
    # pointList = []
    # name = "DEFAULT"

    modelUpdated = pyqtSignal()

    def __init__(self, name="DEFAULT", pointList=None):
        super(EMTileEditorModel, self).__init__()
        self.name = name
        self.pointList = [] if pointList is None else pointList
        self.bgColor = QColor(105, 141, 85)
        self.fgColor = QColor(101, 101, 102)
        self.selectedIndex = -1
        self.uid = -1

    @classmethod
    def createCopy(cls, model):
        mcopy = cls(model.getName(), [])
        bg = model.getBgColor()
        fg = model.getFgColor()

        mcopy.setBgColor(bg.red(), bg.green(), bg.blue())
        mcopy.setFgColor(fg.red(), fg.green(), fg.blue())
        for point in model.pointList:
            mcopy.addPoint(point[0], point[1])
        return mcopy

    def setBgColor(self, r, g, b):
        self.bgColor = QColor(r, g, b)

    def setFgColor(self, r, g, b):
        self.fgColor = QColor(r, g, b)

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def addPoint(self, x, y):
        # if self.selectedIndex == -1:
        #     self.pointList.append((x, y))
        #     self.selectedIndex = len(self.pointList) - 1
        # else:
        self.pointList.insert(self.selectedIndex+1, (x, y))
        self.selectedIndex += 1
        self.modelUpdated.emit()

    def setSelectedPoint(self, x, y):
        self.updatePoint(self.selectedIndex, x, y)

    def updatePoint(self, index, x, y):
        if index >= 0 and index < len(self.pointList):
            self.pointList[index] = (x, y)
            self.modelUpdated.emit()

    def deleteSelectedPoint(self):
        self.deletePoint(self.selectedIndex)

    def deletePoint(self, index):
        del self.pointList[index]
        if self.selectedIndex >= index:
            self.selectedIndex = max(self.selectedIndex - 1, 0)
        if len(self.pointList) == 0:
            self.selectedIndex = -1
        self.modelUpdated.emit()

    def swapPointSelected(self, index):
        self.swapPoints(self.selectedIndex, index)

    def swapPoints(self, i1, i2):
        if (i1 >= 0 and i1 < len(self.pointList)
                and i2 >= 0 and i2 < len(self.pointList)):
            temp = self.pointList[i1]
            self.pointList[i1] = self.pointList[i2]
            self.pointList[i2] = temp
            if self.selectedIndex == i1:
                self.selectedIndex = i2
            elif self.selectedIndex == i2:
                self.selectedIndex = i1
        self.modelUpdated.emit()

    def getPoints(self):
        return self.pointList

    def getFgColor(self):
        return self.fgColor
        self.modelUpdated.emit()

    def getBgColor(self):
        return self.bgColor
        self.modelUpdated.emit()

    def setSelectedIndex(self, index):
        self.selectedIndex = index
        self.modelUpdated.emit()

    def getSelectedIndex(self):
        return self.selectedIndex

    def getSelectedPoint(self):
        return self.pointList[self.selectedIndex]

    def getNumPoints(self):
        return len(self.pointList)

    def generatePointOffset(self, xInd, yInd, scale=100, xOff=0, yOff=0):
        tempPoints = []
        scaleX = (xInd * scale) + xOff
        scaleY = (yInd * scale) + yOff
        pointScale = scale/100
        for point in self.pointList:
            tempPoints.append(QPoint(point[0] * pointScale + scaleX,
                                     point[1] * pointScale + scaleY))
        return tempPoints

    def transformRotate(self, cw):
        for i in range(len(self.pointList)):
            point = self.pointList[i]
            if cw:
                self.pointList[i] = (100 - point[1], point[0])
            else:
                self.pointList[i] = (point[1], 100 - point[0])
        self.modelUpdated.emit()

    def transformFlip(self, h):
        for i in range(len(self.pointList)):
            point = self.pointList[i]
            if h:
                self.pointList[i] = (100 - point[0], point[1])
            else:
                self.pointList[i] = (point[0], 100 - point[1])
        self.modelUpdated.emit()

    def jsonObj(self):

        return {
            "name": self.name,
            "points": self.pointList,
            "uid": self.uid,
            "fg": {
                "r": self.fgColor.red(),
                "g": self.fgColor.green(),
                "b": self.fgColor.blue(),
            },
            "bg": {
                "r": self.bgColor.red(),
                "g": self.bgColor.green(),
                "b": self.bgColor.blue(),
            }

        }
