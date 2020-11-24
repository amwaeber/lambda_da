from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from PyQt5 import QtCore, QtGui, QtWidgets

from user_interfaces.widgets.separator import Separator
from utility.colors import color_wheel
from utility.config import paths
from utility.corrections import reference_fit
from utility.dataframe_info import pv_explore_groups
import utility.globals as glob
from utility.load import load_global_df
from utility.process import pce_vs_reference


class ChangePVWindow(QtWidgets.QMdiSubWindow):

    def __init__(self, parent):
        super(ChangePVWindow, self).__init__(parent)

        self.Widget = ChangePVWidget(self)
        self.setWidget(self.Widget)
        self.setWindowTitle("Improvement over Matrix")
        self.setObjectName('IMPR_PV')


# noinspection PyAttributeOutsideInit
class ChangePVWidget(QtWidgets.QWidget):
    update_plot = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(ChangePVWidget, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("Determine the improvement/change in PCE vs blank matrix.", self))
        vbox.addWidget(QtWidgets.QLabel("1. Specify the file containing processed data. The PCE change"
                                        "will be added to the same file.", self))

        hbox_import = QtWidgets.QHBoxLayout()
        hbox_import.addWidget(QtWidgets.QLabel("File", self))
        file_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        file_button.clicked.connect(self.file_dialog)
        file_button.setToolTip('Choose processed data file')
        hbox_import.addWidget(file_button)
        self.file_edit = QtWidgets.QLineEdit(paths['pv_improve_file'], self)
        self.file_edit.setMinimumWidth(180)
        self.file_edit.setDisabled(True)
        hbox_import.addWidget(self.file_edit)
        load_button = QtWidgets.QPushButton("Load")
        hbox_import.addWidget(load_button)
        load_button.clicked.connect(self.load_data)
        hbox_import.addStretch(-1)
        vbox.addLayout(hbox_import)

        vbox.addWidget(Separator())
        self.load_edit = QtWidgets.QTextEdit("", self)
        vbox.addWidget(self.load_edit)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("2. Specify the groups that are to serve as a reference. Typically, these "
                                        "should be the \'blank matrix\' film sets.\n"
                                        "A linear fit along the specified axis is applied to serve as a baseline"
                                        "that the other films will be compared against.\n"
                                        "Separate group indices with commas", self))
        hbox_fit = QtWidgets.QHBoxLayout()
        hbox_fit.addWidget(QtWidgets.QLabel("Reference groups", self))
        ref_idx_edit = QtWidgets.QLineEdit('', self)
        ref_idx_edit.setFixedWidth(100)
        hbox_fit.addWidget(ref_idx_edit)
        hbox_fit.addWidget(QtWidgets.QLabel("Axis", self))
        xaxis_combobox = QtWidgets.QComboBox(self)
        xaxis_combobox.addItem("Thickness (mm)")
        xaxis_combobox.addItem("Tape Layers")
        hbox_fit.addWidget(xaxis_combobox)
        fit_button = QtWidgets.QPushButton("Fit reference")
        fit_button.clicked.connect(lambda: self.fit_reference(ref_idx_edit.text(),
                                                              xaxis_combobox.currentText()))
        hbox_fit.addWidget(fit_button)
        hbox_fit.addStretch(-1)
        vbox.addLayout(hbox_fit)

        vbox.addWidget(Separator())
        hbox_plot = QtWidgets.QHBoxLayout()
        self.plot_canvas = FigureCanvas(Figure(figsize=(8, 5)))
        self.plot_canvas.figure.tight_layout(pad=0.3)
        self.update_plot.connect(self.plot_canvas.figure.canvas.draw)
        hbox_plot.addWidget(self.plot_canvas)
        hbox_plot.addStretch(-1)
        vbox.addLayout(hbox_plot)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("3. Specify the groups that are to be analysed against the fitted baseline."
                                        "Separate group indices with commas.", self))
        hbox_corr = QtWidgets.QHBoxLayout()
        hbox_corr.addWidget(QtWidgets.QLabel("Film groups", self))
        grp_idx_edit = QtWidgets.QLineEdit('', self)
        grp_idx_edit.setFixedWidth(100)
        hbox_corr.addWidget(grp_idx_edit)
        calc_button = QtWidgets.QPushButton("Calculate")
        calc_button.clicked.connect(lambda: self.compare_to_reference(grp_idx_edit.text(),
                                                                      xaxis_combobox.currentText()))
        hbox_corr.addWidget(calc_button)
        hbox_corr.addStretch(-1)
        vbox.addLayout(hbox_corr)

        vbox.addStretch(-1)
        self.setLayout(vbox)

    def file_dialog(self):
        paths['pv_improve_file'] = str(QtWidgets.QFileDialog.getOpenFileName(self, 'Select File',
                                                                             paths['pv_improve_file'])[0])
        self.file_edit.setText(paths['pv_improve_file'])

    def load_data(self):
        load_global_df(paths['pv_improve_file'])
        group_info = pv_explore_groups(glob.df)
        self.load_edit.append("\t".join(['Grp', 'Matrix', 'QD Type', 'Emis.', 'QD Conc.', 'Solvent',
                                         'Addit.', 'Addit. conc.', 'Made', 'Measured']))
        for gp in group_info:
            self.load_edit.append("\t".join(gp[1:]))

    def fit_reference(self, text_string, xaxis):
        y_pred = reference_fit(eval('[' + text_string + ']'), xaxis)

        mask = glob.df['group'].isin(eval('[' + text_string + ']'))
        df_fit = glob.df[mask].sort_values(by=xaxis)

        self.plot_canvas.figure.clear()
        axes = [None, None, None]
        for i, key in zip(range(2), ['isc_eff', 'pmax_eff']):
            axes[i] = self.plot_canvas.figure.add_subplot(1, 2, i+1)
            axes[i].errorbar(df_fit[xaxis], df_fit[key], yerr=glob.df[mask][f"d{key}"],
                             ecolor=color_wheel[0], elinewidth=1.5, capsize=3,
                             color=color_wheel[1], lw=3, marker='s', ms=8)
            axes[i].plot(df_fit[xaxis], y_pred[i], color=color_wheel[2])
            axes[i].set_xlabel(xaxis)
            axes[i].set_ylabel(key)
        self.plot_canvas.figure.tight_layout(pad=0.3)
        self.plot_canvas.figure.savefig(os.path.join(os.path.dirname(paths['pv_improve_file']),
                                                     f"Matrix_fits_{'-'.join(text_string.split(','))}.png"))
        self.update_plot.emit()

    @staticmethod
    def compare_to_reference(text_string, xaxis):
        pce_vs_reference(eval('[' + text_string + ']'), xaxis)
