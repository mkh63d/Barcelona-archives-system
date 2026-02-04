# PDF Cleaning and Noise Removal Tool

## Overview
This Jupyter notebook provides an automated pipeline for cleaning and enhancing scanned PDF documents. It removes paper texture noise, enhances text clarity, and reconstructs letter strokes while preserving document readability.

## Features
- **Noise Removal**: Eliminates paper texture and grain
- **Text Enhancement**: Improves text clarity using adaptive thresholding
- **Morphological Operations**: Reconstructs broken letters and removes artifacts
- **Batch Processing**: Handles multi-page PDFs automatically
- **High Quality Output**: Generates clean, OCR-ready documents at 300 DPI

## Requirements

### System Dependencies
- `poppler-utils` (for PDF processing)

### Python Libraries
- `opencv-python` (cv2)
- `numpy`
- `pdf2image`
- `img2pdf`

## Installation

The notebook automatically installs all dependencies. If manual installation is needed:

```bash
# System dependencies (Ubuntu/Debian)
apt-get install -y poppler-utils

# Python packages
pip install opencv-python numpy pdf2image img2pdf
```

## Usage

### 1. Configure Paths
Edit the configuration section in the notebook:

```python
RUTA_ENTRADA = '/content/guio.pdf'          # Input PDF path
RUTA_SALIDA  = '/content/guio_ajustado_limpio.pdf'  # Output PDF path
```

### 2. Run the Notebook
Execute all cells in order. The processing pipeline will:
1. Convert PDF pages to images (300 DPI)
2. Apply denoising and enhancement
3. Perform binarization and morphological operations
4. Reassemble into a clean PDF

### 3. Monitor Progress
The script provides real-time feedback:
- Progress updates every 5 pages
- Completion confirmation with output path

## Processing Pipeline

### Step-by-Step Breakdown

1. **Grayscale Conversion**: Converts RGB images to grayscale
2. **Denoising** (`fastNlMeansDenoising`): Removes paper texture (strength: 10)
3. **Contrast Enhancement** (`CLAHE`): Controlled enhancement (clipLimit: 1.5)
4. **Adaptive Thresholding**: Separates text from background
5. **Opening Operation**: Removes small noise artifacts (< 12 pixels)
6. **Closing Operation**: Reconnects broken letter strokes
7. **Component Filtering**: Removes remaining noise by area analysis
8. **Inversion**: Creates black text on white background

## Parameters

You can fine-tune these parameters in the code:

| Parameter | Default | Description |
|-----------|---------|-------------|
| DPI | 300 | Image resolution |
| Denoise strength | 10 | Higher = more smoothing |
| CLAHE clipLimit | 1.5 | Contrast enhancement (1.0-3.0) |
| Min area | 12 px | Minimum component size to keep |
| Max area | 15000 px | Maximum component size |

## Example

### Input
Scanned document with:
- Paper grain/texture
- Uneven lighting
- Broken or faded text
- Background noise

### Output
Clean document with:
- Clear, crisp text
- Uniform white background
- OCR-ready format
- Reduced file size

## Troubleshooting

### File Not Found
```
No se encontró 'archivo.pdf'. Súbelo a la carpeta de la izquierda.
```
**Solution**: Upload your PDF to the correct directory or update `RUTA_ENTRADA`

### Poor Results
- **Too much noise removed**: Decrease denoise strength (default: 10)
- **Text too thin**: Increase closing kernel size
- **Text too thick**: Decrease closing kernel size
- **Background not clean**: Lower `clipLimit` or increase min area filter

## Performance

- **Processing Speed**: ~1-2 seconds per page (300 DPI)
- **Memory Usage**: ~200-300MB for typical documents
- **Output Size**: Typically 50-70% smaller than input

## Use Cases

- Archive digitization
- OCR preprocessing
- Document restoration
- Historical document preservation
- Library digitization projects

## Notes

- Optimized for Spanish archival documents
- Tested with handwritten and printed materials
- Temporary files are automatically cleaned up
- Output is always in PDF format at 300 DPI

## Credits

Preprocessing Pipeline developed by:
- Wasay Rizwani
- Sri Rama Saketh
- Venkata Sai Saketh Goda
- Subhajit Nandi
- Bhoomika Nandihalli
- Andrzej Martinez

## License

Open source - feel free to modify and adapt for your needs.

## Support

For issues or improvements, please refer to the project repository.
