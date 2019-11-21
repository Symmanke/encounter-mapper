from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPolygon
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QListWidget,
                             QListWidgetItem, QDialog, QLineEdit)

# from EMModelEditor import ModelEditor, ModelPreviewWidget
# from EMModel import ModelModel
from EMHelper import ModelManager


class EMModelPicker(QWidget):

    selectedModel = pyqtSignal(int)
    updatedModel = pyqtSignal(int)
    deletedModel = pyqtSignal(int)

    def __init__(self, modelName, modelClass, editorClass, modelPreviewClass):
        super(EMModelPicker, self).__init__()
        self.modelName = modelName
        self.modelClass = modelClass
        self.editorClass = editorClass
        self.modelPreviewClass = modelPreviewClass

        self.currentIndex = -1

        self.modelDialog = None
        self.modelEditor = None

        self.models = []

        self.modelList = QListWidget()
        self.modelList.itemClicked.connect(self.updateSelectedModel)
        self.addModelButton = QPushButton("New " + modelName)
        self.addModelButton.clicked.connect(self.newModelDialog)
        self.editModelButton = QPushButton("Edit " + modelName)
        self.editModelButton.clicked.connect(self.editModelDialog)
        self.duplicateModelButton = QPushButton("Duplicate")
        self.duplicateModelButton.clicked.connect(self.duplicateModel)
        self.deleteModelButton = QPushButton("Delete " + modelName)
        self.deleteModelButton.clicked.connect(self.deleteModel)
        layout = QVBoxLayout()
        layout.addWidget(self.modelList)
        layout.addWidget(self.addModelButton)
        layout.addWidget(self.editModelButton)
        layout.addWidget(self.duplicateModelButton)
        layout.addWidget(self.deleteModelButton)
        self.setLayout(layout)
        self.loadModels()

    def updateSelectedModel(self):
        sr = self.modelList.currentRow()
        if sr >= 0:
            print(self.models[sr].getUid())
            self.selectedModel.emit(self.models[sr].getUid())

    def newModelDialog(self):
        self.modelDialog = QDialog()
        layout = QVBoxLayout()
        self.modelEditor = self.editorClass()
        self.modelEditor.addModel.connect(self.addNewModel)
        self.modelEditor.cancelModel.connect(self.cancelModel)
        layout.addWidget(self.modelEditor)
        self.modelDialog.setLayout(layout)
        self.modelDialog.exec_()

    def editModelDialog(self):
        sr = self.modelList.currentRow()
        if sr >= 0:
            self.modelDialog = QDialog()
            layout = QVBoxLayout()
            tempCopy = self.modelClass.createModelCopy(self.models[sr])

            self.modelEditor = self.editorClass(tempCopy)
            self.modelEditor.addModel.connect(self.updateExistingModel)
            self.modelEditor.cancelModel.connect(self.cancelModel)

            layout.addWidget(self.modelEditor)
            self.modelDialog.setLayout(layout)
            self.modelDialog.exec_()

    def addNewModel(self):
        model = self.modelEditor.getCurrentModel()
        ModelManager.addModel(self.modelName, model)
        self.models.append(model)
        self.modelDialog.close()
        self.modelDialog = None
        self.modelEditor = None
        self.updateUI()

    def updateExistingModel(self):
        model = self.modelEditor.getCurrentModel()
        ModelManager.updateModel(self.modelName, model)
        self.models[self.modelList.currentRow()] = model
        self.modelDialog.close()
        self.modelDialog = None
        self.modelEditor = None
        self.updateUI()
        self.updatedModel.emit(model.getUid())

    def cancelModel(self):
        self.modelDialog.close()
        self.modelDialog = None
        self.modelEditor = None

    def duplicateModel(self):
        sr = self.modelList.currentRow()
        if sr >= 0:
            dupe = self.modelClass.createModelCopy(self.models[sr])

            name = "{}_copy".format(dupe.getName())
            dupe.setName(name)
            ModelManager.addModel(self.modelName, dupe, sr)
            self.models.insert(sr, dupe)
            self.updateUI()

    def deleteModel(self):
        sr = self.modelList.currentRow()
        if sr >= 0:
            uid = self.models[sr].getUid()
            ModelManager.deleteModel(self.modelName, self.models[sr])
            del self.models[sr]
            self.updateUI()
            self.deletedModel.emit(uid)

    def updateUI(self):
        self.modelList.clear()
        for model in self.models:
            listItemWidget = ModelPickerListItem(self.modelPreviewClass, model)
            listItem = QListWidgetItem(self.modelList)
            listItem.setSizeHint(listItemWidget.sizeHint())

            self.modelList.addItem(listItem)
            self.modelList.setItemWidget(listItem, listItemWidget)

    def loadModels(self):
        ModelManager.loadModelFromFile(self.modelName, self.modelClass)
        self.models = ModelManager.fetchModels(self.modelName)
        self.updateUI()

    def appendModel(self, Modeljs):
        """todo"""


class ModelPickerListItem(QWidget):

    def __init__(self, previewClass, model=None):
        super(ModelPickerListItem, self).__init__()
        self.model = model
        if model is not None:
            layout = QHBoxLayout()
            self.preview = previewClass.previewWidget(self.model)
            layout.addWidget(self.preview)
            layout.addWidget(QLabel(self.model.getName()))
            self.setLayout(layout)


class EMModelEditor(QWidget):
    applyModel = pyqtSignal()
    cancelModel = pyqtSignal()

    def __init__(self, model=None):
        super(EMModelEditor, self).__init__()
        self.model = model
        self.applyBtn = QPushButton("Apply")
        self.applyBtn.clicked.connect(self.applyModel.emit)
        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.cancelModel.emit)
        self.modelNameEdit = QLineEdit()
        self.modelNameEdit.textChanged.connect(self.updateModelName)
        self.modelTagsEdit = QLineEdit()
        self.modelNameEdit.textChanged.connect(self.updateModelTags)

    def updateModelName(self):
        self.model.setName(self.modelNameEdit.text())

    def updateModelTags(self):
        self.model.setTags(self.modelTagsEdit.text())

    def getModel(self):
        return self.model


class EMModelGraphics(QWidget):
    def __init__(self, model=None, rows=1, cols=1,
                 tileSize=100, width=500, height=500,
                 pOptions=(-1, 0, False, False), preview=False):
        super(EMModelGraphics, self).__init__()
        self.model = model
        self.numRows = rows
        self.numCols = cols
        self.tileSize = tileSize
        self.width = width
        self.height = height
        self.preview = preview
        self.pOptions = pOptions
        self.modelList = {}
        self.setMouseTracking(True)
        self.calculateOffsets()

    def createModelList(self):
        for id in self.model.getTilesToFetch():
            self.updateModelList(id)
        if self.pOptions[0] != -1 and self.pOptions[0] not in self.modelList:
            self.updateModelList(self.pOptions[0])

    def removeTileCache(self, id):
        if id != -1:
            self.modelList[id] = None
            self.repaint()

    def updateModelList(self, id):
        if id != -1:
            self.modelList[id] = ModelManager.fetchByUid(
                ModelManager.TileName, id)

    def calculateOffsets(self):
        self.xOffset = (self.width - self.numCols*self.tileSize)/2
        self.yOffset = (self.height - self.numRows*self.tileSize)/2

    def drawTile(self, painter, xInd, yInd, model,
                 options=(0, 0, False, False)):
        previewBGColor = Qt.white if self.preview else Qt.Black
        painter.setPen(previewBGColor)
        painter.setBrush(model.getBgColor())
        painter.drawRect(int(self.xOffset + self.tileSize * xInd),
                         int(self.yOffset + self.tileSize * yInd),
                         self.tileSize, self.tileSize)
        points = model.generatePointOffset(
            xInd, yInd, self.tileSize,
            self.xOffset, self.yOffset,
            options[1], options[2], options[3])
        fg = model.getFgColor()
        painter.setPen(fg)
        painter.setBrush(fg)
        poly = QPolygon(points)
        painter.drawPolygon(poly)

    def drawPreviewTile(self, painter, xInd, yInd):
        if self.pTile in self.modelList:
            model = self.modelList[self.pTile]
            if model is not None:
                painter.setPen(Qt.red)
                painter.setBrush(model.getBgColor())
                painter.drawRect(int(self.xOffset + self.tileSize * xInd),
                                 int(self.yOffset + self.tileSize * yInd),
                                 self.tileSize, self.tileSize)
                points = model.generatePointOffset(
                    xInd, yInd, self.tileSize,
                    self.xOffset, self.yOffset,
                    self.pOrientation, self.phFlip, self.pvFlip)
                painter.setBrush(model.getFgColor())
                poly = QPolygon(points)
                painter.drawPolygon(poly)

    def drawEmptyTile(self, painter, xInd, yInd):
        painter.setPen(Qt.black)
        painter.setBrush(Qt.white)
        painter.drawRect(int(self.xOffset + self.tileSize * xInd),
                         int(self.yOffset + self.tileSize * yInd),
                         self.tileSize, self.tileSize)

    def drawErrorTile(self, painter, xInd, yInd):
        painter.setPen(Qt.black)
        painter.setBrush(Qt.yellow)
        painter.drawRect(self.xOffset + self.tileSize * xInd,
                         self.yOffset + self.tileSize * yInd,
                         self.tileSize, self.tileSize)
        painter.setPen(Qt.red)
        painter.drawText(self.xOffset + self.tileSize * xInd+self.tileSize/4,
                         self.yOffset + self.tileSize * yInd+self.tileSize/2,
                         "ERROR")

    def calcMouseIndex(self, mPoint):
        if mPoint.x() < self.xOffset or mPoint.y() < self.yOffset:
            return (-1, -1)
        index = (mPoint.x() - self.xOffset, mPoint.y() - self.yOffset)
        index = (int(index[0]/self.tileSize), int(index[1]/self.tileSize))
        if index[0] >= self.numCols or index[1] >= self.numRows:
            return (-1, -1)
        return index

    def mousePosScale(self, mPoint):
        mp = (int((mPoint.x()-10)/5), int((mPoint.y()-10)/5))
        mp = (max(min(mp[0], 100), 0), max(min(mp[1], 100), 0))
        return mp

    def distanceHelper(self, point1, point2):
        p1 = point1[0] - point2[0]
        p2 = point1[1] - point2[1]
        p1 = p1 * p1
        p2 = p2 * p2
        return p1 + p2
