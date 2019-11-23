from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QListWidget,
                             QListWidgetItem, QDialog)

# from EMModelEditor import ModelEditor, ModelPreviewWidget
# from EMModel import ModelModel
from EMHelper import ModelManager


class EMModelPicker(QWidget):

    selectedModel = pyqtSignal(int)
    updatedModel = pyqtSignal(int)
    deletedModel = pyqtSignal(int)

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
        self.modelList.itemClicked.connect(self.updateSelectedModel)
        self.addModelButton = QPushButton("New " + modelName)
        self.addModelButton.clicked.connect(self.newModelDialog)
        self.editModelButton = QPushButton("Edit " + modelName)
        self.editModelButton.clicked.connect(self.editModelDialog)
        self.duplicateModelButton = QPushButton("Duplicate")
        self.duplicateModelButton.clicked.connect(self.duplicateModel)
        self.deleteModelButton = QPushButton("Delete " + modelName)
        self.deleteModelButton.clicked.connect(self.deleteModel)
        layout = QVBoxLayout()
        layout.addWidget(self.modelList)
        layout.addWidget(self.addModelButton)
        layout.addWidget(self.editModelButton)
        layout.addWidget(self.duplicateModelButton)
        layout.addWidget(self.deleteModelButton)
        self.setLayout(layout)
        self.loadModels()

    def updateSelectedModel(self):
        sr = self.modelList.currentRow()
        if sr >= 0:
            print(self.models[sr].getUid())
            self.selectedModel.emit(self.models[sr].getUid())

    def newModelDialog(self):
        self.modelDialog = QDialog()
        layout = QVBoxLayout()
        self.modelEditor = self.editorClass()
        self.modelEditor.applyModel.connect(self.addNewModel)
        self.modelEditor.cancelModel.connect(self.cancelModel)
        layout.addWidget(self.modelEditor)
        self.modelDialog.setLayout(layout)
        self.modelDialog.exec_()

    def editModelDialog(self):
        sr = self.modelList.currentRow()
        if sr >= 0:
            self.modelDialog = QDialog()
            layout = QVBoxLayout()
            tempCopy = self.modelClass.createModelCopy(self.models[sr])

            self.modelEditor = self.editorClass(tempCopy)
            self.modelEditor.applyModel.connect(self.updateExistingModel)
            self.modelEditor.cancelModel.connect(self.cancelModel)

            layout.addWidget(self.modelEditor)
            self.modelDialog.setLayout(layout)
            self.modelDialog.exec_()

    def addNewModel(self):
        model = self.modelEditor.getModel()
        ModelManager.addModel(self.modelName, model)
        self.models.append(model)
        self.modelDialog.close()
        self.modelDialog = None
        self.modelEditor = None
        self.updateUI()

    def updateExistingModel(self):
        model = self.modelEditor.getModel()
        ModelManager.updateModel(self.modelName, model)
        self.models[self.modelList.currentRow()] = model
        self.modelDialog.close()
        self.modelDialog = None
        self.modelEditor = None
        self.updateUI()
        self.updatedModel.emit(model.getUid())

    def cancelModel(self):
        self.modelDialog.close()
        self.modelDialog = None
        self.modelEditor = None

    def duplicateModel(self):
        sr = self.modelList.currentRow()
        if sr >= 0:
            dupe = self.modelClass.createModelCopy(self.models[sr])

            name = "{}_copy".format(dupe.getName())
            dupe.setName(name)
            ModelManager.addModel(self.modelName, dupe, sr)
            self.models.insert(sr, dupe)
            self.updateUI()

    def deleteModel(self):
        sr = self.modelList.currentRow()
        if sr >= 0:
            uid = self.models[sr].getUid()
            ModelManager.deleteModel(self.modelName, self.models[sr])
            del self.models[sr]
            self.updateUI()
            self.deletedModel.emit(uid)

    def updateUI(self):
        self.modelList.clear()
        for model in self.models:
            listItemWidget = ModelPickerListItem(self.modelPreviewClass, model)
            listItem = QListWidgetItem(self.modelList)
            listItem.setSizeHint(listItemWidget.sizeHint())

            self.modelList.addItem(listItem)
            self.modelList.setItemWidget(listItem, listItemWidget)

    def loadModels(self):
        ModelManager.loadModelFromFile(self.modelName, self.modelClass)
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
            self.preview = previewClass.previewWidget(self.model)
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
