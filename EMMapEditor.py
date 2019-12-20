from PyQt5.QtWidgets import (QApplication,
                             QGridLayout, QTabWidget, QWidget, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter

from EMTileEditor import TileEditor, TilePreviewWidget
from EMModel import TileModel, GroupModel, MapModel
from EMHelper import ModelManager
from EMGroupEditor import GroupEditor, GroupPreview
from EMBaseClasses import EMModelGraphics, EMModelPicker
from EMNotesTab import NotesTab


class MapEditor(QWidget):

    def __init__(self, model=None):
        # Set ui in here
        super(MapEditor, self).__init__()
        layout = QGridLayout()
        # Create a tab widget
        self.model = MapModel() if model is None else model
        self.filePathOfModel = None
        self.mapEditGraphics = MapEditorGraphics(self.model)
        self.mapEditGraphics.updatePreview.connect(self.updateUI)
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

        self.notesWidget = NotesTab()
        self.notesWidget.setCurrentEditor(self)

        self.tabWidget.addTab(self.tilePicker, "Tiles")
        self.tabWidget.addTab(self.groupPicker, "Groups")
        self.tabWidget.addTab(QWidget(), "Objects")
        self.tabWidget.addTab(self.notesWidget, "Notes")

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

        layout.addWidget(self.mapEditGraphics, 0, 0)
        layout.addWidget(self.tabWidget, 0, 1, 2, 1)
        layout.addWidget(self.btnGroup, 1, 0)
        self.setLayout(layout)

    def getModel(self):
        return self.model

    def setModel(self, model):
        self.model = model
        self.mapEditGraphics.setModel(model)
        self.model.modelUpdated.connect(self.updateUI)
        self.updateUI()

    def getFilePath(self):
        return self.filePathOfModel

    def setFilePath(self, path):
        self.filePathOfModel = path

    def rotateTileMapCW(self):
        self.mapEditGraphics.transformS("cw")

    def rotateTileMapCCW(self):
        self.mapEditGraphics.transformS("ccw")

    def flipTileMapH(self):
        self.mapEditGraphics.transformS("h")

    def flipTileMapV(self):
        self.mapEditGraphics.transformS("v")

    def addGroupRow(self):
        self.model.addRow()

    def addGroupCol(self):
        self.model.addCol()

    def delGroupRow(self):
        self.model.delRow()

    def delGroupCol(self):
        self.model.delCol()

    """
    *------------*
    |Note Methods|
    *------------*
    """

    def getNotes(self):
        return self.model.getMapNotes()

    def addNote(self, note, index=-1):
        self.model.addMapNote(note, index)
        self.notesWidget.populateList(self.model.getMapNotes())

    def updateNote(self, note, index):
        self.model.updateMapNote(note, index)
        self.notesWidget.populateList(self.model.getMapNotes())

    def updateNotePosition(self, index, x, y):
        note = self.model.getMapNotes()[index]
        note.setPos(x, y)
        self.updateMapNote(note, index)

    """
    *----------*
    |UI Methods|
    *----------*
    """

    def updateUI(self):
        # update Buttons
        options = self.mapEditGraphics.getSOptions()
        self.hfBtn.setChecked(options[1])
        self.vfBtn.setChecked(options[2])
        self.btnGroup.repaint()
        # self.modelNameEdit.setText(self.model.getName())
        # update the preview
        # self.mapEditGraphics.calculateOffsets()
        self.mapEditGraphics.repaint()


class MapEditorGraphics(EMModelGraphics):

    updatePreview = pyqtSignal()

    def __init__(self, model=None):
        super(MapEditorGraphics, self).__init__(
            model, model.getNumRows(), model.getNumCols())
        self.openTab = 0
        self.selectedGroup = None
        # Need for later, when I introduce objects (unless I decide to make)
        # everything grid based instead for simplicity's sake
        self.mousePosition = (-1, -1)

    def setModel(self, model):
        self.model = model
        self.rows = model.getNumRows()
        self.cols = model.getNumCols()
        self.repaint()

    def updateSelectedTab(self, index):
        self.openTab = index

    def updateSelectedObject(self, uid, objNum=-1):
        self.selectedObject[self.openTab] = uid
        tab = self.openTab if objNum == -1 else objNum
        if tab == 1 and uid > -1:
            group = ModelManager.fetchByUid(ModelManager.GroupName,
                                            self.selectedObject[1])
            if group is None:
                self.selectedGroup = None
            else:
                self.selectedGroup = GroupModel.createModelTransform(
                    group, self.sOptions)

    def indexAlignedGroup(self):
        midIndex = (max(0, self.mouseIndex[0] -
                        int(self.selectedGroup.getNumCols()/2)),
                    max(0, self.mouseIndex[1] -
                        int(self.selectedGroup.getNumRows()/2)))

        edits = [0, 0]
        gmEnd = (midIndex[0] + self.selectedGroup.getNumCols(),
                 midIndex[1] + self.selectedGroup.getNumRows())

        edits[0] = min(0, self.numCols - gmEnd[0])
        edits[1] = min(0, self.numRows - gmEnd[1])

        return (midIndex[0] + edits[0], midIndex[1] + edits[1])

    def transformS(self, type):
        if type == "cw":
            self.sOptions[0] = (self.sOptions[0] + 1) % 4
        elif type == "ccw":
            self.sOptions[0] = (self.sOptions[0] + 3) % 4
        elif type == "h":
            self.sOptions[1] = not self.sOptions[1]
        elif type == "v":
            self.sOptions[2] = not self.sOptions[2]
        print("--Options Updated--")
        print(self.sOptions)
        print(self.selectedObject)
        if self.selectedObject[1] != -1:
            self.updateSelectedObject(self.selectedObject[1], 1)
        self.updatePreview.emit()

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if(self.model is not None):
            painter.setBrush(Qt.black)
            painter.setPen(Qt.black)
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
        print(self.selectedObject[0])
        self.drawTile(
            painter, self.mouseIndex[0],
            self.mouseIndex[1], model, self.sOptions, True)

    def drawPreviewTileGroup(self, painter):
        tGrid = self.selectedGroup.getTileGrid()
        groupIndex = self.indexAlignedGroup()
        for y in range(len(tGrid)):
            for x in range(len(tGrid[y])):
                tile = tGrid[y][x]
                if(tile[0] > 0):
                    if tile[0] not in self.modelList:
                        self.updateModelList(tile[0])
                    # draw single object
                    model = self.modelList[tile[0]]
                    self.drawTile(
                        painter, groupIndex[0] + x,
                        groupIndex[1] + y, model,
                        (tile[1], tile[2], tile[3]), True)

        # def keyPressEvent(self, event):
        #     if self.preview:
        #         event.ignore()
        #     else:
        #         key = event.key() | int(event.modifiers())
        #         if key in self.keyBindings:
        #             command = self.keyBindings[key]
        #             command[0](command[1])
        #
    def mousePressEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            if QMouseEvent.button() & Qt.LeftButton:
                self.mousePressed = True
                if self.mouseIndex != (-1, -1):
                    if self.openTab == 0 and self.selectedObject[0] != -1:
                        tile = (self.selectedObject[0],
                                self.sOptions[0], self.sOptions[1],
                                self.sOptions[2])
                        self.model.setTileForIndex(
                            self.mouseIndex[0], self.mouseIndex[1], tile)
                        self.repaint()
                    elif self.openTab == 1 and self.selectedObject[1] != -1:
                        print("Adding...")
                        groupIndex = self.indexAlignedGroup()
                        gGrid = self.selectedGroup.getTileGrid()
                        for y in range(self.selectedGroup.getNumRows()):
                            for x in range(self.selectedGroup.getNumCols()):
                                tile = gGrid[y][x]
                                print(tile)
                                self.model.setTileForIndex(
                                    groupIndex[0] + x, groupIndex[1] + y,
                                    tile)
                        self.repaint()

                        # perform stuff

    def mouseMoveEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            self.setFocus()
            self.mousePosition = self.mousePosScale(QMouseEvent.pos())
            prevIndex = self.mouseIndex
            self.mouseIndex = self.calcMouseIndex(QMouseEvent.pos())
            if prevIndex != self.mouseIndex:
                if (self.mousePressed and self.mouseIndex != (-1, -1)
                        and self.openTab == 0):
                    tile = [self.selectedObject[0], self.sOptions[0],
                            self.sOptions[1], self.sOptions[2]]
                    self.model.setTileForIndex(
                        self.mouseIndex[0], self.mouseIndex[1],
                        tile)
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
        # print("option={}".format(i))
        printRot(i, grid, numRows, numCols)


def main():

    # doMath()
    app = QApplication([])

    mainWidget = MapEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
