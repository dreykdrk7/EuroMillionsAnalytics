import argparse
from datetime import datetime
from time import sleep
from dateutil.relativedelta import relativedelta
from modules.database.db_handler import DatabaseHandler
from modules.database.queries import Queries
import requests

# Argument parser setup
parser = argparse.ArgumentParser(description='Fetch and classify Euromillions draw data.')
parser.add_argument('--historical', action='store_true', help='Fetch the entire history of draws from a specific start date.')
parser.add_argument('--start_date', type=str, help='Start date for historical data in YYYY-MM-DD format. Works only with --historical.')
parser.add_argument('--period', type=str, choices=['week', 'month'], default='week', help='Period for recent draws: "week" or "month".')
args = parser.parse_args()

# Define constants
API_URL = 'https://www.loteriasyapuestas.es/servicios/buscadorSorteos'
DB_PATH = 'data/euromillones.db'

# Define headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "es-ES,es;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.loteriasyapuestas.es/es/resultados/euromillones",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-GPC": "1",
    "Cookie": "cms=AD7qKYF7b8H/fN5iewO/dg$$; usr-lang=es; UUID=WEB-d3122575-a4d2-4b02-bb07-f4684ac953b9",
}

# Fetch and process draws
def fetch_draws(start_date, end_date, db_handler):
    """
    Fetch draws from the API and process them.

    Args:
        start_date (datetime): Start date for the draw fetch.
        end_date (datetime): End date for the draw fetch.
        db_handler (DatabaseHandler): Database handler instance.
    """
    while start_date < end_date:
        period_end = start_date + relativedelta(months=3)
        if period_end > end_date:
            period_end = end_date

        params = {
            'game_id': 'EMIL',
            'celebrados': 'true',
            'fechaInicioInclusiva': start_date.strftime('%Y%m%d'),
            'fechaFinInclusiva': period_end.strftime('%Y%m%d')
        }

        print(f"Fetching draws between {start_date} and {period_end}...")
        try:
            response = requests.get(API_URL, params=params, headers=HEADERS)
            response.raise_for_status()

            try:
                draws = response.json()
                if not isinstance(draws, list):
                    print("Unexpected API response format.")
                    continue
                process_draws(draws, db_handler)
            except ValueError as e:
                print(f"Invalid JSON response: {e}")
            except Exception as e:
                print(f"Error processing draws: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            print("Retrying after a brief wait...")
            sleep(30)

        start_date = period_end + relativedelta(days=1)
        print("Waiting before the next request...")
        sleep(20)

def process_draws(draws, db_handler):
    """
    Process and insert draw data into the database.

    Args:
        draws (list): List of draw data.
        db_handler (DatabaseHandler): Database handler instance.
    """
    for draw in draws:
        try:
            if not db_handler.is_draw_registered(draw["id_sorteo"]):
                db_handler.insert_draw(draw)
                db_handler.classify_draw(draw["id_sorteo"], draw["combinacion"])
            else:
                print(f"Draw {draw['id_sorteo']} is already registered.")
        except Exception as e:
            print(f"Error processing draw {draw.get('id_sorteo', 'Unknown')}: {e}")

if __name__ == '__main__':
    end_date = datetime.now()

    if args.historical:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d') if args.start_date else datetime(2004, 1, 1)
    else:
        if args.period == 'week':
            start_date = end_date - relativedelta(weeks=1)
        elif args.period == 'month':
            start_date = end_date - relativedelta(months=1)

    db_handler = DatabaseHandler(DB_PATH)

    fetch_draws(start_date, end_date, db_handler)

    db_handler.close()
    print("Process complete.")
