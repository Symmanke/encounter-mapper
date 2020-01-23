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

from PyQt5.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QListWidget,
                             QPushButton, QLabel, QTextEdit, QLineEdit,
                             QVBoxLayout, QComboBox, QDialog)

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap
from EMBaseClasses import EMEditor
from EMHelper import ModelManager, EMImageGenerator
from EMModel import NoteData


class NotesTab(QWidget):
    """
    Tab used to create and organize notes for a given map

    Unlike the other options, notes are based in text, not in pictures. Thus
    a unique picker is needed to sift through them. The notes tab allows users
    to create notes, switch between them, and open the editor to make changes.

    Notes will become more relevant once LaTex integration is complete

    Signals:
    ---------
    noteSelected(int):
    emitted whenever a new note index is selected. Used to update the map
    """
    noteSelected = pyqtSignal(int)

    def __init__(self, currentEditor=None):
        super(NotesTab, self).__init__()

        notes = [NoteData(0, "Hello World", "Here is a Sample Note")]

        self.currentEditor = currentEditor

        self.noteBadge = NoteBadge()
        self.noteTitle = QLineEdit("New Note")
        self.noteTitle.setReadOnly(True)
        self.editBtn = QPushButton("Edit")
        self.editBtn.clicked.connect(self.editNoteDialog)
        self.editBtn.setEnabled(False)

        titleGroup = QWidget()
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(self.noteBadge)
        titleLayout.addWidget(self.noteTitle)
        titleLayout.addWidget(self.editBtn)
        titleGroup.setLayout(titleLayout)

        self.noteDesc = QTextEdit("Note Description goes here")
        self.noteDesc.setReadOnly(True)

        self.noteList = QListWidget()
        self.noteList.currentItemChanged.connect(self.updateNoteSelected)
        self.populateList(notes)

        self.newBtn = QPushButton("New")
        self.newBtn.clicked.connect(self.newNoteDialog)
        self.delBtn = QPushButton("Del")
        self.delBtn.clicked.connect(self.deleteNote)
        self.delBtn.setEnabled(False)
        self.upBtn = QPushButton("UP")
        self.upBtn.clicked.connect(self.moveNoteUp)
        self.upBtn.setEnabled(False)
        self.downBtn = QPushButton("DOWN")
        self.downBtn.clicked.connect(self.moveNoteDown)
        self.downBtn.setEnabled(False)

        self.btnGroup = QWidget()
        btnLayout = QGridLayout()
        btnLayout.addWidget(self.newBtn, 0, 0)
        btnLayout.addWidget(self.delBtn, 1, 0)
        btnLayout.addWidget(self.upBtn, 0, 1)
        btnLayout.addWidget(self.downBtn, 1, 1)

        self.btnGroup.setLayout(btnLayout)

        layout = QVBoxLayout()
        layout.addWidget(titleGroup)
        layout.addWidget(self.noteDesc)
        layout.addWidget(self.noteList)
        layout.addWidget(self.btnGroup)
        self.setLayout(layout)

    def setCurrentEditor(self, editor):
        self.currentEditor = editor
        self.populateList(editor.getNotes())

    def populateList(self, notes):
        self.noteList.clear()
        self.noteList.addItem("(new)")
        for i in range(len(notes)):
            note = notes[i]
            self.noteList.addItem("{}: {}".format(i+1, note.getName()))

    def setSelectedNote(self, index):
        self.noteList.setCurrentRow(index)

    def updateNoteSelected(self, index):
        cr = self.noteList.currentRow()
        setNote = None
        if cr > 0:
            setNote = self.currentEditor.getNotes()[cr-1]
        self.noteBadge.setNote(setNote, cr)

        self.updateUI()
        self.noteSelected.emit(index)

    def newNoteDialog(self):
        self.noteDialog = QDialog()
        layout = QVBoxLayout()
        self.noteEditor = NoteEditor()
        self.noteEditor.applyEdit.connect(self.addNewNote)
        self.noteEditor.cancelEdit.connect(self.cancelNote)
        layout.addWidget(self.noteEditor)
        self.noteDialog.setLayout(layout)
        self.noteDialog.exec_()

    def editNoteDialog(self):
        pass

    def deleteNote(self):
        pass

    def moveNoteUp(self):
        pass

    def moveNoteDown(self):
        pass

    def addNewNote(self):
        newNote = self.noteEditor.getGeneratedNote()
        self.currentEditor.addNote(newNote)

        self.noteDialog.close()
        self.noteDialog = None
        self.noteEditor = None

    def cancelNote(self):
        self.noteDialog.close()
        self.noteDialog = None
        self.noteEditor = None

    def updateUI(self):
        cr = self.noteList.currentRow()
        if cr > 0:
            displayedNote = self.currentEditor.getNotes()[cr-1]
            self.noteTitle.setText(displayedNote.getName())
            self.noteDesc.setText(displayedNote.getDesc())
        else:
            self.noteTitle.setText("Create a new Note")
            self.noteDesc.setText(
                "Notes can be used to describe what is going on in an " +
                "encounter. Click 'Edit' or 'New' to get started!")


class NoteEditor(EMEditor):
    """
    Editor for note data. Note data contains 3 parts: The title, description,
    and type (indicates the badge).

    Since most of the data will be typed out, and to prevent excess calls from
    constantly updating note data, the data is not generated inside the editor.
    At the time of saving, getGeneratedNote() should be called, which will
    create note data from the stuff.
    """

    def __init__(self, note=None):
        super(NoteEditor, self).__init__()
        self.note = NoteData() if note is None else note

        self.noteBadge = NoteBadge(self.note)
        self.title = QLineEdit()
        self.noteType = QComboBox()
        self.noteType.currentIndexChanged.connect(self.note.setType)
        self.noteType.addItems(["General", "Combat", "Hidden", "Treasure"])
        self.desc = QTextEdit()

        layout = QVBoxLayout()
        titleGroup = QWidget()
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(self.noteBadge)
        titleLayout.addWidget(QLabel("Title:"))
        titleLayout.addWidget(self.title)
        titleLayout.addWidget(self.noteType)
        titleGroup.setLayout(titleLayout)

        layout.addWidget(titleGroup)
        layout.addWidget(QLabel("Desc:"))
        layout.addWidget(self.desc)

        btnGroup = QWidget()
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.applyBtn)
        btnLayout.addWidget(self.cancelBtn)
        btnGroup.setLayout(btnLayout)
        layout.addWidget(btnGroup)
        self.setLayout(layout)

    def getGeneratedNote(self):
        self.note.setName(self.title.text())
        self.note.setDesc(self.desc.toPlainText())

        return self.note


class NoteBadge(QLabel):
    """
    Note badge is a graphical represenation of the note on the map and
    elsewhere. It will contain an image representing the different types
    of notes, as well as a number, specifying the note index.

    Current implementation uses a colored rectangle as a placeholder for images
    """

    def __init__(self, note=None, index=0):
        super(NoteBadge, self).__init__()
        self.note = note
        self.index = index
        if note is not None:
            self.note.modelUpdated.connect(self.updateUI)
        self.setMinimumHeight(48)
        self.setMinimumWidth(48)

    def setNote(self, note, index=0):
        self.note = note
        self.index = index
        if note is not None:
            self.note.modelUpdated.connect(self.updateUI)

    def updateUI(self):
        self.repaint()

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if self.note is not None:
            EMImageGenerator.drawNoteIcon(painter, self.note,
                                          0, 0, 48, self.index)
        else:
            painter.setPen(Qt.black)
            painter.setBrush(Qt.white)
            painter.drawRect(0, 0, 48, 48)
