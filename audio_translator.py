import sys
import threading
import speech_recognition as sr
import pyttsx3
from googletrans import Translator, LANGUAGES
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QFrame, QGraphicsDropShadowEffect, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QPalette

class TranslatorWorker(QThread):
    finished = pyqtSignal(str, str)  # original, translated
    error = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, target_lang):
        super().__init__()
        self.target_lang = target_lang
        self.recognizer = sr.Recognizer()
        self.translator = Translator()

    def run(self):
        try:
            with sr.Microphone() as source:
                self.status.emit("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            self.status.emit("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            
            self.status.emit(f"Translating to {LANGUAGES[self.target_lang]}...")
            translation = self.translator.translate(text, dest=self.target_lang)
            
            # Text-to-Speech
            try:
                self.status.emit("Speaking...")
                engine = pyttsx3.init()
                # Try to set voice based on target language (best effort)
                voices = engine.getProperty('voices')
                for voice in voices:
                    if self.target_lang in voice.languages or self.target_lang.split('-')[0] in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
                engine.say(translation.text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"TTS Error: {e}")

            self.finished.emit(text, translation.text)
        except sr.WaitTimeoutError:
            self.error.emit("Listening timed out. Please try again.")
        except sr.UnknownValueError:
            self.error.emit("Could not understand audio.")
        except sr.RequestError:
            self.error.emit("Could not request results; check your internet.")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class AudioTranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("EchoTranslate AI")
        self.setFixedSize(500, 650)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#RecordBtn {
                background-color: #BB86FC;
                color: #000000;
                border-radius: 40px;
                font-weight: bold;
                font-size: 16px;
                border: none;
            }
            QPushButton#RecordBtn:hover {
                background-color: #CFA9FF;
            }
            QPushButton#RecordBtn:pressed {
                background-color: #9965f4;
            }
            QComboBox {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 8px;
                min-width: 150px;
            }
            QFrame#Card {
                background-color: #1E1E1E;
                border-radius: 15px;
                border: 1px solid #333333;
            }
            QTextEdit {
                background-color: transparent;
                color: #B0B0B0;
                border: none;
                font-size: 14px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(25)

        # Header
        header = QLabel("EchoTranslate")
        header.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Language Selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Target Language:")
        lang_label.setFont(QFont('Segoe UI', 10))
        self.lang_combo = QComboBox()
        
        # Popular languages first
        popular = {'fr': 'French', 'es': 'Spanish', 'de': 'German', 'zh-cn': 'Chinese', 'ar': 'Arabic', 'ru': 'Russian', 'ja': 'Japanese'}
        for code, name in popular.items():
            self.lang_combo.addItem(name.title(), code)
        self.lang_combo.insertSeparator(len(popular))
        for code, name in LANGUAGES.items():
            if code not in popular:
                self.lang_combo.addItem(name.title(), code)

        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # Result Cards
        self.original_card = self.create_card("You said:", "Click record and speak...")
        self.translated_card = self.create_card("Translation:", "...")
        
        layout.addWidget(self.original_card)
        layout.addWidget(self.translated_card)

        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #03DAC6; font-size: 12px;")
        layout.addWidget(self.status_label)

        # Record Button
        btn_container = QHBoxLayout()
        self.record_btn = QPushButton("Record")
        self.record_btn.setObjectName("RecordBtn")
        self.record_btn.setFixedSize(120, 80)
        self.record_btn.clicked.connect(self.start_recording)
        
        # Glow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(187, 134, 252, 150))
        shadow.setOffset(0, 0)
        self.record_btn.setGraphicsEffect(shadow)
        
        btn_container.addStretch()
        btn_container.addWidget(self.record_btn)
        btn_container.addStretch()
        layout.addLayout(btn_container)

    def create_card(self, title, placeholder):
        frame = QFrame()
        frame.setObjectName("Card")
        v_layout = QVBoxLayout(frame)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #BB86FC; font-weight: bold; font-size: 12px;")
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setText(placeholder)
        content.setFixedHeight(80)
        
        v_layout.addWidget(title_lbl)
        v_layout.addWidget(content)
        
        # Store the text edit for updates
        if "You said" in title:
            self.original_text = content
        else:
            self.translated_text = content
            
        return frame

    def start_recording(self):
        target_lang = self.lang_combo.currentData()
        self.record_btn.setEnabled(False)
        self.record_btn.setText("Listening...")
        self.record_btn.setStyleSheet("background-color: #03DAC6; color: black;")
        
        self.worker = TranslatorWorker(target_lang)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def update_status(self, msg):
        self.status_label.setText(msg)
        if "Listening" in msg:
            self.record_btn.setText("Listening")
        elif "Recognizing" in msg:
            self.record_btn.setText("...")
        elif "Speaking" in msg:
            self.record_btn.setText("Speaking")

    def on_finished(self, original, translated):
        self.original_text.setText(original)
        self.translated_text.setText(translated)
        self.reset_btn()
        self.status_label.setText("Success!")

    def on_error(self, msg):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet("color: #CF6679; font-size: 12px;")
        self.reset_btn()

    def reset_btn(self):
        self.record_btn.setEnabled(True)
        self.record_btn.setText("Record")
        self.record_btn.setStyleSheet("") # Reverts to default ID style

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioTranslatorApp()
    window.show()
    sys.exit(app.exec())
