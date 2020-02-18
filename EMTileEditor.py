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
from EMModel import TileModel, GeneratedTextureModel
from EMBaseClasses import EMModelEditor, EMModelGraphics, EMModelPicker
from EMHelper import EMImageGenerator, ModelManager
from EMTextureEditor import TextureEditor, TexturePreview


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
        self.selectedShape = -1
        self.selectedPoint = -1
        self.selectedTexture = -1
        self.previewWidget = TilePreviewWidget()
        self.previewWidget.pointSelected.connect(self.setSelectedPoint)

        self.textureList = EMModelPicker(
            ModelManager.TextureName, GeneratedTextureModel,
            TextureEditor, TexturePreview)
        self.textureList.selectedModel.connect(self.setSelectedTexture)
        self.shapeList = QListWidget()
        self.shapeList.itemClicked.connect(self.shapeClicked)
        self.shapePointList = QListWidget()
        self.shapePointList.itemClicked.connect(self.pointClicked)
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

        self.addShapeBtn = QPushButton("Add Shape")
        self.addShapeBtn.clicked.connect(self.addShape)
        self.delShapeBtn = QPushButton("Del Shape")
        # self.delShapeBtn.clicked.connect(self.delShape)
        self.addPointBtn = QPushButton("Add Point")
        self.addPointBtn.clicked.connect(self.addPoint)
        self.delPointBtn = QPushButton("Del Point")
        self.delPointBtn.clicked.connect(self.deletePoint)
        self.upPointBtn = QPushButton("Move Point Up")
        self.upPointBtn.clicked.connect(self.moveUpPoint)
        self.downPointBtn = QPushButton("Move Point Down")
        self.downPointBtn.clicked.connect(self.moveDownPoint)

        self.shapeTextureBtn = QPushButton("Set Shape Texture")
        self.shapeTextureBtn.clicked.connect(self.setCurShapeTexture)
        self.bgTextureBtn = QPushButton("Set BG Texture")
        self.bgTextureBtn.clicked.connect(self.setBgTexture)

        self.buttonHolder = QWidget()
        bhLayout = QGridLayout()
        # bhLayout.addWidget(self.addShapeBtn, 0, 0, 1, 3)
        # bhLayout.addWidget(self.delShapeBtn, 0, 3, 1, 3)
        bhLayout.addWidget(self.addPointBtn, 1, 0, 1, 3)
        bhLayout.addWidget(self.delPointBtn, 1, 3, 1, 3)
        bhLayout.addWidget(self.upPointBtn, 2, 0, 1, 3)
        bhLayout.addWidget(self.downPointBtn, 2, 3, 1, 3)
        bhLayout.addWidget(self.shapeTextureBtn, 3, 0, 1, 3)
        bhLayout.addWidget(self.bgTextureBtn, 3, 3, 1, 3)
        bhLayout.addWidget(self.cwBtn, 4, 0, 1, 3)
        bhLayout.addWidget(self.ccwBtn, 5, 0, 1, 3)
        bhLayout.addWidget(self.hfBtn, 4, 3, 1, 3)
        bhLayout.addWidget(self.vfBtn, 5, 3, 1, 3)
        self.buttonHolder.setLayout(bhLayout)

        layout.addWidget(self.previewWidget, 0, 0, 7, 1)
        layout.addWidget(QLabel("Tile Name:"), 0, 1)
        layout.addWidget(self.modelNameEdit, 0, 2, 1, 3)
        layout.addWidget(QLabel("X:"), 1, 1)
        layout.addWidget(self.pointXEdit, 1, 2)
        layout.addWidget(QLabel("Y:"), 1, 3)
        layout.addWidget(self.pointYEdit, 1, 4)
        layout.addWidget(self.shapeList, 2, 1, 2, 2)
        layout.addWidget(self.shapePointList, 2, 3, 4, 2)
        layout.addWidget(self.addShapeBtn, 4, 1, 1, 2)
        layout.addWidget(self.delShapeBtn, 5, 1, 1, 2)
        layout.addWidget(self.buttonHolder, 6, 1, 1, 4)

        # buttons to add fhe model
        acbtn = QWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.applyBtn)
        hbox.addWidget(self.cancelBtn)
        acbtn.setLayout(hbox)
        layout.addWidget(acbtn, 7, 0, 1, 5)

        layout.addWidget(self.textureList, 0, 5, 8, 1)

        self.setLayout(layout)
        self.previewWidget.setModel(self.model)
        self.updateUI()

    def addShape(self):
        self.model.addShape()

    def addPoint(self):
        if self.selectedShape > -1:
            self.model.addPoint(self.selectedShape, self.selectedPoint,
                                self.pointXEdit.value(),
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
        self.model.updatePoint(self.selectedShape, self.selectedPoint,
                               self.pointXEdit.value(),
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

    def shapeClicked(self):
        self.setSelectedShape(self.shapeList.currentRow())

    def pointClicked(self):
        self.setSelectedPoint(self.shapePointList.currentRow())

    def setSelectedShape(self, index):
        self.selectedShape = index
        self.selectedPoint = -1
        self.previewWidget.setSelectedShape(index)
        self.previewWidget.setSelectedPoint(-1)
        self.updateUI()

    def setSelectedPoint(self, index):
        self.selectedPoint = index
        self.previewWidget.setSelectedPoint(index)
        self.updateUI()

    def setSelectedTexture(self, txtUid):
        self.selectedTexture = txtUid

    def setCurShapeTexture(self):
        if self.selectedTexture > -1:
            self.model.setShapeTexture(self.selectedShape, self.selectedTexture)

    def setBgTexture(self):
        if self.selectedTexture > -1:
            self.model.setBgTexture(self.selectedTexture)

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
        self.model.setSelectedIndex(self.shapePointList.currentRow())

    def updateUI(self):
        self.reloadLists()
        self.previewWidget.repaint()
        self.updateCurrentValues()
        self.modelNameEdit.setText(self.model.getName())
        # self.enableButtons()

    def reloadLists(self):
        self.shapeList.clear()
        self.shapePointList.clear()
        shapes = self.model.getShapes()
        for i in range(len(shapes)):
            self.shapeList.addItem("Shape {}".format(i+1))

        if self.selectedShape > -1:
            shapePoints = shapes[self.selectedShape][1]
            for i in range(len(shapePoints)):
                point = shapePoints[i]
                self.shapePointList.addItem("{}. ({}, {})"
                                            .format(i+1, point[0], point[1]))
            self.shapeList.setCurrentRow(self.selectedShape)
            if self.selectedPoint > -1:
                self.shapePointList.setCurrentRow(self.selectedPoint)

        # TODO
        # self.shapePointList.setCurrentRow(self.model.getSelectedIndex())

    def updateCurrentValues(self):
        if self.selectedShape > -1 and self.selectedPoint > -1:
            point = (self.model.getShape(self.selectedShape)[1]
                     [self.selectedPoint])
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
        self.selectedShape = -1
        self.selectedPoint = -1

    # Class method for constructing different ones
    @classmethod
    def previewWidget(cls, model):
        return cls(50, 0, model, True)

    def setModel(self, model):
        self.model = model

    def setSelectedShape(self, shape):
        self.selectedShape = shape

    def setSelectedPoint(self, point):
        self.selectedPoint = point

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if(self.model is not None):
            self.modelImage = EMImageGenerator.genImageFromModel(self.model)
            # tempImg = EMImageGenerator.genImageFromModel(
            #     self.model)
            # TODO: Convert to Pixmap
            painter.drawImage(10, 10,
                              self.modelImage.scaled(
                                  self.tileSize, self.tileSize))
            EMImageGenerator.drawGrid(painter, 1, 1, 10, 10, self.tileSize)

            # self.drawTile(painter, 0, 0, self.model)
            if not self.preview and self.selectedShape > -1:
                points = self.model.generateShapeOffset(
                    self.selectedShape, 0, 0, self.tileSize,
                    self.xOffset, self.yOffset)
                self.drawPointObjects(painter, points)

    def drawPointObjects(self, painter, points):
        painter.setPen(Qt.black)
        r = 10
        d = 2*r
        for i in range(len(points)):
            point = points[i]
            if i != self.selectedPoint:
                painter.setBrush(Qt.white)
                painter.drawEllipse(point.x()-r, point.y()-r, d, d)
        painter.setBrush(Qt.red)

        if self.selectedPoint >= 0:
            # draw white point at the end so it always shows up
            selectedPoint = points[self.selectedPoint]
            painter.drawEllipse(selectedPoint.x()-r, selectedPoint.y()-r, d, d)

    def mousePressEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            mp = self.mousePosScale(QMouseEvent.pos())
            # check if selected one is clicked first
            if self.selectedShape != -1:
                shapePoints = self.model.getShape(self.selectedShape)[1]
                if self.selectedPoint > -1 and self.distanceHelper(
                        mp, shapePoints[self.selectedPoint]) <= 100:
                    self.binkedPoint = True
                else:
                    for i in range(len(shapePoints)):
                        point = shapePoints[i]
                        if self.distanceHelper(mp, point) <= 100:
                            self.binkedPoint = True
                            self.pointSelected.emit(i)
                            break

    def mouseMoveEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            if self.binkedPoint:
                mp = self.mousePosScale(QMouseEvent.pos())
                print("updating shape {}".format(self.selectedShape))
                self.model.updatePoint(self.selectedShape, self.selectedPoint,
                                       mp[0], mp[1])

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
    model = TileModel()
    mainWidget = TileEditor(model)
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
