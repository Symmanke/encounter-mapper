from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout)
from PyQt5.QtCore import (Qt, QPoint)
from PyQt5.QtGui import (QPainter, QPolygon, QPen, QBrush, QColor)

from EMTileModel import EMTileModel


class EMMapWidget(QWidget):
    def __init__(self):
        super(EMMapWidget, self).__init__()
        self.setMinimumHeight(500)
        self.setMinimumWidth(500)
        self.label = QLabel("TBD")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.grid = [
            [
                EMTileModel("Sample"),
                EMTileModel("Sample")
            ],
            [
                EMTileModel("Sample"),
                EMTileModel("Sample")
            ]
        ]

        self.gridStyles = [(4, 4, Qt.black), (2, 2, Qt.black), (1, 1, Qt.black)]

        self.scale = 200
        self.gridScale = 4

        # pen4 = QPen(QColor.black)
        # # pen4.setColor(QColor.black)
        # pen4.setWidth(4)
        #
        # pen2 = QPen()
        # pen2.setColor(QColor.black)
        # pen2.setWidth(2)
        #
        # pen1 = QPen()
        # pen1.setColor(QColor.black)
        # pen1.setWidth(1)

    def mousePressEvent(self, QMouseEvent):
        point = QMouseEvent.pos()
        self.label.setText("clicked at {}, {}".format(point.x(), point.y()))

    def mouseReleaseEvent(self, QMouseEvent):
        point = QMouseEvent.pos()
        self.label.setText("released at {}, {}".format(point.x(), point.y()))

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        painter.setPen(Qt.blue)
        self.paintTiles(painter)
        self.paintGrid(painter)

    def paintTiles(self, painter):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                tileSet = self.grid[y][x]
                painter.setPen(tileSet.backgroundColor)
                painter.setBrush(tileSet.backgroundColor)
                painter.drawRect(x*self.scale, y*self.scale, self.scale, self.scale)

                painter.setPen(tileSet.foregroundColor)
                painter.setBrush(tileSet.foregroundColor)
                points = tileSet.generatePointOffset(x, y, self.scale)
                foregroundPoly = QPolygon(points)
                painter.drawPolygon(foregroundPoly)

    def paintGrid(self, painter):
        gridOffset = self.scale / self.gridScale
        height = self.scale * len(self.grid)
        width = self.scale * len(self.grid[0])

        for y in range(len(self.grid) * self.gridScale + 1):
            for style in self.gridStyles:
                if y % self.gridScale == style[0]:
                    painter.setPen(style[2])
                    painter.pen().setWidth(style[1])
                    break
            painter.drawLine(0, y * gridOffset, width, y * gridOffset)

        for x in range(len(self.grid[0]) * self.gridScale + 1):
            for style in self.gridStyles:
                if x % self.gridScale == style[0]:
                    painter.setPen(style[2])
                    painter.pen().setWidth(style[1])
                    break

            painter.drawLine(x * gridOffset, 0, x * gridOffset, height)
