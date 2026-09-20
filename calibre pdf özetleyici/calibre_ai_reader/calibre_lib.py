"""Calibre metadata.db dosyasını doğrudan (calibredb olmadan) okuyan modül."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


class KitapBulunamadiHatasi(Exception):
    """Aranan kitap ID'si veya sorgusu ile eşleşen kitap bulunamadığında fırlatılır."""


@dataclass
class Kitap:
    id: int
    baslik: str
    yazar: str
    goreli_yol: str
    dosya_adi: str

    def pdf_yolunu_coz(self, library_path: Path) -> Path:
        return library_path / self.goreli_yol / f"{self.dosya_adi}.pdf"


def _baglanti_ac(library_path: Path) -> sqlite3.Connection:
    metadata_db = library_path / "metadata.db"
    uri = f"file:{metadata_db.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


_PDF_KITAP_SORGUSU = """
    SELECT books.id, books.title, books.author_sort, books.path, data.name
    FROM books
    JOIN data ON data.book = books.id
    WHERE data.format = 'PDF'
"""


def list_books(library_path: Path) -> list[Kitap]:
    """Kütüphanedeki PDF formatına sahip tüm kitapları döner."""
    with _baglanti_ac(library_path) as conn:
        rows = conn.execute(f"{_PDF_KITAP_SORGUSU} ORDER BY books.title").fetchall()
    return [Kitap(*row) for row in rows]


def search_books(library_path: Path, query: str) -> list[Kitap]:
    """Başlık veya yazara göre (büyük/küçük harf duyarsız) arama yapar."""
    like_pattern = f"%{query}%"
    with _baglanti_ac(library_path) as conn:
        rows = conn.execute(
            f"""{_PDF_KITAP_SORGUSU}
            AND (books.title LIKE ? COLLATE NOCASE
                 OR books.author_sort LIKE ? COLLATE NOCASE)
            ORDER BY books.title""",
            (like_pattern, like_pattern),
        ).fetchall()
    return [Kitap(*row) for row in rows]


def get_book_by_id(library_path: Path, book_id: int) -> Kitap:
    """Verilen ID'ye sahip (PDF formatındaki) kitabı döner."""
    with _baglanti_ac(library_path) as conn:
        row = conn.execute(
            f"{_PDF_KITAP_SORGUSU} AND books.id = ?", (book_id,)
        ).fetchone()
    if row is None:
        raise KitapBulunamadiHatasi(
            f"ID={book_id} olan ve PDF formatına sahip bir kitap bulunamadı."
        )
    return Kitap(*row)


def find_book(library_path: Path, identifier: str) -> Kitap:
    """Verilen tanımlayıcıyı (sayısal ID ya da başlık alt dizesi) çözer.

    - Sayısal ise doğrudan ID ile arar.
    - Değilse başlık/yazar araması yapar; tam olarak bir sonuç bulunmalıdır,
      birden fazla veya sıfır sonuç durumunda KitapBulunamadiHatasi fırlatılır.
    """
    if identifier.isdigit():
        return get_book_by_id(library_path, int(identifier))

    sonuclar = search_books(library_path, identifier)
    if len(sonuclar) == 0:
        raise KitapBulunamadiHatasi(f"'{identifier}' ile eşleşen bir kitap bulunamadı.")
    if len(sonuclar) > 1:
        baslik_listesi = "\n".join(
            f"  [{k.id}] {k.baslik} — {k.yazar}" for k in sonuclar
        )
        raise KitapBulunamadiHatasi(
            f"'{identifier}' birden fazla kitapla eşleşti, lütfen ID kullanın:\n{baslik_listesi}"
        )
    return sonuclar[0]
