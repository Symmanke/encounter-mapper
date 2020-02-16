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
from PyQt5.QtGui import QPainter, QColor, QPalette
from PyQt5.QtWidgets import (QWidget, QPushButton, QSpinBox, QSlider,
                             QApplication, QGridLayout, QLabel, QComboBox,
                             QHBoxLayout)

from EMBaseClasses import EMModelEditor, EMModelGraphics
from EMModel import GeneratedTextureModel
from EMHelper import EMImageGenerator


class TextureEditor(EMModelEditor):
    def __init__(self, model=None):
        if model is None:
            model = GeneratedTextureModel()
        super(TextureEditor, self).__init__(model)

        self.previewWidget = TexturePreview(self.model)
        self.currentSelectedColor = QColor(255, 255, 255)

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
            c = model.getBgColor()
            initialColor = c

        nameParent = QWidget()
        nameLayout = QHBoxLayout()
        nameLayout.addWidget(QLabel("Name:"))
        nameLayout.addWidget(self.modelNameEdit)
        nameParent.setLayout(nameLayout)

        # Preview Stuff
        self.bgColorPreview = QWidget()
        self.bgColorPreview.setMinimumHeight(50)
        self.bgColorPreview.setAutoFillBackground(True)
        self.currentColorPreview = QWidget()
        self.currentColorPreview.setMinimumHeight(50)
        self.currentColorPreview.setAutoFillBackground(True)
        self.subColorPreview = QWidget()
        self.subColorPreview.setMinimumHeight(50)
        self.subColorPreview.setAutoFillBackground(True)
        self.subColorLabel = QLabel("Txt 1")

        colorPreviewLayout = QGridLayout()
        colorPreviewLayout.addWidget(self.bgColorPreview, 0, 0)
        colorPreviewLayout.addWidget(self.currentColorPreview, 0, 1)
        colorPreviewLayout.addWidget(self.subColorPreview, 0, 2)
        colorPreviewLayout.addWidget(QLabel("BG"), 1, 0)
        colorPreviewLayout.addWidget(QLabel("Cur"), 1, 1)
        colorPreviewLayout.addWidget(self.subColorLabel, 1, 2)

        colorPreviewWidget = QWidget()
        colorPreviewWidget.setLayout(colorPreviewLayout)

        self.setBGColorBtn = QPushButton("Set BG")
        self.setBGColorBtn.clicked.connect(self.setBgColor)
        self.setSubColorBtn = QPushButton("Set TXT")
        self.setSubColorBtn.clicked.connect(self.setSubColor)

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
        editorLayout.addWidget(colorPreviewWidget, 2, 0, 1, 4)
        editorLayout.addWidget(QLabel("Texture:"), 3, 0)
        editorLayout.addWidget(self.txtPicker, 3, 1, 1, 3)
        editorLayout.addWidget(self.colorWidget, 4, 0, 1, 4)
        editorLayout.addWidget(self.setBGColorBtn, 5, 0, 1, 2)
        editorLayout.addWidget(self.setSubColorBtn, 5, 2, 1, 2)
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

            qclr = self.currentSelectedColor
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

            self.updateBgColorPreview()
            self.updateTxtColorPreview()
            self.setCurrentColor()

        self.colorWidget.repaint()
        self.removeImageBtn.repaint()
        self.previewWidget.updateImage()
        self.previewWidget.repaint()

    def setCurrentColor(self):
        palette = QPalette()
        palette.setColor(QPalette.Background, self.currentSelectedColor)
        self.currentColorPreview.setPalette(palette)
        self.currentColorPreview.repaint()

    def updateBgColorPreview(self):
        palette = QPalette()
        palette.setColor(QPalette.Background, self.model.getBgColor())
        self.bgColorPreview.setPalette(palette)
        self.bgColorPreview.repaint()

    def updateTxtColorPreview(self):
        palette = QPalette()
        palette.setColor(QPalette.Background, self.model.getTexture(0)[1])
        self.subColorPreview.setPalette(palette)
        self.subColorPreview.repaint()

    def rgbUpdated(self):
        qclr = QColor(self.rSlider.value(),
                      self.gSlider.value(),
                      self.bSlider.value())
        self.currentSelectedColor = qclr

        self.hBox.setValue(qclr.hue())
        self.hSlider.setValue(qclr.hue())
        self.sBox.setValue(qclr.saturation())
        self.sSlider.setValue(qclr.saturation())
        self.vBox.setValue(qclr.value())
        self.vSlider.setValue(qclr.value())

        self.setCurrentColor()

    def hsvUpdated(self):
        qclr = QColor.fromHsv(self.hSlider.value(),
                              self.sSlider.value(),
                              self.vSlider.value())
        self.currentSelectedColor = qclr

        self.rBox.setValue(qclr.red())
        self.rSlider.setValue(qclr.red())
        self.gBox.setValue(qclr.green())
        self.gSlider.setValue(qclr.green())
        self.bBox.setValue(qclr.blue())
        self.bSlider.setValue(qclr.blue())

        self.setCurrentColor()

    def uploadImage(self):
        pass

    def removeImage(self):
        pass

    def rUpdated(self, r):
        self.rBox.setValue(r)
        self.rSlider.setValue(r)
        self.rgbUpdated()
        # color = self.model.getColors()[0]
        # self.model.setColor((r, color[1], color[2]), 0)

    def gUpdated(self, g):
        self.gBox.setValue(g)
        self.gSlider.setValue(g)
        self.rgbUpdated()
        # color = self.model.getColors()[0]
        # self.model.setColor((color[0], g, color[2]), 0)

    def bUpdated(self, b):
        self.bBox.setValue(b)
        self.bSlider.setValue(b)
        self.rgbUpdated()
        # color = self.model.getColors()[0]
        # self.model.setColor((color[0], color[1], b), 0)

    def hUpdated(self, h):
        self.hBox.setValue(h)
        self.hSlider.setValue(h)
        self.hsvUpdated()

        # color = self.model.getColors()[0]
        # qc = QColor(color[0], color[1], color[2])
        # uqc = QColor.fromHsv(h, qc.saturation(), qc.value())
        # self.model.setColor((uqc.red(), uqc.green(), uqc.blue()), 0)

    def sUpdated(self, s):
        self.sBox.setValue(s)
        self.sSlider.setValue(s)
        self.hsvUpdated()

        # color = self.model.getColors()[0]
        # qc = QColor(color[0], color[1], color[2])
        # uqc = QColor.fromHsv(qc.hue(), s, qc.value())
        # self.model.setColor((uqc.red(), uqc.green(), uqc.blue()), 0)

    def vUpdated(self, v):
        self.vBox.setValue(v)
        self.vSlider.setValue(v)
        self.hsvUpdated()

        # color = self.model.getColors()[0]
        # qc = QColor(color[0], color[1], color[2])
        # uqc = QColor.fromHsv(qc.hue(), qc.saturation(), v)
        # self.model.setColor((uqc.red(), uqc.green(), uqc.blue()), 0)

    def genTxtUpdate(self, v):
        self.model.setTextureType(self.txtPicker.currentText(), 0)

    def setBgColor(self):
        self.model.setBgColor(QColor(self.currentSelectedColor))

    def setSubColor(self):
        self.model.setTextureColor(QColor(self.currentSelectedColor), 0)


class TexturePreview(EMModelGraphics):
    def __init__(self, model):
        super(TexturePreview, self).__init__(model, 1, 1, 216, 216, 216)
        self.generatedImage = None

    def updateImage(self):
        self.generatedImage = EMImageGenerator.genImageFromModel(self.model)

    def paintEvent(self, paintEvent):
        # if self.model is not None:
        #     painter.setPen(Qt.NoPen)
        #     painter.setBrush(self.model.getBgColor())
        #     painter.drawRect(0, 0, 216, 216)
        # EMImageGenerator.drawGeneratedTexture(painter, self.model)
        if self.generatedImage is not None:
            painter = QPainter(self)
            painter.drawImage(0, 0, self.generatedImage, 0, 0,
                              self.width, self.height)

            painter.end()


def main():
    app = QApplication([])
    mainWidget = TextureEditor()
    mainWidget.show()
    app.exec_()


if __name__ == "__main__":
    main()
