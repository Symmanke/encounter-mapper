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
from PyQt5.QtCore import (QObject, pyqtSignal, QPoint)


class EMModel(QObject):
    """
    Base model class. Contians the necessary methods used to save, load,
    and fetch models from ModelManager.
    """

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

    def getPreviewName(self):
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
    """
    Model for an individual tile. Current tile models contain a list of
    points to draw the FG object, and FG and BG colors.

    Future implementations may allow for multiple FG objects, as well as
    different textures to overlay on top of the BG.
    """

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
        self.bgTexture = "None" if bgTupe is None else bgTupe[3]
        self.selectedIndex = len(self.pointList) - 1
        self.tags = []

    @classmethod
    def createModelCopy(cls, model):
        bg = model.getBgColor()
        fg = model.getFgColor()
        mcopy = cls(model.getName(), model.getPoints(),
                    (fg.red(), fg.green(), fg.blue()),
                    (bg.red(), bg.green(), bg.blue(), model.getBgTexture()),
                    model.getUid())
        return mcopy

    @classmethod
    def createModelJS(cls, modelJS):
        fg = modelJS["fg"]
        bg = modelJS["bg"]
        text = "None" if "bgTexture" not in modelJS else modelJS["bgTexture"]
        model = cls(modelJS["name"], modelJS["points"][0],
                    (fg["r"], fg["g"], fg["b"]),
                    (bg["r"], bg["g"], bg["b"], text),
                    modelJS["uid"])
        return model

    def setBgColor(self, r, g, b):
        self.bgColor = QColor(r, g, b)

    def setFgColor(self, r, g, b):
        self.fgColor = QColor(r, g, b)

    def setBGTexture(self, texture):
        self.bgTexture = texture
        self.modelUpdated.emit()

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

    def getBgTexture(self):
        return self.bgTexture

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
            },
            "bgTexture": self.bgTexture
        }


class GroupModel(EMModel):
    """
    Model representation of a group of tiles. Contains a matrix which contains
    the UID of each tile inside it, as well as any rotations/transformations
    added to them.
    """

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

    @classmethod
    def createModelTransform(cls, model, options):
        print("Transform Options: {}".format(options))
        tmGrid = model.getTileGrid()
        mGrid = []
        for row in tmGrid:
            mGrid.append([])
            for tile in row:
                mGrid[-1].append((tile[0], tile[1], tile[2], tile[3]))
                # loop 1: rotate tiles inside
        print("Before:{}".format(mGrid))
        for y in range(len(mGrid)):
            for x in range(len(mGrid[y])):
                tile = mGrid[y][x]
                # print(tile)

                mGrid[y][x] = [tile[0], (tile[1]+options[0]) % 4,
                               tile[2] ^ options[1], tile[3] ^ options[2]]
                if(tile[2] ^ tile[3]) and mGrid[y][x][1] % 2:
                    mGrid[y][x][1] = (mGrid[y][x][1] + 2) % 4

        print("after:{}".format(mGrid))
        # loop 2: rotate grid itself
        tGrid = []
        numRows = model.getNumRows()
        numCols = model.getNumCols()
        if options[0] == 0:
            if options[1] or options[2]:
                for y in range(numRows):
                    tGrid.append([])
                    for x in range(numCols):
                        y2 = (numRows-1) - y if options[2] else y
                        x2 = (numCols-1) - x if options[1] else x
                        print("1:({},{}) 2:({},{})".format(x, y, x2, y2))
                        print(len(tGrid))

                        tGrid[-1].append(mGrid[y2][x2])
            else:
                tGrid = mGrid

        elif options[0] == 1:
            for y in range(numCols):
                tGrid.append([])
                for x in range(numRows-1, -1, -1):
                    y2 = (numCols-1) - y if options[2] else y
                    x2 = (numRows-1) - x if options[1] else x

                    tGrid[-1].append(mGrid[x2][y2])
        elif options[0] == 2:
            for y in range(numRows-1, -1, -1):
                tGrid.append([])
                for x in range(numCols-1, -1, -1):
                    y2 = (numRows-1) - y if options[2] else y
                    x2 = (numCols-1) - x if options[1] else x

                    tGrid[-1].append(mGrid[y2][x2])
        elif options[0] == 3:
            for y in range(numCols-1, -1, -1):
                tGrid.append([])
                for x in range(numRows):
                    y2 = (numCols-1) - y if options[2] else y
                    x2 = (numRows-1) - x if options[1] else x

                    tGrid[-1].append(mGrid[x2][y2])

        mGrid = tGrid

        return cls(model.getName(), mGrid)

    def jsonObj(self):
        return {
            "name": self.name,
            "grid": self.tileGrid,
            "ttf": self.tilesToFetch,
            "uid": self.uid,
        }

    def updateModel(self, model):
        self.name = model.getName()
        self.grid = model.getTileGrid()
        self.tilesToFetch = model.getTilesToFetch()
        self.rows = model.getNumRows()
        self.cols = model.getNumCols()
        self.modelUpdated.emit()

    def getTileGrid(self):
        return self.tileGrid

    def getNumRows(self):
        return self.rows

    def getNumCols(self):
        return self.cols

    def getPreviewName(self):
        return "{} ({}x{})".format(self.name, self.cols, self.rows)

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


class MapModel(GroupModel):
    """
    Model for the Map objects.

    Unlike other models, the MapModel doesn't get stored in ModelManager;
    rather, it is meant to be saved and loaded by the user. MapModel inherits
    the grid from groupModel, but also contains a list of notes and objects to
    populate the grid with.
    """

    def __init__(self, name="my encounter", tileGrid=None,
                 ttf=None, mapObjects=None, mapNotes=None, uid=-1):
        grid = [] if tileGrid is None else tileGrid
        if len(grid) == 0:
            rows = 5
            cols = 5
            for y in range(rows):
                grid.append([])
                for x in range(cols):
                    grid[-1].append((-1, 0, False, False))

        super(MapModel, self).__init__(name, grid, ttf, uid)
        self.mapObjects = [] if mapObjects is None else mapObjects
        self.mapNotes = [] if mapNotes is None else mapNotes

    @classmethod
    def createModelJS(cls, jsonObj):
        noteList = []
        for note in jsonObj["notes"]:
            noteList.append(NoteData.createModelJS(note))
        return cls(jsonObj["name"], jsonObj["grid"], jsonObj["ttf"],
                   jsonObj["objects"], noteList, jsonObj["uid"])

    def getMapObjects(self):
        return self.mapObjects

    def getMapNotes(self):
        return self.mapNotes

    def addMapNote(self, note, index=-1):
        index = len(self.mapNotes) if index == -1 else index
        self.mapNotes.insert(index, note)
        self.modelUpdated.emit()

    def updateMapNote(self, note, index):
        if index > 0 and index < len(self.mapNotes):
            self.mapNotes[index] = note
        self.modelUpdated.emit()

    def jsonObj(self):
        noteList = []
        for note in self.mapNotes:
            noteList.append(note.jsonObj())
        return {
            "name": self.name,
            "grid": self.tileGrid,
            "ttf": self.tilesToFetch,
            "uid": self.uid,
            "objects": self.mapObjects,
            "notes": noteList
        }


class NoteData(QObject):
    """
    Data for the note.

    Unlike the model objects, notes do not exist on their own and are always
    tied to a map. Thus, it didn't completely make sense to have them be an
    EMModel object. During saving, the noteData is added in JSon Format to the
    EMMapModel data.
    """

    noteEmblemUpdated = pyqtSignal()

    def __init__(self, type=0, title="", desc="", xPos=0, yPos=0):
        super(NoteData, self).__init__()
        self.type = type
        self.title = title
        self.desc = desc
        self.xPos = xPos
        self.yPos = yPos

    @classmethod
    def createModelJS(cls, jsonObj):
        return cls(jsonObj["type"], jsonObj["title"], jsonObj["desc"],
                   jsonObj["x"], jsonObj["y"])

    def getType(self):
        return self.type

    def getTitle(self):
        return self.title

    def getDesc(self):
        return self.desc

    def getPos(self, scale=1):
        return (self.xPos * scale, self.yPos * scale)

    def setType(self, type):
        self.type = type
        self.noteEmblemUpdated.emit()

    def setTitle(self, title):
        self.title = title

    def setDesc(self, desc):
        self.desc = desc

    def setPos(self, x, y):
        self.xPos = x
        self.yPos = y
        self.noteEmblemUpdated.emit()

    # def drawNoteIcon(self, painter, x, y, size=48, num=0):
    #     if NoteBadge.badgeIcons is None:
    #         NoteBadge.loadNoteImages()
    #     painter.drawPixmap(x, y, size, size, NoteBadge.badgeIcons[self.type])
    #     # painter.setBrush(NoteBadge.badgeColors[self.type])
    #     # painter.setPen(Qt.black)
    #     # painter.drawRect(x, y, size, size)
    #     if num > 0:
    #         numImgs = []
    #         numWidth = 0
    #         while num > 0:
    #             n = num % 10
    #             numImgs.insert(0, NoteBadge.badgeNums[n])
    #             numWidth += NoteBadge.badgeNums[-1].width()
    #             num = int(num/10)
    #         # Get offsets to center the numbers
    #         xNumOffset = x + int((size-numWidth)/2)
    #         # draw the num images
    #         for i in numImgs:
    #             painter.drawPixmap(xNumOffset, y+14, i)
    #             xNumOffset += i.width()

        # painter.drawPixmap(x+10, y+10, NoteBadge.badgeNums[num])
        # painter.setPen(Qt.white)
        # painter.drawText(x+size/2, y+size/2, "{}".format(num))

    def jsonObj(self):
        return {
            "type": self.type,
            "title": self.title,
            "desc": self.desc,
            "x": self.xPos,
            "y": self.yPos
        }
