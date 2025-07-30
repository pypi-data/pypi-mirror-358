import requests
import json

PROMPT = "请给我讲一个关于人工智能的笑话。"
API_URL = "http://localhost:8000/generate"

def main():
    payload = {
        "prompt": PROMPT,
        "max_new_tokens": 100
    }
    
    print(f"Sending request to: {API_URL}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
    print("-" * 30)

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        generated_text = response_data.get('text')
        
        print("✅ Request successful!")
        print("-" * 30)
        print("Prompt:", PROMPT)
        print("\nGenerated Text:", generated_text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error making request: {e}")
        if e.response:
            print(f"Response Body: {e.response.text}")

if __name__ == '__main__':
    main()