import dataloader
import os.path
from utils import *
from config import *


def init():
    if os.path.isfile(f'{DIR_PATH}/models/{MODEL_NAME}/{MODEL_NAME}.model'):
        print(f"{FILE_NAME}.model already downloaded!")
    else:
        dataloader.download(MODEL_NAME, FILE_NAME)

if __name__ == '__main__':
    init()
