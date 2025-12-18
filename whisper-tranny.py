#!/usr/bin/env python3
"""
Cross-Platform Audio Recorder & Whisper Transcriber
Works on Linux, Windows, and macOS
"""

import sys
import tempfile
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QProgressBar, QMessageBox
)

# Whisper import - adjust based on your setup
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: whisper not installed. Install with: pip install openai-whisper")


class AudioRecorder:
    """Handles audio recording from default microphone"""

    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []

    def start(self):
        self.audio_data = []
        self.recording = True

        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            callback=callback
        )
        self.stream.start()

    def stop(self) -> np.ndarray:
        self.recording = False
        self.stream.stop()
        self.stream.close()

        if self.audio_data:
            return np.concatenate(self.audio_data, axis=0).flatten()
        return np.array([])

    def save_to_file(self, audio: np.ndarray, filepath: str):
        sf.write(filepath, audio, self.sample_rate)


class TranscriptionWorker(QThread):
    """Background thread for Whisper transcription"""

    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, audio_path: str, model_name: str = "small"):
        super().__init__()
        self.audio_path = audio_path
        self.model_name = model_name

    def run(self):
        try:
            if not WHISPER_AVAILABLE:
                self.error.emit("Whisper nicht installiert!")
                return

            model = whisper.load_model(self.model_name)
            result = model.transcribe(self.audio_path, language="de")
            self.finished.emit(result["text"])
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.is_recording = False
        self.temp_audio_path = None

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("🎤 Whisper Tranny")
        self.setMinimumSize(500, 400)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Record button
        self.record_btn = QPushButton("🎤 Aufnahme starten")
        self.record_btn.setMinimumHeight(60)
        self.record_btn.setFont(QFont("", 14))
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        layout.addWidget(self.record_btn)

        # Status label
        self.status_label = QLabel("Bereit")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("", 14))
        layout.addWidget(self.status_label)

        # Progress bar (hidden by default)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.hide()
        layout.addWidget(self.progress)

        # Transcript text area
        self.transcript_edit = QTextEdit()
        self.transcript_edit.setPlaceholderText(
            "Das Transkript erscheint hier...\n\n"
            "Du kannst Text markieren und mit Strg+C kopieren,\n"
            "oder den 'Alles kopieren' Button verwenden."
        )
        self.transcript_edit.setReadOnly(True)
        self.transcript_edit.setFont(QFont("", 14))
        self.transcript_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                background-color: #fafafa;
                color: #000000;
            }
        """)
        layout.addWidget(self.transcript_edit, stretch=1)

        # Bottom buttons
        btn_layout = QHBoxLayout()

        self.copy_btn = QPushButton("📋 Alles kopieren")
        self.copy_btn.setMinimumHeight(40)
        self.copy_btn.clicked.connect(self.copy_all)
        self.copy_btn.setEnabled(False)
        btn_layout.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("🗑️ Löschen")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_transcript)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        try:
            self.recorder.start()
            self.is_recording = True
            self.record_btn.setText("⏹ Aufnahme beenden")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.status_label.setText("🔴 Aufnahme läuft...")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Mikrofon-Fehler: {e}")

    def stop_recording(self):
        self.is_recording = False
        audio = self.recorder.stop()

        self.record_btn.setText("🎤 Aufnahme starten")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.record_btn.setEnabled(False)

        if len(audio) == 0:
            self.status_label.setText("Keine Audio-Daten aufgenommen")
            self.record_btn.setEnabled(True)
            return

        # Save to temp file
        self.temp_audio_path = tempfile.mktemp(suffix=".wav")
        self.recorder.save_to_file(audio, self.temp_audio_path)

        duration = len(audio) / self.recorder.sample_rate
        self.status_label.setText(f"⏳ Transkribiere... ({duration:.1f}s Audio)")
        self.status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        self.progress.show()

        # Start transcription in background
        self.worker = TranscriptionWorker(self.temp_audio_path, model_name="small")
        self.worker.finished.connect(self.on_transcription_done)
        self.worker.error.connect(self.on_transcription_error)
        self.worker.start()

    def on_transcription_done(self, text: str):
        self.progress.hide()
        self.record_btn.setEnabled(True)
        self.status_label.setText("✅ Fertig!")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

        self.transcript_edit.setPlainText(text.strip())
        self.copy_btn.setEnabled(True)

        # Cleanup temp file
        if self.temp_audio_path:
            Path(self.temp_audio_path).unlink(missing_ok=True)

    def on_transcription_error(self, error: str):
        self.progress.hide()
        self.record_btn.setEnabled(True)
        self.status_label.setText(f"❌ Fehler: {error}")
        self.status_label.setStyleSheet("color: #f44336;")

        if self.temp_audio_path:
            Path(self.temp_audio_path).unlink(missing_ok=True)

    def copy_all(self):
        text = self.transcript_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("📋 In Zwischenablage kopiert!")
            self.status_label.setStyleSheet("color: #4CAF50;")

    def clear_transcript(self):
        self.transcript_edit.clear()
        self.copy_btn.setEnabled(False)
        self.status_label.setText("Bereit")
        self.status_label.setStyleSheet("")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()