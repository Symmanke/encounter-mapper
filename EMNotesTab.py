from PyQt5.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QListWidget,
                             QPushButton, QLabel, QTextEdit, QLineEdit,
                             QListWidgetItem, QVBoxLayout)

from PyQt5.QtCore import pyqtSignal


class NotesTab(QWidget):
    def __init__(self, notes=None):
        super(NotesTab, self).__init__()

        self.notes = [NoteData(0, "Hello World", "Here is a Sample Note")
                      ] if notes is None else notes

        self.noteBadge = QWidget()
        self.noteTitle = QLineEdit("New Note")
        self.noteTitle.setReadOnly(True)
        self.editBtn = QPushButton("Edit")
        self.editBtn.clicked.connect(self.editNote)
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
        self.populateList()
        # Todo: display notes

        self.newBtn = QPushButton("New")
        self.newBtn.clicked.connect(self.newNote)
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

    def populateList(self):
        self.noteList.addItem("(new)")
        for i in range(len(self.notes)):
            note = self.notes[i]
            self.noteList.addItem("{}: {}".format(i+1, note.getTitle()))

    def newNote(self):
        pass

    def editNote(self):
        pass

    def deleteNote(self):
        pass

    def moveNoteUp(self):
        pass

    def moveNoteDown(self):
        pass


class NoteData():

    noteEmblemUpdated = pyqtSignal()

    def __init__(self, type=0, title="", desc="", xPos=0, yPos=0):
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

    def getCoordinates(self):
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

    def getJSON(self):
        return {
            "type": self.type,
            "title": self.title,
            "desc": self.desc,
            "x": self.xPos,
            "y": self.yPos
        }
