"""Komut satırı arayüzü (click tabanlı)."""
from __future__ import annotations

import sys

import click
from rich.table import Table

from pathlib import Path

from . import calibre_lib
from .ai_analyzer import AIAnalizHatasi, analyze_book
from .anythingllm_sync import AnythingLLMHatasi, sync_folder
from .config import (
    DEFAULT_MODEL,
    YapilandirmaHatasi,
    get_anythingllm_api_key,
    get_anythingllm_base_url,
    get_anythingllm_workspace,
    resolve_library_path,
)
from .output import console, render_to_terminal, save_as_markdown
from .pdf_extractor import PdfMetniBosHatasi, extract_pages

LIBRARY_OPTION = click.option(
    "--library",
    "-l",
    "library",
    default=None,
    help="Calibre kütüphane dizini (verilmezse CALIBRE_LIBRARY_PATH ortam değişkeni kullanılır).",
)


def _kitaplari_tabloda_goster(kitaplar: list[calibre_lib.Kitap]) -> None:
    if not kitaplar:
        console.print("[yellow]Eşleşen PDF kitap bulunamadı.[/yellow]")
        return

    tablo = Table(title="Kitaplar")
    tablo.add_column("ID", justify="right", style="cyan")
    tablo.add_column("Başlık", style="bold")
    tablo.add_column("Yazar", style="dim")
    for kitap in kitaplar:
        tablo.add_row(str(kitap.id), kitap.baslik, kitap.yazar)
    console.print(tablo)


def _sayfa_araligi_ayristir(deger: str | None) -> tuple[int, int] | None:
    if deger is None:
        return None
    try:
        baslangic_str, bitis_str = deger.split("-", 1)
        return int(baslangic_str), int(bitis_str)
    except ValueError as exc:
        raise click.BadParameter("Sayfa aralığı 'BAŞLANGIÇ-BİTİŞ' biçiminde olmalı, örn. 10-40") from exc


@click.group()
def cli() -> None:
    """Calibre kütüphanesindeki PDF kitapları AI ile özetleyen/analiz eden araç."""


@cli.command("list")
@LIBRARY_OPTION
def list_command(library: str | None) -> None:
    """Kütüphanedeki PDF formatına sahip kitapları listeler."""
    try:
        library_path = resolve_library_path(library)
        kitaplar = calibre_lib.list_books(library_path)
    except YapilandirmaHatasi as exc:
        console.print(f"[red]Hata:[/red] {exc}")
        sys.exit(1)
    _kitaplari_tabloda_goster(kitaplar)


@cli.command("search")
@click.argument("query")
@LIBRARY_OPTION
def search_command(query: str, library: str | None) -> None:
    """Başlık veya yazara göre kitap arar."""
    try:
        library_path = resolve_library_path(library)
        kitaplar = calibre_lib.search_books(library_path, query)
    except YapilandirmaHatasi as exc:
        console.print(f"[red]Hata:[/red] {exc}")
        sys.exit(1)
    _kitaplari_tabloda_goster(kitaplar)


@cli.command("analyze")
@click.argument("book")
@LIBRARY_OPTION
@click.option("--question", "-q", "question", default=None, help="Özel soru/istek (örn. '3. bölümü özetle').")
@click.option("--pages", "pages", default=None, help="Sayfa aralığı, örn. 10-40 (verilmezse tüm kitap kullanılır).")
@click.option("--model", "model_adi", default=DEFAULT_MODEL, show_default=True, help="Kullanılacak Gemini modeli.")
@click.option("--save/--no-save", "save_flag", default=None, help="Sonucu Markdown olarak kaydet (belirtilmezse sorulur).")
@click.option("--output-dir", "output_dir", default="analiz_ciktilari", show_default=True, help="Markdown çıktı klasörü.")
def analyze_command(
    book: str,
    library: str | None,
    question: str | None,
    pages: str | None,
    model_adi: str,
    save_flag: bool | None,
    output_dir: str,
) -> None:
    """Belirtilen kitabı (ID veya başlık) özetler ve derinlemesine analiz eder."""
    try:
        library_path = resolve_library_path(library)
        kitap = calibre_lib.find_book(library_path, book)
        pdf_yolu = kitap.pdf_yolunu_coz(library_path)
        if not pdf_yolu.is_file():
            raise calibre_lib.KitapBulunamadiHatasi(f"PDF dosyası bulunamadı: {pdf_yolu}")

        sayfa_araligi = _sayfa_araligi_ayristir(pages)

        console.print(f"[dim]PDF okunuyor: {pdf_yolu}[/dim]")
        sayfalar = extract_pages(pdf_yolu, page_range=sayfa_araligi)

        console.print(f"[dim]{model_adi} ile analiz üretiliyor, bu biraz zaman alabilir...[/dim]")
        sonuc = analyze_book(
            sayfalar,
            kitap_basligi=kitap.baslik,
            yazar=kitap.yazar,
            custom_question=question,
            model_adi=model_adi,
        )
    except (YapilandirmaHatasi, calibre_lib.KitapBulunamadiHatasi, PdfMetniBosHatasi, AIAnalizHatasi) as exc:
        console.print(f"[red]Hata:[/red] {exc}")
        sys.exit(1)

    render_to_terminal(kitap.baslik, kitap.yazar, sonuc)

    kaydet = save_flag
    if kaydet is None:
        kaydet = click.confirm("\nSonucu Markdown dosyası olarak kaydetmek ister misiniz?", default=True)

    if kaydet:
        dosya_yolu = save_as_markdown(kitap.baslik, kitap.yazar, sonuc, model_adi, output_dir)
        console.print(f"[green]Kaydedildi:[/green] {dosya_yolu}")


@cli.command("anythingllm-sync")
@click.option(
    "--output-dir",
    "output_dir",
    default="analiz_ciktilari",
    show_default=True,
    help="AnythingLLM'e gönderilecek Markdown analizlerinin bulunduğu klasör.",
)
@click.option(
    "--workspace",
    "workspace_adi",
    default=None,
    help="AnythingLLM çalışma alanı adı (verilmezse ANYTHINGLLM_WORKSPACE ortam değişkeni "
    "veya 'Kitap Analizlerim' kullanılır).",
)
@click.option(
    "--base-url",
    "base_url",
    default=None,
    help="AnythingLLM sunucu adresi (verilmezse ANYTHINGLLM_BASE_URL ortam değişkeni "
    "veya http://localhost:3001 kullanılır).",
)
def anythingllm_sync_command(output_dir: str, workspace_adi: str | None, base_url: str | None) -> None:
    """Kaydedilmiş kitap analizlerini yerel AnythingLLM uygulamasına gönderir."""
    try:
        api_key = get_anythingllm_api_key()
    except YapilandirmaHatasi as exc:
        console.print(f"[red]Hata:[/red] {exc}")
        sys.exit(1)

    base_url = base_url or get_anythingllm_base_url()
    workspace_adi = workspace_adi or get_anythingllm_workspace()

    console.print(
        f"[dim]{base_url} adresindeki AnythingLLM'e bağlanılıyor, "
        f"'{workspace_adi}' çalışma alanına gönderiliyor...[/dim]"
    )
    try:
        sonuc = sync_folder(base_url, api_key, workspace_adi, Path(output_dir))
    except AnythingLLMHatasi as exc:
        console.print(f"[red]Hata:[/red] {exc}")
        sys.exit(1)

    if sonuc.yuklenen_dosyalar:
        console.print(f"[green]Gönderildi ({len(sonuc.yuklenen_dosyalar)} dosya):[/green]")
        for dosya_adi in sonuc.yuklenen_dosyalar:
            console.print(f"  - {dosya_adi}")
    if sonuc.atlanan_dosyalar:
        console.print(f"[yellow]Gönderilemedi ({len(sonuc.atlanan_dosyalar)} dosya):[/yellow]")
        for dosya_adi in sonuc.atlanan_dosyalar:
            console.print(f"  - {dosya_adi}")

    console.print(
        f"\n[bold cyan]Kontrol etmek için:[/bold cyan] AnythingLLM uygulamasını açın, "
        f"sol menüden [bold]{sonuc.workspace_adi}[/bold] çalışma alanına girin ve "
        "belgeler (Documents) listesinde bu dosyaları görmelisiniz."
    )


if __name__ == "__main__":
    cli()
