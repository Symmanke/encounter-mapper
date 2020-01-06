"""
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

# from EMMapWidget import EMMapWidget
from EMMapEditor import MapEditor
from EMModel import MapModel
from EMHelper import ModelManager


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
        quitAction = QAction("Quit", self)

        undoAction = QAction("Undo", self)
        redoAction = QAction("Redo", self)

        self.statusBar()

        fileMenu = menuBar.addMenu("File")
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)

        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(quitAction)

        editMenu = menuBar.addMenu("Edit")
        editMenu.addAction(undoAction)
        editMenu.addAction(redoAction)

        menuBar.setNativeMenuBar(False)
        self.editStack = QStackedWidget()
        self.editStack.addWidget(self.initialWidget())
        self.editStack.addWidget(self.mapEditor)

        self.setCentralWidget(self.editStack)

    def initialWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        new = QPushButton("New Encounter")
        new.clicked.connect(self.newEncounter)
        open = QPushButton("Open Encounter")
        open.clicked.connect(self.openEncounter)

        layout.addWidget(QLabel("Welcome To Encounter Mapper"))
        layout.addWidget(new)
        layout.addWidget(open)
        widget.setLayout(layout)

        return widget

    def newEncounter(self):
        self.editStack.setCurrentIndex(1)
        self.setWindowTitle("untitled*")

    def openEncounter(self):
        pathToOpen = QFileDialog.getOpenFileName()
        if pathToOpen is not None:
            self.model = ModelManager.loadModelFromFile(pathToOpen[0],
                                                        MapModel)
            if self.model is not None:

                self.mapEditor.setModel(self.model)
                self.editStack.setCurrentIndex(1)

    def saveAsEncounter(self):
        filePath = QFileDialog.getSaveFileName()
        if filePath is not None:
            self.mapEditor.setFilePath(filePath)
            model = self.mapEditor.getModel()
            modelJS = model.jsonObj()
            ModelManager.saveJSONToFile(modelJS, filePath[0])

    def saveEncounter(self):
        pass


app = QApplication([])
mainWindow = EMMain()
mainWindow.show()
app.exec_()
