import os
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
import pyttsx3
from PyQt6.QtCore import QThread, pyqtSignal

class TranslationWorker(QThread):
    finished = pyqtSignal(str, str)  # original, translated
    error = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, mode, target_lang, audio_path=None, text_input=None):
        super().__init__()
        self.mode = mode  # 'voice' or 'text'
        self.target_lang = target_lang
        self.audio_path = audio_path
        self.text_input = text_input
        self.recognizer = sr.Recognizer()
        self.translator = Translator()

    def run(self):
        try:
            if self.mode == 'voice':
                if not self.audio_path or not os.path.exists(self.audio_path):
                    self.error.emit("Audio recording failed.")
                    return
                
                self.status.emit("Processing audio...")
                with sr.AudioFile(self.audio_path) as source:
                    audio = self.recognizer.record(source)
                
                self.status.emit("Transcribing...")
                original_text = self.recognizer.recognize_google(audio)
            else:
                original_text = self.text_input
                if not original_text or not original_text.strip():
                    self.error.emit("Please enter some text.")
                    return

            self.status.emit(f"Translating...")
            translation = self.translator.translate(original_text, dest=self.target_lang)
            
            # Cleanup audio file
            if self.mode == 'voice' and self.audio_path and os.path.exists(self.audio_path):
                try:
                    os.remove(self.audio_path)
                except Exception as e:
                    print(f"Cleanup error: {e}")
            
            self.finished.emit(original_text, translation.text)
            
        except sr.UnknownValueError:
            self.error.emit("Speech not understood.")
        except sr.RequestError:
            self.error.emit("API unavailable. Check connection.")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class TTSWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, text, lang_code):
        super().__init__()
        self.text = text
        self.lang_code = lang_code

    def run(self):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Attempt to find matching voice
            matched = False
            for voice in voices:
                if self.lang_code.lower() in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    matched = True
                    break
            
            engine.say(self.text)
            engine.runAndWait()
            engine.stop()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
