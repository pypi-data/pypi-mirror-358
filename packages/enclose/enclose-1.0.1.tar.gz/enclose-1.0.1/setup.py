from setuptools import setup, find_namespace_packages

# Read requirements from requirements.txt
try:
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
except FileNotFoundError:
    requirements = [
        'markdown>=3.3.0',
        'weasyprint>=52.5',
        'reportlab>=3.6.0',
        'Pillow>=8.0.0',
        'cairosvg>=2.5.0',
        'pdf2image>=1.16.0',
        'pytesseract>=0.3.8',
        'beautifulsoup4>=4.9.0',
    ]

setup(
    name="enclose",
    version="1.0.0",
    description="A modular document processing pipeline for Markdown to PDF/SVG/PNG conversion with OCR",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Tom",
    author_email="info@softreck.dev",
    url="https://github.com/veridock/aggregate",
    packages=find_namespace_packages(include=['processor', 'processor.*']),
    py_modules=['__main__'],
    entry_points={
        'console_scripts': [
            'enclose=__main__:main',
        ],
    },
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
