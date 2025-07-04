# # get_transcript.py
# import sys
# from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

# def get_youtube_transcript(video_id):
#     """
#     Fetches the transcript for a given YouTube video ID.
#     It tries a list of common languages to find an available transcript.
#     """
#     # A comprehensive list of languages to try, starting with the most common.
#     # You can reorder this based on your target audience.
#     languages_to_try = [
#         'en', 'es', 'fr', 'de', 'pt', 'it', 'nl', 'ru', 'ja', 'ko', 'zh-Hans',
#         'zh-Hant', 'hi', 'ar', 'tr', 'vi', 'pl', 'sv', 'fi', 'da', 'no', 'id',
#         'ms', 'th', 'el', 'cs', 'hu', 'ro', 'uk'
#     ]
    
#     # First, try to fetch the transcript without specifying a language,
#     # allowing the API to pick the original or best available one.
#     try:
#         transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
#         full_transcript = " ".join([item['text'] for item in transcript_list])
#         print("Transcript found in original language.", file=sys.stderr)
#         return full_transcript
#     except (NoTranscriptFound, TranscriptsDisabled):
#         # If no default transcript is found, try auto-generated ones in common languages.
#         print("No default transcript found. Trying to find a generated transcript...", file=sys.stderr)
#         for lang in languages_to_try:
#             try:
#                 transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
#                 full_transcript = " ".join([item['text'] for item in transcript_list])
#                 print(f"Transcript found for language: {lang}", file=sys.stderr)
#                 return full_transcript
#             except (NoTranscriptFound, TranscriptsDisabled):
#                 # This language didn't work, continue to the next one.
#                 continue
#             except Exception as e:
#                 # A different error occurred for this language attempt.
#                 print(f"An unexpected error occurred while trying language '{lang}': {e}", file=sys.stderr)
#                 continue
#     except Exception as e:
#         # An error occurred on the initial fetch attempt.
#         print(f"An unexpected error occurred: {e}", file=sys.stderr)
#         return None

#     # If the loop completes without finding any transcript
#     return None

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python get_transcript.py <video_id>", file=sys.stderr)
#         sys.exit(1)

#     video_id = sys.argv[1]
#     transcript = get_youtube_transcript(video_id)

#     if transcript:
#         # Print the final transcript to standard output for Node.js
#         print(transcript)
#     else:
#         # Print an error to stderr and exit with an error code
#         print("No transcript could be found for the video after trying multiple languages.", file=sys.stderr)
#         sys.exit(1)




# get_transcript.py
import sys
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

def get_youtube_transcript(video_id):
    languages_to_try = [
        'en', 'es', 'fr', 'de', 'pt', 'it', 'nl', 'ru', 'ja', 'ko', 'zh-Hans',
        'zh-Hant', 'hi', 'ar', 'tr', 'vi', 'pl', 'sv', 'fi', 'da', 'no', 'id',
        'ms', 'th', 'el', 'cs', 'hu', 'ro', 'uk'
    ]
    
    # İlk olarak, API'nin orijinal veya en iyi mevcut olanı seçmesine izin vererek
    # bir dil belirtmeden transkripti almaya çalışın.
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([item['text'] for item in transcript_list])
        print("Transcript found in original language.", file=sys.stderr)
        return full_transcript
    except (NoTranscriptFound, TranscriptsDisabled):
        # Varsayılan transkript bulunamazsa, ortak dillerde otomatik oluşturulanları bulmaya çalışın.
        print("No default transcript found. Trying to find a generated transcript...", file=sys.stderr)
        for lang in languages_to_try:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                full_transcript = " ".join([item['text'] for item in transcript_list])
                print(f"Transcript found for language: {lang}", file=sys.stderr)
                return full_transcript
            except (NoTranscriptFound, TranscriptsDisabled):
                # Bu dil işe yaramadı, bir sonrakine devam et.
                continue
            except Exception as e:
                # Bu dil denemesinde farklı bir hata oluştu.
                print(f"An unexpected error occurred while trying language '{lang}': {e}", file=sys.stderr)
                continue
    except Exception as e:
        # İlk alma denemesinde bir hata oluştu.
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return None

    # Döngü herhangi bir transkript bulamadan tamamlarsa
    return None

if __name__ == "__main__":
    # Bu kısmı sadece test için değiştiriyoruz
    # Test etmek istediğiniz video ID'sini buraya yazın
    test_video_id = "LBs2VVVsVks" # Örneğin, Render logunuzdaki video ID

    print(f"Attempting to get transcript for video ID: {test_video_id}", file=sys.stderr)
    transcript = get_youtube_transcript(test_video_id)

    if transcript:
        print("\n--- TEST TRANSKRİPTİ BAŞLANGICI ---", file=sys.stderr)
        print(transcript[:500] + "...", file=sys.stderr) # İlk 500 karakteri yazdır
        print("--- TEST TRANSKRİPTİ SONU ---", file=sys.stderr)
        print("Test successful: Transcript retrieved.", file=sys.stderr)
    else:
        print("\n--- TEST BAŞARISIZ ---", file=sys.stderr)
        print("Test failed: No transcript could be found for the video. Check the logs above for specific errors.", file=sys.stderr)
        sys.exit(1)

    # Orijinal argv kontrolünü isterseniz yorum satırı yapabilirsiniz veya bırakabilirsiniz
    # if len(sys.argv) < 2:
    #     print("Usage: python get_transcript.py <video_id>", file=sys.stderr)
    #     sys.exit(1)
    # video_id = sys.argv[1]
    # transcript = get_youtube_transcript(video_id)
    # if transcript:
    #     print(transcript)
    # else:
    #     print("No transcript could be found for the video after trying multiple languages.", file=sys.stderr)
    #     sys.exit(1)
