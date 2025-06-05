# test_env.py

from dotenv import load_dotenv
import os

load_dotenv()

print("API KEY:", os.getenv("BINANCE_API_KEY"))
print("API SECRET:", os.getenv("BINANCE_API_SECRET"))
