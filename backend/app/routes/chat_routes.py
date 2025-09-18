# app/routes/chat_routes.py
from fastapi import APIRouter
from pydantic import BaseModel
import os, requests, re
from openai import OpenAI

router = APIRouter()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Exchangerate API
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")
EXCHANGE_API_URL = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/"

# Binance API
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    reply: str

# ─── Helper functions ───
def fetch_forex(base_currency, target_currencies):
    """Fetch live rates for target currencies relative to base_currency."""
    try:
        resp = requests.get(EXCHANGE_API_URL + base_currency, timeout=5).json()
        table = "| Currency Pair | Exchange Rate |\n| --- | --- |\n"
        rates = {}
        for curr in target_currencies:
            if curr in resp.get("conversion_rates", {}):
                rate = resp["conversion_rates"][curr]
                table += f"| {base_currency} to {curr} | {rate} |\n"
                rates[curr] = rate
            else:
                table += f"| {base_currency} to {curr} | ⚠️ Not available |\n"
        return table, rates
    except:
        return "⚠️ Forex rates unavailable.", {}

def fetch_crypto(symbols):
    """Fetch live crypto prices for requested symbols."""
    table = "| Crypto | Price (USDT) |\n| --- | --- |\n"
    prices = {}
    try:
        for sym in symbols:
            resp = requests.get(f"{BINANCE_API_URL}?symbol={sym}").json()
            price = float(resp["price"])
            table += f"| {sym} | {price} |\n"
            prices[sym] = price
        return table, prices
    except:
        return "⚠️ Crypto prices unavailable.", {}

def extract_amounts(prompt):
    """Extract all numeric amounts from the prompt."""
    # ✅ Fixed regex: only returns strings, no tuple
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", prompt)]

def detect_currencies(prompt):
    """Detect currency codes in the prompt."""
    all_currencies = ["USD","PKR","EUR","GBP","JPY","AUD","CAD","CHF","CNY","NZD","INR"]
    words = prompt.upper().split()
    return [c for c in all_currencies if c in words]

def detect_cryptos(prompt):
    """Detect cryptocurrencies in the prompt."""
    all_crypto = ["BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","DOGEUSDT"]
    return [sym for sym in all_crypto if sym[:-4].lower() in prompt]

def detect_base_currency(prompt):
    """Detect base currency from prompt; default USD."""
    all_currencies = ["USD","PKR","EUR","GBP","JPY","AUD","CAD","CHF","CNY","NZD","INR"]
    words = prompt.upper().split()
    for w in words:
        if w in all_currencies:
            return w
    return "USD"

# ─── Chat endpoint ───
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_prompt = request.prompt.strip().lower()

    # ─── Detect base currency, target currencies, and cryptos ───
    base_currency = detect_base_currency(user_prompt)
    target_currencies = detect_currencies(user_prompt)
    if base_currency in target_currencies:
        target_currencies.remove(base_currency)  # no self-conversion
    cryptos = detect_cryptos(user_prompt)

    # ─── Fetch live rates ───
    forex_table, forex_rates = fetch_forex(base_currency, target_currencies) if target_currencies else ("", {})
    crypto_table, crypto_prices = fetch_crypto(cryptos) if cryptos else ("", {})

    # ─── Extract amounts ───
    amounts = extract_amounts(user_prompt)
    amount = amounts[0] if amounts else None

    # ─── Build conversion table ───
    conversion_msg = ""
    if amount:
        if forex_rates:
            conversion_msg += "| Currency | Converted Amount |\n| --- | --- |\n"
            for curr, rate in forex_rates.items():
                converted = round(amount * rate, 4)
                conversion_msg += f"| {curr} | {converted} |\n"
        if crypto_prices:
            if conversion_msg:
                conversion_msg += "\n| Crypto | Amount |\n| --- | --- |\n"
            else:
                conversion_msg += "| Crypto | Amount |\n| --- | --- |\n"
            for sym, price in crypto_prices.items():
                crypto_amount = round(amount / price, 8)
                conversion_msg += f"| {sym[:-4]} | {crypto_amount} |\n"

    # ─── Build system prompt for AI ───
    system_msg = "You are a helpful assistant."
    if forex_table or crypto_table:
        system_msg += (
            "\nBelow are the latest live rates fetched from APIs. "
            "If the user asks for conversion, refer to the provided conversion table. "
            "Do NOT repeat numbers already shown. Explain, summarize, or give advice.\n"
            f"Forex Rates:\n{forex_table}\nCrypto Prices:\n{crypto_table}"
        )

    # ─── Call OpenAI ───
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=600
        )
        ai_reply = response.choices[0].message.content.strip()
    except Exception:
        ai_reply = f"AI fallback reply: {user_prompt}"

    # ─── Combine everything ───
    final_reply = ""
    if forex_table:
        final_reply += f"💵 Forex Rates ({base_currency} Base):\n{forex_table}\n"
    if crypto_table:
        final_reply += f"💰 Crypto Prices:\n{crypto_table}\n"
    if conversion_msg:
        final_reply += f"🔢 Conversion based on your amount:\n{conversion_msg}\n"
    final_reply += ai_reply

    return ChatResponse(reply=final_reply)
