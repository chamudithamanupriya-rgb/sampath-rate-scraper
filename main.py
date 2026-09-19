import datetime
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Supabase Configurations
SUPABASE_URL = "https://ndytcywjbieigajfgvor.supabase.co"
SUPABASE_KEY = "sb_publishable_hHkL9KYzeEuVqvK4Cw_WiQ_6ZRrcq_o"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_and_save_rates():
    url = "https://www.sampath.lk/rates-and-charges?activeTab=exchange-rates"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        usd_buy = None
        usd_sell = None

        # Page එකේ ඇති සියලුම Table rows පරීක්ෂා කිරීම
        rows = soup.find_all("tr")
        for row in rows:
            text = row.text.upper()
            if "USD" in text or "US DOLLAR" in text:
                cols = [ele.text.strip().replace(",", "") for ele in row.find_all(["td", "th"])]
                
                numbers = []
                for val in cols:
                    try:
                        num = float(val)
                        numbers.append(num)
                    except ValueError:
                        continue
                
                if len(numbers) >= 2:
                    usd_buy = numbers[0]
                    usd_sell = numbers[1]
                    break

        if usd_buy and usd_sell:
            data = {
                "currency": "USD",
                "buying_rate": usd_buy,
                "selling_rate": usd_sell,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            
            res = supabase.table("exchange_rates").insert(data).execute()
            print("Successfully saved rates:", data)
        else:
            print("Error: Could not extract USD rates from the page.")

    except Exception as e:
        print("Error fetching rates:", e)

if __name__ == "__main__":
    fetch_and_save_rates()
