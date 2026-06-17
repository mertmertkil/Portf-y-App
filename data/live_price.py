import yfinance as yf


def get_live_price(hisse_kodu):
    """Tek bir hisse senedinin en güncel fiyatını döndürür."""
    try:
        if not hisse_kodu.upper().endswith(".IS"):
            ticker_kod = f"{hisse_kodu.upper()}.IS"
        else:
            ticker_kod = hisse_kodu.upper()

        ticker = yf.Ticker(ticker_kod)
        data = ticker.history(period="1d")

        if not data.empty:
            return data["Close"].iloc[-1]
        return 0
    except Exception as e:
        print(f"{hisse_kodu} fiyatı alınamadı: {e}")
        return 0


def get_bist100_price():
    """BIST 100 endeks fiyatını ve web sitesiyle uyumlu yüzde değişimini döndürür."""
    try:
        bist = yf.Ticker("XU100.IS")

        # fast_info doğrudan web sitesindeki ham özet veriyi çeker
        current_price = bist.fast_info["last_price"]
        prev_close = bist.fast_info["previous_close"]

        if current_price and prev_close:
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
            return current_price, change_percent

        return None, None
    except Exception as e:
        # Eğer fast_info'da anlık bir dalgalanma olursa hata vermemesi için yedek yöntem
        try:
            data = bist.history(period="2d")
            if len(data) >= 2:
                dunku_kapanis = data["Close"].iloc[-2]
                bugunku_fiyat = data["Close"].iloc[-1]
                change = bugunku_fiyat - dunku_kapanis
                change_percent = (change / dunku_kapanis) * 100
                return bugunku_fiyat, change_percent
        except:
            pass
        print(f"BIST 100 verisi alınırken hata oluştu: {e}")
        return None, None
