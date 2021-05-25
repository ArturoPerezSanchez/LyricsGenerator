from aitextgen import aitextgen
import os
from django.conf import settings

#Cargamos el modelo entrenado, que se guarda por defecto en trained_model y el tokenizer en el directorio raíz
if('trained_model' not in os.listdir(os.path.join(settings.BASE_DIR))):
    os.mkdir(os.path.join(settings.BASE_DIR, 'trained_model'))

if len(os.listdir(os.path.join(settings.BASE_DIR, 'trained_model')) ) != 0:
    ai = aitextgen(model_folder=(os.path.join(settings.BASE_DIR, 'trained_model')), 
              tokenizer_file=(os.path.join(settings.BASE_DIR, 'aitextgen.tokenizer.json')))
else:
    ai = None

def generate(verses, firstWords, max_length, temperature, ai=ai):
    if not ai:
        res = None
    else:
        res = ai.generate(n=verses, prompt=firstWords, max_length=max_length, temperature=temperature, return_as_list=True)
    return res