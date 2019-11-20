from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QListWidget,
                             QListWidgetItem, QDialog)

# from EMTileEditor import TileEditor, TilePreviewWidget
# from EMModel import TileModel
from EMGroupEditor import GroupEditor, GroupPreview
from EMModel import GroupModel
from EMHelper import ModelManager


class GroupPicker(QWidget):
    tileDialog = None
    tileEditor = None

    currentIndex = -1

    selectedGroup = pyqtSignal(int)
    updatedGroup = pyqtSignal(int)

    def __init__(self):
        super(GroupPicker, self).__init__()
        self.groupModels = []
        self.groupList = QListWidget()
        self.groupList.itemClicked.connect(self.updateSelectedGroup)
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

    def updateSelectedTile(self):
        sr = self.tileList.currentRow()
        if sr >= 0:
            self.selectedTile.emit(self.tileModels[sr].getUid())

    def newTileDialog(self):
        self.tileDialog = QDialog()
        layout = QVBoxLayout()
        self.tileEditor = TileEditor()
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
            tempCopy = TileModel.createModelCopy(self.tileModels[sr])

            self.tileEditor = TileEditor(tempCopy)
            self.tileEditor.addModel.connect(self.updateExistingTileModel)
            self.tileEditor.cancelModel.connect(self.cancelTileModel)

            layout.addWidget(self.tileEditor)
            self.tileDialog.setLayout(layout)
            self.tileDialog.exec_()

    def addNewTileModel(self):
        tileModel = self.tileEditor.getCurrentModel()
        ModelManager.addTile(tileModel)
        self.tileModels.append(tileModel)
        self.tileDialog.close()
        self.tileDialog = None
        self.tileEditor = None
        self.updateUI()

    def updateExistingTileModel(self):
        tileModel = self.tileEditor.getCurrentModel()
        ModelManager.updateTile(tileModel)
        self.tileModels[self.tileList.currentRow()] = tileModel
        self.tileDialog.close()
        self.tileDialog = None
        self.tileEditor = None
        self.updateUI()
        self.updatedTile.emit(tileModel.getUid())

    def cancelTileModel(self):
        self.tileDialog.close()
        self.tileDialog = None
        self.tileEditor = None

    def duplicateTile(self):
        sr = self.tileList.currentRow()
        if sr >= 0:
            dupe = TileModel.createModelCopy(self.tileModels[sr])

            name = "{}_copy".format(dupe.getName())
            dupe.setName(name)
            ModelManager.addTile(dupe, sr)
            self.tileModels.insert(sr, dupe)
            self.updateUI()

    def deleteTile(self):
        """TODO"""

    def updateUI(self):
        self.tileList.clear()
        for model in self.tileModels:
            listItemWidget = TilePickerListItem(model)
            listItem = QListWidgetItem(self.tileList)
            listItem.setSizeHint(listItemWidget.sizeHint())

            self.tileList.addItem(listItem)
            self.tileList.setItemWidget(listItem, listItemWidget)

    def loadTiles(self):
        self.tileModels = ModelManager.fetchTiles()
        self.updateUI()

    def appendTile(self, tilejs):
        """todo"""


class TilePickerListItem(QWidget):
    tileModel = None
    preview = None

    def __init__(self, model=None):
        super(TilePickerListItem, self).__init__()
        self.tileModel = model
        if model is not None:
            layout = QHBoxLayout()
            self.preview = TilePreviewWidget.previewWidget(self.tileModel)
            layout.addWidget(self.preview)
            layout.addWidget(QLabel(self.tileModel.getName()))
            self.setLayout(layout)


def main():
    app = QApplication([])

    mainWidget = TilePicker()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
