#Importamos las librerías necesarias
# pip3 install aitextgen
from aitextgen.TokenDataset import TokenDataset
from aitextgen.tokenizers import train_tokenizer
from aitextgen.utils import GPT2ConfigCPU
from aitextgen import aitextgen
import os
from django.conf import settings

def train():
    # Indicamos el fichero a utilizar para entrenar el modelo
    file_name = os.path.join(settings.BASE_DIR, "lyrics/data/song_lyrics.txt")

    # Train a custom BPE Tokenizer on the downloaded text
    # This will save one file: `aitextgen.tokenizer.json`, which contains the
    # information needed to rebuild the tokenizer.
    train_tokenizer(file_name)
    tokenizer_file = "aitextgen.tokenizer.json"


    # GPT2ConfigCPU is a mini variant of GPT-2 optimized for CPU-training
    # e.g. the # of input tokens here is 64 vs. 1024 for base GPT-2.
    config = GPT2ConfigCPU()

    # Instantiate aitextgen using the created tokenizer and config.
    ai = aitextgen(tokenizer_file=tokenizer_file, config=config)

    # You can build datasets for training by creating TokenDatasets,
    # which automatically processes the dataset with the appropriate size.
    data = TokenDataset(file_name, tokenizer_file=tokenizer_file, block_size=64)

    # Train the model! It will save pytorch_model.bin periodically and after completion to the `trained_model` folder.
    # On a 2020 8-core iMac, this took ~25 minutes to run.
    ai.train(data, batch_size=16, num_steps=10000)