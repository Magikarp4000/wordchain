from gensim.models import Word2Vec

import random

from utils import *


class DataProcessor:
    def __init__(self):
        self.data = None
    
    def read(self, file):
        return open(f"datasets/{file}", 'r').read().split('\n')

    def get_sample(self, population, sample_size):
        return random.sample(population, sample_size)

    def _clean_line(self, line):
        splitted = line.split()
        return [word.strip(" \"'.,-_/") for word in splitted]

    def _clean(self, raw_data):
        words = [self._clean_line(line) for line in raw_data]
        return words
    
    def clean(self, file, sample_size=None):
        raw_data = self.read(file)
        if sample_size is not None:
            sample = self.get_sample(raw_data, sample_size)
            self.data = self._clean(sample)
        else:
            self.data = self._clean(raw_data)
    
    def get_data(self):
        return self.data

if __name__ == '__main__':
    data_processor = DataProcessor()
    data_processor.clean('wikisent2.txt', sample_size=1000)
    print(data_processor.get_data())
