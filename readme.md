# Medical Prescription Validator

## ⚠️ Disclaimer

**This project is for demonstration purposes only!**

This code is provided as a demonstration of how to integrate Google Cloud services (Document AI and Vertex AI) for document processing and validation. It is not intended for production use and comes with no warranties or guarantees. The code should not be used in any production environment or for processing real medical prescriptions without proper security reviews, compliance checks, and substantial modifications to meet production standards.

Key points:
- This is a proof-of-concept demonstration only
- Not suitable for production use
- No warranty or guarantee of accuracy
- Not compliant with healthcare regulations or standards
- Intended purely for learning and demonstration purposes

## Overview

A Python application that validates medical prescriptions using Google Cloud's Document AI and Vertex AI services. The system can classify prescriptions as handwritten or typed, perform OCR on handwritten prescriptions, and validate prescription details against transaction data.

## Features

- Image classification (handwritten vs typed prescriptions)
- Optical Character Recognition (OCR) for handwritten prescriptions
- Prescription validation against transaction data
- User-friendly web interface built with Streamlit
- Integration with Google Cloud services (Document AI and Vertex AI)

## Prerequisites

- Python 3.8 or higher
- Google Cloud account with the following APIs enabled:
  - Document AI API
  - Vertex AI API
- Required Python packages (see `requirements.txt`)

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd medical-prescription-validator
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Google Cloud credentials:
   - Create or use an existing Google Cloud project
   - Set up authentication by creating a service account and downloading the JSON key file
   - Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

4. Update the configuration in `config.py`:
```python
PROJECT_ID = "your-project-id"
LOCATION = "your-preferred-region"  # e.g., "us-central1"
MODEL_NAME = "gemini-2.0-flash-exp"
DOCUMENT_AI_PROCESSOR_ID = "your-processor-id"
```

Note: The example images used in the classifier (`manuscritas/` and `digitadas/` directories) should be replaced with your own sample images. The current examples are public domain images used for demonstration purposes only.

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Access the web interface through your browser (typically at `http://localhost:8501`)

3. Upload a prescription image and provide transaction data in JSON format:
```json
{
    "name_in_prescription": "Patient Name",
    "doctor_name": "Doctor Name",
    "prescription_date": "2024-01-01",
    "crm_number": "12345",
    "crm_state": "SP",
    "items": [
        {
            "product": {
                "code": "2126",
                "name": "Medicine Name",
                "ean": "12345678901234",
                "dosage": "500mg",
                "usage_instructions": "Usage instructions here"
            }
        }
    ]
}
```

4. Click "Validate Prescription" to process the image and receive the validation results

## Validation Rules

### Prescription Validation Rules
- Missing regional council number
- Divergent regional council information
- Illegible prescription
- Date discrepancies
- Invalid document format
- Scratched or damaged prescription
- Missing date or patient name
- Beneficiary name mismatches
- Expired prescription
- Authorization mismatches
- Cut or incomplete prescription

### Medicine Validation Rules
- Product not in prescription
- Dosage mismatches
- Purchase quantity exceeds recommended daily dose

## Project Structure

- `app.py`: Main Streamlit application
- `classifier.py`: Prescription image classification logic
- `config.py`: Configuration settings and constants
- `processor.py`: Core prescription processing logic
- `utils.py`: Utility functions

## License

Copyright 2024 Google LLC

Licensed under the Apache License, Version 2.0 - see LICENSE file for details.