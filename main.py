import os
import pandas as pd
from modules.data_processing.fetch_draws import FetchDraws
from modules.data_processing.simulate_draws import SimulateDraws
from modules.statistics.frequency_analysis import FrequencyAnalysis
from modules.statistics.sequence_analysis import SequenceAnalysis
from modules.statistics.parity_analysis import ParityAnalysis
from modules.database.db_handler import DatabaseHandler

# Define paths
DB_PATH = "data/euromillones.db"
STATISTICS_DIR = "data/statistics/"

# Ensure directories exist
os.makedirs(STATISTICS_DIR, exist_ok=True)

def main():
    print("Starting Euromillones Project...")

    # Initialize database handler
    db_handler = DatabaseHandler(DB_PATH)

    # Step 1: Fetch draw data
    print("Fetching draw data...")
    fetcher = FetchDraws(DB_PATH)
    draws = fetcher.fetch_all_draws()

    # Step 2: Analyze statistics
    print("Analyzing statistics...")

    # Frequency Analysis
    frequency_analyzer = FrequencyAnalysis(draws)
    frequency_stats = frequency_analyzer.calculate_statistics()
    frequency_stats.to_csv(os.path.join(STATISTICS_DIR, "frequency.csv"), index=False)

    # Sequence Analysis
    sequence_analyzer = SequenceAnalysis(draws)
    sequence_stats = sequence_analyzer.calculate_statistics()
    sequence_stats.to_csv(os.path.join(STATISTICS_DIR, "sequence.csv"), index=False)

    # Parity Analysis
    parity_analyzer = ParityAnalysis(draws)
    parity_stats = parity_analyzer.calculate_statistics()
    parity_stats.to_csv(os.path.join(STATISTICS_DIR, "parity.csv"), index=False)

    print("Statistics analysis complete. Results saved to CSV.")

    # Step 3: Simulate draws
    print("Simulating draws...")
    simulator = SimulateDraws(DB_PATH)
    simulations = simulator.simulate_draws(100)
    print(f"Simulated {len(simulations)} draws.")

    # Save simulations to database
    simulator.save_simulations_to_db(simulations)

    # Step 4: Export simulation results
    print("Exporting simulation results...")
    simulations_df = pd.DataFrame(simulations)
    simulations_df.to_csv(os.path.join(STATISTICS_DIR, "simulations.csv"), index=False)

    print("Simulation results saved to CSV.")

    # Close database connection
    db_handler.close()

    print("Euromillones Project complete.")

if __name__ == "__main__":
    main()
