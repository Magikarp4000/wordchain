from main import Game


class Tester(Game):
    def __init__(self, model_name=None, tolerance=0.3):
        super().__init__(model_name, tolerance)
    
    def get_average_sim(self, sample_size=100000):
        total = 0
        for _ in range(sample_size):
            w1 = self.get_random_word()
            w2 = self.get_random_word()
            total += self.get_similarity(w1, w2)
        avg = total / sample_size
        return avg


if __name__ == "__main__":
    tester = Tester('v1')
    avg = tester.get_average_sim(100000)
    print(f"\nAverage pairwise similarity: {avg}\n")
