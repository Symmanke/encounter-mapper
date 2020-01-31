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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import (QWidget, QPushButton, QSpinBox, QSlider,
                             QApplication, QGridLayout, QLabel, QComboBox,
                             QHBoxLayout)

from EMBaseClasses import EMModelEditor, EMModelGraphics
from EMModel import ImageTextureModel, GeneratedTextureModel
from EMHelper import EMImageGenerator


class TextureEditor(EMModelEditor):
    def __init__(self, model=None):
        if model is None:
            model = GeneratedTextureModel()
        super(TextureEditor, self).__init__(model)

        self.previewWidget = TexturePreview(self.model)

        self.uploadImageBtn = QPushButton("Upload Image")
        self.uploadImageBtn.clicked.connect(self.uploadImage)
        self.removeImageBtn = QPushButton("Remove Image")
        self.removeImageBtn.clicked.connect(self.removeImage)

        # Pick the Grayscale Textures
        self.txtPicker = QComboBox()
        self.txtPicker.addItem("None")
        self.txtPicker.addItem("Tile")
        self.txtPicker.addItem("Grass")
        self.txtPicker.addItem("Wood")
        self.txtPicker.currentIndexChanged.connect(self.genTxtUpdate)

        initialColor = Qt.white
        if isinstance(model, GeneratedTextureModel):
            c = model.getColors()[0]
            initialColor = QColor(c[0], c[1], c[2])

        nameParent = QWidget()
        nameLayout = QHBoxLayout()
        nameLayout.addWidget(QLabel("Name:"))
        nameLayout.addWidget(self.modelNameEdit)
        nameParent.setLayout(nameLayout)

        # RGB Values
        self.rBox = QSpinBox()
        self.rSlider = QSlider(Qt.Horizontal)
        self.rBox.setRange(0, 255)
        self.rBox.setValue(initialColor.red())
        self.rSlider.setMaximum(255)
        self.rSlider.setValue(initialColor.red())
        self.rSlider.sliderMoved.connect(self.rUpdated)

        self.gBox = QSpinBox()
        self.gSlider = QSlider(Qt.Horizontal)
        self.gBox.setRange(0, 255)
        self.gBox.setValue(initialColor.green())
        self.gSlider.setMaximum(255)
        self.gSlider.setValue(initialColor.green())
        self.gSlider.sliderMoved.connect(self.gUpdated)

        self.bBox = QSpinBox()
        self.bSlider = QSlider(Qt.Horizontal)
        self.bBox.setRange(0, 255)
        self.bBox.setValue(initialColor.blue())
        self.bSlider.setMaximum(255)
        self.bSlider.setValue(initialColor.blue())
        self.bSlider.sliderMoved.connect(self.bUpdated)

        # HSV Values
        self.hBox = QSpinBox()
        self.hSlider = QSlider(Qt.Horizontal)
        self.hBox.setRange(0, 359)
        self.hBox.setValue(initialColor.hue())
        self.hSlider.setMaximum(359)
        self.hSlider.setValue(initialColor.hue())
        self.hSlider.sliderMoved.connect(self.hUpdated)

        self.sBox = QSpinBox()
        self.sSlider = QSlider(Qt.Horizontal)
        self.sBox.setRange(0, 255)
        self.sBox.setValue(initialColor.saturation())
        self.sSlider.setMaximum(255)
        self.sSlider.setValue(initialColor.saturation())
        self.sSlider.sliderMoved.connect(self.sUpdated)

        self.vBox = QSpinBox()
        self.vSlider = QSlider(Qt.Horizontal)
        self.vBox.setRange(0, 255)
        self.vBox.setValue(initialColor.value())
        self.vSlider.setMaximum(255)
        self.vSlider.setValue(initialColor.value())
        self.vSlider.sliderMoved.connect(self.vUpdated)

        self.colorWidget = QWidget()
        colorLayout = QGridLayout()
        colorLayout.addWidget(QLabel("R:"), 0, 0)
        colorLayout.addWidget(self.rBox, 0, 1)
        colorLayout.addWidget(self.rSlider, 0, 2)
        colorLayout.addWidget(QLabel("G:"), 1, 0)
        colorLayout.addWidget(self.gBox, 1, 1)
        colorLayout.addWidget(self.gSlider, 1, 2)
        colorLayout.addWidget(QLabel("B:"), 2, 0)
        colorLayout.addWidget(self.bBox, 2, 1)
        colorLayout.addWidget(self.bSlider, 2, 2)

        colorLayout.addWidget(QLabel("H:"), 3, 0)
        colorLayout.addWidget(self.hBox, 3, 1)
        colorLayout.addWidget(self.hSlider, 3, 2)
        colorLayout.addWidget(QLabel("S:"), 4, 0)
        colorLayout.addWidget(self.sBox, 4, 1)
        colorLayout.addWidget(self.sSlider, 4, 2)
        colorLayout.addWidget(QLabel("V:"), 5, 0)
        colorLayout.addWidget(self.vBox, 5, 1)
        colorLayout.addWidget(self.vSlider, 5, 2)
        self.colorWidget.setLayout(colorLayout)

        self.editorUI = QWidget()
        editorLayout = QGridLayout()
        editorLayout.addWidget(nameParent, 0, 0, 1, 4)
        editorLayout.addWidget(self.uploadImageBtn, 1, 0, 1, 2)
        editorLayout.addWidget(self.removeImageBtn, 1, 2, 1, 2)
        editorLayout.addWidget(QLabel("Texture:"), 2, 0)
        editorLayout.addWidget(self.txtPicker, 2, 1, 1, 3)
        editorLayout.addWidget(self.colorWidget, 4, 0, 1, 4)
        self.editorUI.setLayout(editorLayout)

        layout = QGridLayout()
        layout.addWidget(self.previewWidget, 0, 0)
        layout.addWidget(self.editorUI, 0, 1)

        self.setLayout(layout)
        self.updateUI()

    def updateUI(self):
        isGenModel = isinstance(self.model, GeneratedTextureModel)

        self.removeImageBtn.setEnabled(not isGenModel)
        self.txtPicker.setEnabled(isGenModel)
        self.rBox.setEnabled(isGenModel)
        self.rSlider.setEnabled(isGenModel)
        self.gBox.setEnabled(isGenModel)
        self.gSlider.setEnabled(isGenModel)
        self.bBox.setEnabled(isGenModel)
        self.bSlider.setEnabled(isGenModel)
        self.hBox.setEnabled(isGenModel)
        self.hSlider.setEnabled(isGenModel)
        self.sBox.setEnabled(isGenModel)
        self.sSlider.setEnabled(isGenModel)
        self.vBox.setEnabled(isGenModel)
        self.vSlider.setEnabled(isGenModel)

        if isGenModel:
            clr = self.model.getColors()[0]
            qclr = QColor(clr[0], clr[1], clr[2])
            self.rBox.setValue(qclr.red())
            self.rSlider.setValue(qclr.red())
            self.gBox.setValue(qclr.green())
            self.gSlider.setValue(qclr.green())
            self.bBox.setValue(qclr.blue())
            self.bSlider.setValue(qclr.blue())
            self.hBox.setValue(qclr.hue())
            self.hSlider.setValue(qclr.hue())
            self.sBox.setValue(qclr.saturation())
            self.sSlider.setValue(qclr.saturation())
            self.vBox.setValue(qclr.value())
            self.vSlider.setValue(qclr.value())

        self.colorWidget.repaint()
        self.removeImageBtn.repaint()
        self.previewWidget.repaint()

    def uploadImage(self):
        pass

    def removeImage(self):
        pass

    def rUpdated(self, r):
        color = self.model.getColors()[0]
        self.model.setColor((r, color[1], color[2]), 0)

    def gUpdated(self, g):
        color = self.model.getColors()[0]
        self.model.setColor((color[0], g, color[2]), 0)

    def bUpdated(self, b):
        color = self.model.getColors()[0]
        self.model.setColor((color[0], color[1], b), 0)

    def hUpdated(self, h):
        color = self.model.getColors()[0]
        qc = QColor(color[0], color[1], color[2])
        uqc = QColor.fromHsv(h, qc.saturation(), qc.value())
        self.model.setColor((uqc.red(), uqc.green(), uqc.blue()), 0)

    def sUpdated(self, s):
        color = self.model.getColors()[0]
        qc = QColor(color[0], color[1], color[2])
        uqc = QColor.fromHsv(qc.hue(), s, qc.value())
        self.model.setColor((uqc.red(), uqc.green(), uqc.blue()), 0)

    def vUpdated(self, v):
        color = self.model.getColors()[0]
        qc = QColor(color[0], color[1], color[2])
        uqc = QColor.fromHsv(qc.hue(), qc.saturation(), v)
        self.model.setColor((uqc.red(), uqc.green(), uqc.blue()), 0)

    def genTxtUpdate(self, v):
        self.model.setTexture(self.txtPicker.currentText())


class TexturePreview(EMModelGraphics):
    def __init__(self, model):
        super(TexturePreview, self).__init__(model, 1, 1, 216, 216, 216)

    def paintEvent(self, paintEvent):
        pass
        if self.model is not None:
            painter = QPainter(self)
        image = EMImageGenerator.genImageFromModel(self.model)
        if image is not None:
            # painter.setBrush(QBrush(image))
            # painter.setPen(Qt.NoPen)
            painter.drawImage(0, 0, image, 0, 0, self.width, self.height)


def main():
    app = QApplication([])
    mainWidget = TextureEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
