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
                             QLabel, QPushButton, QVBoxLayout,
                             QWidget, QMainWindow, QAction)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# from EMMapWidget import EMMapWidget
from EMMapEditor import MapEditor
from EMModel import MapModel
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
            Qt.Key_N | Qt.ControlModifier: (self.newEncounter,),
            Qt.Key_O | Qt.ControlModifier: (self.openEncounter,),
        }

    def initialWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        new = QPushButton("New Encounter")
        new.clicked.connect(self.newEncounter)
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

    def newEncounter(self):
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

    def exportEncounterMap(self, mods=None):
        modifiers = ["groupPrint"]  # if mods is None else mods
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


app = QApplication([])
mainWindow = EMMain()
mainWindow.show()
app.exec_()
