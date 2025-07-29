# Document Processing Pipeline - File Tree

## 📁 Initial Project Structure

```
aggregate/
├── 📄 Makefile                    # Build automation and workflow
├── 🐍 processor.py               # Main Python processing pipeline
├── 📋 requirements.txt           # Python package dependencies
├── 🛠️ setup.sh                   # System setup script
└── 📖 README.md                  # Project documentation
```

## 📁 After Installation (`make install`)

```
aggregate/
├── 📄 Makefile
├── 🐍 processor.py
├── 📋 requirements.txt
├── 🛠️ setup.sh
├── 📖 README.md
└── 📁 venv/                      # Virtual environment
    ├── bin/                      # (Linux/macOS) or Scripts/ (Windows)
    │   ├── activate              # Environment activation script
    │   ├── pip                   # Package installer
    │   └── python                # Python interpreter
    ├── lib/                      # Installed packages
    │   └── python3.x/
    │       └── site-packages/    # All pip-installed libraries
    └── pyvenv.cfg               # Environment configuration
```

## 📁 After Running Pipeline (`make all`)

```
aggregate/
├── 📄 Makefile
├── 🐍 processor.py
├── 📋 requirements.txt
├── 🛠️ setup.sh
├── 📖 README.md
├── 📁 venv/                      # Virtual environment
│   └── ... (environment files)
└── 📁 output/                    # Generated files directory
    ├── 📝 invoice_example.md         # Step 1: Source markdown
    ├── 📄 invoice_example.pdf        # Step 2: Generated PDF
    ├── 🎨 invoice_example.svg        # Step 3: SVG with embedded PDF
    ├── 🖼️ page_1.png                # Step 4: PNG page extraction
    ├── 🖼️ page_2.png                # (if multi-page document)
    ├── 📊 metadata.json             # Step 5: Processing metadata
    ├── 🔍 svg_search_results.json   # Step 6: Search results
    └── 🌐 dashboard.html            # Step 7: Interactive dashboard
```

## 📁 Complete File Tree with Details

```
aggregate/
│
├── 📄 Makefile                    # 2KB - Build automation
│   ├── install target            # Setup virtual environment
│   ├── create target             # Generate example files
│   ├── process target            # Run conversion pipeline
│   ├── aggregate target          # Create dashboard
│   ├── search target             # Find SVG files
│   └── clean targets             # Cleanup commands
│
├── 🐍 processor.py               # 15KB - Main processing engine
│   ├── DocumentProcessor class   # Core pipeline handler
│   ├── create_example_markdown() # Step 1: Generate sample
│   ├── markdown_to_pdf()         # Step 2: MD → PDF conversion
│   ├── pdf_to_svg()             # Step 3: PDF → SVG embedding
│   ├── svg_to_png()             # Step 4: PDF → PNG extraction
│   ├── process_ocr()            # Step 5: OCR processing
│   ├── search_svg_files()       # Step 6: File system search
│   ├── aggregate_to_html_table() # Step 7: Dashboard creation
│   └── save_metadata()          # JSON metadata management
│
├── 📋 requirements.txt           # 1KB - Python dependencies
│   ├── markdown==3.4.4          # Markdown processing
│   ├── reportlab==4.0.4         # PDF generation
│   ├── weasyprint==60.0         # HTML to PDF conversion
│   ├── cairosvg==2.7.1          # SVG processing
│   ├── Pillow==10.0.0           # Image manipulation
│   ├── pytesseract==0.3.10      # OCR engine
│   ├── pdf2image==3.1.0         # PDF to image conversion
│   ├── beautifulsoup4==4.12.2   # XML/HTML parsing
│   └── lxml==4.9.3              # XML processing
│
├── 🛠️ setup.sh                   # 2KB - System setup automation
│   ├── OS detection             # Linux/macOS/Windows
│   ├── System dependencies      # tesseract, poppler, cairo
│   └── Project initialization   # File creation and permissions
│
├── 📖 README.md                  # 8KB - Complete documentation
│   ├── Installation guide       # Step-by-step setup
│   ├── Usage examples          # Command demonstrations
│   ├── Pipeline explanation     # Workflow details
│   ├── Troubleshooting guide   # Common issues
│   └── File structure overview # This tree!
│
├── 📁 venv/ (after make install)  # ~50MB - Virtual environment
│   ├── bin/activate             # Environment activation
│   ├── lib/python3.x/site-packages/
│   │   ├── markdown/            # Markdown library
│   │   ├── reportlab/           # PDF generation
│   │   ├── weasyprint/          # HTML to PDF
│   │   ├── cairosvg/            # SVG processing
│   │   ├── PIL/                 # Image processing
│   │   ├── pytesseract/         # OCR wrapper
│   │   ├── pdf2image/           # PDF conversion
│   │   ├── bs4/                 # BeautifulSoup
│   │   └── lxml/                # XML processing
│   └── pyvenv.cfg               # Environment config
│
└── 📁 output/ (after make all)    # ~2MB - Generated content
    ├── 📝 invoice_example.md      # 1KB - Source markdown
    │   ├── Invoice header         # Company/customer info
    │   ├── Service table         # Items, quantities, prices
    │   ├── Summary section       # Totals and taxes
    │   └── Payment terms         # Due dates and notes
    │
    ├── 📄 invoice_example.pdf     # 50KB - Styled PDF
    │   ├── CSS-styled layout     # Professional formatting
    │   ├── Table formatting      # Bordered service table
    │   └── Typography            # Arial font, proper spacing
    │
    ├── 🎨 invoice_example.svg     # 500KB - SVG container
    │   ├── RDF metadata          # Dublin Core elements
    │   ├── Embedded PDF data     # Base64 encoded PDF
    │   ├── Visual elements       # Title, decorative elements
    │   └── Foreign object        # PDF embed container
    │
    ├── 🖼️ page_1.png             # 200KB - Page image
    │   ├── 150 DPI resolution    # High quality extraction
    │   ├── Full page content     # Complete PDF page
    │   └── Base64 encoded        # For metadata storage
    │
    ├── 📊 metadata.json          # 5KB - Processing metadata
    │   ├── File information      # Paths, sizes, timestamps
    │   ├── Processing steps      # Conversion tracking
    │   ├── OCR results          # Text extraction, confidence
    │   ├── Page data            # PNG files, base64 data
    │   └── Validation info      # Success/failure status
    │
    ├── 🔍 svg_search_results.json # 2KB - Search results
    │   ├── Found SVG files      # File paths and metadata
    │   ├── File statistics      # Sizes, modification dates
    │   ├── Metadata presence    # RDF/Dublin Core detection
    │   └── PDF embedding info   # Base64 data detection
    │
    └── 🌐 dashboard.html         # 15KB - Interactive dashboard
        ├── HTML table structure  # Responsive layout
        ├── CSS styling          # Professional appearance
        ├── SVG thumbnails       # Embedded file previews
        ├── File information     # Metadata display
        ├── Navigation links     # File system links
        └── JavaScript          # Interactive features
```

## 📊 File Size Breakdown

| Component | Size | Description |
|-----------|------|-------------|
| **Source Code** | ~26KB | Core project files |
| **Documentation** | ~8KB | README and comments |
| **Dependencies** | ~50MB | Python packages in venv |
| **Generated Files** | ~2MB | Output from pipeline |
| **Total Project** | ~52MB | Complete installation |

## 🔧 Runtime Dependencies

```
System Level:
├── tesseract-ocr     # OCR engine
├── poppler-utils     # PDF processing
├── libcairo2-dev     # SVG rendering
└── python3.7+       # Python interpreter

Python Packages:
├── markdown          # MD → HTML conversion
├── weasyprint       # HTML → PDF with CSS
├── cairosvg         # SVG processing
├── pdf2image        # PDF → PNG conversion
├── pytesseract      # OCR text extraction
├── Pillow           # Image manipulation
├── beautifulsoup4   # XML/SVG parsing
└── reportlab        # PDF generation (backup)
```

## 🚀 Development Files

For development and customization:

```
aggregate/
├── .gitignore        # Git ignore patterns
├── .env.example      # Environment variables template
├── tests/           # Unit tests directory
│   ├── test_processor.py
│   └── test_data/
├── docs/            # Additional documentation
│   ├── API.md
│   └── CONTRIBUTING.md
└── examples/        # Additional examples
    ├── custom_invoice.md
    └── multi_page.md
```

This structure provides a complete, self-contained document processing pipeline with clear separation of concerns and comprehensive documentation!