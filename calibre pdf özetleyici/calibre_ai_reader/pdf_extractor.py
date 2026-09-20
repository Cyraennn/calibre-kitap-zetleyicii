"""PDF'ten metin çıkarma ve büyük metinleri parçalara (chunk) ayırma."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pdfplumber


class PdfMetniBosHatasi(Exception):
    """PDF'ten hiç metin çıkarılamadığında (örn. taranmış/görsel PDF) fırlatılır."""


@dataclass
class SayfaMetni:
    sayfa_no: int
    metin: str


def extract_pages(pdf_path: Path, page_range: tuple[int, int] | None = None) -> list[SayfaMetni]:
    """PDF'ten sayfa sayfa metin çıkarır.

    page_range verilirse (1-indeksli, kapsayıcı) yalnızca o aralıktaki sayfalar okunur.
    """
    sayfalar: list[SayfaMetni] = []
    with pdfplumber.open(pdf_path) as pdf:
        toplam_sayfa = len(pdf.pages)
        baslangic, bitis = 1, toplam_sayfa
        if page_range is not None:
            baslangic, bitis = page_range
            baslangic = max(1, baslangic)
            bitis = min(toplam_sayfa, bitis)
            if baslangic > bitis:
                raise ValueError(
                    f"Geçersiz sayfa aralığı: {page_range} (PDF toplam {toplam_sayfa} sayfa)"
                )

        for sayfa_no in range(baslangic, bitis + 1):
            sayfa = pdf.pages[sayfa_no - 1]
            metin = sayfa.extract_text() or ""
            sayfalar.append(SayfaMetni(sayfa_no=sayfa_no, metin=metin))

    if not any(s.metin.strip() for s in sayfalar):
        raise PdfMetniBosHatasi(
            "PDF'ten metin çıkarılamadı. Dosya muhtemelen taranmış görsellerden "
            "oluşuyor (OCR gerektiriyor) ve bu araç OCR desteklemiyor."
        )

    return sayfalar


def extract_full_text(pages: list[SayfaMetni]) -> str:
    """Sayfaları, sayfa numarası işaretleriyle birlikte tek bir metinde birleştirir."""
    parcalar = []
    for sayfa in pages:
        if sayfa.metin.strip():
            parcalar.append(f"\n\n[Sayfa {sayfa.sayfa_no}]\n\n{sayfa.metin}")
    return "".join(parcalar).strip()


def chunk_text(pages: list[SayfaMetni], chunk_size_chars: int) -> list[str]:
    """Sayfa sınırlarını gözeterek metni karakter bütçesine göre parçalara böler.

    Tek bir sayfa chunk_size_chars'tan büyük olsa bile o sayfa bölünmeden
    kendi başına bir chunk olarak eklenir (bütünlüğü korumak için).
    """
    chunklar: list[str] = []
    mevcut_parcalar: list[str] = []
    mevcut_boyut = 0

    def mevcut_chunki_kapat() -> None:
        nonlocal mevcut_parcalar, mevcut_boyut
        if mevcut_parcalar:
            chunklar.append("".join(mevcut_parcalar).strip())
        mevcut_parcalar = []
        mevcut_boyut = 0

    for sayfa in pages:
        if not sayfa.metin.strip():
            continue
        sayfa_metni = f"\n\n[Sayfa {sayfa.sayfa_no}]\n\n{sayfa.metin}"
        if mevcut_boyut > 0 and mevcut_boyut + len(sayfa_metni) > chunk_size_chars:
            mevcut_chunki_kapat()
        mevcut_parcalar.append(sayfa_metni)
        mevcut_boyut += len(sayfa_metni)

    mevcut_chunki_kapat()
    return chunklar
