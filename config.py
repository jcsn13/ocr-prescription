"""
 Copyright 2024 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from vertexai.generative_models import SafetySetting

PROJECT_ID = "YOUR_PROJECT_NAME"
LOCATION = "us-central1"
MODEL_NAME = "GEMINI_MODEL"
DOCUMENT_AI_PROCESSOR_ID = "YOUR_DOCAI_PROCESSOR_ID"

GENERATION_CONFIG_CLASSIFIER = {
    "max_output_tokens": 8192,
    "temperature": 0.3,
    "top_p": 0.95,
    "response_mime_type": "application/json",
    "response_schema": {"type": "OBJECT", "properties": {"response": {"type": "STRING"}}},
}

GENERATION_CONFIG_PROCESSOR = {
    "max_output_tokens": 8192,
    "temperature": 0.3,
    "top_p": 0.95,
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "OBJECT",
        "required": ["name_in_prescription", "doctor_name", "prescription_date", "crm_number", "crm_state", "status", "reasonsPrescriptionDiscrepancy", "items"],
        "properties": {
            "name_in_prescription": {"type": "STRING"},
            "doctor_name": {"type": "STRING"},
            "prescription_date": {"type": "STRING"},
            "crm_number": {"type": "STRING"},
            "crm_state": {"type": "STRING"},
            "status": {
                "type": "STRING",
                "enum": ["APPROVED", "REPROVED"]
            },
            "reasonsPrescriptionDiscrepancy": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING",
                    "enum": [
                        "MISSING_REGINAL_COUNCIL",
                        "DIVERGENT_REGINAL_COUNCIL",
                        "ILLEGIBLE_PRESCRIPTION",
                        "DIVERGENT_DATE",
                        "INVALID_DOCUMENT_AS_PRESCRIPTION",
                        "SCRATCHED_PRESCRIPTION",
                        "PRESCRIPTION_WITHOUT_DATE",
                        "PRESCRIPTION_WITHOUT_NAME",
                        "PRESCRIPTION_WITH_DIFFERENT_BENEFICIARY_NAME_THIRD_PARTY",
                        "PRESCRIPTION_WITH_DIFFERENT_BENEFICIARY_NAME_FAMILY_GROUP",
                        "EXPIRED_PRESCRIPTION_DATE",
                        "PRESCRIPTION_NOT_RELATED_TO_AUTHORIZATION",
                        "CUT_PRESCRIPTION",
                    ]
                }
            },
            "items": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["product", "status", "reasonsPrescriptionDiscrepancy"],
                    "properties": {
                        "product": {
                            "type": "OBJECT",
                            "required": ["code", "name", "ean"],
                            "properties": {
                                "code": {"type": "STRING"},
                                "name": {"type": "STRING"},
                                "ean": {"type": "STRING"}
                            }
                        },
                        "status": {
                            "type": "STRING",
                            "enum": ["APPROVED", "REPROVED"]
                        },
                        "reasonsPrescriptionDiscrepancy": {
                            "type": "ARRAY",
                            "items": {
                                "type": "STRING",
                                "enum": [
                                    "PRODUCT_NOT_IN_PRESCRIPTION",
                                    "DOSAGE_NOT_MATCHING_PRESCRIPTION",
                                    "PURCHASE_EXCEEDS_RECOMMENDED_DAILY_DOSE"
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
}

SAFETY_SETTINGS = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]