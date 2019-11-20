from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QListWidget,
                             QListWidgetItem, QDialog)

# from EMModelEditor import ModelEditor, ModelPreviewWidget
# from EMModel import ModelModel
from EMHelper import ModelManager


class EMModelPicker(QWidget):

    selectedModel = pyqtSignal(int)
    updatedModel = pyqtSignal(int)

    def __init__(self, modelName, modelClass, editorClass, modelPreviewClass):
        super(EMModelPicker, self).__init__()
        self.modelName = modelName
        self.modelClass = modelClass
        self.editorClass = editorClass
        self.modelPreviewClass = modelPreviewClass

        self.currentIndex = -1

        self.modelDialog = None
        self.modelEditor = None

        self.models = []

        self.modelList = QListWidget()
        self.modelList.itemClicked.connect(self.updateSelectedGroup)
        self.addModelButton = QPushButton("New ".append(modelName))
        self.addModelButton.clicked.connect(self.newModelDialog)
        self.editModelButton = QPushButton("Edit ".append(modelName))
        self.editModelButton.clicked.connect(self.editModelDialog)
        self.duplicateModelButton = QPushButton("Duplicate")
        self.duplicateModelButton.clicked.connect(self.duplicateModel)
        self.deleteModelButton = QPushButton("Delete ".append(modelName))
        self.deleteModelButton.clicked.connect(self.deleteModel)
        layout = QVBoxLayout()
        layout.addWidget(self.ModelList)
        layout.addWidget(self.addModelButton)
        layout.addWidget(self.editModelButton)
        layout.addWidget(self.duplicateModelButton)
        layout.addWidget(self.deleteModelButton)
        self.setLayout(layout)
        self.loadModels()

    def updateSelectedModel(self):
        sr = self.ModelList.currentRow()
        if sr >= 0:
            self.selectedModel.emit(self.ModelModels[sr].getUid())

    def newModelDialog(self):
        self.ModelDialog = QDialog()
        layout = QVBoxLayout()
        self.ModelEditor = self.editorClass()
        self.ModelEditor.addModel.connect(self.addNewModelModel)
        self.ModelEditor.cancelModel.connect(self.cancelModelModel)
        layout.addWidget(self.ModelEditor)
        self.ModelDialog.setLayout(layout)
        self.ModelDialog.exec_()

    def editModelDialog(self):
        sr = self.ModelList.currentRow()
        if sr >= 0:
            self.ModelDialog = QDialog()
            layout = QVBoxLayout()
            tempCopy = self.modelClass.createModelCopy(self.ModelModels[sr])

            self.ModelEditor = self.modelClass(tempCopy)
            self.ModelEditor.addModel.connect(self.updateExistingModelModel)
            self.ModelEditor.cancelModel.connect(self.cancelModelModel)

            layout.addWidget(self.ModelEditor)
            self.ModelDialog.setLayout(layout)
            self.ModelDialog.exec_()

    def addNewModel(self):
        ModelModel = self.ModelEditor.getCurrentModel()
        ModelManager.addModel(ModelModel)
        self.ModelModels.append(ModelModel)
        self.ModelDialog.close()
        self.ModelDialog = None
        self.ModelEditor = None
        self.updateUI()

    def updateExistingModel(self):
        ModelModel = self.ModelEditor.getCurrentModel()
        ModelManager.updateModel(ModelModel)
        self.ModelModels[self.ModelList.currentRow()] = ModelModel
        self.ModelDialog.close()
        self.ModelDialog = None
        self.ModelEditor = None
        self.updateUI()
        self.updatedModel.emit(ModelModel.getUid())

    def cancelModelModel(self):
        self.ModelDialog.close()
        self.ModelDialog = None
        self.ModelEditor = None

    def duplicateModel(self):
        sr = self.ModelList.currentRow()
        if sr >= 0:
            dupe = model.createModelCopy(self.ModelModels[sr])

            name = "{}_copy".format(dupe.getName())
            dupe.setName(name)
            ModelManager.addModel(dupe, sr)
            self.ModelModels.insert(sr, dupe)
            self.updateUI()

    def deleteModel(self):
        """TODO"""

    def updateUI(self):
        self.ModelList.clear()
        for model in self.ModelModels:
            listItemWidget = ModelPickerListItem(model)
            listItem = QListWidgetItem(self.ModelList)
            listItem.setSizeHint(listItemWidget.sizeHint())

            self.ModelList.addItem(listItem)
            self.ModelList.setItemWidget(listItem, listItemWidget)

    def loadModels(self):
        self.models = ModelManager.fetchModels(self.modelName)
        self.updateUI()

    def appendModel(self, Modeljs):
        """todo"""


class ModelPickerListItem(QWidget):

    def __init__(self, previewClass, model=None):
        super(ModelPickerListItem, self).__init__()
        self.model = model
        if model is not None:
            layout = QHBoxLayout()
            self.preview = previewClass.previewWidget(self.ModelModel)
            layout.addWidget(self.preview)
            layout.addWidget(QLabel(self.model.getName()))
            self.setLayout(layout)


# def main():
#     app = QApplication([])
#
#     mainWidget = EMModelPicker()
#     mainWidget.show()
#     app.exec_()
#
#
# if __name__ == "__main__":
#     main()
