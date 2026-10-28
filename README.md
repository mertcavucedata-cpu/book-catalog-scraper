# Book Scraper (HTML Parsing & BeautifulSoup)
[books.toscrape.com](https://books.toscrape.com) sitesinden kitap başlıklarını, fiyatlarını ve stok durumlarını çeken, temizleyen ve çoklu formatta kaydeden Python scraper'ı.

> Bu site web scraping pratikleri için hazırlanmış bir eğitim sitesidir, veri çekmek serbesttir.

## Özellikler

- Çok sayfalı veri çekme (sayfa sayısı ayarlanabilir)
- İstekler arasında rastgele bekleme (siteyi yormamak için)
- Zaman aşımı (timeout) ve hata yönetimi: ağ ve bağlantı hatalarına karşı korumalı
- Eksik veya boş (null) HTML alanlarına karşı korumalı veri okuma (`AttributeError` yönetimi)
- Çıktı: **CSV** ve **SQLite** veritabanı

## Kullanılan Teknolojiler

Python 3, `requests`, `beautifulsoup4`, `pandas`, `sqlite3`

## Kurulum ve Çalıştırma

```bash
pip install requests beautifulsoup4 pandas
python main.py
```

## Çıktı Dosyaları

| Dosya | Açıklama |
|---|---|
| `kitaplar.csv` | Tüm kitaplar (UTF-8) |
| `kitaplarim.db` | SQLite veritabanı (`kitaplar_tablosu`) |

Sütunlar: `Kitap`, `Fiyat`, `Stok`

### Örnek Çıktı

```csv
kitap,fiyat,stok
A Light in the Attic,£51.77,In stock
Tipping the Velvet,£53.74,In stock
Soumission,£50.10,In stock
Sharp Objects,£47.82,In stock
Sapiens: A Brief History of Humankind,£54.23,In stock
```

## Ayarlar

Tüm ayarlar dosyanın en üstündeki sabitlerde ve fonksiyon parametrelerinde durur: sayfa adresi, bekleme süreleri, timeout, dosya adları.

## Notlar

Bu proje, HTML parsing (BeautifulSoup), sayfalama (pagination) takibi, hata yönetimi ve veri dışa aktarma pratiği için hazırlanmıştır.