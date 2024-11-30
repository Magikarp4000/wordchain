from gensim.models import Word2Vec
from gensim.models import KeyedVectors

from sklearn.manifold import TSNE

import random
import numpy as np

from config import *
from utils import *

import json


class Agent:

    class Bounds:
        def __init__(self, arr: np.array):
            self.minX = min(arr[:, 0])
            self.maxX = max(arr[:, 0])
            self.minY = min(arr[:, 1])
            self.maxY = max(arr[:, 1])
            self.rangeX = self.maxX - self.minX
            self.rangeY = self.maxY - self.minY
        
        def __str__(self):
            return f"minX: {self.minX}, minY: {self.minY}, maxX: {self.maxX}, maxY: {self.maxY}, rangeX: {self.rangeX}, rangeY: {self.rangeY}"

    def __init__(self, model_name='v1', tolerance=0.3):
        self.model = self.load_model(model_name)
        self.vocab = list(self.model.wv.key_to_index.keys())
        self.vocab_set = set(self.vocab)
        self.dictionary = self.load_words()

        self.embedding = self.load_embedding(model_name)
        self.bounds = Agent.Bounds(np.array(list(self.embedding.values())))
        # self.embedding = self.train_embedding()
        # self.save_embedding(model_name)

        self.tolerance = tolerance

        self.start = None
        self.target = None

        self.guesses = []
        self.guesses_set = set()

    def load_model(self, model_name):
        path = f"{DIR_PATH}/models/{model_name}/{model_name}.model"
        try:
            return Word2Vec.load(path)
        except:
            keyed_vectors = KeyedVectors.load(path)
            model = Word2Vec()
            model.wv = keyed_vectors
            return model
    
    def load_words(self):
        return open(f"{DIR_PATH}/datasets/words/en.txt", 'r').read().split('\n')

    def train_embedding(self):
        vectors = np.array(self.model.wv.vectors)
        tsne = TSNE(n_components=2, random_state=0)
        raw = tsne.fit_transform(vectors).tolist()
        embedding = {word: val for word, val in zip(self.vocab, raw)}
        return embedding
    
    def save_embedding(self, model_name):
        path = f'{DIR_PATH}/models/{model_name}/{model_name}_embed.json'
        f = open(path, 'w')
        data = json.dumps(self.embedding)
        f.write(data)

    def load_embedding(self, model_name):
        path = f'{DIR_PATH}/models/{model_name}/{model_name}_embed.json'
        f = open(path, 'r')
        data = json.load(f)
        return {word: np.array(data[word]) for word in data}

    def get_random_word(self):
        return random.choice(self.vocab)
    
    def get_random_dictionary_word(self):
        return random.choice(self.dictionary)
    
    def check_valid_word(self, word):
        return word.isalpha() and word.islower() and word in self.vocab_set

    def find_valid_word(self):
        word = "_"
        while not self.check_valid_word(word):
            word = self.get_random_dictionary_word()
        return word

    def parse_input(self, stream):
        return stream.strip()

    def get_input(self):
        raw_stream = input("What word would you like to guess? ")
        stream = self.parse_input(raw_stream)
        return stream
    
    def validate_word(self, word):
        try:
            self.model.wv.key_to_index[word]
        except:
            return False
        return True
    
    def norm_similarity(self, sim):
        return (sim + 1) / 2

    def get_similarity(self, w1, w2):
        return self.model.wv.similarity(w1, w2)
    
    def get_2d(self, word):
        return self.embedding[word]

    def norm(self, pos):
        return (pos - (self.bounds.minX, self.bounds.minY)) / (self.bounds.rangeX, self.bounds.rangeY)
    
    def get_2d_similarity(self, w1, w2):
        return np.linalg.norm(self.embedding[w1] - self.embedding[w2])
    
    def get_closest_word_and_score(self, word):
        """
        Return:
            tuple(str, float): (best word, best score)
        """
        sims = [self.get_similarity(word, guess) for guess in self.guesses]
        best_index = np.argmax(sims)
        return self.guesses[best_index], sims[best_index]
    
    def validate_score(self, score):
        return score >= self.tolerance
    
    def is_target(self, word):
        return word == self.target

    def guessed(self, word):
        return word in self.guesses_set
    
    def add_word(self, word):
        self.guesses.append(word)
        self.guesses_set.add(word)

    def win(self):
        print(f"Congratulations! You chained from '{self.start}' to '{self.target}' in {len(self.guesses) - 1} guesses!")

    def get_invalid_feedback(self):
        return "Sorry, that word is invalid. Please try again."
    
    def get_guessed_feedback(self):
        return "That word has already been guessed! Please try again."
    
    def get_unsimilar_feedback(self, best_word, best_score):
        percent = round(best_score * 100, 2)
        return f"Sorry, the closest word found is '{best_word}' with a similarity score of {percent}%. Please try again."

    def display_invalid_feedback(self):
        print(self.get_invalid_feedback() + "\n")
    
    def display_guessed_feedback(self):
        print(self.get_guessed_feedback() + "\n")
    
    def display_unsimilar_feedback(self, best_word, best_score):
        print(self.get_unsimilar_feedback(best_word, best_score) + "\n")
    
    def display_valid_feedback(self, word, best_score=None, best_word=None):
        print(f"Nice job! '{word}' has been added to the chain.")
        print(f"DEBUG: {best_word} {round(best_score * 100, 2)}%\n")

    def display_hints(self, word):
        hints = self.get_hints(word)
        print(f"Hint: Try these words: {', '.join(hints)}\n")

    def get_similarity_to_target(self, word):
        return self.get_similarity(word, self.target)
    
    def get_max_similarity(self, word):
        return max([self.get_similarity(word, guess) for guess in self.guesses])

    def get_hints(self, word):
        closest_words = self.model.wv.most_similar(positive=[word], topn=5)
        closest_words = self.get_column(closest_words, axis=0)
        closest_words.sort(key=self.get_max_similarity, reverse=True)
        return closest_words

    def get_column(self, arr, axis=0):
        return [item[axis] for item in arr]
    
    def update(self, guess):
        if not self.validate_word(guess):
            return INVALID, self.get_invalid_feedback()
        elif self.guessed(guess):
            return GUESSED, self.get_guessed_feedback()
        else:
            best_word, best_score = self.get_closest_word_and_score(guess)

            if self.validate_score(best_score):
                self.add_word(guess)
                if self.is_target(guess):
                    return WON, best_word
                else:
                    return VALID, best_word
            else:
                return UNSIMILAR, self.get_unsimilar_feedback(best_word, best_score)
                self.display_hints(guess)

    def init_core(self):
        self.start = self.find_valid_word()
        self.target = self.find_valid_word()
        self.add_word(self.start)

    def main(self):
        self.init_core()

        self.running = True
        while self.running:
            guess = self.get_input()
            self.update(guess)


if __name__ == '__main__':
    game = Agent('googlenews', tolerance=0.3)
    game.main()
