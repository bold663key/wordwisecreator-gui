#WordWise Generator GUI

A desktop application that automatically creates ebooks with word meaning hints (like Kindle's Word Wise feature).

    ⚠️ Note: This is a modified version of xnohat/wordwisecreator with a GUI interface.

✨ Features

    Simple GUI built with PyQt6

    Multi-format support: EPUB, AZW3, PDF

    Adjustable hint levels (1-10)

    Batch processing - generate multiple formats at once

    Real-time progress tracking

🚀 Quick Start

    Install requirements:

bash

pip install PyQt6

    Install Calibre (ensure ebook-convert is in PATH)

    Run the app:

bash

python wordwise_generator.py

🛠️ Usage

    Select your ebook file (EPUB/AZW3/PDF)

    Set hint level difficulty

    Choose output formats

    Click "Generate WordWise"

📁 Files

    wordwise_generator.py - Main application

    stopwords.txt - Words to exclude from hints

    wordwise-dict.csv - Word definitions database

🔄 Modifications from Original

    Added graphical interface (PyQt6)

    Multi-threaded processing - no UI freezing

    Progress bar and real-time logs

    Batch format generation

    Enhanced configuration options

Simplify your reading experience! 📚
