from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import (QPainter, QPolygon)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,  QLabel,
                             QLineEdit, QPushButton, QSpinBox, QWidget,
                             QListWidget, QDialog, QVBoxLayout)

from EMPaletteEditor import EMPaletteEditor
from EMTileEditorModel import EMTileEditorModel


class TileGroupEditor(QWidget):
    def __init__(self):
        """Todo"""


class TileGroupPreviewWidget(QWidget):
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

    mainWidget = TileGroupEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
