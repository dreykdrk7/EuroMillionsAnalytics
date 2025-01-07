import pandas as pd

class ParityAnalysis:
    def __init__(self, draws):
        """
        Initialize the ParityAnalysis class with a list of draws.

        Args:
            draws (list): A list of dictionaries with draw data, 
                          each containing 'numbers' and 'stars'.
        """
        self.draws = draws

    def calculate_statistics(self):
        """
        Analyze the parity (odd/even split) of numbers and stars in the draws.

        Returns:
            DataFrame: A pandas DataFrame with parity statistics.
        """
        parities = []

        for draw in self.draws:
            numbers = draw["numbers"]
            stars = draw["stars"]

            num_even = sum(1 for n in numbers if n % 2 == 0)
            num_odd = len(numbers) - num_even

            star_even = sum(1 for s in stars if s % 2 == 0)
            star_odd = len(stars) - star_even

            parities.append({
                "date": draw.get("date", "Unknown"),
                "num_even": num_even,
                "num_odd": num_odd,
                "star_even": star_even,
                "star_odd": star_odd
            })

        return pd.DataFrame(parities)

if __name__ == "__main__":
    # Example draw data
    draws = [
        {"numbers": [4, 7, 19, 23, 45], "stars": [2, 11]},
        {"numbers": [2, 12, 19, 22, 35], "stars": [4, 6]},
        {"numbers": [10, 11, 19, 31, 50], "stars": [1, 12]},
    ]

    analyzer = ParityAnalysis(draws)
    parity_stats = analyzer.calculate_statistics()
    print("Parity Statistics:")
    print(parity_stats)
