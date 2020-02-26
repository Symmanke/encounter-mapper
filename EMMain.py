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

from PyQt5.QtWidgets import (QApplication, QStackedWidget, QFileDialog,
                             QLabel, QPushButton, QVBoxLayout, QComboBox,
                             QWidget, QMainWindow, QAction, QSpinBox,
                             QGridLayout, QDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

# from EMMapWidget import EMMapWidget
from EMMapEditor import MapEditor, TileModel
from EMModel import MapModel
from EMTileEditor import TilePreviewWidget
from EMHelper import ModelManager, EMImageGenerator
import math


class EMMain(QMainWindow):
    """
    The main class for Encounter Mapper.

    Handles the saving and loading of maps. Future implementations may include
    setting up tabs for maps, enabling multiple encounters to be edited at once
    """

    def __init__(self, map=None):
        super(EMMain, self).__init__()
        if map is None:
            self.model = MapModel()
        self.mapEditor = MapEditor(self.model)
        self.setWindowTitle("Encounter Mapper")
        # Set Menu Elements
        menuBar = self.menuBar()

        newAction = QAction("New", self)
        openAction = QAction("Open", self)
        saveAction = QAction("Save", self)
        saveAction.triggered.connect(self.saveEncounter)
        saveAsAction = QAction("Save As", self)
        saveAsAction.triggered.connect(self.saveAsEncounter)
        exportImageAction = QAction("Export Map", self)
        exportImageAction.triggered.connect(self.exportEncounterMap)

        quitAction = QAction("Quit", self)

        undoAction = QAction("Undo", self)
        redoAction = QAction("Redo", self)

        self.statusBar()

        fileMenu = menuBar.addMenu("File")
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)

        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(exportImageAction)
        fileMenu.addAction(quitAction)

        editMenu = menuBar.addMenu("Edit")
        editMenu.addAction(undoAction)
        editMenu.addAction(redoAction)

        menuBar.setNativeMenuBar(False)
        self.editStack = QStackedWidget()
        self.editStack.addWidget(self.initialWidget())
        self.editStack.addWidget(self.mapEditor)

        self.setCentralWidget(self.editStack)

        self.keyBindings = {
            Qt.Key_S | Qt.ControlModifier: (self.saveEncounter,),
            Qt.Key_S | Qt.ControlModifier | Qt.ShiftModifier:
            (self.saveAsEncounter,),
            Qt.Key_N | Qt.ControlModifier: (self.newEncounterOpenDialog,),
            Qt.Key_O | Qt.ControlModifier: (self.openEncounter,),
        }

    def initialWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        new = QPushButton("New Encounter")
        new.clicked.connect(self.newEncounterOpenDialog)
        open = QPushButton("Open Encounter")
        open.clicked.connect(self.openEncounter)
        imageLabel = QLabel()
        imageLabel.setPixmap(QPixmap(
            ModelManager.resourcePath("res/Title.png")).scaled(972, 540))

        layout.addWidget(imageLabel)
        layout.addWidget(new)
        layout.addWidget(open)
        widget.setLayout(layout)

        return widget

    def keyPressEvent(self, event):
        key = event.key() | int(event.modifiers())
        if key in self.keyBindings:
            command = self.keyBindings[key]
            if len(command) == 1:
                command[0]()
            else:
                command[0](command[1])

    def newEncounterOpenDialog(self):
        self.newEncounterDialog = QDialog()
        layout = QVBoxLayout()
        self.newEncounterWidget = NewMapDialog()
        self.newEncounterWidget.creatingNewMap.connect(self.createNewEncounter)
        self.newEncounterWidget.cancelNewMap.connect(self.cancelNewEncounter)
        layout.addWidget(self.newEncounterWidget)
        self.newEncounterDialog.setLayout(layout)
        self.newEncounterDialog.exec_()

    def cancelNewEncounter(self):
        self.newEncounterDialog.close()
        self.newEncounterDialog = None
        self.newEncounterWidget = None

    def createNewEncounter(self):
        self.model = self.newEncounterWidget.mapFromDialog()

        self.newEncounterDialog.close()
        self.newEncounterDialog = None
        self.newEncounterWidget = None

        if self.model is not None:

            self.mapEditor.setModel(self.model)
            self.editStack.setCurrentIndex(1)
            self.setWindowTitle("untitled*")

    def openEncounter(self):
        pathToOpen = QFileDialog.getOpenFileName(self, 'Open File',
                                                 '', "Encounter Map (*.emap)")
        if pathToOpen is not None and pathToOpen[0]:
            self.model = ModelManager.loadModelFromFile(pathToOpen[0],
                                                        MapModel)
            if self.model is not None:

                self.mapEditor.setModel(self.model)
                self.mapEditor.setFilePath(pathToOpen)
                self.editStack.setCurrentIndex(1)

                self.setWindowTitle(pathToOpen[0])

    def saveAsEncounter(self):
        filePath = QFileDialog.getSaveFileName(self, 'Save File',
                                               '', "Encounter Map (*.emap)")
        if filePath is not None:
            self.mapEditor.setFilePath(filePath)
            model = self.mapEditor.getModel()
            # Grab name from FilePath
            fp = filePath[0]
            if "/" in fp:
                fp = fp.split("/")[-1]
            if fp.endswith(".emap"):
                fp = fp[:-5]
            model.setName(fp)
            modelJS = model.jsonObj()
            ModelManager.saveJSONToFile(modelJS, filePath[0])
            # update the string
            self.mapEditor.markEdited(False)
            self.setWindowTitle(filePath[0])

    def saveEncounter(self):
        fp = self.mapEditor.getFilePath()
        if fp is None:
            self.saveAsEncounter()
        else:
            model = self.mapEditor.getModel()
            modelJS = model.jsonObj()
            ModelManager.saveJSONToFile(modelJS, fp[0])

    def exportEncounterMap(self):  # , mods=None):
        modifiers = []
        print(modifiers)
        filePath = QFileDialog.getSaveFileName(self, "Open Encounter",
                                               "", "Image (*.png)")
        if filePath is not None:
            fp = filePath[0]
            if fp.endswith(".png"):
                fp = fp[:-4]
            # self.mapEditor.setFilePath(filePath)
            model = self.mapEditor.getModel()
            if model is not None:
                mapImage = EMImageGenerator.genImageFromModel(
                    model, ("drawGrid"))
                if mapImage is not None:
                    if "groupPrint" in modifiers:
                        numY = math.ceil(model.getNumRows()/3)
                        numX = math.ceil(model.getNumCols()/2)
                        width = 6 * 72
                        height = 9 * 72
                        for y in range(numY):
                            for x in range(numX):
                                croppedImage = mapImage.copy(
                                    x*width, y*height, width, height)
                                ModelManager.saveImageToFile(
                                    croppedImage, fp+"{}{}".format(y, x))
                    else:
                        ModelManager.saveImageToFile(mapImage, fp)
                    # pass
                else:
                    print("model is not MapModel")


class NewMapDialog(QWidget):
    creatingNewMap = pyqtSignal()
    cancelNewMap = pyqtSignal()

    def __init__(self):
        super(NewMapDialog, self).__init__()
        self.numColsSB = QSpinBox()
        self.numColsSB.setValue(5)
        self.numRowsSB = QSpinBox()
        self.numRowsSB.setValue(5)
        self.tileToPopulate = QComboBox()
        ModelManager.loadModelListFromFile(ModelManager.TileName, TileModel)
        self.tiles = ModelManager.fetchModels(ModelManager.TileName)
        self.tileToPopulate.addItem("--None--")
        for tile in self.tiles:
            self.tileToPopulate.addItem(tile.getName())
        self.tileToPopulate.currentIndexChanged.connect(self.updateTilePreview)
        self.tilePreview = TilePreviewWidget(216, 0, None, True)

        self.okBtn = QPushButton("OK")
        self.okBtn.clicked.connect(self.okSelected)
        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.cancelSelected)
        layout = QGridLayout()
        layout.addWidget(QLabel("Rows:"), 0, 0)
        layout.addWidget(self.numRowsSB, 0, 1)
        layout.addWidget(QLabel("Cols:"), 0, 2)
        layout.addWidget(self.numColsSB, 0, 3)
        layout.addWidget(QLabel("Tile"), 1, 0)
        layout.addWidget(self.tileToPopulate, 1, 1, 1, 3)
        layout.addWidget(self.tilePreview, 2, 0, 1, 4)
        layout.addWidget(self.okBtn, 3, 0, 1, 2)
        layout.addWidget(self.cancelBtn, 3, 2, 1, 2)
        self.setLayout(layout)

    def okSelected(self):
        self.creatingNewMap.emit()

    def cancelSelected(self):
        self.cancelNewMap.emit()

    def updateTilePreview(self):
        index = self.tileToPopulate.currentIndex() - 1
        model = None
        if index > 0:
            model = self.tiles[index]
        self.tilePreview.setModel(model)
        self.tilePreview.repaint()

    def mapFromDialog(self):
        numRows = self.numRowsSB.value()
        numCols = self.numColsSB.value()
        tileUid = -1
        if self.tileToPopulate.currentIndex() > 0:
            tileUid = self.tiles[self.tileToPopulate.currentIndex()-1].getUid()
        print(tileUid)
        grid = []
        for y in range(numRows):
            grid.append([])
            for x in range(numCols):
                grid[-1].append((tileUid, 0, False, False))
        model = MapModel("Untitled", grid)

        return model


app = QApplication([])
mainWindow = EMMain()
mainWindow.show()
app.exec_()
