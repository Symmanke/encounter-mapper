from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QListWidget,
                             QListWidgetItem, QDialog)

from EMTileEditor import EMTileEditor, EMTilePreviewWidget
from EMTileEditorModel import EMTileEditorModel
from EMModel import TileModel
from EMHelper import ModelManager

import json


class EMTilePicker(QWidget):
    tileDialog = None
    tileEditor = None

    currentIndex = -1

    selectedTile = pyqtSignal()

    def __init__(self):
        super(EMTilePicker, self).__init__()
        self.tileModels = []
        self.tileList = QListWidget()
        self.addTileButton = QPushButton("New Tile")
        self.addTileButton.clicked.connect(self.newTileDialog)
        self.editTileButton = QPushButton("Edit Tile")
        self.editTileButton.clicked.connect(self.editTileDialog)
        self.duplicateTileButton = QPushButton("Duplicate")
        self.duplicateTileButton.clicked.connect(self.duplicateTile)
        self.deleteTileButton = QPushButton("Delete Tile")
        self.deleteTileButton.clicked.connect(self.deleteTile)
        layout = QVBoxLayout()
        layout.addWidget(self.tileList)
        layout.addWidget(self.addTileButton)
        layout.addWidget(self.editTileButton)
        layout.addWidget(self.duplicateTileButton)
        layout.addWidget(self.deleteTileButton)
        self.setLayout(layout)
        self.loadTiles()

    def newTileDialog(self):
        self.tileDialog = QDialog()
        layout = QVBoxLayout()
        self.tileEditor = EMTileEditor()
        self.tileEditor.addModel.connect(self.addNewTileModel)
        self.tileEditor.cancelModel.connect(self.cancelTileModel)
        layout.addWidget(self.tileEditor)
        self.tileDialog.setLayout(layout)
        self.tileDialog.exec_()

    def editTileDialog(self):
        sr = self.tileList.currentRow()
        if sr >= 0:
            self.tileDialog = QDialog()
            layout = QVBoxLayout()
            tempCopy = EMTileEditorModel.createCopy(self.tileModels[sr])
            self.tileEditor = EMTileEditor()
            self.tileEditor.setModel(tempCopy)
            self.tileEditor.addModel.connect(self.updateExistingTileModel)
            self.tileEditor.cancelModel.connect(self.cancelTileModel)

            layout.addWidget(self.tileEditor)
            self.tileDialog.setLayout(layout)
            self.tileDialog.exec_()

    def addNewTileModel(self):
        tileModel = self.tileEditor.getCurrentModel()
        self.tileModels.append(tileModel)
        self.tileDialog.close()
        self.tileDialog = None
        self.tileEditor = None
        self.updateUI()
        self.saveTiles()

    def updateExistingTileModel(self):
        tileModel = self.tileEditor.getCurrentModel()
        self.tileModels[self.tileList.currentRow()] = tileModel
        self.tileDialog.close()
        self.tileDialog = None
        self.tileEditor = None
        self.updateUI()
        self.saveTiles()

    def cancelTileModel(self):
        self.tileDialog.close()
        self.tileDialog = None
        self.tileEditor = None

    def duplicateTile(self):
        sr = self.tileList.currentRow()
        if sr >= 0:
            dupe = EMTileEditorModel.createCopy(self.tileModels[sr])
            name = "{}_copy".format(dupe.getName())
            dupe.setName(name)
            self.tileModels.insert(sr, dupe)
            self.updateUI()
            self.saveTiles()

    def deleteTile(self):
        """TODO"""

    def updateUI(self):
        self.tileList.clear()
        for model in self.tileModels:
            listItemWidget = EMTilePickerListItem(model)
            listItem = QListWidgetItem(self.tileList)
            listItem.setSizeHint(listItemWidget.sizeHint())

            self.tileList.addItem(listItem)
            self.tileList.setItemWidget(listItem, listItemWidget)

    def saveTiles(self):
        tileJS = {
            "tiles": [],
            "patterns": []
        }
        for tm in self.tileModels:
            tileJS["tiles"].append(tm.jsonObj())

        # Do fancy stuff to save the tile map
        text = json.dumps(tileJS)
        f = open("tiles.json", "w+")
        f.write(text)
        f.close()

    def loadTiles(self):
        # f = open("tiles.json", "r")
        # if f.mode == 'r':
        #     contents = f.read()
        #     jsContents = json.loads(contents)
        #     # f.close()
        #
        #     for tilejs in jsContents["tiles"]:
        #         model = EMTileEditorModel(tilejs["name"])
        #         for point in tilejs["points"]:
        #             model.addPoint(point[0], point[1])
        #         self.tileModels.append(model)
        #
        #     self.updateUI()
        self.tileModels = ModelManager.fetchTiles()
        self.updateUI()

    def appendTile(self, tilejs):
        """todo"""


class EMTilePickerListItem(QWidget):
    tileModel = None
    preview = None

    def __init__(self, model=None):
        super(EMTilePickerListItem, self).__init__()
        self.tileModel = model
        if model is not None:
            layout = QHBoxLayout()
            self.preview = EMTilePreviewWidget.previewWidget(self.tileModel)
            layout.addWidget(self.preview)
            layout.addWidget(QLabel(self.tileModel.getName()))
            self.setLayout(layout)


def main():
    app = QApplication([])

    mainWidget = EMTilePicker()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
