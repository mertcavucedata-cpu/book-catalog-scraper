import logging
import random
import sqlite3
import time
from contextlib import closing

import pandas as pd
import requests
from bs4 import BeautifulSoup

FIRST_PAGE_URL = "https://books.toscrape.com/"
PAGE_URL = "https://books.toscrape.com/catalogue/page-{page}.html"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

TIMEOUT = 10
MIN_WAIT = 2
MAX_WAIT = 4
MAX_CONSECUTIVE_ERRORS = 3
CSV_FILE_PATH = "kitaplar.csv"
EXCEL_FILE_PATH = "kitaplar.xlsx"
DB_FILE_PATH = "kitaplarim.db"
TABLE_NAME = "kitaplar_tablosu"

# log kurulumu
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    handlers=[
        logging.FileHandler("books.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def fetch_data(max_page=50):
    """Belirtilen sayfa sayisi kadar kitap verisini ceker."""

    all_books = []
    consecutive_errors = 0

    for page in range(1, max_page + 1):
        url = FIRST_PAGE_URL if page == 1 else PAGE_URL.format(page=page)

        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.encoding = "utf-8"

            if response.status_code != 200:
                log.error("Sayfa %s HATA (kod: %s)", page, response.status_code)
                consecutive_errors += 1
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    log.error("Ust uste %s hata, islem durduruldu.", consecutive_errors)
                    break
                time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            books = soup.find_all("article", class_="product_pod")

            # Bos sayfa, kitaplarin bittigi anlamina gelir
            if not books:
                log.info("Sayfa %s bos geldi, kitaplar bitti.", page)
                break

            for b in books:
                try:
                    title = b.find("h3").find("a")["title"]
                    price = b.find("p", class_="price_color").text
                    stock = b.find("p", class_="instock availability").text.strip()
                except (AttributeError, KeyError):
                    # Tek bir kitabin verisi eksikse onu atla
                    log.warning("Sayfa %s: eksik veri, kitap atlandi.", page)
                    continue

                all_books.append(
                    {
                        "kitap": title,
                        "fiyat": price,
                        "stok": stock,
                    }
                )

            consecutive_errors = 0
            log.info("Sayfa %s basariyla cekildi (%s kitap).", page, len(books))
            time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))

        except requests.exceptions.RequestException as e:
            consecutive_errors += 1
            log.error("Sayfa %s baglanti hatasi: %s", page, e)
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                log.error("Ust uste %s hata, islem durduruldu.", consecutive_errors)
                break
            time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))

    return all_books


def export_data(all_books):
    """Toplanan verileri CSV, Excel ve SQLite formatlarinda kaydeder."""

    if not all_books:
        log.warning("Kaydedilecek veri bulunamadi!")
        return

    df = pd.DataFrame(all_books)

    first = len(df)
    df = df.drop_duplicates()
    log.info("%s tekrar eden kitap silindi.", first - len(df))

    df.to_csv(CSV_FILE_PATH, index=False, encoding="utf-8-sig")
    log.info("Veriler '%s' dosyasina yazildi.", CSV_FILE_PATH)

    try:
        df.to_excel(EXCEL_FILE_PATH, index=False)
        log.info("Veriler '%s' dosyasina yazildi.", EXCEL_FILE_PATH)
    except (ImportError, OSError) as e:
        log.error("Excel kayit hatasi: %s", e)

    try:
        with closing(sqlite3.connect(DB_FILE_PATH)) as connection:
            df.to_sql(TABLE_NAME, connection, if_exists="replace", index=False)
        log.info("Veriler '%s' veritabanina islendi.", DB_FILE_PATH)
    except sqlite3.Error as e:
        log.error("Veritabani kayit hatasi: %s", e)


# --- Ana Calistirma Blogu ---
if __name__ == "__main__":
    log.info("Web scraping operasyonu baslatiliyor...")
    book_list = fetch_data(50)
    log.info("Toplam %s kitap cekildi.", len(book_list))
    export_data(book_list)
    log.info("Tum islemler tamamlandi")