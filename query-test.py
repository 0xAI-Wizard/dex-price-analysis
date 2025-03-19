import requests

url = "https://pro-api.coingecko.com/api/v3/coins/ethereum/contract/0x03C7054BCB39f7b2e5B2c7AcB37583e32D70Cfa3/market_chart?vs_currency=usd&days=3&interval=daily&precision=2"

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": "CG-mCvJbFgB9T2Xn2sftcj2hA5V",
}

response = requests.get(url, headers=headers)

print(response.text)
