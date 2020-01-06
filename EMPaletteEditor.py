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

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (QColor, QPalette)

from EMColorModel import EMColorModel

from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

import json


class EMPaletteEditor(QWidget):
    """
    Editor for the ColorModel. Enables the creation and editing of color
    palettes.

    This class was the first one created in the project, and as a result
    needs to be refactored in order to match the paradigms used later.
    """

    colorApplied = pyqtSignal(int, int, int)
    colorCanceled = pyqtSignal()
    key = ""

    def __init__(self, r, g, b):
        super(EMPaletteEditor, self).__init__()
        layout = QGridLayout()

        self.colorList = []

        self.paletteTitle = QLineEdit()
        self.paletteTitle.textEdited.connect(self.checkCanSave)
        self.paletteColors = QComboBox()
        self.paletteColors.addItem("*New Color*")
        self.paletteColors.currentIndexChanged.connect(self.colorSelected)
        self.colorPreview = QWidget()
        self.colorPreview.setAutoFillBackground(True)
        self.colorName = QLineEdit()
        self.colorName.textEdited.connect(self.checkCanBeAdded)

        self.rScroll = QSlider(Qt.Horizontal, self)
        self.rScroll.setValue(r)
        self.rScroll.setMaximum(255)
        self.rScroll.valueChanged.connect(self.rSliderChanged)

        self.rText = QSpinBox()
        self.rText.setValue(g)
        self.rText.setMaximum(255)
        self.rText.valueChanged.connect(self.rTextChanged)

        self.gScroll = QSlider(Qt.Horizontal, self)
        self.gScroll.setValue(b)
        self.gScroll.setMaximum(255)
        self.gScroll.valueChanged.connect(self.gSliderChanged)

        self.gText = QSpinBox()
        self.gText.setValue(r)
        self.gText.setMaximum(255)
        self.gText.valueChanged.connect(self.gTextChanged)

        self.bScroll = QSlider(Qt.Horizontal, self)
        self.bScroll.setValue(g)
        self.bScroll.setMaximum(255)
        self.bScroll.valueChanged.connect(self.bSliderChanged)

        self.bText = QSpinBox()
        self.bText.setValue(b)
        self.bText.setMaximum(255)
        self.bText.valueChanged.connect(self.bTextChanged)

        self.addButton = QPushButton("Add")
        self.addButton.clicked.connect(self.addUpdateColor)
        self.addButton.setEnabled(False)
        self.deleteButton = QPushButton("Delete")
        self.deleteButton.setEnabled(False)
        self.deleteButton.clicked.connect(self.deleteColor)
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.savePalette)
        self.saveButton.setEnabled(False)

        self.applyButton = QPushButton("Apply")
        self.applyButton.clicked.connect(self.applyColorPick)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancelColorPick)

        layout.addWidget(QLabel("Palette Title:"), 0, 0)
        layout.addWidget(self.paletteTitle, 0, 1, 1, 2)
        layout.addWidget(self.colorPreview, 1, 0, 5, 1)
        layout.addWidget(QLabel("Colors:"), 1, 1)
        layout.addWidget(self.paletteColors, 1, 2)
        layout.addWidget(QLabel("Color Title:"), 2, 1)
        layout.addWidget(self.colorName, 2, 2)
        layout.addWidget(QLabel("R:"), 3, 1)
        layout.addWidget(self.rScroll, 3, 2)
        layout.addWidget(self.rText, 3, 3)
        layout.addWidget(QLabel("G:"), 4, 1)
        layout.addWidget(self.gScroll, 4, 2)
        layout.addWidget(self.gText, 4, 3)
        layout.addWidget(QLabel("B:"), 5, 1)
        layout.addWidget(self.bScroll, 5, 2)
        layout.addWidget(self.bText, 5, 3)

        layout.addWidget(self.addButton, 6, 0)
        layout.addWidget(self.deleteButton, 6, 1)
        layout.addWidget(self.saveButton, 6, 2)
        layout.addWidget(self.applyButton, 7, 0, 1, 2)
        layout.addWidget(self.cancelButton, 7, 2, 1, 2)

        self.setLayout(layout)
        self.loadPaletteFromFile()
        self.updatePreviewColor()

    def checkCanBeAdded(self):
        index = self.paletteColors.currentIndex()
        text = self.colorName.text()
        if(len(text) > 0):
            textIndex = self.paletteColors.findText(self.colorName.text())
            if(index == 0):
                self.addButton.setEnabled(textIndex == -1)
            else:
                self.addButton.setEnabled(textIndex == -1
                                          or textIndex == index)
        else:
            self.addButton.setEnabled(False)

    def checkCanSave(self):
        self.saveButton.setEnabled(len(self.paletteTitle.text()) > 0
                                   and len(self.colorList) > 0)

    def rSliderChanged(self):
        value = self.rScroll.value()
        self.rText.setValue(value)
        self.updatePreviewColor()

    def gSliderChanged(self):
        value = self.gScroll.value()
        self.gText.setValue(value)
        self.updatePreviewColor()

    def bSliderChanged(self):
        value = self.bScroll.value()
        self.bText.setValue(value)
        self.updatePreviewColor()

    def rTextChanged(self):
        value = self.rText.value()
        self.rScroll.setValue(value)
        self.updatePreviewColor()

    def gTextChanged(self):
        value = self.gText.value()
        self.gScroll.setValue(value)
        self.updatePreviewColor()

    def bTextChanged(self):
        value = self.bText.value()
        self.bScroll.setValue(value)
        self.updatePreviewColor()

    def updatePreviewColor(self):
        color = QColor(self.rScroll.value(),
                       self.gScroll.value(),
                       self.bScroll.value())
        palette = QPalette()
        palette.setColor(QPalette.Background, color)
        self.colorPreview.setPalette(palette)

    def addUpdateColor(self):
        index = self.paletteColors.currentIndex()
        name = self.colorName.text()
        rgb = (self.rScroll.value(), self.gScroll.value(),
               self.bScroll.value())

        if(index == 0):
            self.colorList.append(EMColorModel(name, rgb[0], rgb[1], rgb[2]))
            self.paletteColors.addItem(name)
            self.checkCanSave()
        else:
            self.paletteColors.setItemText(index, name)
            self.colorList[index-1].setName(name)
            self.colorList[index-1].setColor(rgb[0], rgb[1], rgb[2])

        self.checkCanBeAdded()

    def colorSelected(self):
        index = max(0, self.paletteColors.currentIndex())
        if(index == 0):
            self.addButton.setText("Add")
            self.deleteButton.setEnabled(False)
        else:
            self.addButton.setText("Update")
            self.deleteButton.setEnabled(True)
            cm = self.colorList[index-1]
            color = cm.getColor()
            self.rScroll.setValue(color.red())
            self.gScroll.setValue(color.green())
            self.bScroll.setValue(color.blue())
            self.colorName.setText(cm.getName())

        self.checkCanBeAdded()

    def savePalette(self):
        paletteName = self.paletteTitle.text()
        paletteJS = {
            "palette_name": paletteName,
            "colors": []
        }
        for cm in self.colorList:
            paletteJS["colors"].append(cm.jsonObj())
        # Do fancy stuff to save the palette
        text = json.dumps(paletteJS)
        f = open("palette.json", "w+")
        f.write(text)
        f.close()

    def deleteColor(self):
        index = self.paletteColors.currentIndex()
        if(index != 0):
            index -= 1
        del self.colorList[index]
        self.reloadPaletteColors(index)
        self.checkCanSave()

    def reloadPaletteColors(self, index):
        self.paletteColors.clear()
        self.paletteColors.addItem("*New Color*")
        for cm in self.colorList:
            self.paletteColors.addItem(cm.getName())
        if(index < self.paletteColors.count()):
            self.paletteColors.setCurrentIndex(index)
        else:
            self.paletteColors.setCurrentIndex(0)

    def loadPaletteFromFile(self):
        paletteName = ""
        paletteColors = []
        f = open("palette.json", "r")
        if f.mode == 'r':
            contents = f.read()
            jsContents = json.loads(contents)
            f.close()
            paletteName = jsContents["palette_name"]
            for c in jsContents["colors"]:
                paletteColors.append(EMColorModel(c["name"],
                                                  c["r"], c["g"], c["b"]))
        self.colorList = paletteColors
        self.paletteTitle.setText(paletteName)
        self.reloadPaletteColors(0)

    def applyColorPick(self):
        rgb = (self.rScroll.value(), self.gScroll.value(),
               self.bScroll.value())
        self.colorApplied.emit(rgb[0], rgb[1], rgb[2])

    def cancelColorPick(self):
        self.colorCanceled.emit()

# code to run this widget directly from this file for testing


def main():
    app = QApplication([])

    mainWidget = EMPaletteEditor(100, 100, 100)
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
