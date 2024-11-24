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

        self.start_word = None
        self.target_word = None

        self.guesses = []
        self.guesses_set = set()
    
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

    def guessed(self, word):
        return word in self.guesses_set
    
    def add_word(self, word):
        self.guesses.append(word)
        self.guesses_set.add(word)

    def win(self):
        print(f"Congratulations! You chained from '{self.start_word}' to '{self.target_word}' in {len(self.guesses) - 1} guesses!")

    def display_valid_feedback(self, word):
        print(f"Nice job! '{word}' has been added to the chain.\n")
    
    def display_unsimilar_feedback(self, best_word, best_score):
        percent = round(best_score * 100, 2)
        print(f"Sorry, the closest word found is '{best_word}' with a similarity score of {percent}%, which is below the threshold. Please try again.\n")

    def display_invalid_feedback(self):
        print("Sorry, that word is invalid. Please try again.\n")
    
    def display_guessed_feedback(self):
        print("That word has already been guessed! Please try again.\n")

    def init_main(self):
        print(f"Starting word: {self.start_word}")
        print(f"Target word: {self.target_word}\n")
        self.add_word(self.start_word)
    
    def main(self):
        self.start_word = self.get_random_word()
        self.target_word = self.get_random_word()
        self.init_main()

        running = True
        while running:
            guess = self.get_input()

            if not self.validate_word(guess):
                self.display_invalid_feedback()
            
            elif self.guessed(guess):
                self.display_guessed_feedback()
            
            else:
                best_word, best_score = self.get_closest_word_and_score(guess)

                if self.validate_score(best_score):
                    self.add_word(guess)
                    self.display_valid_feedback(guess)

                    if self.is_target(guess, self.target_word):
                        self.win()
                        running = False
                else:
                    self.display_unsimilar_feedback(best_word, best_score)


if __name__ == '__main__':
    game = Game('v1')
    game.main()
