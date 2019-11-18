from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

from EMMapWidget import EMMapWidget
from EMNotesTab import EMNotesTab
from EMTilePicker import EMTilePicker


class EMMain(object):
    """docstring for EMMain."""

    def __init__(self, arg):
        # Set ui in here
        super(EMMain, self).__init__()
        self.arg = arg


def setTilesLayout():
    tilesTab = QWidget()
    return tilesTab


# def setNotesLayout():
#     notesTab = QWidget()
#     notesGridLayout = QGridLayout()
#     notesGridLayout.addWidget(QPushButton("New Note"), 0, 0)
#     notesCombo = QComboBox()
#     notesCombo.addItems(["Note 1", "Note 2", "Note 3"])
#     notesGridLayout.addWidget(notesCombo, 0, 1)
#
#     titleWidget = QWidget()
#     titleLayout = QHBoxLayout()
#     titleLayout.addWidget(QLabel("Title:"))
#     titleLayout.addWidget(QLineEdit())
#     titleWidget.setLayout(titleLayout)
#     notesGridLayout.addWidget(titleWidget, 1, 0, 1, 2)
#     notesGridLayout.addWidget(QLabel("Notes:"), 2, 0, 1, 2)
#     notesGridLayout.addWidget(QTextEdit(), 3, 0, 2, 2)
#
#     notesGridLayout.addWidget(QPushButton("Delete"), 5, 1)
#
#     notesTab.setLayout(notesGridLayout)
#     return notesTab


app = QApplication([])

mainWidget = QWidget()

mainLayout = QHBoxLayout()

# Create a tab widget
tabWidget = QTabWidget()
tab1 = QWidget()
# Set a box layout

tab2 = QWidget()


tabWidget.addTab(EMTilePicker(), "Tiles")
tabWidget.addTab(QWidget(), "Groups")
tabWidget.addTab(setTilesLayout(), "Objects")
tabWidget.addTab(EMNotesTab(), "Notes")

# mainLayout.addWidget(QLabel("TBD"))
mainLayout.addWidget(EMMapWidget())
mainLayout.addWidget(tabWidget)

mainWidget.setLayout(mainLayout)

mainWidget.show()


# label = QLabel('Hello World!')
# label.show()
app.exec_()
