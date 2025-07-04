# get_transcript.py
import sys
import os # Ortam değişkenlerini okumak için eklendi
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.proxies import WebshareProxyConfig # WebshareProxyConfig'i import et

# --- Webshare Proxy Yapılandırması ---
# Webshare kullanıcı adı ve şifresini ortam değişkenlerinden alın
# Bu değişkenleri Render.com'da ayarlamanız gerekecek (Adım 3'e bakın)
proxy_username = os.getenv('WEBSHARE_PROXY_USERNAME')
proxy_password = os.getenv('WEBSHARE_PROXY_PASSWORD')

# YouTubeTranscriptApi örneğini proxy yapılandırmasıyla başlatın
ytt_api = None
if proxy_username and proxy_password:
    try:
        proxy_config = WebshareProxyConfig(
            proxy_username=proxy_username,
            proxy_password=proxy_password,
        )
        ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        print("YouTubeTranscriptApi Webshare proxy ile başlatıldı.", file=sys.stderr)
    except Exception as e:
        print(f"Webshare proxy yapılandırması başlatılırken hata oluştu: {e}", file=sys.stderr)
else:
    print("Webshare proxy kimlik bilgileri (WEBSHARE_PROXY_USERNAME, WEBSHARE_PROXY_PASSWORD) bulunamadı. Proxy olmadan deneniyor.", file=sys.stderr)

# --- get_youtube_transcript fonksiyonu ---
def get_youtube_transcript(video_id):
    """
    Belirli bir YouTube video ID'si için transkripti getirir.
    Mevcut bir transkript bulmak için yaygın dillerin bir listesini dener.
    """
    languages_to_try = [
        'en', 'es', 'fr', 'de', 'pt', 'it', 'nl', 'ru', 'ja', 'ko', 'zh-Hans',
        'zh-Hant', 'hi', 'ar', 'tr', 'vi', 'pl', 'sv', 'fi', 'da', 'no', 'id',
        'ms', 'th', 'el', 'cs', 'hu', 'ro', 'uk'
    ]
    
    # ytt_api başlatıldıysa onu kullanın, aksi takdirde doğrudan çağrıya geri dönün
    # (ancak proxy sorunu için ytt_api'nin doğru şekilde başlatılması gerekir)
    api_instance = ytt_api if ytt_api else YouTubeTranscriptApi

    try:
        # ytt_api'nin fetch yöntemini kullanın
        transcript_list = api_instance.fetch(video_id)
        full_transcript = " ".join([item['text'] for item in transcript_list])
        print("Transkript orijinal dilde bulundu.", file=sys.stderr)
        return full_transcript
    except (NoTranscriptFound, TranscriptsDisabled):
        print("Varsayılan transkript bulunamadı. Oluşturulmuş bir transkript bulunmaya çalışılıyor...", file=sys.stderr)
        for lang in languages_to_try:
            try:
                # ytt_api'nin fetch yöntemini kullanın
                transcript_list = api_instance.fetch(video_id, languages=[lang])
                full_transcript = " ".join([item['text'] for item in transcript_list])
                print(f"Transkript şu dil için bulundu: {lang}", file=sys.stderr)
                return full_transcript
            except (NoTranscriptFound, TranscriptsDisabled):
                continue
            except Exception as e:
                print(f"'{lang}' dilini denerken beklenmeyen bir hata oluştu: {e}", file=sys.stderr)
                continue
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}", file=sys.stderr)
        return None

    return None

# --- Main (Ana) kısım ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python get_transcript.py <video_id>", file=sys.stderr)
        sys.exit(1)

    video_id = sys.argv[1]
    transcript = get_youtube_transcript(video_id)

    if transcript:
        # Node.js için nihai transkripti standart çıktıya yazdırın
        print(transcript)
    else:
        # Standart hataya bir hata yazdırın ve bir hata koduyla çıkın
        print("Birden fazla dil denendikten sonra video için transkript bulunamadı.", file=sys.stderr)
        sys.exit(1)