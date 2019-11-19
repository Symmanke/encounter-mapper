from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import (QPainter, QPolygon)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,  QLabel,
                             QLineEdit, QPushButton, QSpinBox, QWidget,
                             QListWidget, QDialog, QVBoxLayout)

from EMTilePicker import TilePicker
from EMModel import GroupModel
from EMHelper import ModelManager


class GroupEditor(QWidget):
    def __init__(self, model=None):
        super(GroupEditor, self).__init__()

        self.groupModel = GroupModel() if model is None else model

        titleGroup = QWidget()
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(QLabel("Group Title:"))
        self.titleEdit = QLineEdit()
        titleLayout.addWidget(self.titleEdit)
        titleGroup.setLayout(titleLayout)

        self.groupPreview = GroupPreview(self.groupModel)
        self.tilePicker = TilePicker()
        self.btnGroup = QWidget()
        btnLayout = QGridLayout()
        self.cwBtn = QPushButton("CW")
        self.cwBtn.clicked.connect(self.rotateTileMapCW)
        self.ccwBtn = QPushButton("CCW")
        self.ccwBtn.clicked.connect(self.rotateTileMapCCW)
        self.hfBtn = QPushButton("|")
        self.hfBtn.clicked.connect(self.flipTileMapH)
        self.vfBtn = QPushButton("--")
        self.vfBtn.clicked.connect(self.flipTileMapV)
        self.addRowBtn = QPushButton("Add Row")
        self.delRowBtn = QPushButton("Del Row")
        self.addColBtn = QPushButton("Add Col")
        self.delColBtn = QPushButton("Del Col")

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


class GroupPreview(QWidget):

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
        self.pTile = 0
        self.modelList = self.createModelList()
        self.setMouseTracking(True)

    def transformP(self, type):
        if type == "cw":
            self.pOrientation = (self.pOrientation + 1) % 4
        elif type == "ccw":
            self.pOrientation = (self.pOrientation + 3) % 4
        elif type == "h":
            self.phFlip = not self.phFlip

        elif type == "v":
            self.pvFlip = not self.pvFlip

    def calculateOffsets(self):
        self.xOffset = (500 - self.groupModel.getNumCols()*self.tileSize)/2
        self.yOffset = (500 - self.groupModel.getNumRows()*self.tileSize)/2

    def createModelList(self):
        modelList = {}
        for id in self.groupModel.getTilesToFetch():
            modelList[id] = ModelManager.fetchTileById(id)
        if self.pTile != -1 and self.pTile not in modelList:
            modelList[self.pTile] = ModelManager.fetchTileById(self.pTile)
        return modelList

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
            if self.mouseIndex != (-1, -1):
                self.drawPreviewTile(painter,
                                     self.mouseIndex[0], self.mouseIndex[1])

    def mousePressEvent(self, QMouseEvent):
        if self.mouseIndex != (-1, -1):
            tile = (self.pTile, self.pOrientation, self.phFlip, self.pvFlip)
            self.groupModel.setTileForIndex(
                self.mouseIndex[0], self.mouseIndex[1], tile)
            # perform stuff
            self.repaint()

    def mouseMoveEvent(self, QMouseEvent):
        prevIndex = self.mouseIndex
        self.mouseIndex = self.calcMouseIndex(QMouseEvent.pos())
        if(prevIndex != self.mouseIndex):
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
        painter.drawRect(self.xOffset + self.tileSize * xInd,
                         self.yOffset + self.tileSize * yInd,
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
                painter.drawRect(self.xOffset + self.tileSize * xInd,
                                 self.yOffset + self.tileSize * yInd,
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
        painter.drawRect(self.xOffset + self.tileSize * xInd,
                         self.yOffset + self.tileSize * yInd,
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
