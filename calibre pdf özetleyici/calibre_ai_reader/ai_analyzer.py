"""Google Gemini API ile özet/analiz üretimi (gerekirse map-reduce ile)."""
from __future__ import annotations

from google import genai

from . import prompts
from .config import CHUNK_SIZE_CHARS, DEFAULT_MODEL, MAX_SINGLE_CALL_CHARS, get_gemini_api_key
from .pdf_extractor import SayfaMetni, chunk_text, extract_full_text


class AIAnalizHatasi(Exception):
    """Gemini API çağrısı başarısız olduğunda fırlatılır."""


def _client_olustur() -> genai.Client:
    return genai.Client(api_key=get_gemini_api_key())


def _uret(client: genai.Client, model_adi: str, prompt: str) -> str:
    try:
        yanit = client.models.generate_content(model=model_adi, contents=prompt)
    except Exception as exc:  # google-genai kendi geniş hata hiyerarşisini kullanıyor
        raise AIAnalizHatasi(f"Gemini API çağrısı başarısız oldu: {exc}") from exc

    if not getattr(yanit, "text", None):
        raise AIAnalizHatasi(
            "Gemini modeli boş bir yanıt döndürdü (içerik güvenlik filtresine "
            "takılmış olabilir)."
        )
    return yanit.text


def analyze_book(
    pages: list[SayfaMetni],
    kitap_basligi: str,
    yazar: str,
    custom_question: str | None = None,
    model_adi: str = DEFAULT_MODEL,
) -> str:
    """Verilen sayfa listesini özetler/analiz eder.

    custom_question verilirse, genel özet yerine o soruya odaklanılır.
    Metin MAX_SINGLE_CALL_CHARS altındaysa tek çağrı, üstündeyse map-reduce kullanılır.
    """
    tam_metin = extract_full_text(pages)
    client = _client_olustur()

    if len(tam_metin) <= MAX_SINGLE_CALL_CHARS:
        if custom_question:
            prompt = prompts.OZEL_SORU_TEK_GECIS_PROMPT.format(
                kitap_basligi=kitap_basligi, yazar=yazar, soru=custom_question, metin=tam_metin
            )
        else:
            prompt = prompts.SINGLE_PASS_PROMPT.format(
                kitap_basligi=kitap_basligi,
                yazar=yazar,
                format_talimati=prompts.YAPILANDIRILMIS_CIKTI_FORMATI,
                metin=tam_metin,
            )
        return _uret(client, model_adi, prompt)

    # Map aşaması: her chunk için ara özet/not çıkar.
    chunklar = chunk_text(pages, CHUNK_SIZE_CHARS)
    ara_ozetler: list[str] = []
    for i, chunk in enumerate(chunklar, start=1):
        if custom_question:
            map_prompt = prompts.OZEL_SORU_MAP_PROMPT.format(
                kitap_basligi=kitap_basligi, soru=custom_question, metin=chunk
            )
        else:
            map_prompt = prompts.MAP_PROMPT.format(kitap_basligi=kitap_basligi, metin=chunk)
        ozet = _uret(client, model_adi, map_prompt)
        ara_ozetler.append(f"### Bölüm {i}/{len(chunklar)} Notları\n{ozet}")

    birlesik_ara_ozetler = "\n\n".join(ara_ozetler)

    # Reduce aşaması: ara özetleri sentezle.
    if custom_question:
        reduce_prompt = prompts.OZEL_SORU_REDUCE_PROMPT.format(
            kitap_basligi=kitap_basligi,
            yazar=yazar,
            soru=custom_question,
            ara_ozetler=birlesik_ara_ozetler,
        )
    else:
        reduce_prompt = prompts.REDUCE_PROMPT.format(
            kitap_basligi=kitap_basligi,
            yazar=yazar,
            format_talimati=prompts.YAPILANDIRILMIS_CIKTI_FORMATI,
            ara_ozetler=birlesik_ara_ozetler,
        )
    return _uret(client, model_adi, reduce_prompt)
