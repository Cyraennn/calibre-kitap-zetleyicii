# 📚 Calibre AI Kitap Okuyucu

Bu program, **Calibre** kütüphanenizdeki PDF kitapları okuyup **yapay zeka (Google Gemini)**
ile Türkçe özetler ve derinlemesine analizler çıkaran basit bir araçtır.

Bu döküman, bilgisayarınızda **hiçbir programlama bilgisi olmasa bile** bu aracı adım adım
kurup çalıştırmanız için hazırlanmıştır. Sırasıyla ilerleyin, hiçbir adımı atlamayın.

---

## İçindekiler

1. [Gerekenler](#1-gerekenler)
2. [Adım 1 – Python'u Kurma](#adım-1--pythonu-kurma)
3. [Adım 2 – Proje Klasörünü Terminalde Açma](#adım-2--proje-klasörünü-terminalde-açma)
4. [Adım 3 – Gerekli Kütüphaneleri Kurma](#adım-3--gerekli-kütüphaneleri-kurma)
5. [Adım 4 – Google Gemini API Anahtarı Alma](#adım-4--google-gemini-api-anahtarı-alma)
6. [Adım 5 – Calibre Kütüphane Yolunu Bulma](#adım-5--calibre-kütüphane-yolunu-bulma)
7. [Adım 6 – Ayar Dosyasını (.env) Oluşturma](#adım-6--ayar-dosyasını-env-oluşturma)
8. [Adım 7 – Programı Çalıştırma](#adım-7--programı-çalıştırma)
9. [Kullanılabilir Komutlar](#kullanılabilir-komutlar)
10. [AnythingLLM ile Bağlantı](#anythingllm-ile-bağlantı)
11. [Sorun Giderme (Sık Karşılaşılan Hatalar)](#sorun-giderme-sık-karşılaşılan-hatalar)
12. [Notlar](#notlar)

---

## 1. Gerekenler

Başlamadan önce bilgisayarınızda şunlar olmalı:

- **Windows** işletim sistemi (bu döküman Windows için yazılmıştır)
- **Calibre** programı kurulu ve içinde en az bir **PDF** kitap ekli olmalı
  ([calibre-ebook.com](https://calibre-ebook.com/download) adresinden ücretsiz indirilir)
- İnternet bağlantısı (yapay zeka analizleri internet üzerinden çalışır)

Bunların dışında hiçbir şeyin kurulu olmasına gerek yok, aşağıdaki adımlarda hepsini
birlikte kuracağız.

---

## Adım 1 – Python'u Kurma

Bu program **Python** dili ile yazılmıştır, o yüzden önce Python'u bilgisayarınıza kurmalısınız.

1. Tarayıcınızdan şu adrese gidin: **https://www.python.org/downloads/**
2. Sarı/mavi **"Download Python 3.x.x"** butonuna tıklayıp indirin.
3. İndirilen dosyayı (örn. `python-3.12.x-amd64.exe`) çift tıklayarak çalıştırın.
4. **ÇOK ÖNEMLİ:** Kurulum penceresinin **en altında** bulunan
   **"Add python.exe to PATH"** (veya "Add Python to PATH") kutucuğunu **mutlaka işaretleyin**.
   Bu adımı atlarsanız program çalışmaz.
5. **"Install Now"** butonuna tıklayın ve kurulumun bitmesini bekleyin.
6. Kurulum bittiğinde "Disable path length limit" gibi bir seçenek çıkarsa ona da
   tıklayabilirsiniz (zorunlu değil).

**Kurulumu test edin:**

1. Klavyeden `Windows tuşu` + `R` tuşlarına basın, açılan kutuya `powershell` yazıp Enter'a basın.
   (Ya da Başlat menüsüne "PowerShell" yazıp açabilirsiniz.)
2. Açılan mavi/siyah pencereye şunu yazıp Enter'a basın:
   ```powershell
   python --version
   ```
3. Ekranda `Python 3.12.x` gibi bir yazı görüyorsanız kurulum başarılı demektir.
   Eğer "python is not recognized..." gibi bir hata görürseniz, [Sorun Giderme](#sorun-giderme-sık-karşılaşılan-hatalar)
   bölümüne bakın.

---

## Adım 2 – Proje Klasörünü Terminalde Açma

Şimdi bu proje dosyalarının bulunduğu klasörü terminalde (PowerShell'de) açmamız gerekiyor.
Bunun en kolay yolu:

1. Dosya Gezgini'nde (Windows Explorer) bu projenin bulunduğu klasöre gidin
   (içinde `main.py`, `requirements.txt` gibi dosyaların olduğu klasör).
2. Klasörün içindeyken, üstteki adres çubuğuna tıklayın, yazan yolu silin ve `powershell`
   yazıp Enter'a basın.
   - Alternatif: Klasör içinde boş bir yere **Shift tuşuna basılı tutarak sağ tıklayın**,
     çıkan menüden **"PowerShell penceresini burada aç"** (veya "Open PowerShell window here")
     seçeneğine tıklayın.
3. Açılan pencerede terminal artık bu proje klasörünün içinde demektir. Şunu yazarak
   kontrol edebilirsiniz:
   ```powershell
   dir
   ```
   Karşınıza `main.py`, `requirements.txt`, `calibre_ai_reader` gibi dosya/klasör isimleri
   çıkmalı.

> 📌 Bundan sonraki tüm komutları, bu şekilde açtığınız aynı terminal penceresine
> yazıp Enter'a basarak çalıştıracaksınız.

---

## Adım 3 – Gerekli Kütüphaneleri Kurma

Bu programın çalışması için bazı ek Python kütüphanelerine ihtiyaç var. Terminale şunu yazıp
Enter'a basın:

```powershell
pip install -r requirements.txt
```

Ekranda bir sürü indirme/kurulum yazısı akacak, bu normaldir. Birkaç dakika sürebilir.
En sonda hata yazmıyorsa (kırmızı "ERROR" yazısı yoksa) kurulum tamamlanmış demektir.

---

## Adım 4 – Google Gemini API Anahtarı Alma

Program, kitap analizlerini yapmak için Google'ın yapay zekasını (Gemini) kullanıyor.
Bunu kullanabilmek için ücretsiz bir "API anahtarı" almanız gerekiyor.

1. Tarayıcınızdan şu adrese gidin: **https://aistudio.google.com/apikey**
2. Google hesabınızla giriş yapın (yoksa ücretsiz bir Gmail hesabı oluşturabilirsiniz).
3. **"Create API key"** (veya "API anahtarı oluştur") butonuna tıklayın.
4. Karşınıza uzun bir harf/rakam dizisi çıkacak, örneğin: `AIzaSyD1a2B3c4D5e6F7...`
5. Bu anahtarı kopyalayın (yanındaki kopyala ikonuna tıklayarak) ve bir kenara not edin.
   **Bu anahtarı kimseyle paylaşmayın**, kendi şifreniz gibidir.

---

## Adım 5 – Calibre Kütüphane Yolunu Bulma

Programın, kitaplarınızın Calibre'de nerede saklandığını bilmesi gerekiyor.

1. Calibre programını açın.
2. Üst menüden **Tercihler (Preferences)** simgesine tıklayın (dişli çark ikonu).
3. Açılan pencerede **"Klasörleri Göster"** (İngilizce sürümde "Open calibre configuration
   directory" değil, doğrudan ana ekranda **"Kütüphaneleri Değiştir/Oluştur/Kaldır"** gibi bir
   seçenek de olabilir) — en kolay yol: Calibre ana penceresinin sol üstünde kütüphane adının
   yazdığı yere tıklayın, "Kütüphane Klasörünü Aç" gibi bir seçenek çıkar.
   - Alternatif ve en garanti yöntem: Calibre ana penceresinde sol taraftaki kütüphane
     ismine sağ tıklayın → **"Konumu göster"** ya da benzeri bir seçenek çıkacaktır.
4. Açılan Dosya Gezgini penceresinde, adres çubuğundaki **tam yolu** kopyalayın.
   Örneğin şuna benzer bir şey olacaktır:
   ```
   C:\Users\KullaniciAdiniz\Documents\Calibre Library
   ```
5. Bu klasörün içinde `metadata.db` adında bir dosya olduğundan emin olun — doğru
   klasör budur.

---

## Adım 6 – Ayar Dosyasını (.env) Oluşturma

Şimdi elimizdeki API anahtarını ve Calibre yolunu programa tanıtacağız.

1. Terminalde (proje klasöründeyken) şunu yazıp Enter'a basın. Bu, örnek ayar dosyasını
   kopyalayarak gerçek ayar dosyasını oluşturur:
   ```powershell
   copy .env.example .env
   ```
2. Dosya Gezgini'nden proje klasörüne gidin, oluşan **`.env`** adlı dosyayı bulun
   (uzantısız, sadece `.env` ismiyle görünür — gizli dosyaların görünmesi kapalıysa
   Dosya Gezgini'nde "Görünüm → Gizli öğeler" seçeneğini açmanız gerekebilir).
3. `.env` dosyasına sağ tıklayıp **Not Defteri (Notepad) ile aç**'ı seçin.
4. İçeriği şu şekilde düzenleyin (kendi bilgilerinizle):
   ```
   GOOGLE_API_KEY=Adım_4te_aldığınız_anahtarı_buraya_yapıştırın
   CALIBRE_LIBRARY_PATH=Adım_5te_bulduğunuz_klasör_yolunu_buraya_yapıştırın
   ```
   Örnek (gerçek bilgilerle doldurulmuş hali):
   ```
   GOOGLE_API_KEY=AIzaSyD1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P7
   CALIBRE_LIBRARY_PATH=C:\Users\Ahmet\Documents\Calibre Library
   ```
5. Dosyayı kaydedin (`Ctrl + S`) ve Not Defteri'ni kapatın.

> ⚠️ `.env` dosyasını asla başkalarıyla paylaşmayın veya internete yüklemeyin — içinde
> gizli API anahtarınız var. Bu dosya zaten `.gitignore` içinde olduğu için GitHub'a
> yanlışlıkla yüklenmez.

---

## Adım 7 – Programı Çalıştırma

Artık her şey hazır! Terminalde (proje klasörünün içindeyken) aşağıdaki komutu yazıp
Enter'a basarak kütüphanenizdeki PDF kitapları listeleyin:

```powershell
python main.py list
```

Karşınıza kitaplarınızın ID, Başlık ve Yazar bilgilerini içeren bir tablo çıkmalı.
Eğer bu tablo çıktıysa, kurulum tamamen başarılı demektir. 🎉

Bir kitabı analiz etmek için (aşağıdaki `42` yerine tablodan gördüğünüz gerçek ID'yi yazın):

```powershell
python main.py analyze 42
```

---

## Kullanılabilir Komutlar

Aşağıdaki komutları, terminalde proje klasörünün içindeyken çalıştırırsınız.

**Kitapları listele:**
```powershell
python main.py list
```

**Başlık veya yazara göre ara:**
```powershell
python main.py search "Dostoyevski"
```

**Bir kitabı özetle ve analiz et** (ID veya başlığın bir kısmıyla):
```powershell
python main.py analyze 42
python main.py analyze "Suç ve Ceza"
```

**Özel bir soru/istekle analiz et:**
```powershell
python main.py analyze 42 --question "Raskolnikov'un suç teorisini eleştirel olarak değerlendir"
```

**Sadece belirli sayfaları analiz et:**
```powershell
python main.py analyze 42 --pages 50-90 --question "Bu bölümü özetle"
```

**Sonucu sormadan doğrudan kaydet:**
```powershell
python main.py analyze 42 --save --output-dir analizlerim
```

**Farklı bir Gemini modeli kullan:**
```powershell
python main.py analyze 42 --model gemini-2.5-pro
```

`.env` dosyası yerine her komutta `--library "C:\yol\Calibre Library"` parametresini de
kullanabilirsiniz.

**Kaydedilmiş analizleri AnythingLLM'e gönder** (bkz. [AnythingLLM ile Bağlantı](#anythingllm-ile-bağlantı)):
```powershell
python main.py anythingllm-sync
```

---

## AnythingLLM ile Bağlantı

Bilgisayarınızda **[AnythingLLM](https://anythingllm.com/)** kuruluysa, bu programın ürettiği
kitap analizlerini (`analiz_ciktilari/` klasöründeki Markdown dosyalarını) tek komutla
AnythingLLM'e gönderip orada bir "çalışma alanına" (workspace) ekleyebilirsiniz. Böylece
daha sonra AnythingLLM'i açtığınızda kitap analizlerinizle ilgili sohbet edebilir, sorular
sorabilirsiniz.

### Adım 1 – AnythingLLM'de API Anahtarı Oluşturma

1. **AnythingLLM masaüstü uygulamasını açın** (kapalıysa bu bölümdeki komutlar çalışmaz).
2. Sol alttaki **dişli çark (Settings/Ayarlar)** simgesine tıklayın.
3. Soldaki menüden **"Developer API"** (Geliştirici API) seçeneğine tıklayın.
4. **"Generate New API Key"** (Yeni API Anahtarı Oluştur) butonuna tıklayın.
5. Oluşan anahtarı kopyalayın (uzun bir harf/rakam dizisi).

### Adım 2 – Ayar Dosyasına (.env) Ekleme

`.env` dosyanızı (bkz. [Adım 6](#adım-6--ayar-dosyasını-env-oluşturma)) Not Defteri ile açıp
en alta şu satırları ekleyin:

```
ANYTHINGLLM_API_KEY=az_önce_kopyaladığınız_anahtar
ANYTHINGLLM_BASE_URL=http://localhost:3001
ANYTHINGLLM_WORKSPACE=Kitap Analizlerim
```

- `ANYTHINGLLM_BASE_URL` genelde değiştirmenize gerek yok (AnythingLLM varsayılan olarak bu
  adreste çalışır).
- `ANYTHINGLLM_WORKSPACE`, analizlerinizin ekleneceği çalışma alanının adıdır; bu isimde bir
  çalışma alanı yoksa program otomatik olarak oluşturur.

### Adım 3 – Senkronizasyonu Çalıştırma

> ⚠️ `anythingllm-sync` komutu **sadece** AnythingLLM bağlantısını (API anahtarını) kontrol
> eder; kitap analizi üretmek için hâlâ [Adım 4](#adım-4--google-gemini-api-anahtarı-alma)'teki
> Gemini API anahtarına ve [Adım 5](#adım-5--calibre-kütüphane-yolunu-bulma)'teki Calibre
> kütüphane yoluna ihtiyacınız var. Bu ikisi `.env` dosyanızda ayarlı değilse `analyze --save`
> çalışmaz ve gönderilecek analiz dosyası olmaz.

En az bir analiz kaydettikten sonra (`python main.py analyze ... --save`), terminale şunu
yazın:

```powershell
python main.py anythingllm-sync
```

Bu komut, `analiz_ciktilari/` klasöründeki tüm `.md` dosyalarını AnythingLLM'e yükler ve
belirttiğiniz çalışma alanına ekler. Ekranda hangi dosyaların gönderildiği listelenir.

Farklı bir klasör veya çalışma alanı kullanmak isterseniz:

```powershell
python main.py anythingllm-sync --output-dir analiz_ciktilari --workspace "Kitap Analizlerim"
```

### Adım 4 – AnythingLLM'de Kontrol Etme

1. AnythingLLM uygulamasını açın (veya zaten açıksa öne getirin).
2. Sol menüden **`Kitap Analizlerim`** (veya `.env` dosyasında belirttiğiniz isim) çalışma
   alanına tıklayın.
3. Sağ üstteki **belgeler (Documents)** simgesine/paneline bakın — gönderdiğiniz analiz
   dosyalarını burada listeli görmelisiniz.
4. Bu çalışma alanında sohbet kutusuna kitaplarınızla ilgili soru yazarak analizlerinizi
   AnythingLLM üzerinden sorgulayabilirsiniz.

> 📌 `anythingllm-sync` komutunu, yeni analizler kaydettikçe tekrar tekrar çalıştırabilirsiniz;
> daha önce gönderilmiş bir dosyayı tekrar gönderirse AnythingLLM içinde ayrı bir kopya
> olarak eklenir, o yüzden istemediğiniz eski dosyaları AnythingLLM tarafında silebilirsiniz.

---

## Sorun Giderme (Sık Karşılaşılan Hatalar)

**`python : 'python' terimi bir cmdlet, işlev...olarak tanınmıyor` / "python is not recognized"**
→ Python kurulurken "Add python.exe to PATH" kutucuğu işaretlenmemiş demektir.
Python'u kaldırıp ([Adım 1](#adım-1--pythonu-kurma)) kutucuğu işaretleyerek tekrar kurun.
Kurulumdan sonra terminali kapatıp yeniden açmayı unutmayın.

**`pip : 'pip' terimi tanınmıyor`**
→ Aynı sebep; Python kurulumunu PATH kutucuğunu işaretleyerek tekrarlayın.

**`ModuleNotFoundError: No module named 'click'` (veya benzeri bir modül adı)**
→ [Adım 3](#adım-3--gerekli-kütüphaneleri-kurma)'teki `pip install -r requirements.txt`
komutunu tekrar çalıştırın. Doğru klasörde olduğunuzdan emin olun (`dir` yazınca
`requirements.txt` görünmeli).

**`Hata: GOOGLE_API_KEY ayarlanmamış` (veya benzeri bir yapılandırma hatası)**
→ `.env` dosyasını doğru düzenlemediniz veya kaydetmediniz. [Adım 6](#adım-6--ayar-dosyasını-env-oluşturma)'yı
tekrar kontrol edin. Dosya adının tam olarak `.env` olduğundan emin olun (`.env.txt` gibi
bir uzantı eklenmemiş olmalı — Not Defteri'nde kaydederken "Dosya türü: Tüm Dosyalar" seçin).

**`Kütüphane bulunamadı` / `metadata.db bulunamadı`**
→ `.env` içindeki `CALIBRE_LIBRARY_PATH` yanlış. [Adım 5](#adım-5--calibre-kütüphane-yolunu-bulma)'i
tekrar yapıp doğru klasör yolunu (içinde `metadata.db` olan klasör) yapıştırın.

**API anahtarıyla ilgili bir hata (geçersiz anahtar, kota aşıldı vb.)**
→ [Adım 4](#adım-4--google-gemini-api-anahtarı-alma)'e dönüp anahtarı doğru kopyaladığınızdan
(başında/sonunda boşluk olmadan) emin olun. Gerekirse yeni bir anahtar oluşturun.

**`anythingllm-sync` komutu "AnythingLLM sunucusuna bağlanılamadı" diyor**
→ AnythingLLM masaüstü uygulamasının açık olduğundan emin olun. Yine de çalışmazsa
`.env` dosyasındaki `ANYTHINGLLM_BASE_URL` adresinin doğru olduğunu kontrol edin.

**`anythingllm-sync` komutu "API anahtarı geçersiz" diyor**
→ [AnythingLLM ile Bağlantı](#anythingllm-ile-bağlantı) bölümündeki Adım 1'i tekrarlayıp
yeni bir API anahtarı oluşturun ve `.env` dosyasındaki `ANYTHINGLLM_API_KEY` değerini
güncelleyin.

**`anythingllm-sync` komutu "'analiz_ciktilari' klasöründe '\*.md' ile eşleşen dosya
bulunamadı" diyor**
→ Bu, AnythingLLM bağlantısının (API anahtarının) **çalıştığı** anlamına gelir — sadece
gönderilecek analiz dosyası yok demektir. Önce `.env` dosyasına `GOOGLE_API_KEY` ve
`CALIBRE_LIBRARY_PATH` değerlerinizi girip (bkz. [Adım 4](#adım-4--google-gemini-api-anahtarı-alma),
[Adım 5](#adım-5--calibre-kütüphane-yolunu-bulma)) `python main.py analyze <kitap> --save`
ile en az bir analiz kaydedin, sonra `anythingllm-sync`'i tekrar çalıştırın.

**Terminal komutları çalışmıyor, hiçbir şey olmuyor**
→ Terminalin gerçekten proje klasöründe açık olduğundan emin olun ([Adım 2](#adım-2--proje-klasörünü-terminalde-açma)).
`dir` yazdığınızda `main.py` dosyasını görmelisiniz.

Hiçbiri işe yaramazsa: hata mesajının **tamamını** kopyalayıp yardım istediğiniz kişiye
gönderin — hata mesajı sorunun ne olduğunu gösterir.

---

## Notlar

- Taranmış (görsel/fotoğraf) PDF'ler desteklenmez; bunlar için OCR gerekir.
- Çok büyük kitaplarda analiz süreci birden fazla yapay zeka çağrısı gerektirdiğinden
  işlem birkaç dakika sürebilir, bu normaldir.
- Üretilen Markdown dosyaları varsayılan olarak `analiz_ciktilari/` klasörüne kaydedilir
  (bu klasör `.gitignore` içindedir, yani proje paylaşılırsa bu dosyalar paylaşılmaz).
