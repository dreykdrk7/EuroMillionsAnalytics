import sqlite3
import json
from modules.database.queries import Queries

class DatabaseHandler:
    def __init__(self, db_path):
        """
        Initialize the database handler.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self._initialize_tables()

    def _initialize_tables(self):
        """
        Create necessary tables if they do not exist.
        """
        self.cursor.execute(Queries.CREATE_RESULTS_TABLE)
        self.cursor.execute(Queries.CREATE_SIMULATED_TABLE)
        self.connection.commit()

    def is_draw_registered(self, draw_id):
        """
        Check if a draw is already registered in the database.

        Args:
            draw_id (str): The ID of the draw to check.

        Returns:
            bool: True if the draw is registered, False otherwise.
        """
        self.cursor.execute(Queries.CHECK_DRAW, (draw_id,))
        return self.cursor.fetchone() is not None

    def insert_draw(self, draw):
        """
        Insert a draw into the database.

        Args:
            draw (dict): Draw data to insert.
        """
        try:
            # Parse the combination
            combination = draw["combinacion"].strip()
            numbers = [int(x) for x in combination.split('-')[:5]]
            stars = [int(x) for x in combination.split('-')[5:]]

            # Serialized JSON format
            combination_json = json.dumps(numbers + stars)

            escrutinio = json.dumps(draw.get("escrutinio", []))

            self.cursor.execute(Queries.INSERT_DRAW, (
                draw["id_sorteo"],
                combination,             # Original combination format
                combination_json,        # Serialized JSON format
                numbers[0], numbers[1], numbers[2], numbers[3], numbers[4],
                stars[0], stars[1],
                draw["fecha_sorteo"],
                draw["dia_semana"],
                draw.get("anyo", ""),
                draw.get("numero", 0),
                draw.get("premio_bote", ""),
                draw.get("apuestas", 0),
                draw["combinacion_acta"],
                draw.get("premios", ""),
                escrutinio
            ))
            self.connection.commit()
        except Exception as e:
            print(f"Failed to insert draw {draw['id_sorteo']}: {e}")
    
    def classify_draw(self, draw_id, combination):
        """
        Classify a draw by figures, ranges, sequences, and more.

        Args:
            draw_id (str): The ID of the draw to classify.
            combination (str): The combination to classify.
        """
        try:
            # Parse combination
            numbers = [int(n) for n in combination.split('-')[:5]]
            stars = [int(s) for s in combination.split('-')[5:]]

            # Classify figures (pares/impares)
            num_pares = sum(1 for n in numbers if n % 2 == 0)
            num_impares = len(numbers) - num_pares
            self.cursor.execute(Queries.CLASSIFY_FIGURES, (num_pares, num_impares, draw_id))

            # Classify ranges (bajos/altos)
            num_bajos = sum(1 for n in numbers if n <= 25)
            num_altos = len(numbers) - num_bajos
            self.cursor.execute(Queries.CLASSIFY_RANGES, (num_bajos, num_altos, draw_id))

            # Classify sequences
            numbers.sort()
            secuencias = sum(1 for i in range(len(numbers) - 1) if numbers[i + 1] - numbers[i] == 1)
            self.cursor.execute(Queries.CLASSIFY_SEQUENCES, (secuencias, draw_id))

            self.connection.commit()
        except Exception as e:
            print(f"Failed to classify draw {draw_id}: {e}")

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()
