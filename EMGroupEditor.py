from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,  QLabel,
                             QPushButton, QWidget)

# from EMTilePicker import TilePicker
from EMModel import GroupModel, TileModel
from EMTileEditor import TileEditor, TilePreviewWidget
from EMHelper import ModelManager
from EMBaseClasses import EMModelEditor, EMModelGraphics, EMModelPicker


class GroupEditor(EMModelEditor):
    """
    The GroupEditor handles the creation of groupModels, which are groups of
    Tiles. It contains a ModelPicker displaying tiles and a groupPreview which
    handles the graphical representation and interaction with the model.
    """

    def __init__(self, model=None):
        super(GroupEditor, self).__init__(model)
        titleGroup = QWidget()
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(QLabel("Group Title:"))
        titleLayout.addWidget(self.modelNameEdit)
        titleGroup.setLayout(titleLayout)

        self.groupPreview = GroupPreview(self.model)
        self.groupPreview.updatePreview.connect(self.updateUI)
        self.tilePicker = EMModelPicker(ModelManager.TileName, TileModel,
                                        TileEditor, TilePreviewWidget)
        self.tilePicker.selectedModel.connect(self.groupPreview.setPTile)
        self.tilePicker.updatedModel.connect(self.updateGroupList)
        self.tilePicker.deletedModel.connect(self.groupPreview.removeTileCache)
        self.btnGroup = QWidget()
        btnLayout = QGridLayout()
        self.cwBtn = QPushButton("CW")
        self.cwBtn.clicked.connect(self.rotateTileMapCW)
        self.ccwBtn = QPushButton("CCW")
        self.ccwBtn.clicked.connect(self.rotateTileMapCCW)
        self.hfBtn = QPushButton("|")
        self.hfBtn.setCheckable(True)
        self.hfBtn.clicked.connect(self.flipTileMapH)
        self.vfBtn = QPushButton("--")
        self.vfBtn.setCheckable(True)
        self.vfBtn.clicked.connect(self.flipTileMapV)
        self.addRowBtn = QPushButton("Add Row")
        self.addRowBtn.clicked.connect(self.addGroupRow)
        self.delRowBtn = QPushButton("Del Row")
        self.delRowBtn.clicked.connect(self.delGroupRow)
        self.addColBtn = QPushButton("Add Col")
        self.addColBtn.clicked.connect(self.addGroupCol)
        self.delColBtn = QPushButton("Del Col")
        self.delColBtn.clicked.connect(self.delGroupCol)

        btnLayout.addWidget(self.cwBtn, 0, 0)
        btnLayout.addWidget(self.ccwBtn, 1, 0)
        btnLayout.addWidget(self.hfBtn, 0, 1)
        btnLayout.addWidget(self.vfBtn, 1, 1)
        btnLayout.addWidget(self.addRowBtn, 0, 2)
        btnLayout.addWidget(self.delRowBtn, 1, 2)
        btnLayout.addWidget(self.addColBtn, 0, 3)
        btnLayout.addWidget(self.delColBtn, 1, 3)
        self.btnGroup.setLayout(btnLayout)

        bottomGroup = QWidget()
        bottomLayout = QHBoxLayout()

        bottomLayout.addWidget(self.applyBtn)
        bottomLayout.addWidget(self.cancelBtn)
        bottomGroup.setLayout(bottomLayout)

        layout = QGridLayout()
        layout.addWidget(titleGroup, 0, 0)
        layout.addWidget(self.groupPreview, 1, 0)
        layout.addWidget(self.tilePicker, 0, 1, 3, 1)
        layout.addWidget(self.btnGroup, 2, 0)
        layout.addWidget(bottomGroup, 3, 0, 1, 2)
        self.setLayout(layout)

        self.updateUI()

    def rotateTileMapCW(self):
        self.groupPreview.transformP("cw")

    def rotateTileMapCCW(self):
        self.groupPreview.transformP("ccw")

    def flipTileMapH(self):
        self.groupPreview.transformP("h")

    def flipTileMapV(self):
        self.groupPreview.transformP("v")

    def addGroupRow(self):
        self.model.addRow()

    def addGroupCol(self):
        self.model.addCol()

    def delGroupRow(self):
        self.model.delRow()

    def delGroupCol(self):
        self.model.delCol()

    def updateGroupList(self, id):
        self.groupPreview.updateModelList(id)
        self.groupPreview.repaint()

    def updateUI(self):
        # update Buttons
        options = self.groupPreview.getSOptions()
        self.hfBtn.setChecked(options[1])
        self.vfBtn.setChecked(options[2])
        self.btnGroup.repaint()
        self.modelNameEdit.setText(self.model.getName())
        # update the preview
        self.groupPreview.calculateOffsets()
        self.groupPreview.repaint()


class GroupPreview(EMModelGraphics):
    """
    Preview object for displaying and interacting with groups. Can be Used
    in conjunction with the GroupEditor to create a group of tiles, or in the
    picker class to depict a group of objects.
    """

    updatePreview = pyqtSignal()

    def __init__(self, model, tileSize=100,
                 width=500, height=500, preview=False):
        super(GroupPreview, self).__init__(
            model, model.getNumRows(), model.getNumCols(), tileSize,
            width, height, preview, True)

        self.keyBindings = {
            Qt.Key_R: (self.transformP, "cw"),
            Qt.Key_R | Qt.ShiftModifier: (self.transformP, "ccw"),
            Qt.Key_F: (self.transformP, "h"),
            Qt.Key_F | Qt.ShiftModifier: (self.transformP, "v")

        }

    @classmethod
    def previewWidget(cls, model):
        maxRowCol = max(model.getNumRows(), model.getNumCols())
        tileSize = 50/maxRowCol
        return cls(model, tileSize, 50, 50, True)

    def setPTile(self, tileId):
        print(tileId)
        self.selectedObject[0] = tileId
        self.updateModelList(tileId)

    def transformP(self, type):
        if type == "cw":
            self.sOptions[0] = (self.sOptions[0] + 1) % 4
        elif type == "ccw":
            self.sOptions[0] = (self.sOptions[0] + 3) % 4
        elif type == "h":
            self.sOptions[1] = not self.sOptions[1]
        elif type == "v":
            self.sOptions[2] = not self.sOptions[2]
        self.updatePreview.emit()

    def removeTileCache(self, id):
        if id != -1:
            self.modelList[id] = None
            self.repaint()

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if(self.model is not None):
            bgColor = Qt.white if self.preview else Qt.black
            painter.setBrush(bgColor)
            painter.setPen(bgColor)
            painter.drawRect(0, 0, self.width, self.height)
            grid = self.model.getTileGrid()
            for y in range(self.model.getNumRows()):
                for x in range(self.model.getNumCols()):
                    tile = grid[y][x]
                    if tile[0] == -1:
                        # Draw empty tile
                        self.drawEmptyTile(painter, x, y)
                    else:
                        if tile[0] not in self.modelList:
                            self.drawErrorTile(painter, x, y)
                        else:
                            cachedTM = self.modelList[tile[0]]
                            if cachedTM is None:
                                # Draw error tile
                                self.drawErrorTile(painter, x, y)
                            else:
                                # draw actual tile
                                self.drawTile(painter, x, y, cachedTM,
                                              (tile[1], tile[2], tile[3]))
            if not self.preview:
                if self.mouseIndex != (-1, -1) and not self.mousePressed:
                    if self.selectedObject[0] in self.modelList:
                        model = self.modelList[self.selectedObject[0]]
                        self.drawTile(
                            painter, self.mouseIndex[0], self.mouseIndex[1],
                            model, self.sOptions, True)

    def keyPressEvent(self, event):
        if self.preview:
            event.ignore()
        else:
            key = event.key() | int(event.modifiers())
            if key in self.keyBindings:
                command = self.keyBindings[key]
                command[0](command[1])

    def mousePressEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            if QMouseEvent.button() & Qt.LeftButton:
                self.mousePressed = True
                if self.mouseIndex != (-1, -1):
                    tileOptions = [self.selectedObject[0], self.sOptions[0],
                                   self.sOptions[1], self.sOptions[2]]
                    self.model.setTileForIndex(
                        self.mouseIndex[0], self.mouseIndex[1],
                        tileOptions)
                    # perform stuff
                    self.repaint()

    def mouseMoveEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            self.setFocus()
            prevIndex = self.mouseIndex
            self.mouseIndex = self.calcMouseIndex(QMouseEvent.pos())
            if(prevIndex != self.mouseIndex):
                if self.mousePressed and self.mouseIndex != (-1, -1):
                    tileOptions = [self.selectedObject[0], self.sOptions[0],
                                   self.sOptions[1], self.sOptions[2]]
                    self.model.setTileForIndex(
                        self.mouseIndex[0], self.mouseIndex[1],
                        tileOptions)
                    print(tileOptions)
                self.repaint()

    def mouseReleaseEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            self.mousePressed = False


def main():
    app = QApplication([])

    mainWidget = GroupEditor(GroupModel())
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
