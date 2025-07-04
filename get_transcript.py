# get_transcript.py
import sys
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import random # Proxy listesini karıştırmak için

def get_youtube_transcript(video_id):
    """
    Belirli bir YouTube video kimliği için transkripti getirir.
    Mevcut bir transkript bulmak için bir dizi yaygın dil dener.
    Proxy listesi kullanarak YouTube API kısıtlamalarını aşmaya çalışır.
    """
    # Proxy listesi ve kimlik bilgileri
    proxy_list = [
        "38.154.227.167:5868",
        "198.23.239.134:6540",
        "207.244.217.165:6712",
        "107.172.163.27:6543",
        "216.10.27.159:6837",
        "136.0.207.84:6661",
        "64.64.118.149:6732",
        "142.147.128.93:6593",
        "104.239.105.125:6655",
        "206.41.172.74:6634"
    ]
    username = "aqytvvai"
    password = "qb9bosniacof"

    # Proxy listesini her denemede rastgele karıştır
    random.shuffle(proxy_list)

    # Denenecek dillerin kapsamlı listesi, en yaygın olanlarla başlayarak.
    # Hedef kitlenize göre bunu yeniden sıralayabilirsiniz.
    languages_to_try = [
        'en', 'es', 'fr', 'de', 'pt', 'it', 'nl', 'ru', 'ja', 'ko', 'zh-Hans',
        'zh-Hant', 'hi', 'ar', 'tr', 'vi', 'pl', 'sv', 'fi', 'da', 'no', 'id',
        'ms', 'th', 'el', 'cs', 'hu', 'ro', 'uk'
    ]
    
    # Her bir proxy'yi dene
    for proxy in proxy_list:
        proxy_url = f"http://{username}:{password}@{proxy}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        print(f"Proxy kullanarak transkript denemesi: {proxy}", file=sys.stderr)
        try:
            # İlk olarak, bir dil belirtmeden transkripti getirmeye çalışın,
            # API'nin orijinal veya en iyi mevcut olanı seçmesine izin verin.
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
            full_transcript = " ".join([item['text'] for item in transcript_list])
            print("Transkript orijinal dilde bulundu.", file=sys.stderr)
            return full_transcript
        except (NoTranscriptFound, TranscriptsDisabled):
            # Varsayılan transkript bulunamazsa, yaygın dillerde otomatik oluşturulanları deneyin.
            print(f"Varsayılan transkript bulunamadı. Oluşturulmuş transkript aranıyor {proxy}...", file=sys.stderr)
            for lang in languages_to_try:
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang], proxies=proxies)
                    full_transcript = " ".join([item['text'] for item in transcript_list])
                    print(f"Transkript dil için bulundu: {lang} (Proxy: {proxy})", file=sys.stderr)
                    return full_transcript
                except (NoTranscriptFound, TranscriptsDisabled):
                    # Bu dil çalışmadı, bir sonraki dile devam et.
                    continue
                except Exception as e:
                    # Bu dil denemesi için farklı bir hata oluştu.
                    print(f"'{lang}' dili denenirken beklenmeyen bir hata oluştu (Proxy: {proxy}): {e}", file=sys.stderr)
                    continue
        except Exception as e:
            # İlk getirme denemesinde bir hata oluştu.
            print(f"Beklenmeyen bir hata oluştu (Proxy: {proxy}): {e}", file=sys.stderr)
            continue

    # Döngü herhangi bir transkript bulamadan tamamlanırsa
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python get_transcript.py <video_id>", file=sys.stderr)
        sys.exit(1)

    video_id = sys.argv[1]
    transcript = get_youtube_transcript(video_id)

    if transcript:
        # Son transkripti Node.js için standart çıktıya yazdır
        print(transcript)
    else:
        # Hata mesajını stderr'e yazdır ve hata koduyla çık
        print("Birden fazla dil denendikten sonra video için transkript bulunamadı.", file=sys.stderr)
        sys.exit(1)
