import pyaudio
import wave
import threading
import os

class AudioRecorder:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self._lock = threading.Lock()

    def start_recording(self):
        with self._lock:
            if self.is_recording:
                return
            self.frames = []
            self.is_recording = True
            
            try:
                self.stream = self.p.open(format=pyaudio.paInt16,
                                          channels=1,
                                          rate=16000,
                                          input=True,
                                          frames_per_buffer=1024)
            except Exception as e:
                print(f"Failed to open audio stream: {e}")
                self.is_recording = False
                return False
            
            self.thread = threading.Thread(target=self._record, daemon=True)
            self.thread.start()
            return True

    def _record(self):
        while True:
            with self._lock:
                if not self.is_recording:
                    break
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Recording error: {e}")
                break

    def stop_recording(self, filename="temp_voice.wav"):
        with self._lock:
            if not self.is_recording:
                return None
            self.is_recording = False
            
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        if self.frames:
            try:
                wf = wave.open(filename, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(b''.join(self.frames))
                wf.close()
                return filename
            except Exception as e:
                print(f"Failed to save WAV: {e}")
                return None
        return None

    def cleanup(self):
        self.p.terminate()
