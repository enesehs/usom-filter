# 🛡️ USOM Zararlı URL Listesi Engelleme Sistemi

<div align="center">
    <a href="./requirements.txt"><img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white"></a>&nbsp;
    <a href="#lisans"><img alt="License" src="https://img.shields.io/badge/License-MIT-success"></a>&nbsp;
    <a href="https://github.com/enesehs/usom-filter/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/enesehs/usom-filter?logo=github"></a>&nbsp;
    <a href="https://github.com/enesehs/usom-filter/issues"><img alt="Issues" src="https://img.shields.io/github/issues/enesehs/usom-filter"></a>&nbsp;
    <img alt="Status" src="https://img.shields.io/badge/Status-Active-22c55e">&nbsp;
    <img alt="Last commit" src="https://img.shields.io/github/last-commit/enesehs/usom-filter">&nbsp;
    <a href="https://enesehs.me/usom-filter"><img alt="Website" src="https://img.shields.io/badge/Website-enesehs.dev%2Fusom--filter-3b82f6"></a>
</div>

Bu proje, T.C. Ulaştırma ve Altyapı Bakanlığı Siber Güvenlik Daire Başkanlığı (USOM) tarafından yayınlanan [zararlı URL listesini](https://www.usom.gov.tr/url-list.txt) çeşitli güvenlik araçları için uygun formatlara dönüştürmektedir.

Canlı web sayfası: https://enesehs.dev/usom-filter

## İçindekiler

- [📁 Çıktı Dosyaları](#-çıktı-dosyaları)
- [🚀 Temel Özellikler](#-temel-özellikler)
- [🛠️ Kurulum ve Kullanım](#️-kurulum-ve-kullanım)
- [📋 Sistem Mimarisi](#-sistem-mimarisi)
- [🔧 Yapılandırma](#-yapılandırma)
- [📖 API Dokümantasyonu](#-api-dokümantasyonu)
- [🌐 Entegrasyon Örnekleri](#-entegrasyon-örnekleri)
- [📈 GitHub Actions Otomasyonu](#-github-actions-otomasyonu)
- [🤝 Katkı Sağlama](#-katkı-sağlama)
- [� Lisans](#lisans)
- [🔗 İlgili Kaynaklar](#-ilgili-kaynaklar)
- [⚠️ Yasal Uyarı](#️-yasal-uyarı)

## �📁 Çıktı Dosyaları

| Dosya Adı | Açıklama | Kullanım Alanları |
|-----------|----------|-------------------|
| `ips.txt` | Zararlı IP adres listesi | Güvenlik duvarı, IPS/IDS sistemleri |
| `urls.txt` | Zararlı bağlantı listesi | Proxy sunucuları, güvenlik araçları |
| `urls_pihole.txt` | Alan adı listesi | Pi-hole, AdGuard Home |
| `urls_UBL.txt` | Adblock formatı | uBlock Origin, AdBlock Plus, Brave |

## 🚀 Temel Özellikler

- ✅ **Performanslı veri işleme**: `aiohttp` kütüphanesi ile asenkron işlemler
- ✅ **Güvenilir hata yönetimi**: Eksponansiyel geri çekilme ile 8 deneme
- ✅ **Otomatik kategorizasyon**: IP adresleri, URL'ler ve alan adlarının ayrıştırılması
- ✅ **Çoklu format desteği**: Pi-hole ve uBlock Origin için optimize edilmiş formatlar
- ✅ **Otomatik güncelleme**: GitHub Actions ile günlük otomatizasyon
- ✅ **Web erişimi**: GitHub Pages üzerinden dokümentasyon
- ✅ **Kapsamlı günlük kayıtları**: Detaylı işlem logları
- ✅ **Modern Python**: 3.11+ sürümü ile tip güvenliği

## 🛠️ Kurulum ve Kullanım

### Sistem Gereksinimleri

- Python 3.11 veya üzeri
- `aiohttp` kütüphanesi
- `tldextract` kütüphanesi

### Manuel Çalıştırma (Windows PowerShell)

```powershell
# (İsteğe bağlı) Sanal ortam
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Bağımlılıklar
pip install -r .\requirements.txt

# Çalıştırma
python .\generator.py

# Çıktıları listele
Get-ChildItem .\output\
```

## 📋 Sistem Mimarisi

### İşlem Akışı

1. **Veri İndirme**: USOM zararlı URL listesinin `aiohttp` ile asenkron çekilmesi
2. **Veri Temizleme**: Geçersiz ve boş girişlerin filtrelenmesi
3. **Kategorizasyon**:
    - IPv4/IPv6 adreslerinin tespiti
    - URL'lerden alan adı bilgisinin çıkarılması
    - Kategorilere göre sınıflandırma
4. **Format Dönüştürme**:
    - **Pi-hole formatı**: `example.com` yapısında
    - **uBlock Origin formatı**: `||example.com^` yapısında
    - **Ham veri**: Orijinal format
5. **Dosya Çıktısı**: Alfabetik sıralama ve zaman damgası ile kayıt

### Hata Yönetimi

- **Yeniden Deneme Mekanizması**: 1s, 2s, 4s, 8s artan aralıklarla deneme
- **Zaman Aşımı Kontrolü**: 30 saniye bekleme süresi
- **Kapsamlı Loglama**: Tüm hata durumlarının kaydedilmesi
- **Süreklilik**: Kısmi hata durumlarında işleme devam etme

## 🔧 Yapılandırma

Betik başlangıcındaki parametreler:

```python
USOM_URL = "https://www.usom.gov.tr/url-list.txt"
MAX_RETRIES = 8
BASE_DELAY = 1.0
TIMEOUT_SECONDS = 30
```

## 📖 API Dokümantasyonu

### `USOMProcessor` Sınıfı

```python
async with USOMProcessor() as processor:
     islem_durumu = await processor.process()
```

#### Temel Metodlar

- `fetch_url_list()`: Zararlı URL listesinin indirilmesi
- `categorize_entries()`: Verilerin kategorizasyonu
- `write_output_files()`: Çıktı dosyalarının oluşturulması

### Yardımcı Fonksiyonlar

- `is_valid_ip(text)`: IP adresi doğrulama
- `is_valid_domain(text)`: Alan adı format kontrolü
- `extract_domain_info(url)`: URL'den alan adı bilgisi çıkarma

## 🌐 Entegrasyon Örnekleri

### Pi-hole Entegrasyonu

```bash
curl -o /etc/pihole/custom.list https://enesehs.github.io/usom-filter/output/urls_UBL.txt
pihole restartdns
```

### uBlock Origin Entegrasyonu

1. uBlock Origin ayarlarına erişim
2. "Filter lists" bölümüne geçiş
3. "Import" seçeneğini kullanma
4. URL ekleme: `https://enesehs.github.io/usom-filter/output/urls_UBL.txt`

### Güvenlik Duvarı Entegrasyonu (IP Engelleme)

```bash
curl -s https://enesehs.github.io/usom-filter/output/urls_UBL.txt | \
grep -v '^#' | while read ip; do
     iptables -I INPUT -s $ip -j DROP
done
```

## 📈 GitHub Actions Otomasyonu

Otomatik işlem adımları:

1. Python çalışma ortamının hazırlanması
2. Gerekli bağımlılıkların kurulması
3. Ana betiğin çalıştırılması
4. Değişikliklerin commit edilmesi
5. GitHub Pages'a dağıtım

## 🤝 Katkı Sağlama

1. Repository'yi fork edin
2. Yeni özellik dalı oluşturun (`git checkout -b yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Dalınızı push edin (`git push origin yeni-ozellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasını inceleyiniz.

## 🔗 İlgili Kaynaklar

- [T.C. Ulaştırma ve Altyapı Bakanlığı Siber Güvenlik Daire Başkanlığı (USOM)](https://www.usom.gov.tr/)
- [USOM Zararlı URL Listesi](https://www.usom.gov.tr/url-list.txt)
- [Pi-hole Projesi](https://pi-hole.net/)
- [uBlock Origin](https://github.com/gorhill/uBlock)

## ⚠️ Yasal Uyarı

Bu proje USOM ile resmi bir ilişkisi bulunmayan bağımsız bir açık kaynak projesidir. Veriler halka açık API'lar aracılığıyla erişilmektedir. Kullanım sorumluluğu son kullanıcıya aittir.

---

**Son Güncelleme**: `2025-09-01` | **Sürüm**: `1.0.0`

