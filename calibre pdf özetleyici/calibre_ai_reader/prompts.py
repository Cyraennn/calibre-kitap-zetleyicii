"""Gemini modeline gönderilecek Türkçe prompt şablonları."""

YAPILANDIRILMIS_CIKTI_FORMATI = """\
# Özet

## Ana Temalar
(Kitabın/metnin ele aldığı temel temaları maddeler halinde listele)

## Olay Örgüsü / Ana Tez
(Kurgu ise olay örgüsünü, kurgu değilse yazarın ana tezini/argümanını özetle)

## Önemli Noktalar
(Öne çıkan, akılda kalması gereken noktaları maddeler halinde listele)

# Eleştirel Analiz ve Yorum

## Yazarın Savunması / Argümantasyonu
(Yazar tezini nasıl temellendiriyor, hangi kanıt/anlatım tekniklerini kullanıyor)

## Güçlü ve Zayıf Yönler
(Metnin ikna ediciliği, tutarlılığı, üslubu üzerine eleştirel değerlendirme)

## Çıkarımlar ve Genel Değerlendirme
(Bu metinden çıkarılabilecek dersler, güncel önemi, kişisel/entelektüel çıkarımlar)
"""

SINGLE_PASS_PROMPT = """\
Sen deneyimli, eleştirel düşünen bir edebiyat ve fikir kitapları eleştirmenisin.
Aşağıda "{kitap_basligi}" ({yazar}) adlı kitabın tam metni (veya seçilen bölümü) verilmiştir.

Bu metni dikkatlice oku ve TÜRKÇE olarak, aşağıdaki formatta yapılandırılmış bir
özet ve derinlemesine eleştirel analiz üret. Yüzeysel kalma; metinden somut
örnekler ve alıntılara atıfta bulunarak analiz derinliğini göster.

FORMAT:
{format_talimati}

METİN:
{metin}
"""

MAP_PROMPT = """\
Aşağıdaki metin, "{kitap_basligi}" adlı kitabın bir bölümüdür (kitabın tamamı
değildir). Bu parçayı dikkatlice oku ve TÜRKÇE olarak kısa ama öz bir ara özet
çıkar: bu parçada işlenen temalar, gelişen olaylar/argümanlar ve dikkat çeken
önemli noktalar/alıntılar neler? Sonraki adımda bu ara özetler birleştirilip
kitabın tam analizi yapılacağı için, bu bölümün içeriğini kaybetmeden, ancak
gereksiz tekrar olmadan aktar.

METİN PARÇASI:
{metin}
"""

REDUCE_PROMPT = """\
Sen deneyimli, eleştirel düşünen bir edebiyat ve fikir kitapları eleştirmenisin.
"{kitap_basligi}" ({yazar}) adlı kitabın tamamı, sırasıyla aşağıdaki ara
bölüm özetlerine dönüştürülmüştür (kitabın başından sonuna doğru sıralıdır).

Bu ara özetleri sentezleyerek TÜRKÇE olarak, aşağıdaki formatta yapılandırılmış,
kitabın BÜTÜNÜNÜ kapsayan bir özet ve derinlemesine eleştirel analiz üret.
Ara özetleri birbirine bağla, tekrarları ayıkla, kitabın genel bir değerlendirmesini yap.

FORMAT:
{format_talimati}

ARA BÖLÜM ÖZETLERİ:
{ara_ozetler}
"""

OZEL_SORU_MAP_PROMPT = """\
Aşağıdaki metin, "{kitap_basligi}" adlı kitabın bir bölümüdür (kitabın tamamı
değildir). Okuyucunun şu sorusu/isteği var: "{soru}"

Bu metin parçasında, yukarıdaki soru/istekle İLGİLİ olan bilgi, alıntı veya
argümanları TÜRKÇE olarak çıkar. Eğer bu parça soruyla hiç ilgili değilse,
sadece "Bu bölümde ilgili içerik bulunmuyor." yaz.

METİN PARÇASI:
{metin}
"""

OZEL_SORU_REDUCE_PROMPT = """\
Sen deneyimli, eleştirel düşünen bir edebiyat ve fikir kitapları eleştirmenisin.
"{kitap_basligi}" ({yazar}) adlı kitap hakkında okuyucunun sorusu/isteği şu:
"{soru}"

Kitabın farklı bölümlerinden bu soruyla ilgili çıkarılan notlar aşağıdadır.
Bu notları sentezleyerek TÜRKÇE, kapsamlı, derinlemesine ve eleştirel bir
yanıt/analiz yaz. Yüzeysel kalma; somut örneklere ve alıntılara atıfta bulun.
İlgisiz bölümlerden gelen "ilgili içerik bulunmuyor" notlarını yok sayabilirsin.

İLGİLİ BÖLÜM NOTLARI:
{ara_ozetler}
"""

OZEL_SORU_TEK_GECIS_PROMPT = """\
Sen deneyimli, eleştirel düşünen bir edebiyat ve fikir kitapları eleştirmenisin.
Aşağıda "{kitap_basligi}" ({yazar}) adlı kitabın tam metni (veya seçilen bölümü)
verilmiştir. Okuyucunun şu sorusu/isteği var: "{soru}"

Bu soruyu/isteği metne dayanarak TÜRKÇE, kapsamlı, derinlemesine ve eleştirel
biçimde yanıtla. Somut örneklere ve alıntılara atıfta bulun.

METİN:
{metin}
"""
