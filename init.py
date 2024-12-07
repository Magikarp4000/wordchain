import dataloader
import os.path
from utils import *


# ---------------------- CONFIG ----------------------
MODEL_NAME = 'word2vec-google-news-300'
FILE_NAME = 'googlenews'
# ----------------------------------------------------


if __name__ == '__main__':
    if os.path.isfile(f'{DIR_PATH}/models/{MODEL_NAME}/{MODEL_NAME}.model'):
        print(f"{FILE_NAME}.model already downloaded!")
    else:
        dataloader.download(MODEL_NAME, FILE_NAME)
