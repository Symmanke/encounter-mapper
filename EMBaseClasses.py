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

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPolygon
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QListWidget,
                             QListWidgetItem, QDialog, QLineEdit)

# from EMModelEditor import ModelEditor, ModelPreviewWidget
# from EMModel import ModelModel
from EMHelper import ModelManager


class EMModelPicker(QWidget):
    """
    A class used to organize and select objects instantiated from models

    For a majority of the models used to populate the map, I need some way
    of selecting, creating, editing the models, etc. The model picker is
    a base class that can fetch said models from memory, populate a list
    with depictions of the models, and allow for the creation/selection
    of new models. Use of the EMModelPicker requires a modelClass, which
    is the data being organized, a modelPreviewClass, which generates a
    graphical representation of the model, and an editorClass, which is opened
    whenever editing/creating a new instance of the model

    Signals
    -------

    selectedModel -> int
        emitted whenever a new model has been selected. emits the uid value
        of the model
    updatedModel -> int
        Emits whenever an existing model has been updated. Should be used in
        conjunction with modelPreviewClasses to update the graphics. Emits uid
    deletedModel -> int
        Emitted whenever a model is deleted from the list. Should be used to
        update graphical representations of grids using said model.




    """

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
            self.selectedModel.emit(self.models[sr].getUid())

    def newModelDialog(self):
        self.modelDialog = QDialog()
        layout = QVBoxLayout()
        self.modelEditor = self.editorClass(self.modelClass())
        self.modelEditor.applyEdit.connect(self.addNewModel)
        self.modelEditor.cancelEdit.connect(self.cancelEdit)
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
            self.modelEditor.applyEdit.connect(self.updateExistingModel)
            self.modelEditor.cancelEdit.connect(self.cancelEdit)

            layout.addWidget(self.modelEditor)
            self.modelDialog.setLayout(layout)
            self.modelDialog.exec_()

    def addNewModel(self):
        model = self.modelEditor.getModel()
        ModelManager.addModel(self.modelName, model)
        self.models.append(model)
        self.modelDialog.close()
        self.modelDialog = None
        self.modelEditor = None
        self.updateUI()

    def updateExistingModel(self):
        model = self.modelEditor.getModel()
        ModelManager.updateModel(self.modelName, model)
        self.models[self.modelList.currentRow()] = model
        self.modelDialog.close()
        self.modelDialog = None
        self.modelEditor = None
        self.updateUI()
        self.updatedModel.emit(model.getUid())

    def cancelEdit(self):
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
        ModelManager.loadModelListFromFile(self.modelName, self.modelClass)
        self.models = ModelManager.fetchModels(self.modelName)
        self.updateUI()

    def appendModel(self, Modeljs):
        """todo"""


class ModelPickerListItem(QWidget):
    """
    List item used in conjunction with EMModelPicker. Takes a model, and the
    associated preview class used in depicting the model
    """

    def __init__(self, previewClass, model=None):
        super(ModelPickerListItem, self).__init__()
        self.model = model
        if model is not None:
            layout = QHBoxLayout()
            self.preview = previewClass.previewWidget(self.model)
            layout.addWidget(self.preview)
            layout.addWidget(QLabel(self.model.getName()))
            self.setLayout(layout)


class EMEditor(QWidget):
    applyEdit = pyqtSignal()
    cancelEdit = pyqtSignal()

    def __init__(self):
        super(EMEditor, self).__init__()

        self.applyBtn = QPushButton("Apply")
        self.applyBtn.clicked.connect(self.applyEdit.emit)
        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.cancelEdit.emit)


class EMModelEditor(EMEditor):
    """
    Editor used to create and update existing models. Typically created through
    EMModelPicker.

    Methods of editing and depictions of models will vary based off the model's
    function and use. This provides two buttons, the apply and cancel button.
    EMModelEditor also has two signals, applyEdit and cancelEdit.
    When instanciatng a ModelEditor, both signals should be applied, and used
    to determine when a model is finished editing. To prevent unnecessary
    changes, it is suggested to pass a clone of an existing model to the
    model editor, rather than a reference when trying to edit models.

    Signals
    _______

    applyEdit -> None
        Emitted when the apply button is pressed, signifying the changes to
        the model are complete and ready to be saved. When hooked into
        EMModelPicker, will close the Editor
    cancelEdit -> None
        Emitted when the cancel button is pressed, signifying the edit is to
        be cancelled.
    """

    def __init__(self, model=None):
        super(EMModelEditor, self).__init__()
        self.model = model
        if self.model is not None:
            self.model.modelUpdated.connect(self.updateUI)
        self.modelNameEdit = QLineEdit()
        self.modelNameEdit.textChanged.connect(self.updateModelName)
        self.modelTagsEdit = QLineEdit()
        self.modelNameEdit.textChanged.connect(self.updateModelTags)
        self.setMouseTracking(True)

    def updateModelName(self):
        self.model.setName(self.modelNameEdit.text())

    def updateModelTags(self):
        self.model.setTags(self.modelTagsEdit.text())

    def getModel(self):
        return self.model

    def updateUI(self):
        # must implement this class
        pass


class EMModelGraphics(QWidget):
    """
    Graphical representation of the model, used when editing the model, or
    as a preview depicting the model

    The EMModelGraphics is a graphical representation of a model, specifically
    used for the tile-based models. As such, it contains multiple helper
    methods for drawing tiles and updating a cache of existing tiles. Future
    changes may make the tile functionality as a subclass, when non-tile-based
    models are added.

    The preview property determines when the graphics can be interacted with,
    and should only be True when used in conjunction with an editor.
    """

    updatePreview = pyqtSignal()
    selectedItem = pyqtSignal(int, int)
    selectedGroup = pyqtSignal(int, int, int, int, int)

    def __init__(self, model=None, rows=1, cols=1,
                 tileSize=100, width=500, height=500,
                 preview=False, cached=False, sOptions=None):
        super(EMModelGraphics, self).__init__()
        self.model = model
        self.numRows = rows
        self.numCols = cols
        self.tileSize = tileSize
        self.width = width
        self.height = height
        self.preview = preview
        self.openTab = 0
        self.selectedObject = [-1, -1, -1, -1]
        self.sOptions = [0, False, False] if sOptions is None else sOptions
        self.modelList = {}
        self.mouseIndex = (-1, -1)
        self.mousePressed = False
        self.modelImage = None
        if cached:
            self.createModelList()

        self.setMinimumHeight(height)
        self.setMinimumWidth(width)
        self.setMouseTracking(True)
        self.calculateOffsets()

    def createModelList(self):
        for id in self.model.getTilesToFetch():
            self.updateModelList(id)
        if (self.selectedObject[0] != -1 and
                self.selectedObject[0] not in self.modelList):
            self.updateModelList(self.selectedObject[0])

    def removeTileCache(self, id):
        if id != -1:
            self.modelList[id] = None
            self.repaint()

    def updateModelList(self, id):
        if id != -1:
            self.modelList[id] = ModelManager.fetchByUid(
                ModelManager.TileName, id)

    def getModelImage(self):
        return self.modelImage

    def getSOptions(self):
        return (self.sOptions[0], self.sOptions[1],
                self.sOptions[2])

    def calculateOffsets(self):
        self.xOffset = (self.width - self.numCols*self.tileSize)/2
        self.yOffset = (self.height - self.numRows*self.tileSize)/2

    def drawTile(self, painter, xInd, yInd, model,
                 options=(0, False, False), previewTile=False):
        painter.setPen(Qt.red if previewTile else Qt.black)
        painter.setBrush(model.getBgColor())
        painter.drawRect(int(self.xOffset + self.tileSize * xInd),
                         int(self.yOffset + self.tileSize * yInd),
                         self.tileSize, self.tileSize)
        points = model.generatePointOffset(
            xInd, yInd, self.tileSize,
            self.xOffset, self.yOffset,
            options[0], options[1], options[2])
        fg = model.getFgColor()
        painter.setPen(Qt.red if previewTile else fg)
        painter.setBrush(fg)
        poly = QPolygon(points)
        painter.drawPolygon(poly)

    def drawPreviewTile(self, painter, xInd, yInd):
        if self.openTab == 0 and self.selectedObject[0] in self.modelList:
            model = self.modelList[self.selectedObject[0]]
            if model is not None:
                painter.setPen(Qt.red)
                painter.setBrush(model.getBgColor())
                painter.drawRect(int(self.xOffset + self.tileSize * xInd),
                                 int(self.yOffset + self.tileSize * yInd),
                                 self.tileSize, self.tileSize)
                points = model.generatePointOffset(
                    xInd, yInd, self.tileSize,
                    self.xOffset, self.yOffset,
                    self.sOptions[0], self.sOptions[1], self.sOptions[2])
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

    def mousePosScale(self, mPoint, xOff=10, yOff=10, scale=500):
        calcScale = self.tileSize/100
        mp = (int((mPoint.x()-xOff)/calcScale), int((mPoint.y()-10)/calcScale))
        ms = [self.numCols*100, self.numRows*100]
        mp = (max(min(mp[0], ms[0]), 0), max(min(mp[1], ms[1]), 0))
        return mp

    def distanceHelper(self, point1, point2):
        p1 = point1[0] - point2[0]
        p2 = point1[1] - point2[1]
        p1 = p1 * p1
        p2 = p2 * p2
        return p1 + p2
