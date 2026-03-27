# Trading Bot

Prosty bot tradingowy oparty na strategii EMA crossover + RSI, napisany w Pythonie.

---

## Wymagania

- Python 3.10+
- Konto na giełdzie z kluczami API (zalecane: najpierw **testnet**)

---

## Instalacja zależności

```bash
pip install ccxt pandas numpy python-dotenv
```

lub korzystając z pliku `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Konfiguracja

1. Skopiuj plik przykładowy:

```bash
cp .env.example .env
```

2. Uzupełnij plik `.env` swoimi kluczami API i ustawieniami:

```env
EXCHANGE_ID=binance
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
USE_TESTNET=True        # <- zacznij zawsze od True!

SYMBOL=BTC/USDT
TIMEFRAME=1h
TRADE_AMOUNT_USDT=10
```

> **Telegram (opcjonalnie):** Jeśli chcesz otrzymywać powiadomienia, uzupełnij `TELEGRAM_TOKEN` i `TELEGRAM_CHAT_ID`. W przeciwnym razie zostaw puste.

---

## Uruchomienie

```bash
cd trading-bot
python main.py
```

Logi trafiają jednocześnie do konsoli oraz do pliku `trading.log`.

---

## ⚠️ Ostrzeżenie

> **Zawsze zaczynaj od `USE_TESTNET=True`.**
>
> Handel na prawdziwych środkach (`USE_TESTNET=False`) wiąże się z ryzykiem utraty kapitału.
> Przetestuj strategię dokładnie na testnecie przed uruchomieniem na rachunku live.

---

## Struktura projektu

```
trading-bot/
├── .env                 # klucze API (NIE wrzucaj na GitHub!)
├── .env.example         # wzór pliku .env z placeholderami
├── config.py            # konfiguracja (wczytuje zmienne z .env)
├── exchange_client.py   # połączenie z giełdą (ccxt)
├── strategy.py          # logika strategii (EMA crossover + RSI)
├── risk_manager.py      # zarządzanie ryzykiem (SL/TP/rozmiar pozycji)
├── logger.py            # konfiguracja logowania
├── main.py              # główna pętla bota
├── requirements.txt     # zależności
└── trading.log          # plik logów (tworzony automatycznie)
```
