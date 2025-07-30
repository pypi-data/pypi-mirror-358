import requests
import json

# --- 配置 ---
TRITON_SERVER_URL = "http://localhost:8000"
MODEL_NAME = "deepseek_trtllm"
PROMPT = "请给我讲一个关于人工智能的笑话。"
MAX_TOKENS = 256
STREAM = False
# ----------------------------------------------------

def main():
    """向Triton服务器发送请求并打印结果。"""
    url = f"{TRITON_SERVER_URL}/v2/models/{MODEL_NAME}/generate"
    payload = {
        "text_input": PROMPT,
        "max_new_tokens": MAX_TOKENS,
        "temperature": 0.7,
        "stream": STREAM
    }
    print(f"Sending request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    print("-" * 30)

    try:
        response = requests.post(url, json=payload, headers={"Accept": "application/json"})
        response.raise_for_status()
        response_data = response.json()
        generated_text = response_data.get('text_output', 'Error: "text_output" key not found.')
        
        print("✅ Request successful!")
        print("-" * 30)
        print("Prompt:", PROMPT)
        print("\nGenerated Text:", generated_text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error making request to Triton server: {e}")
        if e.response:
            print(f"Response Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")

if __name__ == '__main__':
    main()