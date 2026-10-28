import random
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


def kitaplari_cek(max_sayfa=50):
  """Web sitesinden belirtilen sayfa sayısı kadar kitap verisini çeker."""
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
      ),
      "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en=0.7",
  }

  tum_kitaplar = []

  for sayfa in range(1, max_sayfa + 1):
    url = (
        "https://books.toscrape.com/"
        if sayfa == 1
        else f"https://books.toscrape.com/catalogue/page-{sayfa}.html"
    )

    try:
      # 1. Güvenlik Katmanı: Ağ ve bağlantı hatalarını yakalama
      response = requests.get(url, headers=headers, timeout=10)
      response.encoding = "utf-8"

      if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        data = soup.find_all("article", class_="product_pod")

        for d in data:
          try:
            # 2. Güvenlik Katmanı: HTML etiketlerinde eksiklik çıkarsa çökmemesi için
            baslik = d.find("h3").find("a")["title"]
            fiyat = d.find("div", class_="product_price").find(
                "p", class_="price_color"
            ).text
            stok = d.find("p", class_="instock availability").text.strip()

            tum_kitaplar.append({"Kitap": baslik, "Fiyat": fiyat, "Stok": stok})
          except AttributeError:
            # Tek bir kitabın verisi eksikse döngüyü kırmadan pas geçer
            continue

        print(f"{sayfa}. sayfa başarıyla çekildi ve sepete eklendi.")
        time.sleep(random.uniform(2, 4))
      else:
        print(f"{sayfa}. sayfada sunucu hata kodu döndürdü: {response.status_code}")

    except requests.exceptions.RequestException as e:
      print(f"Bağlantı hatası oluştu ({sayfa}. sayfa): {e}")
      continue

  return tum_kitaplar


def verileri_disari_aktar(tum_kitaplar):
  """Toplanan verileri Pandas ile CSV ve SQLite veritabanına kaydeder."""
  if not tum_kitaplar:
    print("Kaydedilecek veri bulunamadı!")
    return

  # DataFrame oluşturma
  df = pd.DataFrame(tum_kitaplar)

  # CSV Kaydı
  df.to_csv("kitaplar.csv", index=False, encoding="utf-8-sig")
  print("Veriler başarıyla 'kitaplar.csv' dosyasına yazıldı.")

  # SQLite Veritabanı Kaydı
  try:
    baglanti = sqlite3.connect("kitaplarim.db")
    df.to_sql("kitaplar_tablosu", baglanti, if_exists="replace", index=False)
    baglanti.close()
    print("Veriler başarıyla 'kitaplarim.db' veritabanına işlendi.")
  except Exception as e:
    print(f"Veritabanı kayıt hatası: {e}")


# --- Ana Çalıştırma Bloğu ---
if __name__ == "__main__":
  print("Web scraping operasyonu başlatılıyor...")
  kitaplar_listesi = kitaplari_cek(50)
  verileri_disari_aktar(kitaplar_listesi)
  print("Tüm işlemler başarıyla tamamlandı!")