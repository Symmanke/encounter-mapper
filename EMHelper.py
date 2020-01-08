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

from EMModel import TileModel, GroupModel, MapModel
from PyQt5.QtGui import QPolygon, QImage, QPainter

import json


class ModelManager():
    """
    ModelManager is responsible for the loading, caching, and maintaining of
    all Models internal to the Application.

    When a model type is first needed, it should be loaded through
    loadModelListFromFile(). Models should be fetched by type, and can be
    done so through fetchByUid(). Future implementations will allow for basic
    search functionality via model name and tags.

    Calling saveModelToFile() will save the mentioned list of models. This
    should be done whenever a model is updated. For models that are not meant
    to be internal resources (ex. maps) they should be saved instead via
    saveJSONToFile() and loaded through loadModelFromFile()
    """

    TileName = "Tile"
    GroupName = "Group"
    PaletteName = "Palette"

    List = "List"
    ByUid = "ByUid"
    ByTag = "ByTag"
    ByName = "ByName"
    NextUid = "NextUid"
    ClassRef = "ClassRef"

    ConfigExt = ".json"
    MapExt = ".emmap"

    loadedModels = {}

    paletteModels = None

    tileModels = None
    tileModelsByID = {}
    tileModelTags = {}
    tileModelsByName = {}
    tileModelNextUID = 0

    groupModels = None
    groupModelsByID = {}
    groupModelsByTag = {}
    groupModelsByName = {}
    groupModelNextUID = 0

    @classmethod
    def loadModelListFromFile(cls, name, classType, ext=".json"):
        if name not in cls.loadedModels:
            # fetch data according to filename
            modelList = []
            f = open(name+ext, "r")
            if f.mode == "r":
                contents = f.read()
                jsContents = json.loads(contents)
                f.close()

                for modeljs in jsContents:
                    modelList.append(classType.createModelJS(modeljs))
                modelDict = {
                    cls.List: modelList,
                    cls.ByUid: {},
                    cls.ByName: {},
                    cls.ByTag: {},
                    cls.NextUid: 0,
                    cls.ClassRef: classType
                }

                cls.loadedModels[name] = modelDict
                cls.createCache(name)

    @classmethod
    def loadModelFromFile(cls, path, classType):
        f = open(path, "r")
        if f.mode == "r":
            contents = f.read()
            jsContents = json.loads(contents)
            f.close()

            return classType.createModelJS(jsContents)
        return None

    @classmethod
    def saveModelToFile(cls, name, ext=".json"):
        modelJS = []
        for model in cls.loadedModels[name][cls.List]:
            modelJS.append(model.jsonObj())

        text = json.dumps(modelJS)
        f = open(name+ext, "w+")
        f.write(text)
        f.close()

    @classmethod
    def saveJSONToFile(cls, jsObj,  path, ext=""):
        text = json.dumps(jsObj)
        f = open(path+ext, "w+")
        f.write(text)
        f.close()

    @classmethod
    def saveImageToFile(cls, img, path):
        # f = open(path+".png", "w+")
        img.save(path+".png", "PNG")
        # f.close()

    @classmethod
    def createCache(cls, name):
        modelList = cls.loadedModels[name][cls.List]
        idCache = cls.loadedModels[name][cls.ByUid]
        idCache.clear()
        for model in modelList:
            idCache[model.getUid()] = model

    @classmethod
    def fetchByUid(cls, modelName, uid):
        if modelName in cls.loadedModels:
            uidDict = cls.loadedModels[modelName][cls.ByUid]
            cr = cls.loadedModels[modelName][cls.ClassRef]
            if uid in uidDict:
                return cr.createModelCopy(uidDict[uid])
        return None

    @classmethod
    def fetchModels(cls, modelName, keyword=None, searchType=None):
        if modelName in cls.loadedModels:
            modelType = cls.loadedModels[modelName]
            if keyword is None or searchType is None:
                return cls.copyModelList(
                    modelType[cls.List], modelType[cls.ClassRef])
            return cls.copyModelList(
                modelType[cls.List], modelType[cls.ClassRef])
        return None

    @classmethod
    def copyModelList(cls, list, classRef):
        copiedList = []
        for model in list:
            copiedList.append(classRef.createModelCopy(model))
        return copiedList

    def generateNextUid(cls, modelName):
        if modelName in cls.loadedModels:
            modelType = cls.loadedModels[modelName]
            uid = modelType[cls.NextUid]
            while uid in modelType[cls.ByUid]:
                uid += 1
            modelType[cls.NextUid] = uid
            return uid
        return -1

    @classmethod
    def updateModel(cls, name, model):
        if name in cls.loadedModels:
            modelType = cls.loadedModels[name]
            if model.getUid() in modelType[cls.ByUid]:
                mainModel = modelType[cls.ByUid][model.getUid()]
                mainModel.updateModel(model)
                cls.saveModelToFile(name)

    @classmethod
    def addModel(cls, name, model, index=-1):
        if name in cls.loadedModels:
            model.setUid(cls.generateNextUid(cls, name))
            modelType = cls.loadedModels[name]
            if(index < 0):
                modelType[cls.List].append(model)
            else:
                modelType[cls.List].insert(index, model)
            modelType[cls.ByUid][model.getUid()] = model
            cls.saveModelToFile(name)

    @classmethod
    def deleteModel(cls, name, model):
        if name in cls.loadedModels:
            modelType = cls.loadedModels[name]
            uid = model.getUid()
            # remove from main list
            for m in modelType[cls.List]:
                if m.getUid() == uid:
                    modelType[cls.List].remove(m)
                    break
            # remove from UID cache
            del modelType[cls.ByUid][uid]
            cls.saveModelToFile(name)

    @classmethod
    def loadPalette(cls):
        """"Todo"""

    @classmethod
    def loadTiles(cls):
        cls.tileModels = []
        f = open("tiles.json", "r")
        if f.mode == 'r':
            contents = f.read()
            jsContents = json.loads(contents)
            f.close()

            for tilejs in jsContents["tiles"]:
                cls.tileModels.append(TileModel.createModelJS(tilejs))
        cls.createTileCache()

    @classmethod
    def generateNewTileUid(cls):
        while cls.tileModelNextUID in cls.tileModelsByID:
            cls.tileModelNextUID += 1
        return cls.tileModelNextUID

    @classmethod
    def createTileCache(cls):
        cls.tileModelsByID.clear()
        for model in cls.tileModels:
            cls.tileModelsByID[model.getUid()] = model

    @classmethod
    def updateTileCache(cls, model):
        if model.getUid in cls.tileModelsByID:
            # Update the id instead of creating a new model
            pass
        else:
            # this will have been added,
            pass

    @classmethod
    def loadGroups(cls):
        """"Todo"""

    @classmethod
    def savePalette(cls):
        """"Todo"""

    @classmethod
    def saveTiles(cls):
        tileJS = {
            "tiles": [],
            "patterns": []
        }
        for tm in cls.tileModels:
            tileJS["tiles"].append(tm.jsonObj())

        # Do fancy stuff to save the tile map
        text = json.dumps(tileJS)
        f = open("tiles.json", "w+")
        f.write(text)
        f.close()

    @classmethod
    def saveGroups(cls):
        """"Todo"""

    @classmethod
    def copyList(cls, list, type):
        copiedList = []
        if type == "tile":
            for model in list:
                copiedList.append(TileModel.createModelCopy(model))
        return copiedList

    @classmethod
    def fetchPalette(cls):
        if cls.paletteModels is None:
            cls.loadPalette()
        return cls.paletteModels

    @classmethod
    def fetchTiles(cls, keyword=None, searchType=None):
        if cls.tileModels is None:
            cls.loadTiles()
        if keyword is None or searchType is None:
            return cls.copyList(cls.tileModels, "tile")
        return cls.copyList(cls.tileModels, "tile")

    @classmethod
    def fetchTileById(cls, id):
        if cls.tileModels is None:
            cls.loadTiles()
        if id in cls.tileModelsByID:
            return TileModel.createModelCopy(cls.tileModelsByID[id])
        return None

    @classmethod
    def fetchGroups(cls, keyword=None, searchType=None):
        """"Todo"""

    @classmethod
    def updatePalette(cls, model):
        """Todo"""

    @classmethod
    def updateTile(cls, model):
        if model.getUid() in cls.tileModelsByID:
            mainModel = cls.tileModelsByID[model.getUid()]
            mainModel.updateModel(model)
        cls.saveTiles()

    @classmethod
    def updateGroup(cls, model):
        """Todo"""

    @classmethod
    def addTile(cls, model, index=-1):
        model.setUid(cls.generateNewTileUid())
        if(index < 0):
            cls.tileModels.append(model)
        else:
            cls.tileModels.insert(index, model)
        cls.tileModelsByID[model.getUid()] = model
        cls.saveTiles()


class EMImageGenerator():
    """
    Helper class for generating the images used to display the tileMap.

    Rather than always passing inheritance, I am planning on using the Helper
    class instead. This can be used in a variety of scenarios, but also assist
    with creating images to save.

    images generated will default to 72ppi, with 3 in. Tiles (216p per tile).
    This happen to be the dimensions I use for my own custom tiles, and makes
    things easier for my personal use. In the future, I plan to allow this to
    be customized, although some user-created custom images may be required
    at that time.
    """

    @classmethod
    def genImageFromModel(cls, model,
                          displayObjects=False, displayNotes=False):
        genImage = None
        if isinstance(model, MapModel):
            print("Map Model")
            genImage = QImage(216 * model.getNumCols(),
                              216 * model.getNumRows(),
                              QImage.Format_RGB32)
            painter = QPainter(genImage)
            # painter.begin(genImage)
            cls.drawTileGroup(painter, model)
            # painter.end()
            # displayObjects and displayNotes will be added here in the future
        elif isinstance(model, GroupModel):
            print("Group Model")
            genImage = QImage(216 * model.getNumCols(),
                              216 * model.getNumRows(),
                              QImage.Format_RGB32)
        elif isinstance(model, TileModel):
            print("Tile Model")
            genImage = QImage(216, 216, QImage.Format_RGB32)
            painter = QPainter(genImage)
            cls.drawTile(painter, model)
        else:
            print("Wrong Model")
        return genImage

    def updateModelImage(cls, model, x, y, x2=-1, y2=-1, pointArr=None):
        pass

    @classmethod
    def drawTileGroup(cls, painter, model):
        cachedTiles = {}
        grid = model.getTileGrid()
        for y in range(model.getNumRows()):
            for x in range(model.getNumCols()):
                tile = grid[y][x]
                if tile[0] == -1:
                    # draw Empty Tile
                    pass
                else:
                    if tile[0] not in cachedTiles:
                        cachedTiles[tile[0]] = ModelManager.fetchByUid(
                            ModelManager.TileName, tile[0])
                    tileModel = cachedTiles[tile[0]]
                    if tileModel is not None:
                        cls.drawTile(painter, tileModel, x, y,
                                     (tile[1], tile[2], tile[3]))
                    else:
                        # Draw error Tile
                        pass

        pass

    @classmethod
    def drawTile(cls, painter, model, xind=0, yind=0,
                 options=(0, False, False)):
        # Res = 3 in. at 72ppi. 72*3 = 216
        res = 216
        bg = model.getBgColor()
        painter.setPen(bg)
        painter.setBrush(bg)
        painter.drawRect(int(res * xind),
                         int(res * yind),
                         res, res)
        points = model.generatePointOffset(
            xind, yind, res,
            0, 0,
            options[0], options[1], options[2])
        fg = model.getFgColor()
        painter.setBrush(fg)
        painter.setPen(fg)
        poly = QPolygon(points)
        painter.drawPolygon(poly)
