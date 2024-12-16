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

import streamlit as st
from processor import PrescriptionProcessor
import json

def main():
    st.title("Medical Prescription Validator")
    st.write("Upload a medical prescription image and provide transaction data for validation.")

    processor = PrescriptionProcessor()
    
    # File uploader for prescription image
    uploaded_file = st.file_uploader("Choose a prescription image", type=["jpg", "jpeg", "png"])

    # Text area for transaction JSON
    transaction_json_str = st.text_area(
        "Enter transaction JSON",
        height=200,
        placeholder='''{
            "name_in_prescription": "example_name",
            "doctor_name": "example_doctor_name",
            "prescription_date": "2024-01-01",
            "crm_number": "31024",
            "crm_state": "SP",
            "items": [
                {
                    "product": {
                        "code": "2126",
                        "name": "Dipirona",
                        "ean": "07898148305100",
                        "dosage": "500mg",
                        "usage_instructions": "Tomar 3 vezes ao dia a cada 8 horas de intervalo"
                    }
                }
            ]
        }'''
    )

    if uploaded_file is not None and transaction_json_str:
        st.image(uploaded_file, caption="Uploaded Prescription", use_column_width=True)
        
        if st.button("Validate Prescription"):
            try:
                # Parse transaction JSON
                transaction_json = json.loads(transaction_json_str)
                
                with st.spinner("Analyzing prescription..."):
                    result = processor.process_prescription(uploaded_file, transaction_json)
                    
                    st.success("Analysis Complete")
                    
                    # Display Classification
                    st.markdown("### Classification")
                    st.info(result.classification)
                    
                    # Display Validation Results
                    st.markdown("### Validation Results")
                    if result.validation_result:
                        st.json(result.validation_result)
                    
                    # Display Error (if any)
                    if result.error:
                        st.error(result.error)
            
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check the transaction data.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()