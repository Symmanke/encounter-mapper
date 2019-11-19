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
        self.ccwBtn = QPushButton("CCW")
        self.hfBtn = QPushButton("--")
        self.vfBtn = QPushButton("|")
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


class GroupPreview(QWidget):

    def __init__(self, model=None):
        super(GroupPreview, self).__init__()
        self.setMinimumHeight(500)
        self.setMinimumWidth(500)
        self.tileSize = 100
        self.groupModel = model
        self.modelList = self.createModelList()
        self.calculateOffsets()

    def calculateOffsets(self):
        self.xOffset = (500 - self.groupModel.getNumCols()*self.tileSize)/2
        self.yOffset = (500 - self.groupModel.getNumRows()*self.tileSize)/2

    def createModelList(self):
        modelList = {}
        for id in self.groupModel.getTilesToFetch():
            modelList[id] = ModelManager.fetchTileById(id)
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

                    # if tile[0] == -1:
                    #     # Draw empty tile
                    #     pass
                    print(tile[0])
                    print(self.modelList)
                    cachedTM = self.modelList[tile[0]]
                    # if cachedTM is None:
                    #     # Draw error tile
                    #     pass
                    # else:
                    self.drawTile(painter, x, y, cachedTM, tile)

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

    def drawForegroundPoly(self, painter, points):
        fg = self.tileModel.getFgColor()
        painter.setPen(fg)
        painter.setBrush(fg)
        foregroundPoly = QPolygon(points)
        painter.drawPolygon(foregroundPoly)

    def drawPointObjects(self, painter, points):
        painter.setPen(Qt.black)
        r = 10
        d = 2*r
        si = self.tileModel.getSelectedIndex()
        for i in range(len(points)):
            point = points[i]
            if i != si:
                painter.setBrush(Qt.black)
                painter.drawEllipse(point.x()-r, point.y()-r, d, d)
        painter.setBrush(Qt.white)

        if si >= 0:
            # draw white point at the end so it always shows up
            selectedPoint = points[si]
            painter.drawEllipse(selectedPoint.x()-r, selectedPoint.y()-r, d, d)


def main():
    app = QApplication([])

    mainWidget = GroupEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
