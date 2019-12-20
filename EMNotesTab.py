from PyQt5.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QListWidget,
                             QPushButton, QLabel, QTextEdit, QLineEdit,
                             QListWidgetItem, QVBoxLayout, QComboBox,
                             QDialog, QApplication)

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPainter
from EMBaseClasses import EMEditor


class NotesTab(QWidget):
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
        self.noteList.itemClicked.connect(self.updateNoteSelected)
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
            self.noteList.addItem("{}: {}".format(i+1, note.getTitle()))

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
            self.noteTitle.setText(displayedNote.getTitle())
            self.noteDesc.setText(displayedNote.getDesc())
        else:
            self.noteTitle.setText("Create a new Note")
            self.noteDesc.setText(
                "Notes can be used to describe what is going on in an " +
                "encounter. Click 'Edit' or 'New' to get started!")


class NoteEditor(EMEditor):

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
        self.note.setTitle(self.title.text())
        self.note.setDesc(self.desc.toPlainText())

        return self.note


class NoteBadge(QWidget):
    badgeColors = [Qt.blue, Qt.red, Qt.black, Qt.green]

    def __init__(self, note=None, index=0):
        super(NoteBadge, self).__init__()
        self.note = note
        self.index = index
        if note is not None:
            self.note.noteEmblemUpdated.connect(self.updateUI)
        self.setMinimumHeight(25)
        self.setMinimumWidth(25)

    def setNote(self, note, index=0):
        self.note = note
        self.index = index
        if note is not None:
            self.note.noteEmblemUpdated.connect(self.updateUI)
        self.repaint()

    def updateUI(self):
        self.repaint()

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if self.note is not None:
            self.note.drawNoteIcon(painter, 0, 0, 25, self.index)
        else:
            painter.setPen(Qt.black)
            painter.setBrush(Qt.white)
            painter.drawRect(0, 0, 25, 25)


class NoteData(QObject):

    noteEmblemUpdated = pyqtSignal()

    def __init__(self, type=0, title="", desc="", xPos=0, yPos=0):
        super(NoteData, self).__init__()
        self.type = type
        self.title = title
        self.desc = desc
        self.xPos = xPos
        self.yPos = yPos

    def getType(self):
        return self.type

    def getTitle(self):
        return self.title

    def getDesc(self):
        return self.desc

    def getPos(self):
        return (self.xPos, self.yPos)

    def setType(self, type):
        self.type = type
        self.noteEmblemUpdated.emit()

    def setTitle(self, title):
        self.title = title

    def setDesc(self, desc):
        self.desc = desc

    def setPos(self, x, y):
        self.xPos = x
        self.yPos = y
        self.noteEmblemUpdated.emit()

    def drawNoteIcon(self, painter, x, y, size, num=0):
        painter.setBrush(NoteBadge.badgeColors[self.type])
        painter.setPen(Qt.black)
        painter.drawRect(x, y, size, size)
        if num > 0:
            painter.setPen(Qt.white)
            painter.drawText(x+size/2, y+size/2, "{}".format(num))

    def getJSON(self):
        return {
            "type": self.type,
            "title": self.title,
            "desc": self.desc,
            "x": self.xPos,
            "y": self.yPos
        }
