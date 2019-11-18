from EMModel import TileModel

import json


class ModelManager():
    paletteModels = None

    tileModels = None
    tileModelsByID = {}
    tileModelTags = {}
    tileModelsByName = {}
    tileModelNextUID = -1

    groupModels = None
    groupModelsByID = {}
    groupModelsByTag = {}
    groupModelsByName = {}
    groupModelNextUID = -1

    def __init__(self):
        ModelManager.loadPalette()
        ModelManager.loadTiles()
        ModelManager.loadPalette()

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
        # cls.updateTileCache()

    @classmethod
    def createTileCache(cls):
        # first do
        pass

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
    def fetchGroups(cls, keyword=None, searchType=None):
        """"Todo"""

    @classmethod
    def updatePalette(cls, model):
        """Todo"""

    @classmethod
    def updateTile(cls, model):
        """Todo"""

    @classmethod
    def updateGroup(cls, model):
        """Todo"""
