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

from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,  QLabel,
                             QPushButton, QSpinBox, QWidget,
                             QListWidget, QDialog, QVBoxLayout)

from EMPaletteEditor import EMPaletteEditor
from EMModel import TileModel
from EMBaseClasses import EMModelEditor, EMModelGraphics


class TileEditor(EMModelEditor):
    """
    The TileEditor is a class used to edit TileModels

    It inherits EMModelEditor, and is often called through EMModelPicker.
    """
    selectingColor = ""
    paletteDialog = None
    paletteEditor = None

    addModel = pyqtSignal()
    cancelModel = pyqtSignal()

    def __init__(self, model=None):
        super(TileEditor, self).__init__(model)
        layout = QGridLayout()
        self.previewWidget = TilePreviewWidget()
        self.tilePointList = QListWidget()
        self.tilePointList.itemClicked.connect(self.updateCurrentItem)
        self.pointXEdit = QSpinBox()
        self.pointXEdit.setMaximum(100)
        self.pointXEdit.setMinimum(0)
        self.pointXEdit.valueChanged.connect(self.updatePointPosition)
        self.pointYEdit = QSpinBox()
        self.pointYEdit.setMaximum(100)
        self.pointYEdit.setMinimum(0)
        self.pointYEdit.valueChanged.connect(self.updatePointPosition)
        self.cwBtn = QPushButton("CW")
        self.cwBtn.clicked.connect(self.rotCW)
        self.ccwBtn = QPushButton("CCW")
        self.ccwBtn.clicked.connect(self.rotCCW)
        self.hfBtn = QPushButton("|")
        self.hfBtn.clicked.connect(self.flipH)
        self.vfBtn = QPushButton("--")
        self.vfBtn.clicked.connect(self.flipV)

        self.addPointBtn = QPushButton("Add Point")
        self.addPointBtn.clicked.connect(self.addPoint)
        self.delPointBtn = QPushButton("Del Point")
        self.delPointBtn.clicked.connect(self.deletePoint)
        self.upPointBtn = QPushButton("Move Point Up")
        self.upPointBtn.clicked.connect(self.moveUpPoint)
        self.downPointBtn = QPushButton("Move Point Down")
        self.downPointBtn.clicked.connect(self.moveDownPoint)

        self.fgColorBtn = QPushButton("Set FG")
        self.fgColorBtn.clicked.connect(self.setFGColor)
        self.bgColorBtn = QPushButton("Set BG")
        self.bgColorBtn.clicked.connect(self.setBGColor)

        self.buttonHolder = QWidget()
        bhLayout = QGridLayout()
        bhLayout.addWidget(self.addPointBtn, 0, 0, 1, 3)
        bhLayout.addWidget(self.delPointBtn, 0, 3, 1, 3)
        bhLayout.addWidget(self.upPointBtn, 1, 0, 1, 3)
        bhLayout.addWidget(self.downPointBtn, 1, 3, 1, 3)
        bhLayout.addWidget(self.cwBtn, 2, 0, 1, 2)
        bhLayout.addWidget(self.ccwBtn, 3, 0, 1, 2)
        bhLayout.addWidget(self.hfBtn, 2, 2, 1, 2)
        bhLayout.addWidget(self.vfBtn, 3, 2, 1, 2)
        bhLayout.addWidget(self.fgColorBtn, 2, 4, 1, 2)
        bhLayout.addWidget(self.bgColorBtn, 3, 4, 1, 2)
        self.buttonHolder.setLayout(bhLayout)

        layout.addWidget(self.previewWidget, 0, 0, 7, 1)
        layout.addWidget(QLabel("Tile Name:"), 0, 1)
        layout.addWidget(self.modelNameEdit, 0, 2, 1, 3)
        layout.addWidget(QLabel("X:"), 1, 1)
        layout.addWidget(self.pointXEdit, 1, 2)
        layout.addWidget(QLabel("Y:"), 1, 3)
        layout.addWidget(self.pointYEdit, 1, 4)
        layout.addWidget(self.tilePointList, 2, 1, 4, 3)
        layout.addWidget(self.buttonHolder, 6, 1, 1, 4)

        # buttons to add fhe model
        acbtn = QWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.applyBtn)
        hbox.addWidget(self.cancelBtn)
        acbtn.setLayout(hbox)
        layout.addWidget(acbtn, 7, 0, 1, 5)

        self.setLayout(layout)
        self.previewWidget.setModel(self.model)
        self.updateUI()

    def addPoint(self):
        self.model.addPoint(self.pointXEdit.value(),
                            self.pointYEdit.value())

    def deletePoint(self):
        self.model.deleteSelectedPoint()

    def moveUpPoint(self):
        swap = self.model.getSelectedIndex() - 1
        if swap < 0:
            swap = len(self.model.getPoints())-1
        self.model.swapPointSelected(swap)

    def moveDownPoint(self):
        swap = self.model.getSelectedIndex() + 1
        if swap >= len(self.model.getPoints()):
            swap = 0
        self.model.swapPointSelected(swap)

    def updatePointPosition(self):
        index = self.tilePointList.currentRow()
        self.model.updatePoint(index, self.pointXEdit.value(),
                               self.pointYEdit.value())

    def rotCW(self):
        self.model.transformRotate(True)

    def rotCCW(self):
        self.model.transformRotate(False)

    def flipH(self):
        self.model.transformFlip(True)

    def flipV(self):
        self.model.transformFlip(False)

    def setFGColor(self):
        self.paletteDialog = QDialog()
        layout = QVBoxLayout()

        fg = self.model.getFgColor()
        self.selectingColor = "fg"
        self.paletteEditor = EMPaletteEditor(fg.red(), fg.green(), fg.blue())
        self.paletteEditor.colorApplied.connect(self.applyColorChange)
        self.paletteEditor.colorCanceled.connect(self.cancelColorChange)

        layout.addWidget(self.paletteEditor)
        self.paletteDialog.setLayout(layout)
        self.paletteDialog.exec_()
        # self.paletteEditor.show()

    def setBGColor(self):
        bg = self.model.getFgColor()
        layout = QVBoxLayout()

        self.paletteDialog = QDialog()
        self.selectingColor = "bg"
        self.paletteEditor = EMPaletteEditor(bg.red(), bg.green(), bg.blue())
        self.paletteEditor.colorApplied.connect(self.applyColorChange)
        self.paletteEditor.colorCanceled.connect(self.cancelColorChange)
        # self.paletteEditor.show()

        layout.addWidget(self.paletteEditor)
        self.paletteDialog.setLayout(layout)
        self.paletteDialog.exec_()

    def applyColorChange(self, r, g, b):
        if self.selectingColor == "bg":
            self.model.setBgColor(r, g, b)
        elif self.selectingColor == "fg":
            self.model.setFgColor(r, g, b)
        self.selectingColor = ""
        self.paletteDialog.close()
        self.paletteDialog = None
        self.paletteEditor = None

    def cancelColorChange(self):
        self.selectingColor = ""
        self.paletteDialog.close()
        self.paletteDialog = None
        self.paletteEditor = None

    def setModel(self, model):
        self.model = model
        self.model.modelUpdated.connect(self.updateUI)
        self.previewWidget.setModel(model)
        self.updateUI()

    def updateCurrentItem(self):
        self.model.setSelectedIndex(self.tilePointList.currentRow())

    def updateUI(self):
        self.reloadPointList()
        self.previewWidget.repaint()
        self.updateCurrentValues()
        self.modelNameEdit.setText(self.model.getName())
        self.enableButtons()

    def reloadPointList(self):
        self.tilePointList.clear()
        points = self.model.getPoints()
        for i in range(len(points)):
            point = points[i]
            self.tilePointList.addItem("{}. ({}, {})"
                                       .format(i+1, point[0], point[1]))
        self.tilePointList.setCurrentRow(self.model.getSelectedIndex())

    def updateCurrentValues(self):
        currentIndex = self.model.getSelectedIndex()
        if(currentIndex != -1):
            point = self.model.getPoints()[currentIndex]
            self.pointXEdit.setValue(point[0])
            self.pointYEdit.setValue(point[1])
        else:
            self.pointXEdit.setValue(50)
            self.pointYEdit.setValue(50)

    def enableButtons(self):
        num = self.model.getNumPoints()
        self.delPointBtn.setEnabled(num > 0)
        self.upPointBtn.setEnabled(num > 1)
        self.downPointBtn.setEnabled(num > 1)
        self.cwBtn.setEnabled(num > 0)
        self.ccwBtn.setEnabled(num > 0)
        self.hfBtn.setEnabled(num > 0)
        self.vfBtn.setEnabled(num > 0)

        self.buttonHolder.repaint()


class TilePreviewWidget(EMModelGraphics):
    """
    widget that displays the preview of the object. Contains means to interact
    with specific nodes, modifying the tile appearance through mouse clicks.
    Interaction is turned off only when preview is True
    """

    pointSelected = pyqtSignal(int)
    pointDragged = pyqtSignal(int, int)

    def __init__(self, tileSize=500, border=10, model=None, preview=False):
        super(TilePreviewWidget, self).__init__(model, 1, 1, tileSize,
                                                tileSize + (border * 2),
                                                tileSize + (border * 2),
                                                preview)
        self.binkedPoint = False

    # Class method for constructing different ones
    @classmethod
    def previewWidget(cls, model):
        return cls(50, 0, model, True)

    def setModel(self, model):
        self.model = model

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if(self.model is not None):
            self.drawTile(painter, 0, 0, self.model)
            if not self.preview:
                points = self.model.generatePointOffset(
                    0, 0, self.tileSize, self.xOffset, self.yOffset)
                self.drawPointObjects(painter, points)

    def drawPointObjects(self, painter, points):
        painter.setPen(Qt.black)
        r = 10
        d = 2*r
        si = self.model.getSelectedIndex()
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

    def mousePressEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            mp = self.mousePosScale(QMouseEvent.pos())
            # check if selected one is clicked first
            if self.model.getSelectedIndex() != -1:
                if self.distanceHelper(
                        mp, self.model.getSelectedPoint()) <= 100:
                    self.binkedPoint = True
                else:
                    points = self.model.getPoints()
                    for i in range(len(points)):
                        point = points[i]
                        if self.distanceHelper(mp, point) <= 100:
                            self.binkedPoint = True
                            self.model.setSelectedIndex(i)
                            break

    def mouseMoveEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            if self.binkedPoint:
                mp = self.mousePosScale(QMouseEvent.pos())
                self.model.setSelectedPoint(mp[0], mp[1])

    def mouseReleaseEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            self.binkedPoint = False

    def mousePosScale(self, mPoint):
        mp = (int((mPoint.x()-10)/5), int((mPoint.y()-10)/5))
        mp = (max(min(mp[0], 100), 0), max(min(mp[1], 100), 0))

        return mp

    def distanceHelper(self, point1, point2):
        p1 = point1[0] - point2[0]
        p2 = point1[1] - point2[1]
        p1 = p1 * p1
        p2 = p2 * p2
        return p1 + p2


def main():
    app = QApplication([])
    model = TileModel("tileName", [(50, 50)])
    mainWidget = TileEditor(model)
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
