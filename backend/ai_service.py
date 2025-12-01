import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def analyze_video_with_gemini(video_title, video_description, categories_structure):
    """
    Gemini를 사용하여 비디오 메타데이터를 기반으로 카테고리를 추천합니다.
    
    Args:
        video_title (str): 비디오 제목
        video_description (str): 비디오 설명
        categories_structure (dict): 현재 DB에 있는 카테고리 구조 (type -> list of {id, name})
        
    Returns:
        dict: 추천된 카테고리 ID 목록 (type -> list of ids)
    """
    if not API_KEY:
        raise Exception("API Key not configured")

    # 카테고리 목록을 텍스트로 변환하여 프롬프트에 포함
    categories_text = json.dumps(categories_structure, ensure_ascii=False, indent=2)
    
    prompt = f"""
    Analyze the following YouTube video based on its title and description, and recommend the most appropriate categories from the provided list.

    Video Title: {video_title}
    Video Description: {video_description}

    Available Categories (JSON format):
    {categories_text}

    **Instructions:**
    1.  **Analyze Deeply:** Understand the core topic, style, and vibe of the video.
    2.  **Select Categories:** Choose the most relevant category IDs for each type.
        *   **Industry (Required):** Select at least 1, but feel free to select multiple (2+) if the video covers multiple industries.
        *   **Genre (Required):** Select at least 1, but feel free to select multiple (2+) if the video fits multiple genres.
        *   **Mood (Required):** Select at least 1, but feel free to select multiple (2+) to capture the video's atmosphere.
        *   **Cast (Optional):** Select only if specific types of people/characters are prominent.
        *   **Editing (Optional):** Select only if specific editing styles or visual effects are prominent.
    3.  **Be Smart:** Don't just keyword match. Infer the category from the context.
    4.  **Output Format:** Return ONLY a JSON object with the following keys: "industry", "genre", "cast", "mood", "editing". Each key should map to a list of selected category IDs (strings).

    Example Output:
    {{
      "industry": ["id1", "id2"],
      "genre": ["id3"],
      "cast": [],
      "mood": ["id4", "id5"],
      "editing": ["id6"]
    }}
    """
    
    try:
        # 사용 가능한 모델: gemini-2.0-flash-lite-001 (더 가볍고 안정적)
        model = genai.GenerativeModel('gemini-2.0-flash-lite-001')
        response = model.generate_content(prompt)
        
        # 응답 텍스트에서 JSON 추출 (마크다운 코드 블록 제거)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text)
        
    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
        # 429 에러 등 발생 시 상위에서 처리하도록 예외 전파
        raise e
