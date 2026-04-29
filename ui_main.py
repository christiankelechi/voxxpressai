import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QFrame, 
                             QTextEdit, QStackedWidget, QGraphicsDropShadowEffect,
                             QLineEdit)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage


from audio_recorder import AudioRecorder
from translator_engine import TranslationWorker, TTSWorker, LANGUAGES

class AudioTranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("VoxTranslate Pro Workspace")
        self.resize(1300, 850)
        self.setMinimumSize(1000, 600)

        
        # Premium Dark Theme Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0B0C10;
            }
            QLabel {
                color: #C5C6C7;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton#PrimaryBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #66FCF1, stop:1 #45A29E);
                color: #0B0C10;
            }
            QPushButton#PrimaryBtn:hover {
                background: #66FCF1;
            }
            QPushButton#ModeBtn {
                background-color: #1F2833;
                color: #C5C6C7;
                border: 1px solid #45A29E;
            }
            QPushButton#ModeBtn:checked {
                background-color: #45A29E;
                color: #0B0C10;
            }
            QPushButton#NavBtn {
                background-color: #1F2833;
                color: #66FCF1;
                border: 1px solid #45A29E;
                padding: 5px 10px;
            }
            QComboBox {
                background-color: #1F2833;
                color: #66FCF1;
                border: 1px solid #45A29E;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: #1F2833;
                color: #C5C6C7;
                border: 1px solid #45A29E;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }
            QFrame#Card {
                background-color: #1F2833;
                border-radius: 12px;
                border: 1px solid #2d3748;
            }
            QTextEdit {
                background-color: #0B0C10;
                color: #C5C6C7;
                border: 1px solid #1F2833;
                border-radius: 6px;
                font-size: 14px;
                padding: 8px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Horizontal Split Layout
        workspace_layout = QHBoxLayout(central_widget)
        workspace_layout.setContentsMargins(15, 15, 15, 15)
        workspace_layout.setSpacing(15)

        # =====================================================================
        # LEFT SIDE: Translator Interface
        # =====================================================================
        translator_widget = QWidget()
        translator_layout = QVBoxLayout(translator_widget)
        translator_layout.setContentsMargins(10, 15, 10, 15)
        translator_layout.setSpacing(20)

        # Header
        header = QLabel("VOX XPRESS AI")
        header.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #66FCF1; letter-spacing: 2px;")
        translator_layout.addWidget(header)

        # Mode Selector (Voice vs Text)
        mode_layout = QHBoxLayout()
        self.voice_mode_btn = QPushButton("Voice Note")
        self.voice_mode_btn.setObjectName("ModeBtn")
        self.voice_mode_btn.setCheckable(True)
        self.voice_mode_btn.setChecked(True)
        self.voice_mode_btn.clicked.connect(self.switch_to_voice)

        self.text_mode_btn = QPushButton("Text Input")
        self.text_mode_btn.setObjectName("ModeBtn")
        self.text_mode_btn.setCheckable(True)
        self.text_mode_btn.clicked.connect(self.switch_to_text)

        mode_layout.addWidget(self.voice_mode_btn)
        mode_layout.addWidget(self.text_mode_btn)
        translator_layout.addLayout(mode_layout)

        # Language Picker
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Translate to:")
        lang_label.setFont(QFont('Segoe UI', 11))
        self.lang_combo = QComboBox()
        
        popular = {'fr': 'French', 'es': 'Spanish', 'de': 'German', 'zh-cn': 'Chinese', 'ar': 'Arabic', 'ru': 'Russian', 'ja': 'Japanese'}
        for code, name in popular.items():
            self.lang_combo.addItem(name, code)
        self.lang_combo.insertSeparator(len(popular))
        for code, name in LANGUAGES.items():
            if code not in popular:
                self.lang_combo.addItem(name.title(), code)

        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        translator_layout.addLayout(lang_layout)

        # Stacked Widget for Input Modes
        self.input_stack = QStackedWidget()
        
        # Voice Mode UI
        voice_widget = QWidget()
        voice_layout = QVBoxLayout(voice_widget)
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setObjectName("VoiceBtn")
        self.record_btn.setFixedSize(140, 140)
        self.record_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8A2BE2, stop:1 #4A0E4E); color: white; border-radius: 70px; font-size: 16px;")
        self.record_btn.clicked.connect(self.toggle_recording)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(138, 43, 226, 150))
        shadow.setOffset(0, 0)
        self.record_btn.setGraphicsEffect(shadow)

        voice_layout.addStretch()
        voice_layout.addWidget(self.record_btn, 0, Qt.AlignmentFlag.AlignCenter)
        voice_layout.addStretch()
        self.input_stack.addWidget(voice_widget)

        # Text Mode UI
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type text here to translate...")
        self.text_input.setFixedHeight(120)
        
        self.translate_btn = QPushButton("Translate Text")
        self.translate_btn.setObjectName("PrimaryBtn")
        self.translate_btn.clicked.connect(self.translate_text)
        
        text_layout.addWidget(self.text_input)
        text_layout.addWidget(self.translate_btn)
        self.input_stack.addWidget(text_widget)

        translator_layout.addWidget(self.input_stack)

        # Results Cards
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setPlaceholderText("Original text will appear here...")
        self.original_text.setFixedHeight(80)

        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setPlaceholderText("Translation will appear here...")
        self.translated_text.setFixedHeight(80)

        translator_layout.addWidget(self.create_card("ORIGINAL", self.original_text))
        translator_layout.addWidget(self.create_card("TRANSLATION", self.translated_text))

        # Speak Button
        self.speak_btn = QPushButton("🔊 Listen to Translation")
        self.speak_btn.setObjectName("PrimaryBtn")
        self.speak_btn.clicked.connect(self.speak_translation)
        translator_layout.addWidget(self.speak_btn)

        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #45A29E; font-size: 12px; font-style: italic;")
        translator_layout.addWidget(self.status_label)

        # =====================================================================
        # RIGHT SIDE: Embedded Web Browser (WhatsApp / Web)
        # =====================================================================
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(10)

        # Browser Navigation Bar
        nav_bar = QHBoxLayout()
        
        self.back_btn = QPushButton("◀")
        self.back_btn.setObjectName("NavBtn")
        self.back_btn.setFixedWidth(40)
        
        self.forward_btn = QPushButton("▶")
        self.forward_btn.setObjectName("NavBtn")
        self.forward_btn.setFixedWidth(40)
        
        self.reload_btn = QPushButton("🔄")
        self.reload_btn.setObjectName("NavBtn")
        self.reload_btn.setFixedWidth(40)

        self.url_entry = QLineEdit()
        self.url_entry.setText("https://web.whatsapp.com")
        self.url_entry.returnPressed.connect(self.navigate_to_url)

        self.go_btn = QPushButton("GO")
        self.go_btn.setObjectName("PrimaryBtn")
        self.go_btn.setFixedWidth(50)
        self.go_btn.clicked.connect(self.navigate_to_url)

        nav_bar.addWidget(self.back_btn)
        nav_bar.addWidget(self.forward_btn)
        nav_bar.addWidget(self.reload_btn)
        nav_bar.addWidget(self.url_entry)
        nav_bar.addWidget(self.go_btn)
        browser_layout.addLayout(nav_bar)

        # Browser Profile and Persistence
        storage_name = "VoxTranslateProfile"
        self.browser_profile = QWebEngineProfile(storage_name, self)
        
        # Force persistent cookies
        self.browser_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        
        # Set User Agent & Language
        custom_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        self.browser_profile.setHttpUserAgent(custom_ua)
        self.browser_profile.setHttpAcceptLanguage("en-US,en;q=0.9")

        
        # Create Page and View
        self.browser_page = QWebEnginePage(self.browser_profile, self)
        self.web_view = QWebEngineView()
        self.web_view.setPage(self.browser_page)
        
        # Enable Focus
        self.web_view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.web_view.setUrl(QUrl("https://web.whatsapp.com"))
        self.web_view.urlChanged.connect(self.update_url_bar)


        
        # Connect buttons
        self.back_btn.clicked.connect(self.web_view.back)
        self.forward_btn.clicked.connect(self.web_view.forward)
        self.reload_btn.clicked.connect(self.web_view.reload)

        browser_layout.addWidget(self.web_view)

        # Add to main layout (Translator left, Browser right)
        workspace_layout.addWidget(translator_widget, stretch=2)
        workspace_layout.addWidget(browser_widget, stretch=3)

    def create_card(self, title, text_edit):
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #66FCF1; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        
        layout.addWidget(title_lbl)
        layout.addWidget(text_edit)
        return frame

    def switch_to_voice(self):
        self.voice_mode_btn.setChecked(True)
        self.text_mode_btn.setChecked(False)
        self.input_stack.setCurrentIndex(0)

    def switch_to_text(self):
        self.text_mode_btn.setChecked(True)
        self.voice_mode_btn.setChecked(False)
        self.input_stack.setCurrentIndex(1)

    def toggle_recording(self):
        if not self.recorder.is_recording:
            success = self.recorder.start_recording()
            if success:
                self.record_btn.setText("Stop")
                self.record_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #EF4444, stop:1 #B91C1C); color: white; border-radius: 70px; font-size: 16px;")
                self.status_label.setText("Recording... Click Stop when done.")
        else:
            audio_path = self.recorder.stop_recording()
            self.record_btn.setText("Start Recording")
            self.record_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8A2BE2, stop:1 #4A0E4E); color: white; border-radius: 70px; font-size: 16px;")
            if audio_path:
                self.process_translation(mode='voice', audio_path=audio_path)

    def translate_text(self):
        text = self.text_input.toPlainText()
        if text.strip():
            self.process_translation(mode='text', text_input=text)

    def process_translation(self, mode, audio_path=None, text_input=None):
        target_lang = self.lang_combo.currentData()
        self.status_label.setText("Processing...")
        
        self.worker = TranslationWorker(mode, target_lang, audio_path, text_input)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.start()

    def on_translation_finished(self, original, translated):
        self.original_text.setText(original)
        self.translated_text.setText(translated)
        self.status_label.setText("Success!")

    def on_translation_error(self, msg):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet("color: #EF4444; font-size: 12px;")

    def speak_translation(self):
        text = self.translated_text.toPlainText()
        if text:
            target_lang = self.lang_combo.currentData()
            self.status_label.setText("Speaking...")
            self.tts_worker = TTSWorker(text, target_lang)
            self.tts_worker.finished.connect(lambda: self.status_label.setText("Ready"))
            self.tts_worker.error.connect(self.on_translation_error)
            self.tts_worker.start()

    def navigate_to_url(self):
        url = self.url_entry.text()
        if not url.startswith("http"):
            url = "https://" + url
            self.url_entry.setText(url)
        self.web_view.setUrl(QUrl(url))

    def update_url_bar(self, qurl):
        self.url_entry.setText(qurl.toString())

    def closeEvent(self, event):
        self.recorder.cleanup()
        super().closeEvent(event)
