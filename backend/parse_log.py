import json
import sys

try:
    with open('found_log.txt', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Extract JSON part
    start_marker = "Raw Gemini Result: "
    start_index = content.find(start_marker)
    if start_index != -1:
        json_str = content[start_index + len(start_marker):].strip()
        # Try to find the end of the JSON object
        # Simple heuristic: count braces
        brace_count = 0
        end_index = -1
        for i, char in enumerate(json_str):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_index = i + 1
                    break
        
        if end_index != -1:
            json_str = json_str[:end_index]
            
        try:
            data = json.loads(json_str)
            print("✅ Parsed JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {e}")
            print(f"Raw String: {json_str}")
    else:
        print("❌ 'Raw Gemini Result' not found in file.")
        
except Exception as e:
    print(f"❌ Error: {e}")
