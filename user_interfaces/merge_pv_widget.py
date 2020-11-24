import os
from PyQt5 import QtGui, QtWidgets

from user_interfaces.widgets.separator import Separator
from utility.config import paths
from utility.dataframe_edit import merge_processed_data


class MergePVWindow(QtWidgets.QMdiSubWindow):

    def __init__(self, parent):
        super(MergePVWindow, self).__init__(parent)

        self.Widget = MergePVWidget(self)
        self.setWidget(self.Widget)
        self.setWindowTitle("Merge PV Data")
        self.setObjectName('MERG_PV')


# noinspection PyAttributeOutsideInit
class MergePVWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(MergePVWidget, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("Combine two existing, processed IV files into one.", self))
        vbox.addWidget(QtWidgets.QLabel("1. Specify the files to be merged and the target folder for the "
                                        "combined file.", self))

        hbox_import1 = QtWidgets.QHBoxLayout()
        hbox_import1.addWidget(QtWidgets.QLabel("File #1", self))
        file1_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        file1_button.clicked.connect(lambda: self.file_dialog(origin=1))
        file1_button.setToolTip('Choose first file')
        hbox_import1.addWidget(file1_button)
        self.file1_edit = QtWidgets.QLineEdit(paths['last_export'], self)
        self.file1_edit.setMinimumWidth(180)
        self.file1_edit.setDisabled(True)
        hbox_import1.addWidget(self.file1_edit)
        hbox_import1.addStretch(-1)
        vbox.addLayout(hbox_import1)

        hbox_import2 = QtWidgets.QHBoxLayout()
        hbox_import2.addWidget(QtWidgets.QLabel("File #2", self))
        file2_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        file2_button.clicked.connect(lambda: self.file_dialog(origin=2))
        file2_button.setToolTip('Choose second file')
        hbox_import2.addWidget(file2_button)
        self.file2_edit = QtWidgets.QLineEdit(paths['last_export'], self)
        self.file2_edit.setMinimumWidth(180)
        self.file2_edit.setDisabled(True)
        hbox_import2.addWidget(self.file2_edit)
        hbox_import2.addStretch(-1)
        vbox.addLayout(hbox_import2)

        hbox_export = QtWidgets.QHBoxLayout()
        hbox_export.addWidget(QtWidgets.QLabel("Output folder", self))
        save_folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        save_folder_button.clicked.connect(lambda: self.folder_dialog())
        save_folder_button.setToolTip('Choose output folder')
        hbox_export.addWidget(save_folder_button)
        self.save_folder_edit = QtWidgets.QLineEdit(paths['last_export'], self)
        self.save_folder_edit.setMinimumWidth(180)
        self.save_folder_edit.setDisabled(True)
        hbox_export.addWidget(self.save_folder_edit)
        hbox_export.addStretch(-1)
        vbox.addLayout(hbox_export)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("2. Create combined file in the target folder.\n"
                                        "Groups will be reassigned and indices reset.\n"
                                        "If file name exists, the combined file will be named "
                                        "\'Processed IV(1).xlsx\'.", self))
        hbox_merge = QtWidgets.QHBoxLayout()
        merge_button = QtWidgets.QPushButton("Merge Data")
        hbox_merge.addWidget(merge_button)
        merge_button.clicked.connect(self.merge_data)
        hbox_merge.addStretch(-1)
        vbox.addLayout(hbox_merge)
        vbox.addStretch(-1)
        self.setLayout(vbox)

    def folder_dialog(self):
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory', paths['last_export']))
        self.save_folder_edit.setText(path)

    def file_dialog(self, origin):
        path = str(QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', paths['last_export'])[0])
        if origin == 1:
            self.file1_edit.setText(path)
        elif origin == 2:
            self.file2_edit.setText(path)

    def merge_data(self):
        merge_processed_data(self.file1_edit.text(), self.file2_edit.text(), self.save_folder_edit.text())
