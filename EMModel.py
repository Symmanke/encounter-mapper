from PyQt5.QtGui import QColor
from PyQt5.QtCore import (QObject, pyqtSignal, QPoint)


class EMModel(QObject):

    modelUpdated = pyqtSignal()

    def __init__(self, name, tags="", uid=-1):
        super(EMModel, self).__init__()
        self.name = name
        self.tags = tags
        self.uid = uid

    def getUid(self):
        return self.uid

    def setUid(self, uid):
        self.uid = uid

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getTags(self):
        return self.tags

    def setTags(self, tags):
        self.tags = tags

    def updateModel(self, model):
        print("Warning: NEED to implement")

    @classmethod
    def createModelCopy(cls, model):
        return None

    @classmethod
    def createModelJS(cls, modelJS):
        return None

    def jsonObj(self):
        return {
            "Needs": "Implementation"
        }


class TileModel(EMModel):
    def __init__(self, name="new layer", pointList=None,
                 fgTupe=None, bgTupe=None, uid=-1):
        super(TileModel, self).__init__(name, "", uid)
        self.name = name
        self.pointList = []
        if pointList is not None:
            for point in pointList:
                self.pointList.append((point[0], point[1]))
        # self.pointList = [] if pointList is None else pointList
        bg = (105, 141, 85) if bgTupe is None else bgTupe
        fg = (101, 101, 102) if fgTupe is None else fgTupe
        self.bgColor = QColor(bg[0], bg[1], bg[2])
        self.fgColor = QColor(fg[0], fg[1], fg[2])
        self.selectedIndex = len(self.pointList) - 1
        self.tags = []

    @classmethod
    def createModelCopy(cls, model):
        bg = model.getBgColor()
        fg = model.getFgColor()
        mcopy = cls(model.getName(), model.getPoints(),
                    (fg.red(), fg.green(), fg.blue()),
                    (bg.red(), bg.green(), bg.blue()),
                    model.getUid())
        return mcopy

    @classmethod
    def createModelJS(cls, modelJS):
        fg = modelJS["fg"]
        bg = modelJS["bg"]
        model = cls(modelJS["name"], modelJS["points"][0],
                    (fg["r"], fg["g"], fg["b"]),
                    (bg["r"], bg["g"], bg["b"]),
                    modelJS["uid"])
        return model

    def setBgColor(self, r, g, b):
        self.bgColor = QColor(r, g, b)

    def setFgColor(self, r, g, b):
        self.fgColor = QColor(r, g, b)

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

    def updateModel(self, model):
        self.name = model.getName()
        self.pointList = model.getPoints()
        self.bgColor = model.getBgColor()
        self.fgColor = model.getFgColor()
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

    def generatePointOffset(self, xInd, yInd,
                            scale=100, xOff=0, yOff=0,
                            orientation=0, hflip=False, vflip=False):
        tempPoints = []
        scaleX = (xInd * scale) + xOff
        scaleY = (yInd * scale) + yOff
        pointScale = scale/100
        for p in self.pointList:

            if orientation == 1:
                p = (100 - p[1], p[0])
                # flip cw
            elif orientation == 2:
                p = (100 - p[0], 100 - p[1])

            elif orientation == 3:
                # flip ccw
                p = (p[1],  100 - p[0])
                pass
            if hflip:
                p = (100 - p[0], p[1])

            if vflip:
                p = (p[0], 100 - p[1])

            point = (p[0] * pointScale + scaleX,
                     p[1] * pointScale + scaleY)

            tempPoints.append(QPoint(point[0], point[1]))
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
            "points": [self.pointList],
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


class GroupModel(EMModel):
    def __init__(self, name="new group", tileGrid=None,
                 ttf=None, uid=-1):
        super(GroupModel, self).__init__(name, "", uid)
        self.name = name
        if tileGrid is None:
            self.tileGrid = []
            self.rows = 3
            self.cols = 2
            for y in range(self.rows):
                self.tileGrid.append([])
                for x in range(self.cols):
                    self.tileGrid[-1].append((-1, 0, False, False))
        else:
            self.tileGrid = tileGrid
            self.rows = len(self.tileGrid)
            self.cols = 0 if self.rows == 0 else len(self.tileGrid[0])
        self.tilesToFetch = self.generateTilesToFetch() if ttf is None else ttf

    @classmethod
    def createModelJS(cls, modelJS):
        model = cls(modelJS["name"], modelJS["grid"],
                    None, modelJS["uid"])
        return model

    @classmethod
    def createModelCopy(cls, model):
        mcopy = cls(model.getName(), model.getTileGrid(),
                    None, model.getUid())
        return mcopy

    def jsonObj(self):
        return {
            "name": self.name,
            "grid": self.tileGrid,
            "ttf": self.tilesToFetch,
            "uid": self.uid,
        }

    def getTileGrid(self):
        return self.tileGrid

    def getNumRows(self):
        return self.rows

    def getNumCols(self):
        return self.cols

    def getTilesToFetch(self):
        return self.tilesToFetch

    def setTileForIndex(self, x, y, tile):
        self.tileGrid[y][x] = tile
        self.modelUpdated.emit()

    def addRow(self):
        self.tileGrid.append([])
        for i in range(self.cols):
            self.tileGrid[-1].append((-1, 0, False, False))
        self.rows += 1
        self.modelUpdated.emit()

    def delRow(self):
        if(self.rows > 1):
            self.tileGrid.pop()
            self.rows -= 1
            self.modelUpdated.emit()

    def addCol(self):
        for row in self.tileGrid:
            row.append((-1, 0, False, False))
        self.cols += 1
        self.modelUpdated.emit()

    def delCol(self):
        if(self.cols > 1):
            for row in self.tileGrid:
                row.pop()
            self.cols -= 1
            self.modelUpdated.emit()

    def generateTilesToFetch(self):
        ttf = []
        for row in self.tileGrid:
            for tile in row:
                if tile[0] not in ttf:
                    ttf.append(tile[0])
        return ttf
