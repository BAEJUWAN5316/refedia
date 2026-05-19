import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import base64
import io
from PIL import Image

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 2단계: 카테고리 정의
CATEGORIES_JSON = {
    "industry": ["FNB", "Home/Interior", "Shopping/Retail", "IT/Service/Auto", "Corporate/CSR", "Finance/Insurance", "Game", "Beauty/Fashion", "Health/Pharma", "Living/Kids/Pet", "Entertainment", "Leisure/Travel", "Public/Gov", "Construction/RealEstate", "Education"],
    "genre": ["Variety", "Documentary", "Fake Docu", "Survival", "Mukbang", "Review", "Dance", "Road/Street", "Info/Guide", "Experience", "Talk Show", "Podcast", "Participatory", "Branded", "Live", "Challenge", "Viral", "Sketch", "Travel", "Fandom", "Vlog", "Shorts", "Playlist", "Behind", "Reaction", "ASMR", "News/Issue"],
    "cast": ["Influencer", "Celebrity", "Comedian", "Singer", "Virtual", "Alt-Character(Bu-character)", "Expert", "General Public", "Employees/CEO", "Kids", "Pet", "Couple", "Foreigner"],
    "mood": ["Serious", "B-grade", "Humor", "Seasonal", "Meme", "Healing/Emotional", "Retro", "Luxury", "Kitsch", "Dynamic", "Motivational", "Bizarre"],
    "editing": ["Subtitle/Font", "VFX", "Infographic", "AI-Generated", "Interactive", "Motion Graphics", "Cinematic", "Typography", "Vertical", "One-take", "Chroma-key", "Fast-paced"]
}

def extract_video_data(url):
    """
    1단계: 데이터 추출
    yt-dlp를 사용하여 channel_name, video_title, video_description을 가져오고,
    youtube-transcript-api를 사용하여 자막을 가져옵니다.
    추가: youtube_service에서 프레임과 썸네일도 가져옵니다.
    """
    video_data = {
        "channel_name": "Unknown Channel",
        "video_title": "Unknown Title",
        "video_description": "",
        "transcript_snippet": "자막 없음",
        "images_data": []
    }

    # 1. Extract Metadata using yt-dlp
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True, # 메타데이터만 추출
    }
    
    video_id = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_data["channel_name"] = info.get('uploader') or info.get('channel') or info.get('uploader_id')
            video_data["video_title"] = info.get('title')
            video_data["video_description"] = info.get('description')
            video_id = info.get('id')
            
            # 썸네일 URL
            thumbnail_url = info.get('thumbnail')
            
            # Import visual extraction tools from youtube_service
            try:
                from youtube_service import extract_frames, download_image_as_base64
                
                print("🖼️ Extracting visual data...")
                # 썸네일 다운로드
                if thumbnail_url:
                    thumb_b64 = download_image_as_base64(thumbnail_url)
                    if thumb_b64:
                        video_data["images_data"].append(thumb_b64)
                
                # 프레임 추출
                frames = extract_frames(url, count=3)
                if frames:
                    video_data["images_data"].extend(frames)
                    
            except Exception as ve:
                print(f"⚠️ Visual extraction failed: {ve}")

    except Exception as e:
        print(f"Error extracting metadata with yt-dlp: {e}")
        return None

    # 2. Extract Transcript using youtube-transcript-api
    if video_id:
        try:
            # 한국어 우선, 영어 차선
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
            
            # 자막 텍스트 합치기
            full_transcript = " ".join([entry['text'] for entry in transcript_list])
            
            # 500~1000자 제한 (여기서는 1000자)
            if len(full_transcript) > 1000:
                video_data["transcript_snippet"] = full_transcript[:1000] + "..."
            else:
                video_data["transcript_snippet"] = full_transcript
            
        except (TranscriptsDisabled, NoTranscriptFound):
            video_data["transcript_snippet"] = "자막 없음"
        except Exception as e:
            print(f"Error extracting transcript: {e}")
            video_data["transcript_snippet"] = "자막 없음 (오류 발생)"

    return video_data

def analyze_video_category(video_data):
    """
    3단계: Gemini API 호출
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env file")

    # 시스템 프롬프트 구성
    categories_str = json.dumps(CATEGORIES_JSON, ensure_ascii=False, indent=2)
    
    prompt_text = f"""
    [시스템 프롬프트 내용] 당신은 'REFEDIA'를 위한 전문 영상 콘텐츠 분석가입니다. 당신의 임무는 유튜브 영상 데이터를 분석하여 가장 적절한 카테고리로 분류하는 것입니다.

    ### 1. 입력 데이터

    채널명: {video_data['channel_name']}

    영상 제목: {video_data['video_title']}

    영상 설명: {video_data['video_description']}

    시각 정보: (첨부된 이미지들을 참고하세요. 썸네일 및 주요 장면 프레임입니다.)

    자막 요약: {video_data['transcript_snippet']}

    ### 2. 사용 가능한 카테고리 (JSON)
    {categories_str}

    ### 3. 분석 지침 (단계별 추론 - 중요!) 카테고리를 선택하기 전에, 내부적으로 다음 분석을 먼저 수행하세요:

    채널 정체성 파악: 이 채널이 기업인가, 개인인가, 아니면 코미디 채널인가? (예: '피식대학' -> 코미디)

    주된 의도 결정: 목적이 재미(코미디, 콩트)인가 정보 전달(뉴스)인가?

    주의: 만약 유명한 코미디 채널이 진지한 제목의 영상(패러디)을 올렸다면, 속지 말고 엔터테인먼트/코미디로 분류하세요.

    분위기 분석: 콘텐츠가 진지한가, 재치 있는가, 영화 같은가? (첨부된 이미지의 색감, 자막 스타일, 표정 등을 적극 활용하세요!)

    카테고리 선택: 
    - **업종(Industry)은 반드시 1개 이상 선택해야 합니다.** (가장 연관성 높은 것으로 추론)
    - 그 외 항목도 해당된다면 여러 개의 태그를 선택하세요.

    ### 4. 출력 형식 오직 유효한 JSON 객체만 반환하세요. 마크다운(```json)은 쓰지 마세요. {{ "industry": [...], "genre": [...], ... }}
    """

    # 컨텐츠 구성
    contents = [prompt_text]
    
    if video_data.get("images_data"):
        print(f"🖼️ Processing {len(video_data['images_data'])} images for Gemini...")
        for img_str in video_data["images_data"]:
            try:
                if "base64," in img_str:
                    img_str = img_str.split("base64,")[1]
                
                image_bytes = base64.b64decode(img_str)
                image = Image.open(io.BytesIO(image_bytes))
                contents.append(image)
            except Exception as e:
                print(f"⚠️ Failed to process an image: {e}")

    try:
        # 모델: gemini-2.0-flash 사용 (안정성 및 속도 고려)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        response = model.generate_content(contents)
        
        # 응답 텍스트 정제
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)

    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
        return None

if __name__ == "__main__":
    # 샘플 코드
    print("--- REFEDIA Video Analyzer Test ---")
    
    # 더미 URL (피식대학 - 한사랑산악회 예시)
    dummy_url = "https://www.youtube.com/watch?v=0tO0lTqVjXU" 
    
    print(f"Analyzing URL: {dummy_url}...")
    
    # 1. 데이터 추출
    data = extract_video_data(dummy_url)
    
    if data:
        print("\n[Extracted Data]")
        print(f"Channel: {data['channel_name']}")
        print(f"Title: {data['video_title']}")
        print(f"Transcript (First 100 chars): {data['transcript_snippet'][:100]}...")
        
        # 2. AI 분석
        print("\n[Analyzing with Gemini...]")
        result = analyze_video_category(data)
        
        if result:
            print("\n[Analysis Result]")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Analysis failed.")
    else:
        print("Failed to extract video data.")
