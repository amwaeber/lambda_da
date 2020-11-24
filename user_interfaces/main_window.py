import ctypes
import os
from PyQt5 import QtWidgets, QtGui

from user_interfaces.explore_pv_widget import ExplorePVWindow
from user_interfaces.merge_pv_widget import MergePVWindow
from user_interfaces.process_pv_widget import ProcessPVWindow
from utility import config


# noinspection PyAttributeOutsideInit
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        myappid = 'Lambda DA'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        config.read_config()
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QtGui.QIcon(os.path.join(config.paths['icons'], 'lambda_da.png')))
        self.setWindowTitle("%s %s" % (config.global_confs['progname'], config.global_confs['progversion']))

        self.mdi = QtWidgets.QMdiArea()  # create multiple document interface widget
        self.setCentralWidget(self.mdi)
        self.showMaximized()

        # Menu Bar
        spectral_menu = self.menuBar().addMenu('Spectroscopy')
        spectral_menu.addAction('Load Data')
        spectral_menu.addAction('Process Data')
        spectral_menu.addAction('Merge Results')
        spectral_menu.addAction('Explore')

        pv_menu = self.menuBar().addMenu('PV Measurements')
        pv_menu.addAction('Reference Analysis')
        pv_process = QtWidgets.QAction('Process Data', self)
        pv_process.triggered.connect(self.process_pv)
        pv_menu.addAction(pv_process)
        pv_merge = QtWidgets.QAction('Merge Results', self)
        pv_merge.triggered.connect(self.merge_pv)
        pv_menu.addAction(pv_merge)
        pv_explore = QtWidgets.QAction('Explore', self)
        pv_explore.triggered.connect(self.explore_pv)
        pv_menu.addAction(pv_explore)

        microscope_menu = self.menuBar().addMenu('Microscopy')
        microscope_menu.addAction('Load Images')

    def process_pv(self):
        process_pv_widget = ProcessPVWindow(self)
        self.mdi.addSubWindow(process_pv_widget)
        process_pv_widget.show()

    def merge_pv(self):
        merge_pv_widget = MergePVWindow(self)
        self.mdi.addSubWindow(merge_pv_widget)
        merge_pv_widget.show()

    def explore_pv(self):
        explore_pv_widget = ExplorePVWindow(self)
        self.mdi.addSubWindow(explore_pv_widget)
        explore_pv_widget.show()

    def closeEvent(self, *args, **kwargs):
        super(QtWidgets.QMainWindow, self).closeEvent(*args, **kwargs)

        config.write_config()
