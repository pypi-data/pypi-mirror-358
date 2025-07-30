import os
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Thread
from transformers import AutoTokenizer
from tensorrt_llm.runtime import ModelRunner

# --- 全局变量 ---
ENGINE_PATH = "/app/built_engine/deepseek_engine"
TOKENIZER_PATH = "/app/hf_model" # 我们需要原始HF模型中的tokenizer
runner = None
tokenizer = None

# --- FastAPI生命周期事件 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global runner, tokenizer
    print("--- 正在加载模型引擎和Tokenizer... ---")
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True)
    runner = ModelRunner.from_dir(engine_dir=ENGINE_PATH, rank=0, stream=True)
    print("--- ✅ 模型加载完毕，服务准备就绪 ---")
    yield
    print("--- 正在清理资源... ---")
    runner = None
    tokenizer = None

app = FastAPI(lifespan=lifespan)

# --- API请求和响应模型 ---
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256
    temperature: float = 0.7

class GenerateResponse(BaseModel):
    text: str

# --- API端点 ---
@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    print(f"收到请求: {request.prompt}")
    
    # 准备输入
    input_ids = tokenizer.encode(request.prompt, return_tensors="pt").to("cuda")
    
    # 执行推理
    output_ids = runner.generate(
        input_ids,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
    
    # 清理并解码输出
    # output_ids[0] 的形状是 [beam_width, seq_length]
    generated_text = tokenizer.decode(output_ids[0, 0, len(input_ids[0]):], skip_special_tokens=True)
    
    print(f"生成响应: {generated_text}")
    return GenerateResponse(text=generated_text)

@app.get("/health")
async def health_check():
    return {"status": "ok" if runner is not None else "loading"}