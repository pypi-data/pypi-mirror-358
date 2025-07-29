# Document Processing Pipeline

A comprehensive document processing system that converts Markdown files through a complete pipeline: Markdown → PDF → SVG → PNG → OCR → Search → Dashboard.

## 🚀 Features

- **Multi-format conversion**: Markdown to PDF with styling
- **SVG embedding**: PDF embedded as base64 data URI in SVG containers
- **Image extraction**: PDF pages converted to PNG with base64 encoding
- **OCR processing**: Text extraction with confidence scoring
- **Metadata tracking**: JSON metadata throughout the pipeline
- **File system search**: Automatic SVG file discovery
- **Interactive dashboard**: HTML table with SVG thumbnails
- **Automated workflow**: Makefile-driven pipeline

## 📋 Prerequisites

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils libcairo2-dev
```

**macOS:**
```bash
brew install tesseract poppler cairo
```

**Windows:**
- Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Install [Poppler](https://poppler.freedesktop.org/)

### Python Requirements
- Python 3.7+
- pip3

## 🛠️ Installation

### Quick Setup
```bash
# Clone or download the project files
git clone https://github.com/veridock/aggregate.git
cd aggregate

# Install dependencies
make install
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

## 🎯 Usage

### Quick Start
```bash
# Run complete pipeline
make all
```

### Step-by-Step Execution

1. **Create Example Files**
   ```bash
   make create
   ```
   - Generates `invoice_example.md`

2. **Process Documents**
   ```bash
   make process
   ```
   - Converts MD → PDF → SVG → PNG
   - Performs OCR processing
   - Creates metadata JSON

3. **Search & Aggregate**
   ```bash
   make search     # Find all SVG files
   make aggregate  # Create dashboard
   ```

4. **View Results**
   - Dashboard opens automatically in browser
   - Access: `output/dashboard.html`

### Individual Commands

```bash
# Python script direct usage
python processor.py --step create
python processor.py --step process
python processor.py --step search
python processor.py --step aggregate
```

## 📁 Project Structure

```
aggregate/
├── Makefile                 # Build automation
├── processor.py            # Main processing pipeline
├── requirements.txt        # Python dependencies
├── setup.sh               # System setup script
├── README.md              # Project documentation
├── venv/                  # Virtual environment (created)
└── output/                # Generated files (created)
    ├── invoice_example.md     # Source markdown
    ├── invoice_example.pdf    # Generated PDF
    ├── invoice_example.svg    # SVG with embedded PDF
    ├── page_1.png            # Extracted PNG pages
    ├── page_N.png            # (multiple pages if needed)
    ├── metadata.json         # Processing metadata
    ├── svg_search_results.json # Search results
    └── dashboard.html        # Interactive dashboard
```

## 🔄 Pipeline Workflow

```
Step 1: CREATE
├── Generate example markdown file (invoice)
└── Output: invoice_example.md

Step 2: MARKDOWN → PDF
├── Convert markdown to styled HTML
├── Generate PDF with CSS styling
└── Output: invoice_example.pdf

Step 3: PDF → SVG
├── Embed PDF as base64 data URI
├── Add SVG metadata (RDF/Dublin Core)
└── Output: invoice_example.svg + metadata.json

Step 4: PDF → PNG
├── Extract PDF pages as PNG images
├── Convert PNG to base64 encoding
└── Output: page_*.png + updated metadata

Step 5: OCR PROCESSING
├── Extract text from PNG images
├── Calculate confidence scores
└── Output: updated metadata with OCR data

Step 6: FILESYSTEM SEARCH
├── Scan for all SVG files
├── Parse SVG metadata
└── Output: svg_search_results.json

Step 7: DASHBOARD CREATION
├── Generate HTML table with thumbnails
├── Embed SVG previews
└── Output: dashboard.html (opens in browser)
```

## 📊 Output Files

### Metadata Structure
```json
{
  "file": "path/to/file.svg",
  "type": "svg_with_pdf",
  "created": "2025-06-25T10:30:00",
  "pdf_embedded": true,
  "total_pages": 1,
  "pages": [
    {
      "page": 1,
      "file": "page_1.png",
      "base64": "iVBORw0KGgoAAAANSU...",
      "ocr_text": "Invoice #INV-2025-001...",
      "ocr_confidence": 95.7,
      "word_count": 45
    }
  ]
}
```

### Dashboard Features
- **SVG Thumbnails**: Direct embedding of SVG files
- **File Information**: Path, size, modification date
- **PDF Detection**: Indicates embedded PDF data
- **Metadata Status**: Shows RDF metadata presence
- **Interactive Links**: Click to open files

## 🛠️ Makefile Targets

| Target | Description |
|--------|-------------|
| `install` | Install dependencies in virtual environment |
| `create` | Create example markdown file |
| `process` | Run conversion pipeline (steps 2-5) |
| `search` | Search filesystem for SVG files |
| `aggregate` | Create HTML dashboard |
| `clean` | Remove generated files |
| `clean-all` | Remove everything including venv |
| `help` | Show available commands |

## 🔧 Configuration

### OCR Language Support
```bash
# Install additional languages
sudo apt-get install tesseract-ocr-pol  # Polish
sudo apt-get install tesseract-ocr-deu  # German

# Configure in processor.py
pytesseract.image_to_string(image, lang='pol+eng')
```

### PDF Styling
Modify CSS in `markdown_to_pdf()` method:
```python
styled_html = f"""
<style>
    body {{ font-family: 'Your Font', sans-serif; }}
    /* Add custom styles */
</style>
"""
```

## 🐛 Troubleshooting

### Common Issues

**OCR Not Working:**
```bash
# Check tesseract installation
tesseract --version

# Install language packs
sudo apt-get install tesseract-ocr-eng
```

**PDF Conversion Fails:**
```bash
# Check weasyprint dependencies
pip install --upgrade weasyprint
```

**SVG Rendering Issues:**
```bash
# Install cairo development libraries
sudo apt-get install libcairo2-dev
```

### Debug Mode
```bash
# Enable verbose output
python processor.py --step process --verbose
```

## 📝 License

This project is open source. See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: This README
- **Examples**: Check `output/` directory after running pipeline

---

## 🎉 Quick Demo

```bash
# Complete setup and demo
make install
make all

# View results
open output/dashboard.html  # macOS
xdg-open output/dashboard.html  # Linux
```

The dashboard will show your processed documents with interactive thumbnails and metadata!