# WordWise Generator GUI

A desktop application that automatically creates ebooks with word meaning hints (like Kindle's Word Wise feature).

> ⚠️ **Note**: This is a **modified version** of [xnohat/wordwisecreator](https://github.com/xnohat/wordwisecreator) with a GUI interface.

## ✨ Features

- **Simple GUI** built with PyQt6
- **Multi-format support**: EPUB, AZW3, PDF
- **Adjustable hint levels** (1-5)
- **Batch processing** - generate multiple formats at once
- **Real-time progress** tracking

## 🚀 Quick Start

1. **Install requirements:**
```bash
pip install PyQt6
```
2. **Install Calibre** (ensure `ebook-convert` is in PATH)

3. **Run the app:**
```bash
python wordwise_generator.py
```

## 🛠️ Usage

1. Select your ebook file (EPUB/AZW3/PDF)
2. Set hint level difficulty
3. Choose output formats
4. Click "Generate WordWise"

## 📁 Files

- `wordwise_generator.py` - Main application
- `stopwords.txt` - Words to exclude from hints
- `wordwise-dict.csv` - Word definitions database

## 🔄 Modifications from Original

- Added **graphical interface** (PyQt6)
- **Multi-threaded processing** - no UI freezing
- **Progress bar** and real-time logs
- **Batch format generation**
- **Enhanced configuration options**

---

**Simplify your reading experience! 📚**
