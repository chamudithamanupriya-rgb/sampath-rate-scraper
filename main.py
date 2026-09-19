import datetime
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Supabase Configurations
SUPABASE_URL = "https://ndytcywjbieigajfgvor.supabase.co"
SUPABASE_KEY = "sb_publishable_hHkL9KYzeEuVqvK4Cw_WiQ_6ZRrcq_o"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_and_save_rates():
    url = "https://www.sampath.lk/exchange-rates"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # HTML Table එකෙන් USD Rates ලබා ගැනීම
        # Sampath Bank Page structure එක අනුව Table data parse කරගනී
        tables = soup.find_all("table")
        usd_buy = None
        usd_sell = None

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = [ele.text.strip() for ele in row.find_all(["td", "th"])]
                if len(cols) >= 3 and "USD" in cols[0]:
                    usd_buy = float(cols[1].replace(",", ""))
                    usd_sell = float(cols[2].replace(",", ""))
                    break

        if usd_buy and usd_sell:
            data = {
                "currency": "USD",
                "buying_rate": usd_buy,
                "selling_rate": usd_sell,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            # Supabase එකට Insert කිරීම
            res = supabase.table("exchange_rates").insert(data).execute()
            print("Successfully saved rates:", data)
        else:
            print("Could not find USD rates on the page.")

    except Exception as e:
        print("Error fetching rates:", e)

if __name__ == "__main__":
    fetch_and_save_rates()
