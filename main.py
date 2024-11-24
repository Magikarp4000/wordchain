from gensim.models import Word2Vec

import random
import numpy as np

from utils import *


DIR_PATH = get_dir_path(__file__)

class Game:
    def __init__(self, model=None, tolerance=0.3):
        self.model = Word2Vec.load(f"{DIR_PATH}/models/{model}/{model}.model")
        self.vocab = list(self.model.wv.key_to_index.keys())

        self.tolerance = tolerance
        self.guesses = []
    
    def get_random_word(self):
        return random.choice(self.vocab)

    def parse_input(self, stream):
        return stream.lower().strip()

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
    
    def get_similarity(self, w1, w2):
        return self.model.wv.similarity(w1, w2)
    
    def get_closest_word_and_score(self, word):
        sims = [self.get_similarity(word, guess) for guess in self.guesses]
        best_index = np.argmax(sims)
        return self.guesses[best_index], sims[best_index]
    
    def validate_score(self, score):
        return score >= self.tolerance
    
    def is_target(self, word, target):
        return word == target
    
    def win(self):
        print(f"Congratulations! You chained to the target word in {len(self.guesses - 1)} guesses!")

    def init_main(self, start_word, target_word):
        print(f"Starting word: {start_word}")
        print(f"Target word: {target_word}\n")
        self.guesses.append(start_word)
    
    def add_word(self, word):
        self.guesses.append(word)

    def display_valid_feedback(self, word):
        print(f"Nice job! '{word}' has been added to the chain.\n")

    def display_invalid_feedback(self):
        print("Sorry, that word is invalid. Please try again.\n")

    def main(self):
        start_word = self.get_random_word()
        target_word = self.get_random_word()
        self.init_main(start_word, target_word)

        running = True
        while running:
            guess = self.get_input()
            is_valid = False

            if self.validate_word(guess):
                best_word, best_score = self.get_closest_word_and_score(guess)

                if self.validate_score(best_score):
                    is_valid = True
                    self.add_word(best_word)
                    self.display_valid_feedback(guess)

                    if self.is_target(best_word, target_word):
                        self.win()
                        running = False
            
            if not is_valid:
                self.display_invalid_feedback()


if __name__ == '__main__':
    game = Game('v1')
    game.main()
