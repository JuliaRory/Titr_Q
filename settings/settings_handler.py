
from dataclasses import is_dataclass
import json
from dataclasses import asdict

from PyQt5.QtWidgets import QWidget
from numpy import sqrt

class SettingsHandler:
    """
    «Связующее звено» между UI и логикой processing:
    -- Слушает изменения в UI.
    -- Обновляет соответствующие поля в Settings.
    -- Вызывает методы DataProcessor, PlotUpdater или других классов, чтобы применить новые настройки

    Args:
        settings(Settings): 
        data_processor(DataProcessor):
        plot_updater(PlotUpdater):
        ui(QWidget):

    """
    def __init__(self, settings, data_processor, plot_updater, ui):
        self.data_processor = data_processor
        self.settings = settings
        self.plot_updater = plot_updater
        self.ui = ui

        self._init_state()
        self._setup_connections()
    
    def _init_state(self):
        self._filter_panel = self.ui._filter_panel
        self._scale_panel = self.ui._scale_panel
        self._peak_panel = self.ui._peak_panel
        self._graph1 = self.ui._figure_panel1
        self._graph2 = self.ui._figure_panel2
        self._graph3 = self.ui._figure_panel3
        self._stimuli_panel = self.ui._stimuli_panel

        self._setup_units()
        self._update_thr()


    def _setup_connections(self):
        self._scale_panel.spin_box_scale1.valueChanged[int].connect(self._update_scale1)
        self._scale_panel.spin_box_scale2.valueChanged[int].connect(self._update_scale2)
        self._scale_panel.spin_box_scale3.valueChanged[int].connect(self._update_scale3)

        self._scale_panel.spin_box_max_value.valueChanged[int].connect(self._update_ymax)
        self._scale_panel.spin_box_min_value.valueChanged[int].connect(self._update_ymin)
        self._scale_panel.spin_box_scale_offset.valueChanged[int].connect(self._update_offset)
        self._scale_panel.spin_box_time_range.valueChanged[int].connect(self._update_timerange)
        self._scale_panel.combobox_signal_type.currentIndexChanged[int].connect(self._update_tkeo)

        self._filter_panel.spin_box_lower_freq.valueChanged[int].connect(self._update_low_freq)
        self._filter_panel.spin_box_upper_freq.valueChanged[int].connect(self._update_high_freq)
        self._filter_panel.check_box_notch.stateChanged.connect(self._update_notch)
        self._filter_panel.check_box_lowpass.stateChanged.connect(self._update_lowpass)
        self._filter_panel.check_box_highpass.stateChanged.connect(self._update_highpass)

        self._peak_panel.spin_box_threshold_curr.valueChanged[int].connect(self._update_threshold)

        # self._stimuli_panel.combo_box_stimuli.currentIndexChanged[int].connect(self._update_stimuli)
        # self._stimuli_panel.spin_box_stimuli_n.valueChanged[int].connect(self._update_stimuli_n)
        # self._stimuli_panel.check_box_stimuli_inf.stateChanged.connect(self._update_stimuli_inf)
        self._stimuli_panel.spin_box_monitor.valueChanged[int].connect(self._update_monitor)
        self._stimuli_panel.check_box_stimuli_record.stateChanged.connect(self._update_record_status)
        # self._stimuli_panel.combo_box_feedback_mode.currentIndexChanged[int].connect(self._update_feedback_mode)
        # self._stimuli_panel.spin_box_feedback_n.valueChanged[int].connect(self._update_feedback_n)

        self._stimuli_panel.line_edit_filename.textChanged.connect(self._update_filename)
        self._stimuli_panel.line_edit_folder.textChanged.connect(self._update_folder)


    # === plot settings === 

    def _update_threshold(self, thr):
        self.settings.detection_settings.threshold = thr
        self._update_thr()

    
    def _update_thr(self):
        thr = self.settings.detection_settings.threshold * (10 ** (self.settings.plot_settings.scale_factor3))
        self.plot_updater.change_thr_line(thr)

    def _update_scale1(self, scale):
        self.settings.plot_settings.scale_factor1 = scale

        self._graph1.update_yrange()
        self._graph1.set_graph_title()
        
    def _update_scale2(self, scale):
        self.settings.plot_settings.scale_factor2 = scale
        self._graph2.update_yrange()
        self._graph2.set_graph_title()

    def _update_scale3(self, scale):
        self.settings.plot_settings.scale_factor3 = scale
        self._graph3.update_yrange()
        self._graph3.set_graph_title()

        self._setup_units()
        self._update_thr()

    def _update_ymax(self, value):
        self.settings.plot_settings.ymax = value
        for graph in [self._graph1, self._graph2, self._graph3]:
            graph.update_yrange()
    
    def _update_ymin(self, value):
        self.settings.plot_settings.ymin = value
        for graph in [self._graph1, self._graph2, self._graph3]:
            graph.update_yrange()
    
    def _update_offset(self, value):
        self.settings.plot_settings.scale_offset = value
        print("DOES NOT WORK YET")
    
    def _update_timerange(self, value):
        self.settings.plot_settings.time_range_ms = value * 1000
        print("DOES NOT WORK YET")

    def _setup_units(self):
        factor = self.settings.plot_settings.scale_factor3
        text = f"<span style='font-size: 14pt;'>&times; 10<sup>{factor}</sup></span>"
        self._peak_panel.label_units.setText(text)
    
    def _update_tkeo(self, index):
        status = True if index == 1 else False
        self.settings.processing_settings.tkeo = status

    # === stimuli settings === 
    def _update_filename(self, filename):
        self.settings.stimuli_settings.filename = filename
    
    def _update_folder(self, folder):
        self.settings.stimuli_settings.folder = folder

    def _update_stimuli(self, index):
        self.settings.stimuli_settings.stimuli_curr = index
        pw = getattr(self.ui._stimuli_panel, "_player_window", None)
        if isinstance(pw, QWidget) and not pw.isHidden():
            self.ui._stimuli_panel._player_window.set_video_path()
            self.ui._stimuli_panel._player_window.change_stimuli()
    
    
    def _update_stimuli_n(self, n): # DOESNOT INPLEMENTED AT ALL
        self.settings.stimuli_settings.stimuli_n = n
    
    def _update_stimuli_inf(self, status):
        self.settings.stimuli_settings.stimuli_inf = status
    
    def _update_monitor(self, n):
        self.settings.stimuli_settings.monitor = n
        pw = getattr(self.ui._stimuli_panel, "_player_window", None)
        if isinstance(pw, QWidget) and not pw.isHidden():
            self.ui._stimuli_panel._player_window.set_monitor()
        
    def _update_record_status(self, status): # DOESNOT INPLEMENTED AT ALL
        self.settings.stimuli_settings.record = status
        # --> signal to change record status DOESNOT INPLEMENTED AT ALL

    def _update_feedback_mode(self, index):
        self.settings.stimuli_settings.feedback_mode_curr = index
        # --> signal to change feedback mode in video_player
    
    def _update_feedback_n(self, n):
        self.settings.stimuli_settings.feedback_n = n
    
    def _update_limit1(self, value):
        self.settings.stimuli_settings.delay_limit[0] = value
    
    def _update_limit2(self, value):
        self.settings.stimuli_settings.delay_limit[1] = value
    
    def _update_limit3(self, value):
        self.settings.stimuli_settings.delay_limit[2] = value

    # === filter settings === 
    def _update_low_freq(self, value):
        self.settings.processing_settings.freq_low = value
        self.data_processor.create_butter()
    
    def _update_high_freq(self, value):
        self.settings.processing_settings.freq_high = value
        self.data_processor.create_butter()
    
    def _update_notch(self, status):
        self.settings.processing_settings.do_notch = status
        self.data_processor.create_notch()
    
    def _update_lowpass(self, status):
        self.settings.processing_settings.do_lowpass = status
        self.data_processor.create_butter()
    
    def _update_highpass(self, status):
        self.settings.processing_settings.do_highpass = status
        self.data_processor.create_butter()