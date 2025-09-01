"""
USOM URL Block List Generator

Bu script USOM'un zararlı URL listesini çekip farklı formatlarda işler:
- IP listesi (ips.txt)
- URL listesi (urls.txt) 
- Pi-hole formatı (urls_pihole.txt)
- Adblock/uBlock formatı (urls_UBL.txt)

Author: Enesehs
Date: September 2025
Requirements: aiohttp, tldextract
"""

import asyncio
import logging
import socket
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional
from urllib.parse import urlparse
import ipaddress
import aiohttp
import tldextract

USOM_URL = "https://www.usom.gov.tr/url-list.txt"
MAX_RETRIES = 8
BASE_DELAY = 1.0
TIMEOUT_SECONDS = 30
OUTPUT_DIR = Path("./output")
LOG_FILE = "usom_processor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class USOMProcessor:    
    def __init__(self) -> None:
        self.session: Optional[aiohttp.ClientSession] = None
        OUTPUT_DIR.mkdir(exist_ok=True)
        logger.info("USOM Processor başlatıldı")
    
    async def __aenter__(self) -> 'USOMProcessor':
        timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'} #     :D
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
    
    async def fetch_url_list(self) -> Optional[str]:
        if not self.session:
            raise RuntimeError("Session başlatılmamış")
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"USOM URL listesi çekiliyor... (Deneme {attempt + 1}/{MAX_RETRIES})")
                async with self.session.get(USOM_URL) as response:
                    if response.status == 200:
                        content = await response.text(encoding='utf-8', errors='ignore')
                        if content.strip():
                            logger.info(f"URL listesi başarıyla çekildi ({len(content)} karakter)")
                            return content
                        else:
                            logger.warning("Boş veri alındı")
                    else:
                        logger.warning(f"HTTP {response.status} hatası")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout hatası (Deneme {attempt + 1})")
            except aiohttp.ClientError as e:
                logger.warning(f"Client hatası: {e} (Deneme {attempt + 1})")
            except Exception as e:
                logger.error(f"Beklenmeyen hata: {e} (Deneme {attempt + 1})")
            
            if attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)
                logger.info(f"{delay:.1f} saniye bekleniyor...")
                await asyncio.sleep(delay)
        
        logger.error("URL listesi çekme başarısız")
        return None
    
    def is_valid_ip(self, text: str) -> bool:
        try:
            ipaddress.ip_address(text.strip())
            return True
        except ValueError:
            return False
    
    def is_valid_domain(self, text: str) -> bool:
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, text.strip()))
    
    def clean_url(self, url: str) -> str:
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        if url.endswith('/'):
            url = url[:-1]
        return url
    
    def extract_domain_info(self, url: str) -> Tuple[str, str, str]:
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            parsed = urlparse(url)
            hostname = parsed.netloc or parsed.path.split('/')[0]
            hostname = hostname.split(':')[0]
            extracted = tldextract.extract(hostname)
            full_domain = hostname
            registered_domain = f"{extracted.domain}.{extracted.suffix}" if extracted.domain and extracted.suffix else hostname
            suffix = extracted.suffix or ""
            return full_domain, registered_domain, suffix
        except Exception as e:
            logger.debug(f"Domain çıkarma hatası ({url}): {e}")
            return url, url, ""
    
    def categorize_entries(self, content: str) -> Dict[str, List[str]]:
        categories = {
            'ips': set(),
            'urls': set(),
            'domains_pihole': set(),
            'domains_adblock': set()
        }
        
        lines = content.strip().split('\n')
        total_lines = len(lines)
        logger.info(f"Toplam {total_lines} satır işleniyor...")
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if i % 1000 == 0:
                logger.info(f"İşlenen: {i}/{total_lines}")
            
            try:
                if self.is_valid_ip(line):
                    categories['ips'].add(line)
                    continue
                cleaned_url = self.clean_url(line)
                categories['urls'].add(cleaned_url)
                full_domain, registered_domain, suffix = self.extract_domain_info(line)
                if self.is_valid_domain(full_domain):
                    categories['domains_pihole'].add(full_domain)
                if registered_domain and '.' in registered_domain and self.is_valid_domain(registered_domain):
                    adblock_format = f"*://*.{registered_domain}/*"
                    categories['domains_adblock'].add(adblock_format)
            except Exception as e:
                logger.debug(f"Satır işleme hatası ({line}): {e}")
        
        result = {}
        for key, value_set in categories.items():
            result[key] = sorted(list(value_set))
            logger.info(f"{key}: {len(result[key])} entry")
        return result
    
    async def write_output_files(self, categories: Dict[str, List[str]]) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        file_mapping = {
            'ips': 'ips.txt',
            'urls': 'urls.txt',
            'domains_pihole': 'urls_pihole.txt',
            'domains_adblock': 'urls_UBL.txt'
        }
        headers = {
            'ips': f"# USOM Zararlı IP Listesi\n# Son Güncelleme: {timestamp}\n# Toplam: {{count}} IP\n\n",
            'urls': f"# USOM Zararlı URL Listesi\n# Son Güncelleme: {timestamp}\n# Toplam: {{count}} URL\n\n",
            'domains_pihole': f"# USOM Zararlı Domain Listesi (Pi-hole Format)\n# Son Güncelleme: {timestamp}\n# Toplam: {{count}} Domain\n\n",
            'domains_adblock': f"# USOM Zararlı Domain Listesi (Adblock/uBlock Format)\n# Son Güncelleme: {timestamp}\n# Toplam: {{count}} Rule\n\n"
        }
        
        for category, filename in file_mapping.items():
            try:
                file_path = OUTPUT_DIR / filename
                data = categories.get(category, [])
                with open(file_path, 'w', encoding='utf-8') as f:
                    header = headers[category].format(count=len(data))
                    f.write(header)
                    for item in data:
                        f.write(f"{item}\n")
                logger.info(f"{filename} dosyası yazıldı ({len(data)} entry)")
            except Exception as e:
                logger.error(f"{filename} dosyası yazma hatası: {e}")
    
    async def process(self) -> bool:
        try:
            logger.info("USOM URL işleme başlatılıyor...")
            content = await self.fetch_url_list()
            if not content:
                return False
            logger.info("URL'ler kategorize ediliyor...")
            categories = self.categorize_entries(content)
            logger.info("Çıktı dosyaları yazılıyor...")
            await self.write_output_files(categories)
            logger.info("İşlem başarıyla tamamlandı!")
            return True
        except Exception as e:
            logger.error(f"İşlem sırasında hata: {e}")
            return False

async def main() -> None:
    start_time = datetime.now()
    logger.info("=== USOM URL Processor Başlatılıyor ===")
    try:
        async with USOMProcessor() as processor:
            success = await processor.process()
        end_time = datetime.now()
        duration = end_time - start_time
        if success:
            logger.info(f"=== İşlem Başarıyla Tamamlandı ({duration.total_seconds():.1f}s) ===")
        else:
            logger.error(f"=== İşlem Başarısız ({duration.total_seconds():.1f}s) ===")
    except KeyboardInterrupt:
        logger.info("İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")

if __name__ == "__main__":
    asyncio.run(main())
