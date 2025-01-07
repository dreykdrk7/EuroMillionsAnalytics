import pandas as pd

class SequenceAnalysis:
    def __init__(self, draws):
        """
        Initialize the SequenceAnalysis class with a list of draws.

        Args:
            draws (list): A list of dictionaries with draw data, 
                          each containing 'numbers' and 'stars'.
        """
        self.draws = draws

    def calculate_statistics(self):
        """
        Analyze sequences of consecutive numbers in the draws.

        Returns:
            DataFrame: A pandas DataFrame with statistics on sequences.
        """
        sequences = []

        for draw in self.draws:
            numbers = sorted(draw["numbers"])
            stars = sorted(draw["stars"])

            # Calculate sequences for numbers
            num_sequences = self._count_consecutive_sequences(numbers)

            # Calculate sequences for stars
            star_sequences = self._count_consecutive_sequences(stars)

            sequences.append({
                "date": draw.get("date", "Unknown"),
                "num_sequences": num_sequences,
                "star_sequences": star_sequences
            })

        return pd.DataFrame(sequences)

    @staticmethod
    def _count_consecutive_sequences(values):
        """
        Count the number of consecutive sequences in a list of values.

        Args:
            values (list): A sorted list of integers.

        Returns:
            int: The count of consecutive sequences.
        """
        sequence_count = 0
        for i in range(len(values) - 1):
            if values[i] + 1 == values[i + 1]:
                sequence_count += 1
        return sequence_count

if __name__ == "__main__":
    # Example draw data
    draws = [
        {"numbers": [4, 7, 8, 9, 45], "stars": [2, 3]},
        {"numbers": [1, 2, 3, 23, 35], "stars": [4, 5]},
        {"numbers": [10, 11, 19, 31, 50], "stars": [1, 12]},
    ]

    analyzer = SequenceAnalysis(draws)
    sequence_stats = analyzer.calculate_statistics()
    print("Sequence Statistics:")
    print(sequence_stats)