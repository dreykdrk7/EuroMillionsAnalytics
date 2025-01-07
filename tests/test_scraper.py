import requests
from datetime import datetime
from time import sleep
from dateutil.relativedelta import relativedelta

# Configuración de cabeceras
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "es-ES,es;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.loteriasyapuestas.es/es/resultados/euromillones",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-GPC": "1",
    # Incluye cookies si es necesario
    "Cookie": "cms=AD7qKYF7b8H/fN5iewO/dg$$; usr-lang=es; UUID=WEB-d3122575-a4d2-4b02-bb07-f4684ac953b9",
}

API_URL = "https://www.loteriasyapuestas.es/servicios/buscadorSorteos"

def fetch_draws(start_date, end_date):
    while start_date < end_date:
        period_end = start_date + relativedelta(months=3)
        if period_end > end_date:
            period_end = end_date

        params = {
            "game_id": "EMIL",
            "celebrados": "true",
            "fechaInicioInclusiva": start_date.strftime("%Y%m%d"),
            "fechaFinInclusiva": period_end.strftime("%Y%m%d"),
        }

        print(f"Fetching draws between {start_date} and {period_end}...")
        response = requests.get(API_URL, params=params, headers=HEADERS)

        if response.status_code == 200:
            try:
                draws = response.json()
                if not isinstance(draws, list):
                    print("Unexpected API response format.")
                    continue
                print(f"Fetched {len(draws)} draws.")
                # Procesa los datos aquí
            except ValueError:
                print("Invalid JSON response from API.")
        else:
            print(f"API request failed with status code: {response.status_code}")

        start_date = period_end + relativedelta(days=1)
        print("Waiting before the next request...")
        sleep(5)

if __name__ == "__main__":
    start_date = datetime(2010, 1, 1)
    end_date = datetime.now()

    fetch_draws(start_date, end_date)
