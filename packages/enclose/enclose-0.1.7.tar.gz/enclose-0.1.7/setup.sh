#!/bin/bash
# Document Processing Pipeline Setup Script

echo "Setting up Document Processing Pipeline..."

# Create project directory
mkdir -p aggregate
cd aggregate

# Check if running on Linux or macOS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing system dependencies for Linux..."
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr poppler-utils libcairo2-dev
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing system dependencies for macOS..."
    brew install tesseract poppler cairo
else
    echo "Please manually install: tesseract-ocr, poppler-utils, cairo"
fi

# Copy files (assuming they're in the current directory)
echo "Setting up project files..."

# Create Makefile
cat > Makefile << 'EOF'
# (Makefile content would be here - use the Makefile artifact)
EOF

# Create processor.py
cat > processor.py << 'EOF'
# (Python code would be here - use the processor.py artifact)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# (Requirements would be here - use the requirements.txt artifact)
EOF

# Make processor executable
chmod +x processor.py

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run 'make install' to install Python dependencies"
echo "2. Run 'make create' to create example files"
echo "3. Run 'make process' to run the full pipeline"
echo "4. Run 'make aggregate' to create the dashboard"
echo "5. Run 'make help' for all available commands"