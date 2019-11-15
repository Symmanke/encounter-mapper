from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import (QPainter, QPolygon)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,  QLabel,
                             QLineEdit, QPushButton, QSpinBox, QWidget,
                             QListWidget)

from EMPaletteEditor import EMPaletteEditor
from EMTileEditorModel import EMTileEditorModel


class EMTileEditor(QWidget):
    selectingColor = ""
    paletteEditor = None

    addModel = pyqtSignal()
    cancelModel = pyqtSignal()

    def __init__(self):
        super(EMTileEditor, self).__init__()
        layout = QGridLayout()
        self.previewWidget = EMTilePreviewWidget()
        self.tileName = QLineEdit()
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
        layout.addWidget(self.tileName, 0, 2, 1, 3)
        layout.addWidget(QLabel("X:"), 1, 1)
        layout.addWidget(self.pointXEdit, 1, 2)
        layout.addWidget(QLabel("Y:"), 1, 3)
        layout.addWidget(self.pointYEdit, 1, 4)
        layout.addWidget(self.tilePointList, 2, 1, 4, 3)
        layout.addWidget(self.buttonHolder, 6, 1, 1, 4)

        # buttons to add fhe model
        self.addModelBtn = QPushButton("Apply")
        self.addModelBtn.clicked.connect(self.addTile)
        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.cancelTile)
        acbtn = QWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.addModelBtn)
        hbox.addWidget(self.cancelBtn)
        acbtn.setLayout(hbox)
        layout.addWidget(acbtn, 7, 0, 1, 5)

        self.setLayout(layout)

        self.tileModel = EMTileEditorModel("DEFAULT", [])
        self.tileModel.modelUpdated.connect(self.updateUI)
        self.previewWidget.setModel(self.tileModel)

        self.tileModel.addPoint(50, 50)
        self.tilePointList.setCurrentRow(0)

    def addPoint(self):
        self.tileModel.addPoint(self.pointXEdit.value(),
                                self.pointYEdit.value())

    def deletePoint(self):
        self.tileModel.deleteSelectedPoint()

    def moveUpPoint(self):
        swap = self.tileModel.getSelectedIndex() - 1
        if swap < 0:
            swap = len(self.tileModel.getPoints())-1
        self.tileModel.swapPointSelected(swap)

    def moveDownPoint(self):
        swap = self.tileModel.getSelectedIndex() + 1
        if swap >= len(self.tileModel.getPoints()):
            swap = 0
        self.tileModel.swapPointSelected(swap)

    def updatePointPosition(self):
        index = self.tilePointList.currentRow()
        self.tileModel.updatePoint(index, self.pointXEdit.value(),
                                   self.pointYEdit.value())

    def rotCW(self):
        self.tileModel.transformRotate(True)

    def rotCCW(self):
        self.tileModel.transformRotate(False)

    def flipH(self):
        self.tileModel.transformFlip(True)

    def flipV(self):
        self.tileModel.transformFlip(False)

    def setFGColor(self):
        fg = self.tileModel.getFgColor()
        self.selectingColor = "fg"
        self.paletteEditor = EMPaletteEditor(fg.red(), fg.green(), fg.blue())
        self.paletteEditor.colorApplied.connect(self.applyColorChange)
        self.paletteEditor.colorCanceled.connect(self.cancelColorChange)
        self.paletteEditor.show()

    def setBGColor(self):
        bg = self.tileModel.getFgColor()
        self.selectingColor = "bg"
        self.paletteEditor = EMPaletteEditor(bg.red(), bg.green(), bg.blue())
        self.paletteEditor.colorApplied.connect(self.applyColorChange)
        self.paletteEditor.colorCanceled.connect(self.cancelColorChange)
        self.paletteEditor.show()

    def applyColorChange(self, r, g, b):
        if self.selectingColor == "bg":
            self.tileModel.setBgColor(r, g, b)
        elif self.selectingColor == "fg":
            self.tileModel.setFgColor(r, g, b)
        self.selectingColor = ""
        self.paletteEditor = None

    def cancelColorChange(self):
        self.selectingColor = ""
        self.paletteEditor = None

    def setModel(self, model):
        self.tileModel = model
        self.tileModel.modelUpdated.connect(self.updateUI)
        self.previewWidget.setModel(model)
        self.updateUI()

    def updateCurrentItem(self):
        self.tileModel.setSelectedIndex(self.tilePointList.currentRow())

    def updateUI(self):
        self.reloadPointList()
        self.previewWidget.repaint()
        self.updateCurrentValues()
        self.enableButtons()

    def reloadPointList(self):
        self.tilePointList.clear()
        points = self.tileModel.getPoints()
        for i in range(len(points)):
            point = points[i]
            self.tilePointList.addItem("{}. ({}, {})"
                                       .format(i+1, point[0], point[1]))
        self.tilePointList.setCurrentRow(self.tileModel.getSelectedIndex())

    def updateCurrentValues(self):
        currentIndex = self.tileModel.getSelectedIndex()
        if(currentIndex != -1):
            point = self.tileModel.getPoints()[currentIndex]
            self.pointXEdit.setValue(point[0])
            self.pointYEdit.setValue(point[1])
        else:
            self.pointXEdit.setValue(50)
            self.pointYEdit.setValue(50)

    def enableButtons(self):
        num = self.tileModel.getNumPoints()
        self.delPointBtn.setEnabled(num > 0)
        self.upPointBtn.setEnabled(num > 1)
        self.downPointBtn.setEnabled(num > 1)
        self.cwBtn.setEnabled(num > 0)
        self.ccwBtn.setEnabled(num > 0)
        self.hfBtn.setEnabled(num > 0)
        self.vfBtn.setEnabled(num > 0)

        self.buttonHolder.repaint()

    def addTile(self):
        """Todo"""
        self.addModel.emit()

    def cancelTile(self):
        """Todo"""
        self.cancelModel.emit()

    def getCurrentModel(self):
        return self.tileModel


class EMTilePreviewWidget(QWidget):
    """
    widget that displays the preview of the object.
    """

    pointSelected = pyqtSignal(int)
    pointDragged = pyqtSignal(int, int)
    tileModel = None
    binkedPoint = False
    isPreview = False
    borderOffset = 10
    size = 500

    def __init__(self, size=500, border=10, preview=False, model=None):
        super(EMTilePreviewWidget, self).__init__()
        self.size = size
        self.borderOffset = border
        self.setMinimumHeight(self.size+(self.borderOffset*2))
        self.setMinimumWidth(self.size+(self.borderOffset*2))
        self.isPreview = preview
        self.tileModel = model

    # Class method for constructing different ones
    @classmethod
    def previewWidget(cls, model):
        return cls(50, 0, True, model)

    def setModel(self, model):
        self.tileModel = model

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if(self.tileModel is not None):
            # Set background
            painter.setBrush(self.tileModel.getBgColor())
            painter.drawRect(self.borderOffset, self.borderOffset,
                             self.size, self.size)
            # Grab points for drawing of polygons + other stuff
            points = self.tileModel.generatePointOffset(
                0, 0, self.size, self.borderOffset, self.borderOffset)

            # draw FG if possible
            if len(self.tileModel.getPoints()) > 1:
                self.drawForegroundPoly(painter, points)
            if not self.isPreview:
                self.drawPointObjects(painter, points)

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

    def mousePressEvent(self, QMouseEvent):
        if not self.isPreview:
            mp = self.mousePosScale(QMouseEvent.pos())
            # check if selected one is clicked first
            if self.tileModel.getSelectedIndex() != -1:
                if self.distanceHelper(mp,
                                       self.tileModel.getSelectedPoint()) <= 100:
                    self.binkedPoint = True
                else:
                    points = self.tileModel.getPoints()
                    for i in range(len(points)):
                        point = points[i]
                        print("index: {}, MP: {}, P: {}".format(i, mp, point))
                        if self.distanceHelper(mp, point) <= 100:
                            self.binkedPoint = True
                            self.tileModel.setSelectedIndex(i)
                            break

    def mouseMoveEvent(self, QMouseEvent):
        if not self.isPreview:
            if self.binkedPoint:
                mp = self.mousePosScale(QMouseEvent.pos())
                self.tileModel.setSelectedPoint(mp[0], mp[1])

    def mouseReleaseEvent(self, QMouseEvent):
        if not self.isPreview:
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

    mainWidget = EMTileEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
