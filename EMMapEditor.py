from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QTabWidget, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

from EMModelPicker import EMModelPicker
from EMTileEditor import TileEditor, TilePreviewWidget
from EMModel import TileModel, GroupModel, MapModel
from EMHelper import ModelManager
from EMGroupEditor import GroupEditor, GroupPreview
from EMBaseClasses import EMModelGraphics


class MapEditor(QWidget):

    def __init__(self):
        # Set ui in here
        super(MapEditor, self).__init__()
        layout = QHBoxLayout()
        # Create a tab widget
        self.mapEditGraphics = MapEditorGraphics(MapModel())
        self.tabWidget = QTabWidget()
        self.tabWidget.currentChanged.connect(
            self.mapEditGraphics.updateSelectedTab)
        self.tilePicker = EMModelPicker(ModelManager.TileName, TileModel,
                                        TileEditor, TilePreviewWidget)
        self.tilePicker.selectedModel.connect(
            self.mapEditGraphics.updateSelectedObject)
        self.groupPicker = EMModelPicker(ModelManager.GroupName, GroupModel,
                                         GroupEditor, GroupPreview)
        self.groupPicker.selectedModel.connect(
            self.mapEditGraphics.updateSelectedObject)

        self.tabWidget.addTab(self.tilePicker, "Tiles")
        self.tabWidget.addTab(self.groupPicker, "Groups")
        self.tabWidget.addTab(QWidget(), "Objects")
        self.tabWidget.addTab(QWidget(), "Notes")

        layout.addWidget(self.mapEditGraphics)
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)


class MapEditorGraphics(EMModelGraphics):
    def __init__(self, model=None):
        super(MapEditorGraphics, self).__init__(
            model, model.getNumRows(), model.getNumCols())
        self.openTab = 0
        self.selectedObject = [-1, -1, -1, -1]
        self.selectedGroup = None
        # Need for later, when I introduce objects (unless I decide to make)
        # everything grid based instead for simplicity's sake
        self.mousePosition = (-1, -1)

    def updateSelectedTab(self, index):
        self.openTab = index

    def updateSelectedObject(self, uid):
        self.selectedObject[self.openTab] = uid
        if self.openTab == 1 and uid > -1:
            group = ModelManager.fetchByUid(ModelManager.GroupName,
                                            self.selectedObject[1])
            if group is None:
                self.selectedGroup = None
            else:
                self.selectedGroup = GroupModel.createModelTransform(
                    group, self.pOptions)

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        gridModel = None if self.model is None else self.model.getGridModel()
        if(self.model is not None):
            painter.setBrush(Qt.black)
            painter.setPen(Qt.black)
            painter.drawRect(0, 0, self.width, self.height)
            grid = gridModel.getTileGrid()
            for y in range(gridModel.getNumRows()):
                for x in range(gridModel.getNumCols()):
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
                                self.drawTile(painter, x, y, cachedTM, tile)
            if self.mouseIndex != (-1, -1) and not self.mousePressed:
                if self.openTab == 0 and self.selectedObject[0] != -1:
                    self.drawPreviewTileSingle(painter)
                elif self.openTab == 1 and self.selectedObject[1] != -1:
                    self.drawPreviewTileGroup(painter)

    def drawPreviewTileSingle(self, painter):
        if self.selectedObject[0] not in self.modelList:
            self.updateModelList(self.selectedObject[0])
        # draw single object
        model = self.modelList[self.selectedObject[0]]
        self.drawTile(
            painter, self.mouseIndex[0],
            self.mouseIndex[1], model, self.pOptions, True)

    def drawPreviewTileGroup(self, painter):
        tGrid = self.selectedGroup.getTileGrid()
        for y in range(len(tGrid)):
            for x in range(len(tGrid[y])):
                tile = tGrid[y][x]
                if tile[0] not in self.modelList:
                    self.updateModelList(tile[0])
                # draw single object
                model = self.modelList[tile[0]]
                self.drawTile(
                    painter, self.mouseIndex[0] + x,
                    self.mouseIndex[1] + y, model, tile, True)

        # def keyPressEvent(self, event):
        #     if self.preview:
        #         event.ignore()
        #     else:
        #         key = event.key() | int(event.modifiers())
        #         if key in self.keyBindings:
        #             command = self.keyBindings[key]
        #             command[0](command[1])
        #
        # def mousePressEvent(self, QMouseEvent):
        #     if self.preview:
        #         QMouseEvent.ignore()
        #     else:
        #         if QMouseEvent.button() & Qt.LeftButton:
        #             self.mousePressed = True
        #             if self.mouseIndex != (-1, -1):
        #                 self.model.setTileForIndex(
        #                     self.mouseIndex[0], self.mouseIndex[1],
        #                     self.getPOptions())
        #                 # perform stuff
        #                 self.repaint()
        #

    def mouseMoveEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            self.setFocus()
            self.mousePosition = self.mousePosScale(QMouseEvent.pos())
            prevIndex = self.mouseIndex
            self.mouseIndex = self.calcMouseIndex(QMouseEvent.pos())
            if prevIndex != self.mouseIndex:
                if self.mousePressed and self.mouseIndex != (-1, -1):
                    self.model.setTileForIndex(
                        self.mouseIndex[0], self.mouseIndex[1],
                        self.getPOptions())
                self.repaint()
            if self.openTab == 2 and self.selectedObject[2] > -1:
                self.repaint()

    def mouseReleaseEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            self.mousePressed = False


def printRot(rot, grid, numRows, numCols):
    tGrid = []
    if rot == 0:
        tGrid = grid
    if rot == 1:
        for y in range(numCols):
            tGrid.append([])
            for x in range(numRows-1, -1, -1):
                tGrid[-1].append(grid[x][y])
    elif rot == 2:
        for y in range(numRows-1, -1, -1):
            tGrid.append([])
            for x in range(numCols-1, -1, -1):
                tGrid[-1].append(grid[y][x])
    elif rot == 3:
        for y in range(numCols-1, -1, -1):
            tGrid.append([])
            for x in range(numRows):
                tGrid[-1].append(grid[x][y])
    print(tGrid)


def doMath(numRows=2, numCols=3):
    num = 1
    grid = []
    for y in range(numRows):
        grid.append([])
        for x in range(numCols):
            grid[-1].append(num)
            num += 1

    for i in range(4):
        print("option={}".format(i))
        printRot(i, grid, numRows, numCols)


def main():

    # doMath()
    app = QApplication([])

    mainWidget = MapEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
