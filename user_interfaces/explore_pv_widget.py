from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from PyQt5 import QtCore, QtGui, QtWidgets
import seaborn as sns

from user_interfaces.widgets.separator import Separator
from user_interfaces.widgets.treewidgetitem import ItemSignal, TreeWidgetItem
from utility.colors import color_wheel
from utility.config import paths, write_config
from utility.dataframe_info import pv_explore_groups
import utility.globals as glob
from utility.load import load_global_df

sns.set()


class ExplorePVWindow(QtWidgets.QMdiSubWindow):

    def __init__(self, parent):
        super(ExplorePVWindow, self).__init__(parent)

        self.Widget = ExplorePVWidget(self)
        self.setWidget(self.Widget)
        self.setWindowTitle("Explore PV Data")
        self.setObjectName('EXPL_PV')

    def closeEvent(self, *args, **kwargs):
        super(QtWidgets.QMdiSubWindow, self).closeEvent(*args, **kwargs)

        write_config()


# noinspection PyAttributeOutsideInit
class ExplorePVWidget(QtWidgets.QWidget):
    update_plot = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(ExplorePVWidget, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        hbox = QtWidgets.QHBoxLayout()
        vbox_graph = QtWidgets.QVBoxLayout()
        self.plot_canvas = FigureCanvas(Figure(figsize=(7, 7)))
        self.plot_canvas.figure.tight_layout(pad=0.3)
        self.update_plot.connect(self.plot_canvas.figure.canvas.draw)
        vbox_graph.addWidget(self.plot_canvas)
        vbox_graph.addStretch(-1)
        hbox.addLayout(vbox_graph)

        vbox = QtWidgets.QVBoxLayout()
        hbox_load = QtWidgets.QHBoxLayout()
        hbox_load.addWidget(QtWidgets.QLabel("Load file", self))
        file_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        file_button.clicked.connect(self.file_dialog)
        file_button.setToolTip('Choose processed data file')
        hbox_load.addWidget(file_button)
        self.file_edit = QtWidgets.QLineEdit(paths['pv_explore_in'], self)
        self.file_edit.setMinimumWidth(180)
        self.file_edit.setDisabled(True)
        hbox_load.addWidget(self.file_edit)
        load_button = QtWidgets.QPushButton("Load")
        hbox_load.addWidget(load_button)
        load_button.clicked.connect(self.load_data)
        hbox_load.addStretch(-1)
        vbox.addLayout(hbox_load)
        hbox_save = QtWidgets.QHBoxLayout()
        hbox_save.addWidget(QtWidgets.QLabel("Results folder", self))
        folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        folder_button.clicked.connect(self.folder_dialog)
        folder_button.setToolTip('Choose folder for results')
        hbox_save.addWidget(folder_button)
        self.folder_edit = QtWidgets.QLineEdit(paths['pv_explore_out'], self)
        self.folder_edit.setMinimumWidth(180)
        self.folder_edit.setDisabled(True)
        hbox_save.addWidget(self.folder_edit)
        hbox_save.addStretch(-1)
        vbox.addLayout(hbox_save)
        hbox_fname = QtWidgets.QHBoxLayout()
        hbox_fname.addWidget(QtWidgets.QLabel("Save file name", self))
        self.fname_edit = QtWidgets.QLineEdit('Graph', self)
        self.fname_edit.setMinimumWidth(80)
        hbox_fname.addWidget(self.fname_edit)
        save_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'save.png')), '')
        save_button.clicked.connect(self.save_image)
        save_button.setToolTip('Save current graph')
        hbox_fname.addWidget(save_button)
        clipboard_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'clipboard.png')), '')
        clipboard_button.clicked.connect(self.clipboard)
        clipboard_button.setToolTip('Save current graph to clipboard')
        hbox_fname.addWidget(clipboard_button)
        hbox_fname.addStretch(-1)
        vbox.addLayout(hbox_fname)

        vbox.addWidget(Separator())
        self.group_list = QtWidgets.QTreeWidget()
        self.group_list.setRootIsDecorated(False)
        self.group_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.group_list.setHeaderLabels(["Plot", "Group", "Matrix", "QDs", "QD Wl.", "QD Conc.", "Solvent",
                                         "Additives", "Add. Conc.", "Made", "Measured"])
        self.group_list.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.group_list.setSortingEnabled(True)
        vbox.addWidget(self.group_list)

        vbox.addWidget(Separator())
        hbox_xy = QtWidgets.QHBoxLayout()
        hbox_xy.addWidget(QtWidgets.QLabel("X-axis", self))
        xaxis_combobox = QtWidgets.QComboBox(self)
        xaxis_combobox.addItem("Thickness (mm)")
        xaxis_combobox.addItem("Tape Layers")
        hbox_xy.addWidget(xaxis_combobox)
        hbox_xy.addWidget(QtWidgets.QLabel("Y-axis", self))
        yaxis_combobox = QtWidgets.QComboBox(self)
        yaxis_combobox.addItem("pmax")
        yaxis_combobox.addItem("isc")
        yaxis_combobox.addItem("voc")
        yaxis_combobox.addItem("pmax_eff")
        yaxis_combobox.addItem("isc_eff")
        yaxis_combobox.addItem("pmax_impr")
        yaxis_combobox.addItem("isc_impr")
        hbox_xy.addWidget(yaxis_combobox)
        hbox_xy.addStretch(-1)
        vbox.addLayout(hbox_xy)

        hbox_lims = QtWidgets.QHBoxLayout()
        hbox_lims.addWidget(QtWidgets.QLabel("Xmin", self))
        xmin_edit = QtWidgets.QLineEdit('', self)
        xmin_edit.setMinimumWidth(20)
        hbox_lims.addWidget(xmin_edit)
        hbox_lims.addWidget(QtWidgets.QLabel("Xmax", self))
        xmax_edit = QtWidgets.QLineEdit('', self)
        xmax_edit.setMinimumWidth(20)
        hbox_lims.addWidget(xmax_edit)
        hbox_lims.addWidget(QtWidgets.QLabel("Ymin", self))
        ymin_edit = QtWidgets.QLineEdit('', self)
        ymin_edit.setMinimumWidth(20)
        hbox_lims.addWidget(ymin_edit)
        hbox_lims.addWidget(QtWidgets.QLabel("Ymax", self))
        ymax_edit = QtWidgets.QLineEdit('', self)
        ymax_edit.setMinimumWidth(20)
        hbox_lims.addWidget(ymax_edit)
        hbox_lims.addStretch(-1)
        vbox.addLayout(hbox_lims)

        hbox_labels = QtWidgets.QHBoxLayout()
        hbox_labels.addWidget(QtWidgets.QLabel("X Label", self))
        xlabel_edit = QtWidgets.QLineEdit('', self)
        xlabel_edit.setMinimumWidth(80)
        hbox_labels.addWidget(xlabel_edit)
        hbox_labels.addWidget(QtWidgets.QLabel("Y Label", self))
        ylabel_edit = QtWidgets.QLineEdit('', self)
        ylabel_edit.setMinimumWidth(80)
        hbox_labels.addWidget(ylabel_edit)
        hbox_labels.addStretch(-1)
        vbox.addLayout(hbox_labels)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("Include in legend:", self))
        hbox_grid = QtWidgets.QHBoxLayout()
        grid_legend_items = QtWidgets.QGridLayout()
        leg_matrix_cb = QtWidgets.QCheckBox('Matrix')
        grid_legend_items.addWidget(leg_matrix_cb, 0, 0)
        leg_qd_cb = QtWidgets.QCheckBox('QDs')
        grid_legend_items.addWidget(leg_qd_cb, 0, 1)
        leg_qdwl_cb = QtWidgets.QCheckBox('QD Wavel.')
        grid_legend_items.addWidget(leg_qdwl_cb, 0, 2)
        leg_qdconc_cb = QtWidgets.QCheckBox('QD Conc.')
        grid_legend_items.addWidget(leg_qdconc_cb, 0, 3)
        leg_solvent_cb = QtWidgets.QCheckBox('Solvent')
        grid_legend_items.addWidget(leg_solvent_cb, 1, 0)
        leg_add_cb = QtWidgets.QCheckBox('Additives')
        grid_legend_items.addWidget(leg_add_cb, 1, 1)
        leg_addconc_cb = QtWidgets.QCheckBox('Add. Conc.')
        grid_legend_items.addWidget(leg_addconc_cb, 1, 2)
        hbox_grid.addLayout(grid_legend_items)
        hbox_grid.addStretch(-1)
        vbox.addLayout(hbox_grid)

        vbox.addWidget(Separator())
        hbox_plot = QtWidgets.QHBoxLayout()
        plot_button = QtWidgets.QPushButton("Plot")
        plot_button.clicked.connect(lambda: self.plot(groups=self.selected_groups(),
                                                      xaxis=xaxis_combobox.currentText(),
                                                      yaxis=yaxis_combobox.currentText(),
                                                      xlabel=xlabel_edit.text(),
                                                      ylabel=ylabel_edit.text(),
                                                      xlim=[xmin_edit.text(), xmax_edit.text()],
                                                      ylim=[ymin_edit.text(), ymax_edit.text()],
                                                      legend=[leg_matrix_cb.isChecked(), leg_qd_cb.isChecked(),
                                                              leg_qdwl_cb.isChecked(), leg_qdconc_cb.isChecked(),
                                                              leg_solvent_cb.isChecked(), leg_add_cb.isChecked(),
                                                              leg_addconc_cb.isChecked()]))
        hbox_plot.addWidget(plot_button)
        hbox_plot.addStretch(-1)
        vbox.addLayout(hbox_plot)

        vbox.addStretch(-1)
        hbox.addLayout(vbox)
        self.setLayout(hbox)

    def file_dialog(self):
        paths['pv_explore_in'] = str(QtWidgets.QFileDialog.getOpenFileName(self, 'Select Data',
                                                                           paths['pv_explore_in'])[0])
        self.file_edit.setText(paths['pv_explore_in'])

    def folder_dialog(self):
        paths['pv_explore_out'] = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                                 paths['pv_explore_out']))
        self.folder_edit.setText(paths['pv_explore_out'])

    def save_image(self):
        path = os.path.join(paths['pv_explore_out'], f'{self.fname_edit.text()}.png')
        i = 1
        while os.path.isfile(path):
            path = os.path.join(paths['pv_explore_out'], f'{self.fname_edit.text()}({i}).png')
            i += 1
        self.plot_canvas.figure.savefig(path)

    def clipboard(self):
        pixmap = QtWidgets.QWidget.grab(self.plot_canvas)
        QtWidgets.QApplication.clipboard().setPixmap(pixmap)

    def load_data(self):
        load_global_df(paths['pv_explore_in'])
        self.update_groups()

    def update_groups(self):
        self.group_list.clear()
        entries = pv_explore_groups(glob.df)
        for entry in entries:
            group_item = TreeWidgetItem(ItemSignal(), self.group_list, entry)
            group_item.setToolTip(1, entry[1])
            group_item.setCheckState(0, QtCore.Qt.Unchecked)

    def selected_groups(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.group_list)
        groups = list()
        while iterator.value():
            item = iterator.value()
            if item.checkState(0):
                groups.append(item.toolTip(1))
            iterator += 1
        return groups

    def plot(self, groups, xaxis, yaxis, xlabel, ylabel, xlim, ylim, legend):
        self.plot_canvas.figure.clear()
        ax = self.plot_canvas.figure.add_subplot(111)
        for i, group in enumerate(groups):
            df = glob.df[glob.df['group'] == int(group)].sort_values(by=xaxis)
            ls = '--' if df['QD Type'].mode()[0] == 'None' else '-'
            label = self.create_legend(df, legend)
            ax.fill_between(df[xaxis],
                            df[yaxis] - df[f"d{yaxis}"],
                            df[yaxis] + df[f"d{yaxis}"],
                            color=color_wheel[i], alpha=.1)
            ax.plot(df[xaxis], df[yaxis], color=color_wheel[i], lw=3, ls=ls,
                    marker='s', markersize=8, label=label)
        if any(legend):
            ax.legend()
        elif ax.get_legend():
            ax.get_legend().remove()
        if all(xlim):
            ax.set_xlim(float(xlim[0]), float(xlim[1]))
        if all(ylim):
            ax.set_ylim(float(ylim[0]), float(ylim[1]))
        ax.set_xlabel(xlabel if xlabel else xaxis)
        ax.set_ylabel(ylabel if ylabel else yaxis)
        self.plot_canvas.figure.tight_layout(pad=0.3)
        self.update_plot.emit()

    @staticmethod
    def create_legend(dframe, legend):
        label = list()
        for show, col in zip(legend, ['Matrix', 'QD Type', 'Nominal Emission (nm)', 'QD Concentration (mg/g)',
                                      'Solvent', 'Additives', 'Additive concentration (%)']):
            if show:
                label.append(str(dframe[col].fillna('None').mode()[0]))
        return " ".join(label)
