
class ModelManager():
    paletteModels = None

    tileModels = None
    tileModelsByID = {}
    tileModelTags = {}
    tileModelsByName = {}

    groupModels = None
    groupModelsByID = {}
    groupModelsByTag = {}
    groupModelsByName = {}

    def __init__():
        ModelManager.loadPalette()
        ModelManager.loadTiles()
        ModelManager.loadPalette()

    @classmethod
    def loadPalette(cls):
        """"Todo"""

    @classmethod
    def loadTiles(cls):
        """Todo"""

    @classmethod
    def loadGroups(cls):
        """"Todo"""

    @classmethod
    def savePalette(cls):
        """"Todo"""

    @classmethod
    def saveTiles(cls):
        """"Todo"""

    @classmethod
    def saveGroups(cls):
        """"Todo"""

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
            return cls.copyList(cls.tileModels)
        else if

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
