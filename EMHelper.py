from EMModel import TileModel

import json


class ModelManager():
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

    def __init__(self):
        ModelManager.loadPalette()
        ModelManager.loadTiles()
        ModelManager.loadPalette()

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
