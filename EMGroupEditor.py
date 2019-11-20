from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import (QPainter, QPolygon)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,  QLabel,
                             QLineEdit, QPushButton, QWidget)

# from EMTilePicker import TilePicker
from EMModel import GroupModel, TileModel
from EMTileEditor import TileEditor, TilePreviewWidget
from EMHelper import ModelManager
from EMModelPicker import EMModelPicker


class GroupEditor(QWidget):

    addModel = pyqtSignal()
    cancelModel = pyqtSignal()

    def __init__(self, model=None):
        super(GroupEditor, self).__init__()

        self.groupModel = GroupModel() if model is None else model
        self.groupModel.modelUpdated.connect(self.updateUI)

        titleGroup = QWidget()
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(QLabel("Group Title:"))
        self.titleEdit = QLineEdit()
        titleLayout.addWidget(self.titleEdit)
        titleGroup.setLayout(titleLayout)

        self.groupPreview = GroupPreview(self.groupModel)
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
        self.applyBtn = QPushButton("Apply")
        self.cancelBtn = QPushButton("Cancel")

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
        self.setMouseTracking(True)

    def rotateTileMapCW(self):
        self.groupPreview.transformP("cw")

    def rotateTileMapCCW(self):
        self.groupPreview.transformP("ccw")

    def flipTileMapH(self):
        self.groupPreview.transformP("h")

    def flipTileMapV(self):
        self.groupPreview.transformP("v")

    def addGroupRow(self):
        self.groupModel.addRow()

    def addGroupCol(self):
        self.groupModel.addCol()

    def delGroupRow(self):
        self.groupModel.delRow()

    def delGroupCol(self):
        self.groupModel.delCol()

    def updateGroupList(self, id):
        self.groupPreview.updateModelList(id)
        self.groupPreview.repaint()

    def updateUI(self):
        # update Buttons
        options = self.groupPreview.getPOptions()
        self.hfBtn.setChecked(options[1])
        self.vfBtn.setChecked(options[2])
        self.btnGroup.repaint()
        # update the preview
        self.groupPreview.calculateOffsets()
        self.groupPreview.repaint()


class GroupPreview(QWidget):

    updatePreview = pyqtSignal()

    def __init__(self, model=None):
        super(GroupPreview, self).__init__()
        self.setMinimumHeight(500)
        self.setMinimumWidth(500)

        self.tileSize = 100
        self.groupModel = model

        self.calculateOffsets()

        self.numRows = self.groupModel.getNumRows()
        self.numCols = self.groupModel.getNumCols()
        self.mouseIndex = (-1, -1)
        self.pOrientation = 0
        self.pvFlip = False
        self.phFlip = False
        self.pTile = -1
        self.modelList = {}
        self.createModelList()
        self.setMouseTracking(True)
        self.mousePressed = False

        self.keyBindings = {
            Qt.Key_R: (self.transformP, "cw"),
            Qt.Key_R | Qt.ShiftModifier: (self.transformP, "ccw"),
            Qt.Key_F: (self.transformP, "h"),
            Qt.Key_F | Qt.ShiftModifier: (self.transformP, "v")

        }

    def setPTile(self, tileId):
        self.pTile = tileId
        print(tileId)
        self.updateModelList(tileId)

    def getPOptions(self):
        return (self.pOrientation, self.phFlip, self.pvFlip)

    def transformP(self, type):
        if type == "cw":
            self.pOrientation = (self.pOrientation + 1) % 4
        elif type == "ccw":
            self.pOrientation = (self.pOrientation + 3) % 4
        elif type == "h":
            self.phFlip = not self.phFlip
        elif type == "v":
            self.pvFlip = not self.pvFlip
        self.updatePreview.emit()

    def calculateOffsets(self):
        self.numRows = self.groupModel.getNumRows()
        self.numCols = self.groupModel.getNumCols()
        self.xOffset = (500 - self.numCols*self.tileSize)/2
        self.yOffset = (500 - self.numRows*self.tileSize)/2

    def createModelList(self):

        for id in self.groupModel.getTilesToFetch():
            self.updateModelList(id)
        if self.pTile != -1 and self.pTile not in self.modelList:
            self.updateModelList(id)

    def updateModelList(self, id):
        if id != -1:
            self.modelList[id] = ModelManager.fetchByUid(
                ModelManager.TileName, id)

    def removeTileCache(self, id):
        if id != -1:
            self.modelList[id] = None
            self.repaint()

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if(self.groupModel is not None):
            painter.setBrush(Qt.black)
            painter.setPen(Qt.black)
            painter.drawRect(0, 0, 500, 500)
            grid = self.groupModel.getTileGrid()
            for y in range(self.groupModel.getNumRows()):
                for x in range(self.groupModel.getNumCols()):
                    tile = grid[y][x]
                    if tile[0] == -1:
                        # Draw empty tile
                        self.drawEmptyTile(painter, x, y)
                    else:
                        cachedTM = self.modelList[tile[0]]
                        if cachedTM is None:
                            # Draw error tile
                            self.drawErrorTile(painter, x, y)
                        else:
                            # draw actual tile
                            self.drawTile(painter, x, y, cachedTM, tile)
            if self.mouseIndex != (-1, -1) and not self.mousePressed:
                self.drawPreviewTile(painter,
                                     self.mouseIndex[0], self.mouseIndex[1])

    def keyPressEvent(self, event):
        key = event.key() | int(event.modifiers())
        if key in self.keyBindings:
            command = self.keyBindings[key]
            command[0](command[1])

    def mousePressEvent(self, QMouseEvent):

        if QMouseEvent.button() & Qt.LeftButton:
            self.mousePressed = True
            if self.mouseIndex != (-1, -1):
                tile = (self.pTile, self.pOrientation,
                        self.phFlip, self.pvFlip)
                self.groupModel.setTileForIndex(
                    self.mouseIndex[0], self.mouseIndex[1], tile)
                # perform stuff
                self.repaint()

    def mouseMoveEvent(self, QMouseEvent):
        self.setFocus()
        prevIndex = self.mouseIndex
        self.mouseIndex = self.calcMouseIndex(QMouseEvent.pos())
        if(prevIndex != self.mouseIndex):
            if self.mousePressed and self.mouseIndex != (-1, -1):
                tile = (self.pTile, self.pOrientation,
                        self.phFlip, self.pvFlip)
                self.groupModel.setTileForIndex(
                    self.mouseIndex[0], self.mouseIndex[1], tile)
            self.repaint()

    def mouseReleaseEvent(self, QMouseEvent):
        self.mousePressed = False
        self.repaint()

    def calcMouseIndex(self, mPoint):
        if mPoint.x() < self.xOffset or mPoint.y() < self.yOffset:
            return (-1, -1)
        index = (mPoint.x() - self.xOffset, mPoint.y() - self.yOffset)
        index = (int(index[0]/self.tileSize), int(index[1]/self.tileSize))
        if index[0] >= self.numCols or index[1] >= self.numRows:
            return (-1, -1)
        return index

    def drawTile(self, painter, xInd, yInd, model, options):
        painter.setPen(Qt.black)
        painter.setBrush(model.getBgColor())
        # painter.setBrush(Qt.white)
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


def main():
    app = QApplication([])

    mainWidget = GroupEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
