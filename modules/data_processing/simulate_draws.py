import random
import sqlite3

class SimulateDraws:
    def __init__(self, db_path):
        self.db_path = db_path

    def generate_random_combination(self):
        """
        Generate a random draw combination with 5 numbers and 2 stars.

        Returns:
            dict: A dictionary containing the generated numbers and stars.
        """
        numbers = sorted(random.sample(range(1, 51), 5))  # 5 unique numbers between 1 and 50
        stars = sorted(random.sample(range(1, 13), 2))    # 2 unique stars between 1 and 12
        return {
            "numbers": numbers,
            "stars": stars
        }

    def simulate_draws(self, num_simulations=100):
        """
        Simulate a specified number of random draws.

        Args:
            num_simulations (int): The number of draws to simulate.

        Returns:
            list: A list of simulated draws.
        """
        simulated_draws = []
        for _ in range(num_simulations):
            draw = self.generate_random_combination()
            simulated_draws.append(draw)
        return simulated_draws

    def save_simulations_to_db(self, simulations):
        """
        Save simulated draws to the database.

        Args:
            simulations (list): A list of simulated draws.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for draw in simulations:
                numbers = "-".join(map(str, draw["numbers"]))
                stars = "-".join(map(str, draw["stars"]))
                combination = f"{numbers} - {stars}"
                cursor.execute(
                    "INSERT INTO simulated_draws (combination) VALUES (?)",
                    (combination,)
                )
            conn.commit()

if __name__ == "__main__":
    db_path = "data/euromillones.db"
    simulator = SimulateDraws(db_path)

    # Simulate 100 draws
    simulations = simulator.simulate_draws(100)
    print(f"Generated {len(simulations)} simulated draws.")

    # Save to database
    simulator.save_simulations_to_db(simulations)
    print("Simulated draws saved to the database.")
