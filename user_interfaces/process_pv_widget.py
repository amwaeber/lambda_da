from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import os
from PyQt5 import QtCore, QtGui, QtWidgets
import seaborn as sns

from user_interfaces.widgets.separator import Separator
from utility.colors import color_wheel
from utility.config import paths, defaults, write_config
from utility.corrections import iv_temperature_correction, iv_irradiance_fit, iv_irradiance_correction
from utility.dataframe_edit import drop_experiments, select_experiment_range, merge_film_db
from utility.dataframe_info import df_info
import utility.globals as glob
from utility.load import load_experiments
from utility.plot import plot_ty
from utility.process import average_by_experiment, average_by, calc_efficiency

sns.set()


class ProcessPVWindow(QtWidgets.QMdiSubWindow):

    def __init__(self, parent):
        super(ProcessPVWindow, self).__init__(parent)

        self.Widget = ProcessPVWidget(self)
        self.setWidget(self.Widget)
        self.setWindowTitle("Process PV Data")
        self.setObjectName('PROC_PV')

    def closeEvent(self, *args, **kwargs):
        super(QtWidgets.QMdiSubWindow, self).closeEvent(*args, **kwargs)

        write_config()


# noinspection PyAttributeOutsideInit
class ProcessPVWidget(QtWidgets.QWidget):
    update_t_hist = QtCore.pyqtSignal()
    update_voc_t = QtCore.pyqtSignal()
    update_irrad = QtCore.pyqtSignal()
    update_time_dep = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(ProcessPVWidget, self).__init__(parent)

        hbox = QtWidgets.QHBoxLayout()
        self.Stack = QtWidgets.QStackedWidget(self)
        self.stack01_import = QtWidgets.QWidget()
        self.stack01_ui()
        self.Stack.addWidget(self.stack01_import)
        self.stack02_temperature = QtWidgets.QWidget()
        self.stack02_ui()
        self.Stack.addWidget(self.stack02_temperature)
        self.stack03_irradiance = QtWidgets.QWidget()
        self.stack03_ui()
        self.Stack.addWidget(self.stack03_irradiance)
        self.stack04_averaging = QtWidgets.QWidget()
        self.stack04_ui()
        self.Stack.addWidget(self.stack04_averaging)
        self.stack05_film = QtWidgets.QWidget()
        self.stack05_ui()
        self.Stack.addWidget(self.stack05_film)

        hbox.addWidget(self.Stack)
        self.setLayout(hbox)

    def stack01_ui(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("1. Import raw data: specify the root folder for the experiment series.", self))
        hbox_import = QtWidgets.QHBoxLayout()
        hbox_import.addWidget(QtWidgets.QLabel("Folder", self))
        folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        folder_button.clicked.connect(lambda: self.folder_dialog(path='last_import'))
        folder_button.setToolTip('Choose data folder')
        hbox_import.addWidget(folder_button)
        self.folder_edit = QtWidgets.QLineEdit(paths['last_import'], self)
        self.folder_edit.setMinimumWidth(180)
        self.folder_edit.setDisabled(True)
        hbox_import.addWidget(self.folder_edit)
        hbox_import.addStretch(-1)
        vbox.addLayout(hbox_import)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("2. Define output folder for results.", self))
        hbox_export = QtWidgets.QHBoxLayout()
        hbox_export.addWidget(QtWidgets.QLabel("Folder", self))
        save_folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        save_folder_button.clicked.connect(lambda: self.folder_dialog(path='last_export'))
        save_folder_button.setToolTip('Choose output folder')
        hbox_export.addWidget(save_folder_button)
        self.save_folder_edit = QtWidgets.QLineEdit(paths['last_export'], self)
        self.save_folder_edit.setMinimumWidth(180)
        self.save_folder_edit.setDisabled(True)
        hbox_export.addWidget(self.save_folder_edit)
        hbox_export.addStretch(-1)
        vbox.addLayout(hbox_export)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("3. Load the IV data into the data frame and generate a summary Excel sheet.",
                                        self))
        hbox_load = QtWidgets.QHBoxLayout()
        load_button = QtWidgets.QPushButton("Load Data")
        hbox_load.addWidget(load_button)
        hbox_load.addWidget(QtWidgets.QLabel("Overwrite Summary", self))
        overwrite_cbox = QtWidgets.QCheckBox()
        overwrite_cbox.setChecked(defaults['process_pv'][0])
        hbox_load.addWidget(overwrite_cbox)
        load_button.clicked.connect(lambda: self.load_data(path=paths['last_import'],
                                                           overwrite=overwrite_cbox.isChecked()))
        hbox_load.addStretch(-1)
        vbox.addLayout(hbox_load)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("4. Specify experiment numbers to be excluded from analysis.\n"
                                        "Separate experiments with commas.", self))
        hbox_drop = QtWidgets.QHBoxLayout()
        hbox_drop.addWidget(QtWidgets.QLabel("Experiment No", self))
        drop_id_edit = QtWidgets.QLineEdit('', self)
        drop_id_edit.setFixedWidth(100)
        hbox_drop.addWidget(drop_id_edit)
        exclude_button = QtWidgets.QPushButton("Exclude")
        exclude_button.clicked.connect(lambda: self.exclude_data(drop_id_edit.text()))
        hbox_drop.addWidget(exclude_button)
        hbox_drop.addStretch(-1)
        vbox.addLayout(hbox_drop)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("5. Specify experiment ID range to be included in analysis.", self))
        hbox_range = QtWidgets.QHBoxLayout()
        hbox_range.addWidget(QtWidgets.QLabel("Min", self))
        min_id_edit = QtWidgets.QLineEdit('1', self)
        min_id_edit.setFixedWidth(40)
        hbox_range.addWidget(min_id_edit)
        max_id_edit = QtWidgets.QLineEdit('999', self)
        max_id_edit.setFixedWidth(40)
        hbox_range.addWidget(max_id_edit)
        range_button = QtWidgets.QPushButton("Select Range")
        range_button.clicked.connect(lambda: self.select_range(int(min_id_edit.text()), int(max_id_edit.text())))
        hbox_range.addWidget(range_button)
        hbox_range.addStretch(-1)
        vbox.addLayout(hbox_range)

        vbox.addWidget(Separator())
        self.load_edit = QtWidgets.QTextEdit("", self)
        vbox.addWidget(self.load_edit)

        hbox_back_next = QtWidgets.QHBoxLayout()
        hbox_back_next.addStretch(-1)
        forward_button = QtWidgets.QPushButton("Next >>")
        forward_button.clicked.connect(lambda: self.Stack.setCurrentIndex(1))
        hbox_back_next.addWidget(forward_button)
        vbox.addLayout(hbox_back_next)

        self.stack01_import.setLayout(vbox)

    def stack02_ui(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("6. Check temperature as measured by thermistor.\n"
                                        "Specify the name of the repeat baseline measurement.", self))
        hbox_show_temp = QtWidgets.QHBoxLayout()
        hbox_show_temp.addWidget(QtWidgets.QLabel("Baseline name", self))
        baseline_edit = QtWidgets.QLineEdit(defaults['process_pv'][1], self)
        baseline_edit.setFixedWidth(100)
        hbox_show_temp.addWidget(baseline_edit)
        show_button = QtWidgets.QPushButton("Show")
        show_button.clicked.connect(lambda: self.show_t_data(baseline_edit.text()))
        hbox_show_temp.addWidget(show_button)
        hbox_show_temp.addStretch(-1)
        vbox.addLayout(hbox_show_temp)

        vbox.addWidget(Separator())
        hbox_plot = QtWidgets.QHBoxLayout()
        self.t_hist_canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self.t_hist_canvas.figure.tight_layout(pad=0.3)
        self.update_t_hist.connect(self.t_hist_canvas.figure.canvas.draw)
        hbox_plot.addWidget(self.t_hist_canvas)
        self.voc_t_canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self.voc_t_canvas.figure.tight_layout(pad=0.3)
        self.update_voc_t.connect(self.voc_t_canvas.figure.canvas.draw)
        hbox_plot.addWidget(self.voc_t_canvas)
        hbox_plot.addStretch(-1)
        vbox.addLayout(hbox_plot)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("7. Apply temperature correction if the data looks sensible.\n"
                                        "Temperature and Voc are roughly linearly proportional, high Temp "
                                        "corresponding to low Voc.\n"
                                        "However, Voc is also dependent on the irradiance (next step), so if in doubt,"
                                        "apply the temperature correction.", self))
        hbox_apply_temp = QtWidgets.QHBoxLayout()
        temp_corr_button = QtWidgets.QPushButton("Correct to 25 C")
        hbox_apply_temp.addWidget(temp_corr_button)
        hbox_apply_temp.addWidget(QtWidgets.QLabel("Overwrite Existing", self))
        overwrite_cbox = QtWidgets.QCheckBox()
        overwrite_cbox.setChecked(defaults['process_pv'][2])
        hbox_apply_temp.addWidget(overwrite_cbox)
        temp_corr_button.clicked.connect(lambda: self.apply_temp_corr(overwrite=overwrite_cbox.isChecked()))
        hbox_apply_temp.addStretch(-1)
        vbox.addLayout(hbox_apply_temp)
        vbox.addStretch(-1)

        hbox_back_next = QtWidgets.QHBoxLayout()
        back_button = QtWidgets.QPushButton("<< Previous")
        back_button.clicked.connect(lambda: self.Stack.setCurrentIndex(0))
        hbox_back_next.addWidget(back_button)
        hbox_back_next.addStretch(-1)
        forward_button = QtWidgets.QPushButton("Next >>")
        forward_button.clicked.connect(lambda: self.Stack.setCurrentIndex(2))
        hbox_back_next.addWidget(forward_button)
        vbox.addLayout(hbox_back_next)

        self.stack02_temperature.setLayout(vbox)

    def stack03_ui(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("8. Attempt irradiance fit.", self))
        hbox_show_irrad = QtWidgets.QHBoxLayout()
        hbox_show_irrad.addWidget(QtWidgets.QLabel("Baseline name", self))
        baseline_edit = QtWidgets.QLineEdit(defaults['process_pv'][1], self)
        baseline_edit.setFixedWidth(100)
        hbox_show_irrad.addWidget(baseline_edit)
        hbox_show_irrad.addWidget(QtWidgets.QLabel("Diode #", self))
        diode_edit = QtWidgets.QLineEdit(str(defaults['process_pv'][3]), self)
        diode_edit.setFixedWidth(40)
        hbox_show_irrad.addWidget(diode_edit)
        show_button = QtWidgets.QPushButton("Show")
        show_button.clicked.connect(lambda: self.show_irrad_data(baseline_edit.text(), diode_edit.text()))
        hbox_show_irrad.addWidget(show_button)
        hbox_show_irrad.addStretch(-1)
        vbox.addLayout(hbox_show_irrad)

        vbox.addWidget(Separator())
        hbox_plot = QtWidgets.QHBoxLayout()
        self.irrad_canvas = FigureCanvas(Figure(figsize=(12, 5)))
        self.irrad_canvas.figure.tight_layout(pad=0.3)
        self.update_irrad.connect(self.irrad_canvas.figure.canvas.draw)
        hbox_plot.addWidget(self.irrad_canvas)
        hbox_plot.addStretch(-1)
        vbox.addLayout(hbox_plot)

        hbox_fit_pars = QtWidgets.QHBoxLayout()
        hbox_fit_pars.addWidget(QtWidgets.QLabel("Isc = ", self))
        self.isc_edit = QtWidgets.QLineEdit("", self)
        self.isc_edit.setFixedWidth(200)
        self.isc_edit.setDisabled(True)
        hbox_fit_pars.addWidget(self.isc_edit)
        hbox_fit_pars.addWidget(QtWidgets.QLabel("Voc = ", self))
        self.voc_edit = QtWidgets.QLineEdit("", self)
        self.voc_edit.setFixedWidth(200)
        self.voc_edit.setDisabled(True)
        hbox_fit_pars.addWidget(self.voc_edit)
        hbox_fit_pars.addWidget(QtWidgets.QLabel("Pmax = ", self))
        self.pmax_edit = QtWidgets.QLineEdit("", self)
        self.pmax_edit.setFixedWidth(200)
        self.pmax_edit.setDisabled(True)
        hbox_fit_pars.addWidget(self.pmax_edit)
        hbox_fit_pars.addStretch(-1)
        vbox.addLayout(hbox_fit_pars)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("9. Apply irradiance correction if the data looks sensible.\n"
                                        "Irradiance and Isc/Pmax are roughly linearly proportional, high irradiance "
                                        "corresponding to high Isc/Pmax.\n"
                                        "If there are big jumps in the data, try another photodiode or skip this "
                                        "correction step.\n"
                                        "Individual experiment IDs can also be excluded in step 3 (repeat from"
                                        "the start).", self))
        hbox_apply_irrad = QtWidgets.QHBoxLayout()
        hbox_apply_irrad.addWidget(QtWidgets.QLabel("Diode #", self))
        diode_at_1sun = QtWidgets.QLineEdit(str(defaults['process_pv'][4]), self)
        diode_at_1sun.setFixedWidth(60)
        hbox_apply_irrad.addWidget(diode_at_1sun)
        irrad_corr_button = QtWidgets.QPushButton("Correct to 1 sun")
        hbox_apply_irrad.addWidget(irrad_corr_button)
        hbox_apply_irrad.addWidget(QtWidgets.QLabel("Overwrite Existing", self))
        overwrite_cbox = QtWidgets.QCheckBox()
        overwrite_cbox.setChecked(defaults['process_pv'][5])
        hbox_apply_irrad.addWidget(overwrite_cbox)
        irrad_corr_button.clicked.connect(lambda: self.apply_irrad_corr(channel=diode_edit.text(),
                                                                        one_sun=diode_at_1sun.text(),
                                                                        overwrite=overwrite_cbox.isChecked()))
        hbox_apply_irrad.addStretch(-1)
        vbox.addLayout(hbox_apply_irrad)
        vbox.addStretch(-1)

        hbox_back_next = QtWidgets.QHBoxLayout()
        back_button = QtWidgets.QPushButton("<< Previous")
        back_button.clicked.connect(lambda: self.Stack.setCurrentIndex(1))
        hbox_back_next.addWidget(back_button)
        hbox_back_next.addStretch(-1)
        forward_button = QtWidgets.QPushButton("Next >>")
        forward_button.clicked.connect(lambda: self.Stack.setCurrentIndex(3))
        hbox_back_next.addWidget(forward_button)
        vbox.addLayout(hbox_back_next)

        self.stack03_irradiance.setLayout(vbox)

    def stack04_ui(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("10. Average by experiment. Produces an average and standard deviation"
                                        "value for Isc, Voc, and Pmax for each experiment.", self))
        hbox_avg_exp = QtWidgets.QHBoxLayout()
        avg_exp_button = QtWidgets.QPushButton("Average Experiment")
        hbox_avg_exp.addWidget(avg_exp_button)
        hbox_avg_exp.addWidget(QtWidgets.QLabel("Overwrite Existing", self))
        overwrite_avg_exp_cbox = QtWidgets.QCheckBox()
        overwrite_avg_exp_cbox.setChecked(defaults['process_pv'][6])
        hbox_avg_exp.addWidget(overwrite_avg_exp_cbox)
        avg_exp_button.clicked.connect(lambda: self.avg_exp_data(overwrite=overwrite_avg_exp_cbox.isChecked()))
        hbox_avg_exp.addStretch(-1)
        vbox.addLayout(hbox_avg_exp)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("11. Check time dependent behaviour of baseline (or any other "
                                        "film that was measured repeatedly.", self))
        hbox_show_time = QtWidgets.QHBoxLayout()
        hbox_show_time.addWidget(QtWidgets.QLabel("Baseline name", self))
        baseline_edit = QtWidgets.QLineEdit(defaults['process_pv'][7], self)
        baseline_edit.setFixedWidth(100)
        hbox_show_time.addWidget(baseline_edit)
        hbox_show_time.addWidget(QtWidgets.QLabel("Y-axis", self))
        yaxis_combobox = QtWidgets.QComboBox(self)
        yaxis_combobox.addItem("pmax")
        yaxis_combobox.addItem("isc")
        hbox_show_time.addWidget(yaxis_combobox)
        show_button = QtWidgets.QPushButton("Show")
        show_button.clicked.connect(lambda: self.show_avg_exp_data(baseline_edit.text(), yaxis_combobox.currentText()))
        hbox_show_time.addWidget(show_button)
        hbox_show_time.addStretch(-1)
        vbox.addLayout(hbox_show_time)

        vbox.addWidget(Separator())
        hbox_plot = QtWidgets.QHBoxLayout()
        self.time_canvas = FigureCanvas(Figure(figsize=(6, 5)))
        self.time_canvas.figure.tight_layout(pad=0.3)
        self.update_time_dep.connect(self.time_canvas.figure.canvas.draw)
        hbox_plot.addWidget(self.time_canvas)
        hbox_plot.addStretch(-1)
        vbox.addLayout(hbox_plot)
        vbox.addStretch(-1)

        hbox_back_next = QtWidgets.QHBoxLayout()
        back_button = QtWidgets.QPushButton("<< Previous")
        back_button.clicked.connect(lambda: self.Stack.setCurrentIndex(2))
        hbox_back_next.addWidget(back_button)
        hbox_back_next.addStretch(-1)
        forward_button = QtWidgets.QPushButton("Next >>")
        forward_button.clicked.connect(lambda: self.Stack.setCurrentIndex(4))
        hbox_back_next.addWidget(forward_button)
        vbox.addLayout(hbox_back_next)

        self.stack04_averaging.setLayout(vbox)

    def stack05_ui(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("12. Average by experiment name or film ID. Combines repeat measurements of "
                                        "the same film into one datapoint.\n"
                                        "If measurements with the same film ID but different names are not to be "
                                        "combined, select \'name\'.", self))
        hbox_avg_film = QtWidgets.QHBoxLayout()
        hbox_avg_film.addWidget(QtWidgets.QLabel("Average by", self))
        avg_by_combobox = QtWidgets.QComboBox(self)
        avg_by_combobox.addItem("name")
        avg_by_combobox.addItem("film_id")
        hbox_avg_film.addWidget(avg_by_combobox)
        avg_exp_button = QtWidgets.QPushButton("Average Film")
        hbox_avg_film.addWidget(avg_exp_button)
        hbox_avg_film.addWidget(QtWidgets.QLabel("Overwrite Existing", self))
        overwrite_avg_film_cbox = QtWidgets.QCheckBox()
        overwrite_avg_film_cbox.setChecked(defaults['process_pv'][8])
        hbox_avg_film.addWidget(overwrite_avg_film_cbox)
        avg_exp_button.clicked.connect(lambda: self.avg_film_data(col_name=avg_by_combobox.currentText(),
                                                                  overwrite=overwrite_avg_film_cbox.isChecked()))
        hbox_avg_film.addStretch(-1)
        vbox.addLayout(hbox_avg_film)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("13. Calculate change in Pmax/PCE compared to the baseline or another "
                                        "specified reference film.", self))
        hbox_efficiency = QtWidgets.QHBoxLayout()
        hbox_efficiency.addWidget(QtWidgets.QLabel("Baseline name", self))
        baseline_edit = QtWidgets.QLineEdit(defaults['process_pv'][9], self)
        baseline_edit.setFixedWidth(100)
        hbox_efficiency.addWidget(baseline_edit)
        efficiency_button = QtWidgets.QPushButton("Calculate")
        hbox_efficiency.addWidget(efficiency_button)
        hbox_efficiency.addWidget(QtWidgets.QLabel("Overwrite Existing", self))
        overwrite_eff_cbox = QtWidgets.QCheckBox()
        overwrite_eff_cbox.setChecked(defaults['process_pv'][10])
        hbox_efficiency.addWidget(overwrite_eff_cbox)
        efficiency_button.clicked.connect(lambda: self.efficiency_data(name=baseline_edit.text(),
                                                                       overwrite=overwrite_eff_cbox.isChecked()))
        hbox_efficiency.addStretch(-1)
        vbox.addLayout(hbox_efficiency)

        vbox.addWidget(Separator())
        vbox.addWidget(QtWidgets.QLabel("14. Merge processed data with film information. Specify the location of the "
                                        "film database, then merge by ID.", self))
        hbox_import = QtWidgets.QHBoxLayout()
        hbox_import.addWidget(QtWidgets.QLabel("Film DB", self))
        folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        folder_button.clicked.connect(self.file_dialog)
        folder_button.setToolTip('Choose film database')
        hbox_import.addWidget(folder_button)
        self.film_path_edit = QtWidgets.QLineEdit(paths['film_db'], self)
        self.film_path_edit.setMinimumWidth(180)
        self.film_path_edit.setDisabled(True)
        hbox_import.addWidget(self.film_path_edit)
        merge_button = QtWidgets.QPushButton("Merge")
        hbox_import.addWidget(merge_button)
        hbox_import.addWidget(QtWidgets.QLabel("Overwrite Existing", self))
        overwrite_merge_cbox = QtWidgets.QCheckBox()
        overwrite_merge_cbox.setChecked(defaults['process_pv'][11])
        hbox_import.addWidget(overwrite_merge_cbox)
        merge_button.clicked.connect(lambda: self.merge_film_data(overwrite=overwrite_merge_cbox.isChecked()))
        hbox_import.addStretch(-1)
        vbox.addLayout(hbox_import)
        vbox.addStretch(-1)

        hbox_back_next = QtWidgets.QHBoxLayout()
        back_button = QtWidgets.QPushButton("<< Previous")
        back_button.clicked.connect(lambda: self.Stack.setCurrentIndex(3))
        hbox_back_next.addWidget(back_button)
        hbox_back_next.addStretch(-1)
        vbox.addLayout(hbox_back_next)

        self.stack05_film.setLayout(vbox)

    def folder_dialog(self, path):
        paths[path] = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory', paths[path]))
        if path == 'last_import':
            self.folder_edit.setText(paths[path])
        elif path == 'last_export':
            self.save_folder_edit.setText(paths[path])

    def load_data(self, path, overwrite):
        defaults['process_pv'][0] = overwrite

        load_experiments(path, overwrite)
        self.load_edit.append(df_info(glob.df))

    @staticmethod
    def exclude_data(text_string):
        drop_experiments(eval('[' + text_string + ']'))

    @staticmethod
    def select_range(idxmin, idxmax):
        select_experiment_range(idxmin, idxmax)

    def show_t_data(self, baseline):
        defaults['process_pv'][1] = baseline

        self.t_hist_canvas.figure.clear()
        t_hist_ax = self.t_hist_canvas.figure.add_subplot(111)
        t_hist_ax.hist(glob.df['t_sample'], bins=20, color=color_wheel[1])
        t_hist_ax.set_xlabel(r'Temperature ($^o$C)')
        t_hist_ax.set_ylabel("Counts")
        self.t_hist_canvas.figure.tight_layout(pad=0.3)
        self.t_hist_canvas.figure.savefig(os.path.join(paths['last_export'], 'Temp_histogram.png'))
        self.update_t_hist.emit()

        self.voc_t_canvas.figure.clear()
        voc_t_ax = self.voc_t_canvas.figure.add_subplot(111)
        mask = glob.df['name'] == baseline
        voc_t_ax.scatter(glob.df[mask]['t_sample'], glob.df[mask]['voc_fit'], color=color_wheel[2], s=6)
        voc_t_ax.set_xlabel(r'Temperature ($^o$C)')
        voc_t_ax.set_ylabel("Voc (V)")
        self.voc_t_canvas.figure.tight_layout(pad=0.3)
        self.voc_t_canvas.figure.savefig(os.path.join(paths['last_export'], 'Temp_vs_Voc.png'))
        self.update_voc_t.emit()

        plot_ty(baseline, 't_sample')

    @staticmethod
    def apply_temp_corr(overwrite):
        defaults['process_pv'][2] = overwrite
        iv_temperature_correction(overwrite)

    def show_irrad_data(self, baseline, channel):
        defaults['process_pv'][1] = baseline
        defaults['process_pv'][3] = channel

        y_pred = iv_irradiance_fit(baseline, channel)
        mask = glob.df['name'] == baseline

        self.irrad_canvas.figure.clear()
        axes = [None, None, None]
        for i, key in zip(range(3), ['isc_fit', 'voc_fit', 'pmax_fit']):
            axes[i] = self.irrad_canvas.figure.add_subplot(1, 3, i+1)
            glob.df[mask].dropna().plot(x=f'irrad{channel}', y=key, kind='scatter', s=8,
                                        color=color_wheel[1], ax=axes[i])
            axes[i].plot(glob.df[mask][f'irrad{channel}'], y_pred[i], color=color_wheel[2])
            axes[i].set_xlabel(f'irrad{channel}')
            axes[i].set_ylabel(key)
        self.irrad_canvas.figure.tight_layout(pad=0.3)
        self.irrad_canvas.figure.savefig(os.path.join(paths['last_export'], 'Irradiance_fits.png'))
        self.update_irrad.emit()

        plot_ty(baseline, f'irrad{channel}')

        self.isc_edit.setText(f"{glob.irrad_fit_pars[0][0]:.2f} * irrad{channel} + {glob.irrad_fit_pars[0][1]:.2f}")
        self.voc_edit.setText(f"{glob.irrad_fit_pars[1][0]:.2f} * irrad{channel} + {glob.irrad_fit_pars[1][1]:.2f}")
        self.pmax_edit.setText(f"{glob.irrad_fit_pars[2][0]:.2f} * irrad{channel} + {glob.irrad_fit_pars[2][1]:.2f}")

    @staticmethod
    def apply_irrad_corr(channel, one_sun, overwrite):
        defaults['process_pv'][3] = channel
        defaults['process_pv'][4] = one_sun
        defaults['process_pv'][5] = overwrite
        iv_irradiance_correction(channel, float(one_sun), overwrite)

    @staticmethod
    def avg_exp_data(overwrite):
        defaults['process_pv'][6] = overwrite
        average_by_experiment(overwrite)

    def show_avg_exp_data(self, name, yaxis_name):
        defaults['process_pv'][7] = name

        mask = glob.df['name'] == name

        self.time_canvas.figure.clear()
        ax = self.time_canvas.figure.add_subplot(111)
        ax.errorbar(glob.df[mask]['datetime'], glob.df[mask][yaxis_name], yerr=glob.df[mask][f"d{yaxis_name}"],
                    ecolor=color_wheel[0], elinewidth=1.5, capsize=3,
                    color=color_wheel[1], lw=3, marker='s', ms=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.set_xlabel('Time (hs)')
        ax.set_ylabel(yaxis_name)
        self.time_canvas.figure.tight_layout(pad=0.3)
        self.time_canvas.figure.savefig(os.path.join(paths['last_export'], f'{name}_time_vs_{yaxis_name}.png'))
        self.update_time_dep.emit()

    @staticmethod
    def avg_film_data(col_name, overwrite):
        defaults['process_pv'][8] = overwrite
        average_by(col_name, overwrite)

    @staticmethod
    def efficiency_data(name, overwrite):
        defaults['process_pv'][9] = name
        defaults['process_pv'][10] = overwrite
        calc_efficiency(name, overwrite)

    def file_dialog(self):
        paths['film_db'] = str(QtWidgets.QFileDialog.getOpenFileName(self, 'Select Film', paths['film_db'])[0])
        self.film_path_edit.setText(paths['film_db'])

    @staticmethod
    def merge_film_data(overwrite):
        defaults['process_pv'][11] = overwrite
        merge_film_db(overwrite)
