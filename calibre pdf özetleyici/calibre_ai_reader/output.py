"""Terminal gösterimi (rich) ve Markdown dosyasına kaydetme."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


def render_to_terminal(kitap_basligi: str, yazar: str, markdown_metin: str) -> None:
    console.print(
        Panel.fit(
            f"[bold]{kitap_basligi}[/bold]\n[dim]{yazar}[/dim]",
            title="Kitap Analizi",
            border_style="cyan",
        )
    )
    console.print(Markdown(markdown_metin))


def _dosya_adi_temizle(metin: str) -> str:
    temiz = re.sub(r"[^\w\s-]", "", metin, flags=re.UNICODE).strip()
    temiz = re.sub(r"[-\s]+", "_", temiz)
    return temiz[:80] or "kitap"


def save_as_markdown(
    kitap_basligi: str,
    yazar: str,
    markdown_metin: str,
    model_adi: str,
    output_dir: str = "analiz_ciktilari",
) -> Path:
    """Analiz sonucunu Markdown dosyası olarak kaydeder ve dosya yolunu döner."""
    cikti_klasoru = Path(output_dir)
    cikti_klasoru.mkdir(parents=True, exist_ok=True)

    tarih = datetime.now().strftime("%Y-%m-%d_%H%M")
    dosya_adi = f"{tarih}_{_dosya_adi_temizle(kitap_basligi)}.md"
    dosya_yolu = cikti_klasoru / dosya_adi

    baslik_blogu = (
        f"# {kitap_basligi}\n\n"
        f"- **Yazar:** {yazar}\n"
        f"- **Analiz Tarihi:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        f"- **Kullanılan Model:** {model_adi}\n\n"
        "---\n\n"
    )

    dosya_yolu.write_text(baslik_blogu + markdown_metin, encoding="utf-8")
    return dosya_yolu
