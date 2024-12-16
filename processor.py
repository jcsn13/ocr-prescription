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

from google.cloud import documentai_v1beta3 as documentai
from vertexai.generative_models import GenerativeModel, Part
from config import PROJECT_ID, LOCATION, MODEL_NAME, DOCUMENT_AI_PROCESSOR_ID, GENERATION_CONFIG_PROCESSOR, SAFETY_SETTINGS
from classifier import PrescriptionClassifier
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class ProcessingResult:
    classification: str
    validation_result: str
    error: Optional[str] = None

class PrescriptionProcessor:
    def __init__(self):
        self.classifier = PrescriptionClassifier()
        self.document_client = documentai.DocumentProcessorServiceClient()
        self.gemini_model = GenerativeModel(MODEL_NAME)
        
        self.processor_name = f"projects/{PROJECT_ID}/locations/us/processors/{DOCUMENT_AI_PROCESSOR_ID}"
        
    def _perform_ocr(self, image_file):
        """Performs OCR using Document AI."""
        image_content = image_file.getvalue()
        
        document = {"content": image_content, "mime_type": image_file.type}

        request = documentai.ProcessRequest(
            name=self.processor_name,
            raw_document=document
        )

        result = self.document_client.process_document(request=request)
        return result.document.text
    
    def _validate_prescription(self, image_file, ocr_text=None, transaction_json=None):
        """Validates prescription against transaction data using Gemini."""
        image_part = Part.from_data(data=image_file.getvalue(), mime_type=image_file.type)

        json_response_format = """
        {
            "name_in_prescription": "example_name",
            "doctor_name": "example_doctor_name",
            "prescription_date": "2024-01-01",
            "crm_number": "31024",
            "crm_state": "SP"
            "status": "APPROVED" ou "REPROVED",
            "reasonsPrescriptionDiscrepancy": ["CODIGO_ERRO_1", "CODIGO_ERRO_2"] ou []
            "items": [
                {
                    "product": {
                        "code": "código do produto",
                        "name": "nome do produto",
                        "ean": "ean do produto"
                    },
                    "status": "APPROVED" ou "REPROVED",
                    "reasonsPrescriptionDiscrepancy": ["CODIGO_ERRO_1", "CODIGO_ERRO_2"] ou []
                }
            ]
        }
        """

        if ocr_text is not None:
            ocr_text = f"Receita (texto OCR):\n{ocr_text}"
        else:
            ocr_text = ""

        prompt = """
            Você é uma IA especializada em validação de transações com base em receitas médicas. Seu objetivo é verificar a conformidade entre as informações fornecidas em uma transação de venda e os dados contidos na receita médica associada.

            {ocr_text}

            Dados da transação:
            {transaction_data}

            Regras de Validação da Receita:
            - MISSING_REGINAL_COUNCIL: O número do conselho regional está ausente na receita.
            - DIVERGENT_REGINAL_COUNCIL: O conselho regional na receita não corresponde ao fornecido na transação.
            - ILLEGIBLE_PRESCRIPTION: A receita está ilegível.
            - DIVERGENT_DATE: A data na receita não corresponde à data da transação.
            - INVALID_DOCUMENT_AS_PRESCRIPTION: O documento apresentado não é um receituário válido.
            - SCRATCHED_PRESCRIPTION: A receita está rasurada.
            - PRESCRIPTION_WITHOUT_DATE: A receita não possui data.
            - PRESCRIPTION_WITHOUT_NAME: A receita não possui o nome do paciente.
            - PRESCRIPTION_WITH_DIFFERENT_BENEFICIARY_NAME_THIRD_PARTY: O nome na receita é diferente do nome do beneficiário.
            - PRESCRIPTION_WITH_DIFFERENT_BENEFICIARY_NAME_FAMILY_GROUP: O nome na receita é diferente do nome do beneficiário dentro do grupo familiar.
            - EXPIRED_PRESCRIPTION_DATE: A data na receita está vencida.
            - PRESCRIPTION_NOT_RELATED_TO_AUTHORIZATION: A receita não está relacionada com a autorização médica.
            - CUT_PRESCRIPTION: A receita está cortada.
            
            Regras de Validação dos Medicamentos Receitados(campo "items" no JSON de venda):
            - PRODUCT_NOT_IN_PRESCRIPTION: O produto dispensado não está prescrito na receita.
            - DOSAGE_NOT_MATCHING_PRESCRIPTION: A dosagem do medicamento não corresponde à prescrição médica.
            - PURCHASE_EXCEEDS_RECOMMENDED_DAILY_DOSE: A quantidade comprada excede a recomendada na receita

            Importante:
            - Analise todas as regras individualmente.
            - Os campos de do JSON de venda não devem divergir das informações da receita
                - Exemplo: Se o nome no JSON de venda for "name_in_prescription": "João Paulo" e o nome na receita for identificado "Paula Maria" Existe uma Divergência de PRESCRIPTION_WITH_DIFFERENT_BENEFICIARY_NAME_THIRD_PARTY
                - Exemplo: Se a data no JSON de venda for "prescription_date":"2024-10-25" e a data na receita for identificada 14 de dezembro de 2023 Existe uma Divergência de EXPIRED_PRESCRIPTION_DATE
            - Você deve posicionar as regras de acordo com o campo de validação
                - Regras de Validação da Receita no reasonsPrescriptionDiscrepancy no escopo da receita
                - Regras de Validação dos Medicamentos Receitados no reasonsPrescriptionDiscrepancy no escopo dos medicamentos

            Forneça uma resposta no seguinte formato JSON:
            {json_response}
            
            Se houver discrepâncias, liste-as em reasonsPrescriptionDiscrepancy. O status geral deve ser APPROVED apenas se todos os itens forem aprovados.
            Responda APENAS com o JSON, sem explicações adicionais.
            """.format(
                ocr_text=ocr_text,
                transaction_data=transaction_json,
                json_response=json_response_format
            )

        responses = self.gemini_model.generate_content(
            [prompt, image_part],
            generation_config=GENERATION_CONFIG_PROCESSOR,
            safety_settings=SAFETY_SETTINGS,
            stream=True,
        )

        response_text = "".join(response.text for response in responses)

        return json.loads(response_text)
        
    def process_prescription(self, image_file, transaction_json):
        """Main processing pipeline."""
        try:
            # Get classification
            classification_response = self.classifier.classify_image(image_file)

            try:
                if isinstance(classification_response, str):
                    classification_data = json.loads(classification_response)
                    classification = classification_data.get("response", "")
                else:
                    classification = classification_response
            except json.JSONDecodeError:
                classification = classification_response

            if classification.lower() in "[manuscrita]":
                ocr_text = self._perform_ocr(image_file)
                validation_result = self._validate_prescription(image_file, ocr_text, transaction_json)
            else:
                validation_result = self._validate_prescription(image_file, transaction_json=transaction_json)


            return ProcessingResult(
                classification=classification,
                validation_result=validation_result
            )
                
        except Exception as e:
            return ProcessingResult(
                classification="ERROR",
                validation_result={},
                error=f"Error in prescription processing: {str(e)}"
            )