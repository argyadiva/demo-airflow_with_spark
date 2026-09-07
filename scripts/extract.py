import requests
import pandas as pd
from pathlib import Path

url = "https://api.coingecko.com/api/v3/simple/price"

params = {
      "ids": "bitcoin,ethereum,ripple,solana,doge",  # Cryptocurrencies to fetch
      "vs_currencies": "usd"     # Currency to convert to
  }


response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

payload = response.json()
harga_crypto = []
nama_crypto = []
for coin in payload:
  harga_crypto.append(payload[coin]['usd'])
  nama_crypto.append(coin)
df = pd.DataFrame({'coin_name':nama_crypto, 'coin_price':harga_crypto})
Path('data').mkdir(parents=True, exist_ok=True)
df.to_csv('data/extract_result_crypto_pipeline.csv', index=False)
