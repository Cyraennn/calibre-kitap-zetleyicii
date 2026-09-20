"""Ayar ve ortam değişkeni çözümleme yardımcıları."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Proje kök dizinindeki .env dosyasını yükle (varsa).
load_dotenv()

# Tek bir Gemini çağrısında gönderilecek maksimum karakter sayısı.
# Bunun altındaki metinler tek seferde (map-reduce yapmadan) işlenir.
MAX_SINGLE_CALL_CHARS = 600_000

# Map-reduce uygulanırken her bir parçanın (chunk) hedef karakter boyutu.
CHUNK_SIZE_CHARS = 150_000

# Varsayılan Gemini modeli. --model parametresiyle değiştirilebilir.
DEFAULT_MODEL = "gemini-2.5-flash"

ENV_LIBRARY_PATH = "CALIBRE_LIBRARY_PATH"
ENV_GEMINI_API_KEY = "GOOGLE_API_KEY"

ENV_ANYTHINGLLM_BASE_URL = "ANYTHINGLLM_BASE_URL"
ENV_ANYTHINGLLM_API_KEY = "ANYTHINGLLM_API_KEY"
ENV_ANYTHINGLLM_WORKSPACE = "ANYTHINGLLM_WORKSPACE"

DEFAULT_ANYTHINGLLM_BASE_URL = "http://localhost:3001"
DEFAULT_ANYTHINGLLM_WORKSPACE = "Kitap Analizlerim"


class YapilandirmaHatasi(Exception):
    """Eksik/yanlış yapılandırma durumunda fırlatılır."""


def resolve_library_path(cli_arg: str | None) -> Path:
    """Calibre kütüphane yolunu CLI argümanı veya ortam değişkeninden çözer.

    Öncelik sırası: --library argümanı > CALIBRE_LIBRARY_PATH ortam değişkeni.
    """
    raw_path = cli_arg or os.environ.get(ENV_LIBRARY_PATH)

    if not raw_path:
        raise YapilandirmaHatasi(
            "Calibre kütüphane yolu belirtilmedi.\n"
            "Şu yollardan biriyle belirtin:\n"
            "  1) --library \"C:\\yol\\Calibre Library\" parametresi\n"
            f"  2) {ENV_LIBRARY_PATH} ortam değişkeni (veya .env dosyasında {ENV_LIBRARY_PATH}=...)"
        )

    library_path = Path(raw_path).expanduser()
    if not library_path.is_dir():
        raise YapilandirmaHatasi(
            f"Belirtilen Calibre kütüphane dizini bulunamadı: {library_path}"
        )

    metadata_db = library_path / "metadata.db"
    if not metadata_db.is_file():
        raise YapilandirmaHatasi(
            f"Bu dizin bir Calibre kütüphanesine benzemiyor "
            f"(metadata.db bulunamadı): {library_path}"
        )

    return library_path


def get_gemini_api_key() -> str:
    """GOOGLE_API_KEY ortam değişkenini okur, yoksa açıklayıcı hata verir."""
    api_key = os.environ.get(ENV_GEMINI_API_KEY)
    if not api_key:
        raise YapilandirmaHatasi(
            f"{ENV_GEMINI_API_KEY} ortam değişkeni bulunamadı.\n"
            "Google AI Studio'dan bir API anahtarı alıp .env dosyasına "
            f"({ENV_GEMINI_API_KEY}=anahtarınız) veya ortam değişkeni olarak ekleyin."
        )
    return api_key


def get_anythingllm_api_key() -> str:
    """ANYTHINGLLM_API_KEY ortam değişkenini okur, yoksa açıklayıcı hata verir."""
    api_key = os.environ.get(ENV_ANYTHINGLLM_API_KEY)
    if not api_key:
        raise YapilandirmaHatasi(
            f"{ENV_ANYTHINGLLM_API_KEY} ortam değişkeni bulunamadı.\n"
            "AnythingLLM uygulamasında Ayarlar (Settings) > Geliştirici API (Developer API) "
            "bölümünden bir API anahtarı oluşturup .env dosyasına "
            f"({ENV_ANYTHINGLLM_API_KEY}=anahtarınız) ekleyin."
        )
    return api_key


def get_anythingllm_base_url() -> str:
    """ANYTHINGLLM_BASE_URL ortam değişkenini okur, verilmemişse varsayılanı döner."""
    return os.environ.get(ENV_ANYTHINGLLM_BASE_URL) or DEFAULT_ANYTHINGLLM_BASE_URL


def get_anythingllm_workspace() -> str:
    """ANYTHINGLLM_WORKSPACE ortam değişkenini okur, verilmemişse varsayılanı döner."""
    return os.environ.get(ENV_ANYTHINGLLM_WORKSPACE) or DEFAULT_ANYTHINGLLM_WORKSPACE
