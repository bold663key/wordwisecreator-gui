#!/usr/bin/env python3
import sys
import os
import subprocess
import csv
import re
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox,
    QTextEdit, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# --- Funkcje pomocnicze ---
def delete_dir(dir_path):
    if not os.path.isdir(dir_path):
        return
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(dir_path)

def clean_word(word):
    word = re.sub(r"<[^>]+>", "", word)
    word = re.sub(r"[^\w\s'-]+", "", word, flags=re.UNICODE)
    return word.strip()

def load_stopwords():
    if not os.path.exists('stopwords.txt'):
        return []
    with open('stopwords.txt', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

def load_wordwise_dict():
    if not os.path.exists('wordwise-dict.csv'):
        return {}
    with open('wordwise-dict.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return {row['word'].lower(): row for row in reader}

# --- Worker w osobnym wątku ---
class WordWiseWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, bookfile, hint_level, formats):
        super().__init__()
        self.bookfile = bookfile
        self.hint_level = hint_level
        self.formats = formats

    def run(self):
        if not os.path.exists(self.bookfile):
            self.log_signal.emit(f"❌ Plik {self.bookfile} nie istnieje.")
            return

        self.log_signal.emit(f"[+] Hint level: {self.hint_level}")

        # Sprawdź Calibre
        ebook_convert = shutil.which('ebook-convert')
        if not ebook_convert:
            self.log_signal.emit("❌ Nie znaleziono Calibre (ebook-convert).")
            return
        self.log_signal.emit(f"[+] Znaleziono ebook-convert: {ebook_convert}")

        stopwords = load_stopwords()
        wordwise_dict = load_wordwise_dict()

        # Czyszczenie
        delete_dir('book_dump_html') if os.path.exists('book_dump_html') else None
        if os.path.exists('book_dump.htmlz'):
            os.remove('book_dump.htmlz')

        # Konwersja do HTML
        self.log_signal.emit("[+] Konwersja książki do HTML...")
        subprocess.run([ebook_convert, self.bookfile, 'book_dump.htmlz'])
        subprocess.run([ebook_convert, 'book_dump.htmlz', 'book_dump_html'])

        html_file = None
        for f in ['index.html', 'index1.html']:
            if os.path.exists(os.path.join('book_dump_html', f)):
                html_file = os.path.join('book_dump_html', f)
                break
        if not html_file:
            self.log_signal.emit("❌ Nie udało się skonwertować książki do HTML.")
            return

        # Przetwarzanie treści
        self.log_signal.emit("[+] Przetwarzanie treści...")
        with open(html_file, encoding='utf-8') as f:
            content = f.read()

        words = content.split(' ')
        total_words = len(words)
        for i, chunk in enumerate(words):
            word = clean_word(chunk)
            if not word:
                continue
            if word.lower() in stopwords:
                continue
            if word.lower() in wordwise_dict:
                entry = wordwise_dict[word.lower()]
                if int(entry.get('hint_level', 5)) > self.hint_level:
                    continue
                escaped = re.escape(word)
                words[i] = re.sub(
                    fr'\b{escaped}\b',
                    f"<ruby>{word}<rt>{entry['short_def']}</rt></ruby>",
                    chunk
                )
            if i % 100 == 0:
                self.progress_signal.emit(int(i / total_words * 50))  # połowa postępu

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(' '.join(words))

        # Generowanie formatów
        self.log_signal.emit("[+] Tworzenie wybranych formatów...")
        output_base = os.path.splitext(self.bookfile)[0] + '-wordwised'
        cover_path = os.path.join('book_dump_html', 'cover.jpg')
        for idx, fmt in enumerate(self.formats):
            output_file = f"{output_base}.{fmt}"
            cmd = [ebook_convert, html_file, output_file]
            if os.path.exists(cover_path):
                cmd += ['--cover', cover_path]
            self.log_signal.emit(f"[*] Generuję {fmt}...")
            subprocess.run(cmd)
            if os.path.exists(output_file):
                self.log_signal.emit(f"[OK] Utworzono {output_file}")
            else:
                self.log_signal.emit(f"[ERR] Nie udało się utworzyć {fmt}")
            # aktualizacja postępu (druga połowa)
            self.progress_signal.emit(50 + int((idx + 1) / len(self.formats) * 50))

        self.progress_signal.emit(100)
        self.log_signal.emit("✅ Zakończono!")

# --- GUI ---
from PyQt6.QtWidgets import QApplication, QWidget

class WordWiseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WordWise Generator")
        self.setGeometry(300, 100, 700, 550)

        layout = QVBoxLayout()

        # Plik książki
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Nie wybrano pliku")
        file_button = QPushButton("Wybierz plik EPUB/AZW3/PDF")
        file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_button)
        layout.addLayout(file_layout)

        # Poziom hintów
        hint_layout = QHBoxLayout()
        hint_layout.addWidget(QLabel("Poziom hintów:"))
        self.hint_spin = QSpinBox()
        self.hint_spin.setRange(1, 10)
        self.hint_spin.setValue(5)
        hint_layout.addWidget(self.hint_spin)
        layout.addLayout(hint_layout)

        # Wybór formatów
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formaty wyjściowe:"))
        self.epub_check = QCheckBox("EPUB")
        self.epub_check.setChecked(True)
        self.azw3_check = QCheckBox("AZW3")
        self.azw3_check.setChecked(True)
        self.pdf_check = QCheckBox("PDF")
        self.pdf_check.setChecked(True)
        format_layout.addWidget(self.epub_check)
        format_layout.addWidget(self.azw3_check)
        format_layout.addWidget(self.pdf_check)
        layout.addLayout(format_layout)

        # Pasek postępu
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Log
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)

        # Przycisk generuj
        generate_button = QPushButton("Generuj WordWise")
        generate_button.clicked.connect(self.generate)
        layout.addWidget(generate_button)

        self.setLayout(layout)
        self.bookfile = None
        self.worker = None

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Wybierz plik książki", "", "Ebook files (*.epub *.azw3 *.pdf)")
        if file:
            self.bookfile = file
            self.file_label.setText(os.path.basename(file))

    def generate(self):
        if not self.bookfile:
            self.log_widget.append("❌ Wybierz plik najpierw!")
            return
        hint_level = self.hint_spin.value()
        formats = []
        if self.epub_check.isChecked():
            formats.append('epub')
        if self.azw3_check.isChecked():
            formats.append('azw3')
        if self.pdf_check.isChecked():
            formats.append('pdf')
        if not formats:
            self.log_widget.append("❌ Wybierz przynajmniej jeden format wyjściowy!")
            return

        self.progress.setValue(0)
        self.worker = WordWiseWorker(self.bookfile, hint_level, formats)
        self.worker.log_signal.connect(self.update_log)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.start()

    def update_log(self, text):
        self.log_widget.append(text)

# --- Uruchomienie ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordWiseApp()
    window.show()
    sys.exit(app.exec())
