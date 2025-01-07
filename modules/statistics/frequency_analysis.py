from collections import Counter
import pandas as pd

class FrequencyAnalysis:
    def __init__(self, draws):
        """
        Initialize the FrequencyAnalysis class with a list of draws.

        Args:
            draws (list): A list of dictionaries with draw data, 
                          each containing 'numbers' and 'stars'.
        """
        self.draws = draws

    def calculate_statistics(self):
        """
        Calculate the frequency of numbers and stars across all draws.

        Returns:
            DataFrame: A pandas DataFrame with frequencies for numbers and stars.
        """
        number_counts = Counter()
        star_counts = Counter()

        # Count occurrences of numbers and stars
        for draw in self.draws:
            number_counts.update(draw["numbers"])
            star_counts.update(draw["stars"])

        # Convert counts to a DataFrame
        numbers_df = pd.DataFrame(
            number_counts.items(), columns=["Number", "Frequency"]
        ).sort_values(by="Frequency", ascending=False)

        stars_df = pd.DataFrame(
            star_counts.items(), columns=["Star", "Frequency"]
        ).sort_values(by="Frequency", ascending=False)

        # Combine into a single DataFrame for easy viewing
        combined_df = pd.concat(
            [numbers_df.reset_index(drop=True), stars_df.reset_index(drop=True)],
            axis=1
        )
        combined_df.columns = ["Number", "Number Frequency", "Star", "Star Frequency"]

        return combined_df

if __name__ == "__main__":
    # Example draw data
    draws = [
        {"numbers": [4, 7, 19, 23, 45], "stars": [2, 11]},
        {"numbers": [1, 12, 19, 23, 35], "stars": [4, 11]},
        {"numbers": [4, 7, 19, 31, 50], "stars": [2, 12]},
    ]

    analyzer = FrequencyAnalysis(draws)
    frequency_stats = analyzer.calculate_statistics()
    print("Frequency Statistics:")
    print(frequency_stats)
