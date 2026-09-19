import datetime
import requests
from supabase import create_client, Client

# Supabase Configurations
SUPABASE_URL = "https://ndytcywjbieigajfgvor.supabase.co"
SUPABASE_KEY = "sb_publishable_hHkL9KYzeEuVqvK4Cw_WiQ_6ZRrcq_o"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_and_save_rates():
    # Sampath Bank API Endpoint
    url = "https://www.sampath.lk/api/exchange-rates"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    }

    usd_buy = None
    usd_sell = None

    try:
        response = requests.get(url, headers=headers, timeout=20)
        
        # API එකෙන් JSON ලැබුණහොත්
        if response.status_code == 200:
            try:
                data_json = response.json()
                rates = data_json.get("data", []) or data_json.get("rates", []) or data_json
                if isinstance(rates, list):
                    for item in rates:
                        currency = str(item.get("currency", "") or item.get("currency_code", "")).upper()
                        if "USD" in currency:
                            usd_buy = float(str(item.get("buyRate") or item.get("buying_rate")).replace(",", ""))
                            usd_sell = float(str(item.get("sellRate") or item.get("selling_rate")).replace(",", ""))
                            break
            except Exception as json_err:
                print("JSON parsing failed, falling back to HTML fetch:", json_err)

        # JSON හරහා නොලැබුණහොත් Direct Web Scrape කිරීම
        if not (usd_buy and usd_sell):
            web_url = "https://www.sampath.lk/rates-and-charges?activeTab=exchange-rates"
            html_resp = requests.get(web_url, headers=headers, timeout=20)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_resp.text, "html.parser")
            
            for row in soup.find_all("tr"):
                text = row.text.upper()
                if "USD" in text or "US DOLLAR" in text:
                    cols = [ele.text.strip().replace(",", "") for ele in row.find_all(["td", "th"])]
                    numbers = []
                    for val in cols:
                        try:
                            numbers.append(float(val))
                        except ValueError:
                            continue
                    if len(numbers) >= 2:
                        usd_buy = numbers[0]
                        usd_sell = numbers[1]
                        break

        # Data Database එකට එකතු කිරීම
        if usd_buy and usd_sell:
            record = {
                "currency": "USD",
                "buying_rate": usd_buy,
                "selling_rate": usd_sell,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            res = supabase.table("exchange_rates").insert(record).execute()
            print("Successfully saved rates:", record)
        else:
            print("Error: Could not extract USD rates.")

    except Exception as e:
        print("Error during execution:", e)
        raise e

if __name__ == "__main__":
    fetch_and_save_rates()
