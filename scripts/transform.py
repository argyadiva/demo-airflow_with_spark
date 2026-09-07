import pandas as pd
import requests
from datetime import datetime

url = "https://api.frankfurter.app/latest"
params = {
    "from": "USD",
    "to": "IDR"
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()
data = response.json()
exchange_rate = data['rates']['IDR']
print(f"Exchange rate from USD to IDR: {exchange_rate}")

df = pd.read_csv('data/extract_result_crypto_pipeline.csv')
current_datetime = datetime.now()
df['datetime'] = [current_datetime for x in range(df.shape[0])]
df['coin_price_idr'] = df['coin_price']*exchange_rate
df.to_csv('data/transform_result_crypto_pipeline.csv', index=False)
