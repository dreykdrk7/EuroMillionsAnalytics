import argparse
import pandas as pd
from modules.database.annual_statistics import AnnualStatistics
from datetime import datetime

DB_PATH = 'data/euromillones.db'

def initialize_statistics():
    """
    Initialize statistics for all years from 2004 to the current year.
    This is run only if the table is empty.
    """
    stats_handler = AnnualStatistics(DB_PATH)
    current_year = datetime.now().year

    print("Initializing statistics for all years...")
    for year in range(2004, current_year + 1):
        print(f"Calculating statistics for the year {year}...")
        stats_handler.calculate_statistics()

    stats_handler.close()
    print("Statistics initialization complete.")

def update_current_year_statistics():
    """
    Update statistics only for the current year.
    """
    stats_handler = AnnualStatistics(DB_PATH)
    current_year = datetime.now().year

    print(f"Updating statistics for the current year: {current_year}...")
    stats_handler.calculate_statistics()
    stats_handler.close()
    print("Statistics update complete.")

def display_statistics(year):
    """
    Fetch and display statistics for a specific year.

    Args:
        year (int): The year to filter the statistics for.
    """
    stats_handler = AnnualStatistics(DB_PATH)
    df = stats_handler.fetch_statistics()

    # Filter by the given year
    df_filtered = df[df['year'] == year]

    if not df_filtered.empty:
        print(f"Statistics for the year {year}:")
        print(df_filtered)
    else:
        print(f"No statistics found for the year {year}.")

    stats_handler.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='View and calculate annual statistics for Euromillones draws.')
    parser.add_argument('--year', type=int, help='The year to view statistics for.')
    parser.add_argument('--init', action='store_true', help='Initialize statistics for all years (only run once).')
    parser.add_argument('--update', action='store_true', help='Update statistics for the current year.')

    args = parser.parse_args()

    if args.init:
        # Initialize statistics for all years
        initialize_statistics()
    elif args.update:
        # Update statistics for the current year
        update_current_year_statistics()
    elif args.year:
        # Display statistics for the specified year
        display_statistics(args.year)
    else:
        print("No valid arguments provided. Use --help for usage information.")