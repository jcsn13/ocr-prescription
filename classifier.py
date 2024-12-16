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

import vertexai
from vertexai.generative_models import GenerativeModel, Part
from config import PROJECT_ID, LOCATION, MODEL_NAME, GENERATION_CONFIG_CLASSIFIER, SAFETY_SETTINGS
from utils import read_image_file

class PrescriptionClassifier:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel(MODEL_NAME)
        
    def _get_example_images(self):
        return {
            'manuscrita01': Part.from_data(data=read_image_file('manuscritas/manuscrita01.jpg'), mime_type="image/jpeg"),
            'manuscrita02': Part.from_data(data=read_image_file('manuscritas/manuscrita02.jpg'), mime_type="image/jpeg"),
            'digitada01': Part.from_data(data=read_image_file('digitadas/digitada01.jpg'), mime_type="image/jpeg"),
            'digitada02': Part.from_data(data=read_image_file('digitadas/digitada02.png'), mime_type="image/png")
        }
        
    def classify_image(self, image_file):
        if image_file is None:
            return "Please upload an image"
            
        image_bytes = image_file.getvalue()
        image_part = Part.from_data(data=image_bytes, mime_type=image_file.type)
        examples = self._get_example_images()
        
        prompt1 = """
            Analise a receita médica fornecida e classifique-a em uma das seguintes categorias:
            [MANUSCRITA] - Se a maior parte do conteúdo principal da receita (medicamentos, dosagens e instruções) foi escrito à mão
            [DIGITADA] - Se a maior parte do conteúdo principal da receita (medicamentos, dosagens e instruções) foi digitado/impresso
            
            Exemplos [MANUSCRITA]:
        """

        prompt2 = "Exemplos [DIGITADA]:"
        
        prompt3 = """
            Importante:
            - Considere apenas o corpo principal da receita
            - Ignore a assinatura do médico
            - Ignore carimbos e elementos do cabeçalho
            - Foque especificamente em como os medicamentos e instruções foram registrados

            Responda apenas com uma das classificações: MANUSCRITA ou DIGITADA
            Receita Médica:
            """
            
        responses = self.model.generate_content(
            [prompt1, examples["manuscrita01"], examples["manuscrita02"], prompt2, examples["digitada01"], examples["digitada02"], prompt3, image_part],
            generation_config=GENERATION_CONFIG_CLASSIFIER,
            safety_settings=SAFETY_SETTINGS,
            stream=True,
        )
        
        return "".join(response.text for response in responses)