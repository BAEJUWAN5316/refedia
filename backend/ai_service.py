import os
import sys
print("DEBUG: ai_service.py imported")
import google.generativeai as genai
import json
import base64
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def analyze_video_with_gemini(video_title, video_description, categories_structure, channel_name="Unknown Channel", images_data=None):
    """
    Gemini API를 사용하여 비디오 카테고리 분석 (텍스트 + 이미지)
    Args:
        images_data (list): Base64 인코딩된 이미지 문자열 리스트 (썸네일 + 프레임)
    """
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env file")

    # 카테고리 구조를 JSON 문자열로 변환
    categories_str = json.dumps(categories_structure, ensure_ascii=False, indent=2)

    # 프롬프트 구성
    prompt_text = f"""
    [시스템 프롬프트 내용] 당신은 'REFEDIA'를 위한 전문 영상 콘텐츠 분석가입니다. 당신의 임무는 유튜브 영상 데이터를 분석하여 가장 적절한 카테고리로 분류하는 것입니다.

    ### 1. 입력 데이터

    채널명: {channel_name}

    영상 제목: {video_title}

    영상 설명: {video_description}

    시각 정보: (첨부된 이미지들을 참고하세요. 썸네일 및 주요 장면 프레임입니다.)

    자막 요약: (자막 데이터는 현재 API 제한으로 인해 포함되지 않았습니다. 제목, 설명, 그리고 시각 정보를 바탕으로 추론하세요.)

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
    - **중요: 제공된 카테고리 이름(한글)을 정확히 그대로 사용하세요. 번역하거나 수정하지 마세요.**

    ### 4. 출력 형식 오직 유효한 JSON 객체만 반환하세요. 마크다운(```json)은 쓰지 마세요. {{ "industry": [...], "genre": [...], ... }}
    """

    # 컨텐츠 구성 (텍스트 + 이미지)
    contents = [prompt_text]
    
    if images_data:
        print(f"🖼️ Processing {len(images_data)} images for Gemini...")
        for img_str in images_data:
            try:
                # Remove header if present (data:image/png;base64,...)
                if "base64," in img_str:
                    img_str = img_str.split("base64,")[1]
                
                image_bytes = base64.b64decode(img_str)
                image = Image.open(io.BytesIO(image_bytes))
                contents.append(image)
            except Exception as e:
                print(f"⚠️ Failed to process an image: {e}")

    # 역매핑 테이블 생성 (Name -> ID)
    name_to_id = {}
    normalized_name_to_id = {}
    
    try:
        for cat_type, cats in categories_structure.items():
            for c in cats:
                name_to_id[c['name']] = c['id']
                name_to_id[c['id']] = c['id']
                
                # Normalize: lower case and strip whitespace
                norm_name = c['name'].lower().strip()
                normalized_name_to_id[norm_name] = c['id']
                
                # Split by '/' and add parts (e.g., "IT/서비스/자동차" -> "it", "서비스", "자동차")
                if '/' in norm_name:
                    parts = norm_name.split('/')
                    for part in parts:
                        p = part.strip()
                        if p:
                            normalized_name_to_id[p] = c['id']
                            
    except Exception as e:
        print(f"⚠️ Error creating category mapping: {e}")

    try:
        # 모델: gemini-2.0-flash-lite-001 사용
        model = genai.GenerativeModel('gemini-2.0-flash-lite-001')
        
        sys.stderr.write(f"🚀 Sending request to Gemini with {len(contents)} content items...\n")
        response = model.generate_content(contents)
        sys.stderr.write("✅ Gemini response received\n")
        
        # 응답 텍스트 정제
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        # JSON 파싱
        try:
            result = json.loads(text)
            sys.stderr.write(f"🔍 Raw Gemini Result: {json.dumps(result, ensure_ascii=False)}\n")
            
            # Save raw result to file for debugging
            with open("last_gemini_response.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            sys.stderr.write(f"🔍 Result Keys: {list(result.keys())}\n")
        except json.JSONDecodeError:
            sys.stderr.write(f"❌ Failed to parse JSON: {text}\n")
            return {}
        
        sys.stderr.write(f"🔍 Normalized Map Keys (Sample): {list(normalized_name_to_id.keys())[:5]}\n")
        
        final_result = {}
        for key in ["industry", "genre", "cast", "mood", "editing"]:
            final_result[key] = []
            
            # Check for key with whitespace tolerance and case-insensitivity
            found_key = None
            if key in result:
                found_key = key
            else:
                # Try finding key with stripped whitespace and case-insensitive match
                for k in result.keys():
                    if k.strip().lower() == key.lower():
                        found_key = k
                        break
            
            if found_key:
                sys.stderr.write(f"🔍 Processing key: '{found_key}' (mapped to '{key}')\n")
                items = result[found_key]
                
                # Ensure items is a list
                if not isinstance(items, list):
                    sys.stderr.write(f"⚠️ Expected list for {found_key}, got {type(items)}\n")
                    continue
                    
                for item in items:
                    sys.stderr.write(f"   👉 Processing item: '{item}'\n")
                    
                    target_name = None
                    target_id = None
                    
                    # Handle Dictionary item (Gemini might return full object)
                    if isinstance(item, dict):
                        if 'id' in item:
                            target_id = item['id']
                            log_msg = f"✅ Matched (Direct ID): {target_id}"
                            sys.stderr.write(log_msg + "\n")
                            final_result[key].append(target_id)
                            continue
                        elif 'name' in item:
                            target_name = item['name']
                    # Handle String item
                    elif isinstance(item, str):
                        target_name = item
                    else:
                        sys.stderr.write(f"⚠️ Skipping invalid item type in {key}: {type(item)}\n")
                        continue
                    
                    if target_name:
                        # 1. Try Exact Match
                        if target_name in name_to_id:
                            final_result[key].append(name_to_id[target_name])
                            log_msg = f"✅ Matched (Exact): {target_name} -> {name_to_id[target_name]}"
                            sys.stderr.write(log_msg + "\n")
                            with open("debug_ai_matching.log", "a", encoding="utf-8") as f:
                                f.write(log_msg + "\n")
                                
                        # 2. Try Normalized Match
                        elif target_name.lower().strip() in normalized_name_to_id:
                            matched_id = normalized_name_to_id[target_name.lower().strip()]
                            final_result[key].append(matched_id)
                            log_msg = f"✅ Matched (Normalized): {target_name} -> {matched_id}"
                            sys.stderr.write(log_msg + "\n")
                            with open("debug_ai_matching.log", "a", encoding="utf-8") as f:
                                f.write(log_msg + "\n")
                                
                        else:
                            log_msg = f"❌ Unmatched category item: '{target_name}' (Normalized: '{target_name.lower().strip()}')"
                            sys.stderr.write(log_msg + "\n")
                            with open("debug_ai_matching.log", "a", encoding="utf-8") as f:
                                f.write(log_msg + "\n")
                        
        sys.stderr.write(f"🏁 Final Result: {json.dumps(final_result, ensure_ascii=False)}\n")
        return final_result

    except Exception as e:
        import traceback
        print(f"❌ Gemini Analysis Failed: {e}")
        traceback.print_exc()
        raise e
