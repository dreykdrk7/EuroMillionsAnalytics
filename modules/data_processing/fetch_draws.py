import sqlite3

class FetchDraws:
    def __init__(self, db_path):
        self.db_path = db_path

    def fetch_all_draws(self):
        """
        Fetch all draw records from the database.

        Returns:
            list: A list of dictionaries containing draw data.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, combinacion, premio_bote FROM resultados_sorteos")
            rows = cursor.fetchall()

        # Process the rows into a list of dictionaries
        draws = []
        for row in rows:
            draws.append({
                "date": row[0],
                "combination": row[1],
                "jackpot": row[2]
            })

        return draws

if __name__ == "__main__":
    db_path = "data/euromillones.db"
    fetcher = FetchDraws(db_path)
    all_draws = fetcher.fetch_all_draws()
    print(f"Fetched {len(all_draws)} draws from the database.")
