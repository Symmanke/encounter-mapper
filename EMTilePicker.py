from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import (QPainter, QPolygon)
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QWidget, QListWidget,
                             QListWidgetItem, QDialog)

from EMTileEditor import EMTileEditor, EMTilePreviewWidget
from EMTileEditorModel import EMTileEditorModel


class EMTilePicker(QWidget):
    tileDialog = None
    tileEditor = None
    tileModels = []
    currentIndex = -1

    def __init__(self):
        super(EMTilePicker, self).__init__()
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

    def updateExistingTileModel(self):
        tileModel = self.tileEditor.getCurrentModel()
        self.tileModels[self.tileList.currentRow()] = tileModel
        self.tileDialog.close()
        self.tileDialog = None
        self.tileEditor = None
        self.updateUI()

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
