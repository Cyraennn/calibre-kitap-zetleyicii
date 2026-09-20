"""Analiz çıktılarını yerel AnythingLLM sunucusuna gönderip bir çalışma
alanına (workspace) gömen (embed eden) yardımcı fonksiyonlar.

AnythingLLM masaüstü uygulaması açıkken kendi içinde bir web sunucusu
çalıştırır (varsayılan: http://localhost:3001) ve bu sunucu üzerinden bir
"Geliştirici API"si sunar. Bu modül o API'yi kullanarak:

  1. Belirtilen çalışma alanını (workspace) yoksa oluşturur.
  2. Verilen klasördeki Markdown dosyalarını AnythingLLM'e yükler.
  3. Yüklenen dosyaları çalışma alanına ekleyip (embed) aranabilir hale getirir.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import requests

ANYTHINGLLM_TIMEOUT_SANIYE = 60


class AnythingLLMHatasi(Exception):
    """AnythingLLM ile iletişim sırasında oluşan hatalarda fırlatılır."""


@dataclass
class SenkronizasyonSonucu:
    workspace_slug: str
    workspace_adi: str
    yuklenen_dosyalar: list[str]
    atlanan_dosyalar: list[str]


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _istek_hatasini_ele_al(exc: requests.RequestException, base_url: str) -> AnythingLLMHatasi:
    return AnythingLLMHatasi(
        f"AnythingLLM sunucusuna bağlanılamadı ({base_url}).\n"
        "AnythingLLM uygulamasının açık olduğundan ve adresin doğru olduğundan emin olun.\n"
        f"Ayrıntı: {exc}"
    )


def api_anahtarini_dogrula(base_url: str, api_key: str) -> None:
    """API anahtarının geçerli olup olmadığını kontrol eder."""
    try:
        yanit = requests.get(
            f"{base_url}/api/v1/auth",
            headers=_headers(api_key),
            timeout=ANYTHINGLLM_TIMEOUT_SANIYE,
        )
    except requests.RequestException as exc:
        raise _istek_hatasini_ele_al(exc, base_url) from exc

    if yanit.status_code == 403:
        raise AnythingLLMHatasi(
            "AnythingLLM API anahtarı geçersiz. .env dosyasındaki ANYTHINGLLM_API_KEY "
            "değerini AnythingLLM > Ayarlar > Geliştirici API bölümünden aldığınız anahtarla "
            "güncelleyin."
        )
    if not yanit.ok:
        raise AnythingLLMHatasi(f"AnythingLLM API anahtarı doğrulanamadı (HTTP {yanit.status_code}).")


def _workspace_slug_bul(base_url: str, api_key: str, workspace_adi: str) -> str | None:
    try:
        yanit = requests.get(
            f"{base_url}/api/v1/workspaces",
            headers=_headers(api_key),
            timeout=ANYTHINGLLM_TIMEOUT_SANIYE,
        )
    except requests.RequestException as exc:
        raise _istek_hatasini_ele_al(exc, base_url) from exc

    if not yanit.ok:
        raise AnythingLLMHatasi(f"Çalışma alanları listelenemedi (HTTP {yanit.status_code}).")

    for workspace in yanit.json().get("workspaces", []):
        if workspace.get("name") == workspace_adi:
            return workspace.get("slug")
    return None


def _workspace_olustur(base_url: str, api_key: str, workspace_adi: str) -> str:
    try:
        yanit = requests.post(
            f"{base_url}/api/v1/workspace/new",
            headers=_headers(api_key),
            json={"name": workspace_adi},
            timeout=ANYTHINGLLM_TIMEOUT_SANIYE,
        )
    except requests.RequestException as exc:
        raise _istek_hatasini_ele_al(exc, base_url) from exc

    if not yanit.ok:
        raise AnythingLLMHatasi(f"Çalışma alanı oluşturulamadı (HTTP {yanit.status_code}): {yanit.text}")

    slug = yanit.json().get("workspace", {}).get("slug")
    if not slug:
        raise AnythingLLMHatasi("Çalışma alanı oluşturuldu ama sunucu bir 'slug' döndürmedi.")
    return slug


def ensure_workspace(base_url: str, api_key: str, workspace_adi: str) -> str:
    """Belirtilen isimde bir çalışma alanı varsa slug'ını döner, yoksa oluşturur."""
    mevcut_slug = _workspace_slug_bul(base_url, api_key, workspace_adi)
    if mevcut_slug:
        return mevcut_slug
    return _workspace_olustur(base_url, api_key, workspace_adi)


def _dosya_yukle(base_url: str, api_key: str, dosya_yolu: Path) -> str:
    """Tek bir dosyayı AnythingLLM'e yükler, gömme için kullanılacak 'location' değerini döner."""
    try:
        with dosya_yolu.open("rb") as dosya:
            yanit = requests.post(
                f"{base_url}/api/v1/document/upload",
                headers=_headers(api_key),
                files={"file": (dosya_yolu.name, dosya, "text/markdown")},
                timeout=ANYTHINGLLM_TIMEOUT_SANIYE,
            )
    except requests.RequestException as exc:
        raise _istek_hatasini_ele_al(exc, base_url) from exc

    if not yanit.ok:
        raise AnythingLLMHatasi(f"'{dosya_yolu.name}' yüklenemedi (HTTP {yanit.status_code}): {yanit.text}")

    belgeler = yanit.json().get("documents", [])
    if not belgeler:
        raise AnythingLLMHatasi(f"'{dosya_yolu.name}' yüklendi ama sunucu bir belge konumu döndürmedi.")
    return belgeler[0]["location"]


def _embeddingleri_guncelle(base_url: str, api_key: str, workspace_slug: str, konumlar: list[str]) -> None:
    try:
        yanit = requests.post(
            f"{base_url}/api/v1/workspace/{workspace_slug}/update-embeddings",
            headers=_headers(api_key),
            json={"adds": konumlar, "deletes": []},
            timeout=ANYTHINGLLM_TIMEOUT_SANIYE,
        )
    except requests.RequestException as exc:
        raise _istek_hatasini_ele_al(exc, base_url) from exc

    if not yanit.ok:
        raise AnythingLLMHatasi(
            f"Belgeler çalışma alanına eklenemedi (HTTP {yanit.status_code}): {yanit.text}"
        )


def sync_folder(
    base_url: str,
    api_key: str,
    workspace_adi: str,
    klasor: Path,
    desen: str = "*.md",
) -> SenkronizasyonSonucu:
    """Klasördeki dosyaları AnythingLLM'e yükleyip belirtilen çalışma alanına gömer."""
    api_anahtarini_dogrula(base_url, api_key)

    dosyalar = sorted(klasor.glob(desen)) if klasor.is_dir() else []
    if not dosyalar:
        raise AnythingLLMHatasi(
            f"'{klasor}' klasöründe '{desen}' ile eşleşen dosya bulunamadı. "
            "Önce 'python main.py analyze ... --save' ile en az bir analiz kaydedin."
        )

    workspace_slug = ensure_workspace(base_url, api_key, workspace_adi)

    yuklenen: list[str] = []
    atlanan: list[str] = []
    konumlar: list[str] = []
    for dosya in dosyalar:
        try:
            konum = _dosya_yukle(base_url, api_key, dosya)
        except AnythingLLMHatasi:
            atlanan.append(dosya.name)
            continue
        konumlar.append(konum)
        yuklenen.append(dosya.name)

    if konumlar:
        _embeddingleri_guncelle(base_url, api_key, workspace_slug, konumlar)

    return SenkronizasyonSonucu(
        workspace_slug=workspace_slug,
        workspace_adi=workspace_adi,
        yuklenen_dosyalar=yuklenen,
        atlanan_dosyalar=atlanan,
    )
