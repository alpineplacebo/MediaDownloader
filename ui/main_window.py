from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QLabel, QProgressBar, QMessageBox, QApplication,
    QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from ui.styles import get_stylesheet
from ui.components import MaterialButton, VideoCard, MaterialComboBox
from core.downloader import DownloaderThread
from core.settings import SettingsManager
import sys
import os

class MainWindow(QMainWindow):
    request_fetch_info = pyqtSignal(str, str) # Signal to worker (url, browser)
    request_download_action = pyqtSignal(str, dict, str) # Signal to worker (url, options, browser)
    request_download_action = pyqtSignal(str, dict, str) # Signal to worker (url, options, browser)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Downloader")
        self.resize(750, 500)
        self.setStyleSheet(get_stylesheet())
        
        # Settings
        self.settings_manager = SettingsManager()

        # Central Widget & Layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        self.header_label = QLabel("Media Downloader")
        self.header_label.setObjectName("HeaderTitle")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.header_label)

        # Input Section
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Media URL here...")
        self.url_input.returnPressed.connect(self.check_url)
        input_layout.addWidget(self.url_input)
        
        # Paste Button
        self.paste_btn = MaterialButton("Paste", primary=False)
        self.paste_btn.clicked.connect(self.paste_from_clipboard)
        input_layout.addWidget(self.paste_btn)
        
        # Clear Button
        self.clear_btn = MaterialButton("Clear", primary=False)
        self.clear_btn.clicked.connect(self.reset_app_state)
        input_layout.addWidget(self.clear_btn)

        self.main_layout.addLayout(input_layout)

        # === Split Content Area ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # --- LEFT COLUMN (Video Info) ---
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.video_card = VideoCard()
        # Ensure card is visible but empty initially
        self.video_card.setVisible(False) 
        left_layout.addWidget(self.video_card)
        left_layout.addStretch()
        
        content_layout.addLayout(left_layout, stretch=1)

        # --- RIGHT COLUMN (Controls) ---
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.setSpacing(15)

        # Quality
        right_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = MaterialComboBox()
        self.quality_combo.addItems(["Best Quality", "1080p", "720p", "480p", "Audio Only (MP3)"])
        right_layout.addWidget(self.quality_combo)
        
        # Cookies
        right_layout.addWidget(QLabel("Use Cookies From:"))
        self.browser_combo = MaterialComboBox()
        self.browser_combo.addItems(["None", "chrome", "edge", "firefox", "opera", "brave", "vivaldi"])
        saved_browser = self.settings_manager.get_cookies_browser()
        index = self.browser_combo.findText(saved_browser, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.browser_combo.setCurrentIndex(index)
        self.browser_combo.currentTextChanged.connect(self.on_browser_changed)
        right_layout.addWidget(self.browser_combo)

        # Location
        self.location_label = QLabel(f"Save to: {self.get_short_path(self.settings_manager.get_download_path())}")
        self.location_label.setStyleSheet("color: #49454F; font-size: 11px;")
        self.location_label.setWordWrap(True)
        right_layout.addWidget(self.location_label)
        
        self.change_loc_btn = MaterialButton("Change Location", primary=False)
        self.change_loc_btn.clicked.connect(self.change_location)
        right_layout.addWidget(self.change_loc_btn)

        right_layout.addStretch()

        # Status & Progress (Bottom of Right Column)
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMaximumHeight(60) # Approx 3 lines to prevent expansion
        self.status_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        right_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        # Buttons Layout (Cancel + Download)
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(10)

        self.cancel_btn = MaterialButton("Cancel", primary=False)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        btns_layout.addWidget(self.cancel_btn)

        self.download_btn = MaterialButton("Download")
        self.download_btn.setEnabled(False) 
        self.download_btn.clicked.connect(self.start_download)
        btns_layout.addWidget(self.download_btn)

        right_layout.addLayout(btns_layout)

        content_layout.addLayout(right_layout, stretch=1)
        self.main_layout.addLayout(content_layout)

        # Logic / Thread
        self.downloader_thread = DownloaderThread()
        self.worker = self.downloader_thread.worker
        
        # Wiring Signals (GUI -> Worker)
        self.request_fetch_info.connect(self.worker.fetch_info)
        self.request_download_action.connect(self.worker.download)
        
        # Wiring Signals (Worker -> GUI)
        self.worker.info_ready.connect(self.on_info_ready)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)
        
        self.downloader_thread.start()
        
        self.current_url = ""
        self._is_closing = False

    def closeEvent(self, event):
        if self.cancel_btn.isEnabled():
            # active download
            self._is_closing = True
            self.status_label.setText("Cleaning up...")
            self.cancel_download()
            event.ignore()
        else:
            self.downloader_thread.quit()
            event.accept()

    def on_browser_changed(self, text):
        self.settings_manager.set_cookies_browser(text)

    def reset_app_state(self):
        self.url_input.clear()
        self.current_url = ""
        self.video_card.setVisible(False)
        self.status_label.setText("Ready")
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(False)
        
        # Re-enable inputs
        self.url_input.setEnabled(True)
        self.change_loc_btn.setEnabled(True)
        self.quality_combo.setEnabled(True)
        self.browser_combo.setEnabled(True)

    def get_short_path(self, path):
        if len(path) > 30:
            return "..." + path[-27:]
        return path

    def change_location(self):
        current_path = self.settings_manager.get_download_path()
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory", current_path)
        if directory:
            self.settings_manager.set_download_path(directory)
            self.location_label.setText(f"Save to: {self.get_short_path(directory)}")

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())
        self.check_url()

    def check_url(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        self.status_label.setText("Fetching video info...")
        self.download_btn.setEnabled(False)
        self.video_card.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Indeterminate
        
        browser = self.browser_combo.currentText()
        self.request_fetch_info.emit(url, browser)

    @pyqtSlot(dict)
    def on_info_ready(self, info):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.status_label.setText("Ready to download")
        
        title = info.get('title', 'Unknown Title')
        duration = info.get('duration_string', '--:--')
        thumb = info.get('thumbnail', '')
        
        self.video_card.set_data(title, duration, thumb)
        self.current_url = info.get('original_url') or info.get('webpage_url')
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def cancel_download(self):
        self.status_label.setText("Cancelling...")
        self.cancel_btn.setEnabled(False)
        self.worker.trigger_cancel()

    def start_download(self):
        if self.current_url:
            self.download_btn.setEnabled(False)
            self.cancel_btn.setEnabled(True)
            self.url_input.setEnabled(False)
            self.change_loc_btn.setEnabled(False)
            self.quality_combo.setEnabled(False)
            self.status_label.setText("Starting download...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Prepare options with current download path and quality
            quality_map = {
                "Best Quality": {}, # Default behavior
                "1080p": {'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'},
                "720p": {'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]'},
                "480p": {'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]'},
                "Audio Only (MP3)": {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            }
            
            selection = self.quality_combo.currentText()
            opts = {
                'paths': {'home': self.settings_manager.get_download_path()}
            }
            opts.update(quality_map.get(selection, {}))
            
            opts.update(quality_map.get(selection, {}))
            
            browser = self.browser_combo.currentText()
            self.request_download_action.emit(self.current_url, opts, browser)

    @pyqtSlot(dict)
    def on_progress(self, data):
        status = data.get('status')
        if status == 'downloading':
            try:
                percent = float(data.get('percent', 0))
                self.progress_bar.setValue(int(percent))
                self.status_label.setText(f"Downloading: {percent:.1f}%")
            except:
                pass
        elif status == 'finished':
            # Store filename but don't update text yet to prevent expansion glitch
            self.last_filename = data.get('filename', 'Unknown')
            self.progress_bar.setValue(100)

    @pyqtSlot()
    def on_finished(self):
        if self._is_closing:
            self.close()
            return
            
        filename = getattr(self, 'last_filename', 'Unknown')
        # Format the filename to be just the basename if it's a full path
        if os.path.sep in filename:
            filename = os.path.basename(filename)
            
        self.status_label.setText(f"Downloaded : {filename}")
        self.progress_bar.setValue(100)
        self.progress_bar.setValue(100)
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.change_loc_btn.setEnabled(True)
        self.quality_combo.setEnabled(True)
        QMessageBox.information(self, "Success", "Video downloaded successfully!")

    @pyqtSlot(str)
    def on_error(self, err_msg):
        if self._is_closing:
            self.close()
            return

        self.status_label.setText("Error occurred")
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error occurred")
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.change_loc_btn.setEnabled(True)
        self.quality_combo.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{err_msg}")
