import sqlite3
import json
import pandas as pd
from datetime import datetime
from collections import Counter

DB_PATH = 'data/euromillones.db'

class AnnualStatistics:
    def __init__(self, db_path):
        """
        Initialize the Annual Statistics handler.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self._initialize_table()

    def _initialize_table(self):
        """
        Create the annual statistics table if it does not exist.
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS annual_statistics (
            year INTEGER PRIMARY KEY,
            numbers TEXT,
            stars TEXT,
            figures TEXT,
            ranges TEXT,
            parity TEXT,
            number_rentability TEXT,
            star_rentability TEXT
        );
        """)
        self.connection.commit()

    def calculate_statistics(self):
        """
        Calculate statistics for each year, updating for the current year if necessary.
        """
        rows = self.cursor.execute("""
        SELECT num1, num2, num3, num4, num5, estrella1, estrella2, escrutinio, strftime('%Y', fecha_sorteo) as year 
        FROM resultados_sorteos
        """).fetchall()

        current_year = datetime.now().year
        statistics_by_year = {}

        for row in rows:
            numbers = row[:5]
            stars = row[5:7]
            scrutiny = json.loads(row[7])  # Deserialize the scrutiny field
            year = int(row[8])  # Convert year to int for easier comparison

            # Initialize statistics for the year if not already done
            if year not in statistics_by_year:
                statistics_by_year[year] = {
                    'number_counts': Counter(),
                    'star_counts': Counter(),
                    'number_rentability': Counter(),
                    'star_rentability': Counter(),
                    'figures': [0, 0],  # [odd_count, even_count]
                    'ranges': [0, 0],   # [low_count, high_count]
                    'parity': [0, 0]    # [even_stars, odd_stars]
                }

            # Count occurrences of numbers and stars
            statistics_by_year[year]['number_counts'].update(numbers)
            statistics_by_year[year]['star_counts'].update(stars)

            # Calculate rentability
            for entry in scrutiny:
                try:
                    prize = float(entry['premio'].replace(',', '')) if entry['premio'] else 0
                    for number in numbers:
                        statistics_by_year[year]['number_rentability'][number] += prize
                    for star in stars:
                        statistics_by_year[year]['star_rentability'][star] += prize
                except (KeyError, ValueError, TypeError) as e:
                    # Log the error but continue with the calculation
                    print(f"Skipping invalid scrutiny entry: {entry}, Error: {e}")
                    continue

            # Accumulate figures (odd/even distribution)
            odd_count = sum(1 for n in numbers if n % 2 != 0)
            even_count = len(numbers) - odd_count
            statistics_by_year[year]['figures'][0] += odd_count
            statistics_by_year[year]['figures'][1] += even_count

            # Accumulate ranges (low/high distribution)
            low_count = sum(1 for n in numbers if n <= 25)
            high_count = len(numbers) - low_count
            statistics_by_year[year]['ranges'][0] += low_count
            statistics_by_year[year]['ranges'][1] += high_count

            # Accumulate parity (even/odd stars)
            even_stars = sum(1 for s in stars if s % 2 == 0)
            odd_stars = len(stars) - even_stars
            statistics_by_year[year]['parity'][0] += even_stars
            statistics_by_year[year]['parity'][1] += odd_stars

        # Store or update annual statistics in the database
        for year, stats in statistics_by_year.items():
            self.cursor.execute("""
                INSERT OR REPLACE INTO annual_statistics (year, numbers, stars, number_rentability, star_rentability, figures, ranges, parity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                year,
                json.dumps(stats['number_counts']),        # Serialize counts to JSON
                json.dumps(stats['star_counts']),          # Serialize counts to JSON
                json.dumps(stats['number_rentability']),   # Serialize rentability to JSON
                json.dumps(stats['star_rentability']),     # Serialize rentability to JSON
                json.dumps(stats['figures']),              # [odd_count, even_count]
                json.dumps(stats['ranges']),               # [low_count, high_count]
                json.dumps(stats['parity'])                # [even_stars, odd_stars]
            ))

        self.connection.commit()

    def fetch_statistics(self):
        """
        Fetch statistics as a pandas DataFrame.
        """
        df = pd.read_sql_query("SELECT * FROM annual_statistics", self.connection)
        return df

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()


# Main execution for debugging
if __name__ == '__main__':
    stats_handler = AnnualStatistics(DB_PATH)
    stats_handler.calculate_statistics()
    df = stats_handler.fetch_statistics()
    print(df)
    stats_handler.close()
