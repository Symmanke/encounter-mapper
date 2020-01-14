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

from PyQt5.QtWidgets import (QApplication, QLabel, QScrollArea,
                             QGridLayout, QTabWidget, QWidget, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPalette

from EMTileEditor import TileEditor, TilePreviewWidget
from EMModel import TileModel, GroupModel, MapModel
from EMHelper import ModelManager, EMImageGenerator
from EMGroupEditor import GroupEditor, GroupPreview
from EMBaseClasses import EMModelGraphics, EMModelPicker
from EMNotesTab import NotesTab


class MapEditor(QWidget):
    """
    Editor to create maps from tiles, objects, and notes. This class primarily
    handles the context switches whenever a new tab is selected from the tab
    bar.
    """

    def __init__(self, model=None):
        # Set ui in here
        super(MapEditor, self).__init__()
        layout = QGridLayout()
        # Create a tab widget
        self.model = MapModel() if model is None else model
        self.model.modelUpdated.connect(self.updateUI)

        self.pressedItem = None
        self.filePathOfModel = None

        self.mapEditGraphics = MapEditorGraphics(self.model)
        self.mapEditGraphics.updatePreview.connect(self.updateUI)
        self.mapEditGraphics.selectedItem.connect(self.updateSelection)

        # Add Scrollable area for groupPreview
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.mapEditGraphics)
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setAlignment(Qt.AlignCenter)
        self.scrollArea.setMinimumWidth(500)
        self.scrollArea.setMinimumHeight(500)

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
        self.tabWidget.addTab(QLabel("Coming Soon"), "Objects")
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

        layout.addWidget(self.scrollArea, 0, 0)
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

    def updateSelection(self, tab, id):
        if tab == 3:
            self.notesWidget.setSelectedNote(id)

    """
    *------------*
    |Note Methods|
    *------------*
    """

    def getNotes(self):
        return self.model.getMapNotes()

    def addNote(self, note, index=-1, x=-1, y=-1):
        # Since this is a new note, begin in the center
        if x == -1 and y == -1:
            x = (self.model.getNumCols()*100)/2
            y = (self.model.getNumRows()*100)/2
        note.setPos(x, y)
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
        self.mapEditGraphics.calculateSize()
        self.mapEditGraphics.repaint()


class MapEditorGraphics(EMModelGraphics):

    """
    Graphical Representation of the mpap object. Similar to the Group Editor,
    but also contains means to interact with notes, etc.
    """

    updatePreview = pyqtSignal()

    def __init__(self, model=None):
        super(MapEditorGraphics, self).__init__(
            model, model.getNumRows(), model.getNumCols())
        self.openTab = 0
        self.selectedModelImages = [None, None]
        self.selectedGroup = None
        # Need for later, when I introduce objects (unless I decide to make)
        # everything grid based instead for simplicity's sake
        self.mousePosition = (-1, -1)
        self.pressedItem = None

        self.keyBindings = {
            Qt.Key_R: (self.transformS, "cw"),
            Qt.Key_R | Qt.ShiftModifier: (self.transformS, "ccw"),
            Qt.Key_F: (self.transformS, "h"),
            Qt.Key_F | Qt.ShiftModifier: (self.transformS, "v"),
            Qt.Key_0: (self.updateZoom, 5),
            Qt.Key_Minus: (self.updateZoom, -5),
        }

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
        if self.selectedGroup is not None:
            self.selectedModelImages[1] = EMImageGenerator.genImageFromModel(
                self.selectedGroup)
        if self.selectedObject[0] is not None:
            self.selectedModelImages[0] = EMImageGenerator.genImageFromModel(
                ModelManager.fetchByUid(ModelManager.TileName,
                                        self.selectedObject[0]),
                {"transformOptions": self.sOptions})

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
        if self.selectedObject[1] != -1:
            self.updateSelectedObject(self.selectedObject[1], 1)
        if self.selectedObject[0] != -1:
            self.selectedModelImages[0] = EMImageGenerator.genImageFromModel(
                ModelManager.fetchByUid(ModelManager.TileName,
                                        self.selectedObject[0]),
                {"transformOptions": self.sOptions})
        self.updatePreview.emit()

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if(self.model is not None):
            nr = self.model.getNumRows()
            nc = self.model.getNumCols()

            img = EMImageGenerator.genImageFromModel(self.model)

            painter.drawImage(0, 0,
                              img.scaled(self.width, self.height))
            EMImageGenerator.drawGrid(painter, nc, nr,
                                      self.xOffset, self.yOffset,
                                      self.tileSize)

            if self.mouseIndex != (-1, -1) and not self.mousePressed:
                if self.openTab == 0 and self.selectedObject[0] != -1:
                    self.drawPreviewTileSingle(painter)
                elif self.openTab == 1 and self.selectedObject[1] != -1:
                    self.drawPreviewTileGroup(painter)

            # Draw the notes
            index = 1
            for note in self.model.getMapNotes():
                np = note.getPos()
                note.drawNoteIcon(painter, np[0]-12, np[1]-12, 25, index)
                index += 1

    def drawPreviewTileSingle(self, painter):
        if self.selectedModelImages[0] is not None:
            point = (int(self.xOffset + (self.tileSize * self.mouseIndex[0])),
                     int(self.yOffset + (self.tileSize * self.mouseIndex[1])))
            painter.drawImage(point[0], point[1],
                              self.selectedModelImages[0].scaled(
                self.tileSize, self.tileSize))

        # if self.selectedObject[0] not in self.modelList:
        #     self.updateModelList(self.selectedObject[0])
        # # draw single object
        # model = self.modelList[self.selectedObject[0]]
        # img = EMImageGenerator.genImageFromModel(model)
        # point = (int(self.xOffset + (self.tileSize * self.mouseIndex[0])),
        #          int(self.yOffset + (self.tileSize * self.mouseIndex[1])))
        # painter.drawImage(point[0], point[1],
        #                   img.scaled(self.tileSize, self.tileSize))

        EMImageGenerator.drawGrid(
            painter, 1, 1, point[0], point[1],
            self.tileSize, Qt.red)

    def drawPreviewTileGroup(self, painter):
        if self.selectedModelImages[1] is not None:
            model = self.selectedGroup
            groupIndex = self.indexAlignedGroup()
            point = (int(self.xOffset + (self.tileSize * groupIndex[0])),
                     int(self.yOffset + (self.tileSize * groupIndex[1])))

            painter.drawImage(point[0], point[1],
                              self.selectedModelImages[1].scaled(
                              self.tileSize * model.getNumCols(),
                              self.tileSize * model.getNumRows()))

            EMImageGenerator.drawGrid(
                painter, model.getNumCols(), model.getNumRows(),
                point[0], point[1], self.tileSize, Qt.red)

    def keyPressEvent(self, event):
        if self.preview:
            event.ignore()
        else:
            key = event.key() | int(event.modifiers())
            if key in self.keyBindings:
                command = self.keyBindings[key]
                command[0](command[1])

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
                    elif self.openTab == 3:
                        print("Checking the Notes Tab")
                        mp = self.mousePosition
                        notes = self.model.getMapNotes()
                        for i in range(len(notes)):
                            note = notes[i]
                            if self.distanceHelper(mp, note.getPos()) <= 1000:
                                self.pressedItem = (3, note)
                                self.selectedItem.emit(3, i+1)
                                break

    def mouseMoveEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            self.setFocus()
            self.mousePosition = self.mousePosScale(
                QMouseEvent.pos(), 0, 0, 200)
            prevIndex = self.mouseIndex
            self.mouseIndex = self.calcMouseIndex(QMouseEvent.pos())
            if self.openTab == 0 or self.openTab == 1:
                if prevIndex != self.mouseIndex:
                    if (self.mousePressed and self.mouseIndex != (-1, -1)
                            and self.openTab == 0):
                        tile = [self.selectedObject[0], self.sOptions[0],
                                self.sOptions[1], self.sOptions[2]]
                        self.model.setTileForIndex(
                            self.mouseIndex[0], self.mouseIndex[1],
                            tile)
                    self.repaint()
            else:
                if self.mousePressed and self.pressedItem is not None:
                    if self.pressedItem[0] == 3:
                        self.pressedItem[1].setPos(
                            self.mousePosition[0], self.mousePosition[1])
                    self.repaint()

    def mouseReleaseEvent(self, QMouseEvent):
        if self.preview:
            QMouseEvent.ignore()
        else:
            self.mousePressed = False
            self.pressedItem = None


def main():
    app = QApplication([])

    mainWidget = MapEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
