from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, QShortcut
from PyQt5.QtCore import  pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence

import json
import os
import subprocess

from utils.ui_helpers import create_button, create_spin_box, create_check_box, create_combo_box, create_shortcut, create_lineedit
from utils.layout_utils import create_hbox, create_vbox

from .video_player import StimuliPresentation_one_by_one

PLAY_LABEL = "▶"
STOP_LABEL = "⏸"

 # ▶  ⏸

class StimuliControlPanel(QFrame):
    """ --- UI для контроля за стимулами --- """

    stimuliPresentation = pyqtSignal(bool)      # -> stimuli presentation is on
    stimuliEnded = pyqtSignal()

    def __init__(self, settings, resonance, parent=None):
        super().__init__(parent)
        self.parent = parent
        # self.setObjectName("settings_panel")    # для привязки стиля
        self.setMinimumWidth(200)

        self.resonance = resonance
        self._service = self.resonance.getService("nvx136")     # Берем сервис

        self.settings = settings.stimuli_settings                     

        self._init_state()
        self._setup_ui()
        self._setup_layout()
        self._setup_connections()

    def _init_state(self):
        self._restart_stimuli = False
        self._player_window = None
        self._record_on = False

    # =======================
    # =====     UI      =====
    # =======================
    def _setup_ui(self):
        
        self._settings_panel = QFrame(self)
        
        self.line_edit_folder = create_lineedit(parent=self, w=200)
        self.line_edit_folder.setText(self.settings.folder)

        self.line_edit_filename = create_lineedit(parent=self)
        self.line_edit_filename.setText(self.settings.filename)

        self.button_nvx_record = create_button(text='Начать запись', disabled=False, parent=self, w=100)
        self.button_stimuli = create_button(text='Открыть стимулы', disabled=False, parent=self, w=100)

        self.spin_box_monitor = create_spin_box(1, 3, self.settings.monitor, parent=self)
        self.check_box_stimuli_record = create_check_box(self.settings.record, 'Запись NVX', parent=self)
        
        # self.button_stimuli_pause = create_button(text=PLAY_LABEL, disabled=True, parent=self)

        # self.combo_box_stimuli = create_combo_box(self.settings.stimuli, curr_item_idx=self.settings.stimuli_curr, parent=self)
        # self.spin_box_stimuli_n = create_spin_box(0, 100, self.settings.stimuli_n, parent=self)
        # self.check_box_stimuli_inf = create_check_box(self.settings.stimuli_inf, '∞', parent=self)


        # self.combo_box_feedback_mode = create_combo_box(self.settings.feedback_mode, curr_item_idx=self.settings.feedback_mode_curr, parent=self)
        # self.spin_box_feedback_n = create_spin_box(0, 30, self.settings.feedback_n, parent=self)
        # delay_limit = self.settings.delay_limit
        # self.spin_box_limit1 = create_spin_box(0, 1000, delay_limit[0], parent=self)
        # self.spin_box_limit2 = create_spin_box(0, 1000, delay_limit[1], parent=self)
        # self.spin_box_limit3 = create_spin_box(0, 1000, delay_limit[2], parent=self)

        # self.label_stimuli_idx = QLabel("", self)
        # self.label_stimuli_idx.setObjectName("label_stimulus_idx")

    # =======================
    # =====   LAYOUT    =====
    # =======================
    def _setup_layout(self):        
        
        layout_record = create_hbox([self.line_edit_folder])
        layout_filename = create_hbox([self.line_edit_filename])
        layout_stimuli = create_hbox([self.button_stimuli, self.check_box_stimuli_record])
        # layout_stimuli = create_hbox([self.combo_box_stimuli, QLabel("N:", self), self.spin_box_stimuli_n, QLabel("или", self), self.check_box_stimuli_inf])

        layout_monitor = create_hbox([QLabel("монитор", self), self.spin_box_monitor])
        layout_nvx_record = create_hbox([self.button_nvx_record])

        # layout_feedback_mode = create_hbox([QLabel("Режим ОС", self), self.combo_box_feedback_mode])
        # layout_feedback_n = create_hbox([QLabel("N эпох", self), self.spin_box_feedback_n])
        # layout_delay_limit1 = create_hbox([QLabel("поньк #1:", self), self.spin_box_limit1, QLabel("мс", self)])
        # layout_delay_limit2 = create_hbox([QLabel("поньк #2:", self), self.spin_box_limit2, QLabel("мс", self)])
        # layout_delay_limit3 = create_hbox([QLabel("поньк #3:", self), self.spin_box_limit3, QLabel("мс", self)])
        
        layout = QVBoxLayout(self)
        layout.addLayout(layout_record)
        layout.addLayout(layout_filename)
        layout.addLayout(layout_nvx_record)
        layout.addLayout(layout_stimuli)
        # layout.addLayout(layout_stimuli)
        layout.addLayout(layout_monitor)

        # layout.addWidget(self.label_stimuli_idx)
        # layout.addLayout(layout_feedback_mode)
        # layout.addLayout(layout_feedback_n)
        # layout.addLayout(layout_delay_limit1)
        # layout.addLayout(layout_delay_limit2)
        # layout.addLayout(layout_delay_limit3)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # =======================
    # =====   Сигналы    ====
    # =======================
    def _setup_connections(self):
        self.button_stimuli.clicked.connect(self._on_stimuli_start_click)                      # Открыть окно для показа стимулов
        # self.button_stimuli_pause.clicked.connect(self._on_pause_stimuli_button_click)
        self.button_nvx_record.clicked.connect(self._on_nvx_record_start_click)

    
    # def _update_connections(self):
    #     """установление связей после открытия окна с презентацией стимулов"""
    #     self._player_window.stimuliStarted.connect(self._on_start_stimuli)
    #     self._player_window.stimuliPaused.connect(self._change_button_pause_stimuli_text)
    #     self._player_window.stimuliFinished.connect(self._on_finish_stimuli)    

    #     self._player_window.currIdxChanged.connect(self._on_stimuli_idx_changed)
    #     self._player_window.stimulus.connect(self._on_stimuli_order_changed)

    #     self._player_window.volumeChanged.connect(self._on_player_volume_changed)
    #     self._player_window.playerIsMuted.connect(self._on_player_muted)

    #     self._player_window.stimuliEnded.connect(lambda: self.stimuliEnded.emit())

    # =======================
    # =====   Логика    =====
    # =======================

    
    def _start_nvx(self, filename):
        self._service.sendTransition('start', stream="eeg", filename=filename)
    
    def _stop_nvx(self):
        self._service.sendTransition('stop')
    
    def _on_nvx_record_start_click(self):
        if self._record_on:
            self._stop_nvx()
            self._record_on = False
            self.button_nvx_record.setText("Начать запись")
        else:
            folder = self.line_edit_folder.text()
            filename = self.line_edit_filename.text()
            full_path = os.path.join(folder, filename)
            if os.path.exists(full_path):
                full_path = full_path[:-4] +"-$$$.hdf5"
            print(full_path)
            self._start_nvx(full_path)
            self._record_on = True
            self.button_nvx_record.setText("Закончить запись")
            

    def _on_stimuli_start_click(self):
        cwd = os.path.dirname(self.settings.stimuli_bat) # cwd = папка с батником
        subprocess.Popen([self.settings.stimuli_bat], cwd=cwd)

        if self.check_box_stimuli_record.checkState():
            self._on_nvx_record_start_click()
    

    # def _on_stimuli_button_click(self):
    #     # если стимул-презентейшн уже открыт -> хотим закрыть
    #     pw = getattr(self, "_player_window", None)
    #     if isinstance(pw, QWidget) and not pw.isHidden() and not self._restart_stimuli:
    #         self.button_stimuli.setText("Открыть окно")               # опять можно начать презентацию
    #         self._player_window.finish()            # like Escape
                                         
    #     # если не открыт -> хотим начать презентацию и возможно запись nvx
    #     else:
    #         if not self._restart_stimuli:   # если первый запуск окна с показом стимулов
    #             self._player_window = StimuliPresentation_one_by_one(self.settings)
    #             self._player_window.show()
    #             self._player_window.raise_()

    #             self._update_connections()      # устанавливаем связи с новым окном

    #         self.button_stimuli_pause.setEnabled(True)              # кнопка пауза доступна
    #         self.button_stimuli_pause.setText(PLAY_LABEL)
    #         self.button_stimuli.setText("Закрыть окно")                # меняем надпись на кнопке "старт"

    #         self._restart_stimuli = False                           
    
    # # == show delay === 
    # def show_delay(self, delay):
    #     self._player_window.show_feedback(delay)

    # # === изменения состояния кнопок === 
    # def _change_button_pause_stimuli_text(self):
    #     status = PLAY_LABEL if self._player_window.is_paused else STOP_LABEL
    #     self.button_stimuli_pause.setText(status)

    # def _on_pause_stimuli_button_click(self):
    #     pw = getattr(self, "_player_window", None)
    #     if isinstance(pw, QWidget):
    #         self._player_window.pause_video()
    #         self._change_button_pause_stimuli_text()
       
    # def _on_restart_stimuli_presentation(self):

    #     self._restart_stimuli = True
    #     self._on_stimuli_button_click()

    # def _on_finish_stimuli(self):
    #     # запись nvx136
    #     if self.check_box_stimuli_record.isChecked():
    #         self.stimuliPresentation.emit(False)

    #     # self.check_box_stimuli_record.setEnabled(True) # разрешить возможность поменять статус записи nvx

    #     self.label_stimuli_idx.setText(f"")
    #     self.button_stimuli_pause.setText(PLAY_LABEL)

    
    # def _on_start_stimuli(self):
    #     # запись nvx136
    #     if self.check_box_stimuli_record.isChecked():
    #         self.stimuliPresentation.emit(True)

    #     # self.check_box_stimuli_record.setDisabled(True) # сделать недоступной возможность поменять статус записи nvx

    #     self.button_stimuli_pause.setText(STOP_LABEL)
    
    # # === отметки о текущем стимуле === 
    # def _on_stimuli_idx_changed(self, idx):
    #     self.label_stimuli_idx.setText(f"#{idx}")

    # def _on_stimuli_order_changed(self, filename):
    #     message = {"stimulus": filename}
    #     self.output_stream(json.dumps(message))

    
    # # === изменения звука === 
    # def _on_player_volume_changed(self, value):
    #     """изменения от горячих клавиш стрелок вверх-вниз"""
    #     self.stimuli_volume_slider.slider.setValue(value)
    
    # def _on_player_muted(self):
    #     cur_volume = self.stimuli_volume_slider.slider.value()
    #     volume = self._player_window.get_last_volume() if cur_volume == 0 else 0
    #     self.stimuli_volume_slider.slider.setValue(volume)

    # def _on_change_stimuli_volume(self, value):
    #     """изменения от положения слайдера"""
    #     # если открыто окно со стимулами, поменять там громкость !!! не работает :( !!!
    #     pw = getattr(self, "_player_window", None)
    #     if isinstance(pw, QWidget) and not pw.isHidden():
    #         self._player_window.update_volume(value)
    
    # def _on_change_noise_volume(self, value):
    #     """изменения от положения слайдера"""
    #     # если открыто окно со стимулами, поменять там громкость !!! не работает :( !!!
    #     self._audio_player.set_volume(value)
    
    # # -- for
    # def _up_noise_volume(self):
    #     new_value = min(100, self._audio_player.volume + 5)
    #     self.noise_volume_slider.setValue(new_value)
    #     self._on_change_noise_volume(new_value)
    
    # def _down_noise_volume(self):
    #     new_value = max(0, self._audio_player.volume - 5)
    #     self.noise_volume_slider.setValue(new_value)
    #     self._on_change_noise_volume(new_value)
    
    # def _up_stimuli_volume(self):
    #     new_value = min(100, self._player_window.get_last_volume() + 5)
    #     self.stimuli_volume_slider.setValue(new_value)
    #     self._on_change_stimuli_volume(new_value)
    
    # def _down_stimuli_volume(self):
    #     new_value = max(0, self._player_window.get_last_volume() - 5)
    #     self.stimuli_volume_slider.setValue(new_value)
    #     self._on_change_stimuli_volume(new_value)


    # # === получение последовательности стимулов === 
    # def _get_sequence(self, seq_name):
    #     if not seq_name:
    #             return
    #     try:
    #         with open(self.settings.stimuli_filename, "r", encoding="utf-8") as f:
    #             data = json.load(f)
    #     except (FileNotFoundError, json.JSONDecodeError):
    #         data = {}

    #     return data.get(seq_name)

    # def _update_combo_box_stimuli(self):
    #     self.combo_box_stimuli.clear()
    #     try:
    #         with open(self.settings.stimuli_filename, "r", encoding="utf-8") as f:
    #             data = json.load(f)
    #             if isinstance(data, dict):
    #                 self.combo_box_stimuli.addItems(data.keys())
    #     except (FileNotFoundError, json.JSONDecodeError):
    #         print("файл пока пустой")
        
    # def _finilize(self):
    #     # self._update_combo_box_stimuli()
    #     print('that is it')
    

    # === events ===

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Up+Qt.Key_N:                  # -- volume up
    #         new_value = min(100, self._audio_player.volume + 5)
    #         self._on_change_noise_volume(new_value)   
        
    #     # elif event.key() == Qt.Key_Down:                # -- volume down
    #     #     new_value = max(0, self._volume - 1)
    #     #     self.update_volume(new_value)

    #     # elif event.key() == Qt.Key_M:                   # -- mute
    #     #     self._player.audio_toggle_mute()
    #     #     self.playerIsMuted.emit()

    #     else:
    #         super().keyPressEvent(event)
