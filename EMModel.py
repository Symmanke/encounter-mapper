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
        self.modelUpdated.emit()

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

    def __init__(self, name="new tile", shapeList=None, bgTexture=0, uid=-1):
        super(TileModel, self).__init__(name, "", uid)
        self.shapeList = []
        if shapeList is not None:
            for shape in shapeList:
                sh = [shape[0]]
                shapePoints = []
                for point in shape[1]:
                    shapePoints.append((point[0], point[1]))
                sh.append(shapePoints)
                self.shapeList.append(sh)
        self.bgTexture = bgTexture
        self.selectedIndex = -1

    @classmethod
    def createModelCopy(cls, model):
        mcopy = cls(model.getName(), model.getShapes(), model.getBgTexture(),
                    model.getUid())
        return mcopy

    @classmethod
    def createModelJS(cls, modelJS):
        model = cls(modelJS["name"], modelJS["shapeList"],
                    modelJS["bgTexture"], modelJS["uid"])
        return model

    def setBgTexture(self, texture):
        self.bgTexture = texture
        self.modelUpdated.emit()

    def addShape(self):
        self.shapeList.append([1, []])
        self.modelUpdated.emit()

    def addPoint(self, shape, index, x, y):
        index = max(0, index)
        self.shapeList[shape][1].insert(index, (x, y))
        self.modelUpdated.emit()

    def updatePoint(self, shape, index, x, y):
        if shape >= 0 and shape < len(self.shapeList):
            if index >= 0 and index < len(self.shapeList[shape][1]):
                self.shapeList[shape][1][index] = (x, y)
                self.modelUpdated.emit()

    def updateModel(self, model):
        self.name = model.getName()
        self.shapeList = model.getShapes()
        self.bgTexture = model.getBgTexture()
        self.modelUpdated.emit()

    def deleteShape(self, shape):
        del self.shapeList[shape]
        self.modelUpdated.emit()

    def deleteShapePoint(self, shape, index):
        del self.shapeList[shape][1][index]
        self.modelUpdated.emit()

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

    def setShapeTexture(self, index, texture):
        self.shapeList[index][0] = texture
        self.modelUpdated.emit()

    def getShape(self, index):
        return self.shapeList[index]

    def getShapes(self):
        return self.shapeList

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

    def offsetShape(self, points, scaleX, scaleY, pointScale,
                    orientation, hflip, vflip):
        pointList = []
        for p in points:
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

            pointList.append(QPoint(point[0], point[1]))
        return pointList

    def generateShapeOffset(self, si, xInd, yInd,
                            scale=100, xOff=0, yOff=0,
                            orientation=0, hflip=False,
                            vflip=False):
        scaleX = (xInd * scale) + xOff
        scaleY = (yInd * scale) + yOff
        pointScale = scale/100
        return self.offsetShape(self.shapeList[si][1], scaleX, scaleY,
                                pointScale, orientation, hflip, vflip)

    def generateAllShapeOffset(self, xInd, yInd,
                               scale=100, xOff=0, yOff=0,
                               orientation=0, hflip=False,
                               vflip=False):
        tempShapes = []
        scaleX = (xInd * scale) + xOff
        scaleY = (yInd * scale) + yOff
        pointScale = scale/100
        for s in self.shapeList:
            tempShapes.append(
                self.offsetShape(s[1], scaleX, scaleY, pointScale,
                                 orientation, hflip, vflip))
        return tempShapes

    def transformRotate(self, cw):
        for shape in self.shapeList:
            for i in range(len(shape[1])):
                point = shape[1][i]
                if cw:
                    shape[1][i] = (100 - point[1], point[0])
                else:
                    shape[1][i] = (point[1], 100 - point[0])
        self.modelUpdated.emit()

    def transformFlip(self, h):
        for shape in self.shapeList:
            for i in range(len(shape[1])):
                point = shape[1][i]
                if h:
                    shape[1][i] = (100 - point[0], point[1])
                else:
                    shape[1][i] = (point[0], 100 - point[1])
        self.modelUpdated.emit()

    def jsonObj(self):

        return {
            "name": self.name,
            "uid": self.uid,
            "shapeList": self.shapeList,
            "bgTexture": self.bgTexture,
            "tags": ""
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
        # print("Transform Options: {}".format(options))
        tmGrid = model.getTileGrid()
        mGrid = []
        for row in tmGrid:
            mGrid.append([])
            for tile in row:
                mGrid[-1].append((tile[0], tile[1], tile[2], tile[3]))
                # loop 1: rotate tiles inside
        # print("Before:{}".format(mGrid))
        for y in range(len(mGrid)):
            for x in range(len(mGrid[y])):
                tile = mGrid[y][x]
                # print(tile)

                mGrid[y][x] = [tile[0], (tile[1]+options[0]) % 4,
                               tile[2] ^ options[1], tile[3] ^ options[2]]
                if(tile[2] ^ tile[3]) and mGrid[y][x][1] % 2:
                    mGrid[y][x][1] = (mGrid[y][x][1] + 2) % 4

        # print("after:{}".format(mGrid))
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
        if index >= 0 and index < len(self.mapNotes):
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


class NoteData(EMModel):
    """
    Data for the note.

    Unlike the model objects, notes do not exist on their own and are always
    tied to a map. Thus, it didn't completely make sense to have them be an
    EMModel object. During saving, the noteData is added in JSon Format to the
    EMMapModel data.
    """

    def __init__(self, type=0, name="", desc="", xPos=0, yPos=0, uid=-1):
        super(NoteData, self).__init__(name, "", uid)
        self.type = type
        self.desc = desc
        self.xPos = xPos
        self.yPos = yPos

    @classmethod
    def createModelJS(cls, jsonObj):
        return cls(jsonObj["type"], jsonObj["name"], jsonObj["desc"],
                   jsonObj["x"], jsonObj["y"], jsonObj["uid"])

    @classmethod
    def createModelCopy(cls, model):
        pos = model.getPos()
        mcopy = cls(model.getType(), model.getName(), model.getDesc(),
                    pos[0], pos[1], model.getUid())
        return mcopy

    def getType(self):
        return self.type

    def getDesc(self):
        return self.desc

    def getPos(self, scale=1):
        return (self.xPos * scale, self.yPos * scale)

    def setType(self, type):
        self.type = type
        self.modelUpdated.emit()

    def setDesc(self, desc):
        self.desc = desc

    def setPos(self, x, y):
        self.xPos = x
        self.yPos = y
        self.modelUpdated.emit()

    def jsonObj(self):
        return {
            "type": self.type,
            "name": self.name,
            "desc": self.desc,
            "x": self.xPos,
            "y": self.yPos,
            "uid": self.uid
        }


class TextureModel(EMModel):
    """TextureModel contains all the necessary data to generate a texture"""
    ImageTexture = "Image"
    GeneratedTexture = "Generated"
    TextureSize = 648

    def __init__(self, name="", type="", tags="", uid=-1):
        super(TextureModel, self).__init__(name, tags, uid)
        self.dirty = True


class GeneratedTextureModel(TextureModel):
    def __init__(self, name="New Texture", bgColor=None,
                 textures=None, tags="", uid=-1):
        super(GeneratedTextureModel, self).__init__(
            name, TextureModel.GeneratedTexture, tags, uid)
        self.bgColor = QColor(255, 255, 255) if bgColor is None else bgColor
        self.textures = textures
        if textures is None:
            self.textures = [["None", QColor(0, 0, 0)],
                             ["None", QColor(0, 0, 0)]]
        self.dirty = True

    def setDirty(self, dirty):
        self.dirty = dirty

    def isDirty(self):
        return self.dirty

    @classmethod
    def createModelJS(cls, jsonObj):
        jsmodel = None
        if jsonObj["textureType"] == TextureModel.GeneratedTexture:
            txt = []
            for txtTupe in jsonObj["textures"]:
                txt.append([txtTupe[0], QColor(txtTupe[1][0],
                                               txtTupe[1][1], txtTupe[1][2])])
            bgTupe = jsonObj["bgColor"]
            bg = QColor(bgTupe[0], bgTupe[1], bgTupe[2])
            jsmodel = cls(jsonObj["name"], bg,
                          txt, jsonObj["tags"], jsonObj["uid"])
        return jsmodel

    @classmethod
    def createModelCopy(cls, model):
        mcopy = None
        if isinstance(model, GeneratedTextureModel):
            txt = []
            for txtTupe in model.getTextures():
                txt.append([txtTupe[0], QColor(txtTupe[1])])
            bg = QColor(model.getBgColor())
            mcopy = cls(model.getName(), bg, txt,
                        model.getTags(), model.getUid())
        return mcopy

    def updateModel(self, model):
        self.name = model.getName()
        self.bgColor = model.getBgColor()
        self.textures = model.getTextures()
        self.dirty = True

    def setBgColor(self, color):
        self.bgColor = color
        self.dirty = True
        self.modelUpdated.emit()

    def getBgColor(self):
        return self.bgColor

    def setTextureType(self, texture, index):
        self.textures[index][0] = texture
        self.dirty = True
        self.modelUpdated.emit()

    def setTextureColor(self, color, index):
        self.textures[index][1] = color
        self.dirty = True
        self.modelUpdated.emit()

    def getTextures(self):
        return self.textures

    def getTexture(self, index):
        return self.textures[index]

    def jsonObj(self):
        txt = []
        for txtTupe in self.textures:
            txt.append((
                txtTupe[0],
                (txtTupe[1].red(), txtTupe[1].green(), txtTupe[1].blue())))
        bg = (self.bgColor.red(), self.bgColor.green(), self.bgColor.blue())

        return {
            "textureType": TextureModel.GeneratedTexture,
            "name": self.name,
            "tags": self.tags,
            "textures": txt,
            "bgColor": bg,
            "uid": self.uid
        }


class ImageTextureModel(TextureModel):
    """
    ImageTextureModel contains a filepath to an image used as a texture.

    While encounterMapper allows people to generate textures from its existing
    toolset, there are times where due to limitations it is better to upload
    an image instead. The ImageTextureModel removes all the data used by the
    GeneratedTextureModel, and as such, is its own separate class.

    The size of an Image used should ideally be 648 x 648 and repeating. When
    uploading an image, the image will be copied internally and scaled
    appropriately if necessary.
    """

    def __init__(self, name="", filePath="", tags="", uid=-1):
        super(ImageTextureModel, self).__init__(
            name, TextureModel.ImageTexture, tags, uid)
        self.filePath = filePath

    @classmethod
    def createModelJS(cls, jsonObj):
        jsmodel = None
        if jsonObj["textureType"] == TextureModel.ImageTexture:
            jsmodel = cls(jsonObj["name"], jsonObj["filePath"],
                          jsonObj["tags"], jsonObj["uid"])
        return jsmodel

    @classmethod
    def createModelCopy(cls, model):
        mcopy = None
        if isinstance(model, ImageTextureModel):
            mcopy = cls(model.getName(), model.getFilePath(), model.getTags(),
                        model.getUid())
        return mcopy

    def setFilePath(self, fp):
        self.filePath = fp
        self.modelUpdated.emit()

    def getFilePath(self):
        return self.filePath

    def jsonObj(self):
        return {
            "textureType": TextureModel.ImageTexture,
            "name": self.name,
            "tags": self.tags,
            "filePath": self.filePath,
            "uid": self.uid
        }


class TextureModelLoader:
    @classmethod
    def createModelJS(cls, jsonObj):
        model = None
        if jsonObj["textureType"] == TextureModel.GeneratedTexture:
            model = GeneratedTextureModel.createModelJS(jsonObj)
        elif jsonObj["textureType"] == TextureModel.ImageTexture:
            model = ImageTextureModel.createModelJS(jsonObj)
        return model

    @classmethod
    def createModelCopy(cls, model):
        modelCopy = None
        if isinstance(model, GeneratedTextureModel):
            modelCopy = GeneratedTextureModel.createModelCopy(model)
        return modelCopy
