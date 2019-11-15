from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)


class EMNotesTab(QWidget):
    def __init__(self):
        super(EMNotesTab, self).__init__()
        self.setupLayout()

    def setupLayout(self):
        self.notesGridLayout = QGridLayout()
        self.notesGridLayout.addWidget(QPushButton("New Note"), 0, 0)
        self.notesCombo = QComboBox()
        self.notesCombo.addItems(["Note 1", "Note 2", "Note 3"])
        self.notesGridLayout.addWidget(self.notesCombo, 0, 1)

        self.titleWidget = QWidget()
        self.titleLayout = QHBoxLayout()
        self.titleLayout.addWidget(QLabel("Title:"))
        self.titleLayout.addWidget(QLineEdit())
        self.titleWidget.setLayout(self.titleLayout)
        self.notesGridLayout.addWidget(self.titleWidget, 1, 0, 1, 2)
        self.notesGridLayout.addWidget(QLabel("Notes:"), 2, 0, 1, 2)
        self.notesGridLayout.addWidget(QTextEdit(), 3, 0, 2, 2)

        self.notesGridLayout.addWidget(QPushButton("Delete"), 5, 1)

        self.setLayout(self.notesGridLayout)
