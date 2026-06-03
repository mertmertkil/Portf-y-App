import yfinance as yf


def get_live_price(hisse_kodu):
    try:
        # Yahoo Finance BIST hisselerini .IS uzantısıyla tanır
        ticker_kod = f"{hisse_kodu.upper()}"
        ticker = yf.Ticker(ticker_kod)

        # En güncel fiyatı alalım (fast_info veya history ile)
        data = ticker.history(period="1d")
        if not data.empty:
            return data["Close"].iloc[-1]
        return 0
    except Exception as e:
        print(f"{hisse_kodu} fiyatı alınamadı: {e}")
        return 0


def get_bist100_price():
    try:
        # yfinance üzerinden BIST 100 endeksini çekiyoruz
        bist = yf.Ticker("XU100.IS")
        data = bist.history(period="1d")
        if not data.empty:
            current_price = data["Close"].iloc[-1]
            prev_close = data["Open"].iloc[-1]  # Basit değişim hesabı için
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
            return current_price, change_percent
        return None, None
    except:
        return None, None
