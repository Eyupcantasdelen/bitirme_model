import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# FastAPI uygulaması
app = FastAPI(title="Fine-tuned Gelecek Senaryosu AI Servisi")

# CORS yapılandırması - Daha geniş izinler
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver (test için)
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # OPTIONS metodunu ekleyin
    allow_headers=["*"],
)

# Alpaca prompt formatı
ALPACA_PROMPT = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

# Öngörüleri alacak veri yapısı
class Ongoruler(BaseModel):
    ongoruler: str

def format_alpaca_prompt(instruction, input_text, output=""):
    """Alpaca formatında prompt oluştur"""
    return ALPACA_PROMPT.format(instruction, input_text, output)

# Gelecek senaryosunu oluşturacak fonksiyon
def gelecek_senaryosu_olustur(ongoruler):
    try:
        instruction = """Verilen öngörülere dayalı olarak 2050 yılına yönelik detaylı bir gelecek senaryosu yaz. Senaryo en fazla 100 kelime uzunluğunda olsun. Hikaye formatında, akıcı ve yaratıcı bir anlatım oluştur.Dil bilgisi kurallarına dikkat et. Senaryoyu "teşekkür ederim" ile bitir. """
        
        input_text = f"Öngörüler: {ongoruler}"
        formatted_prompt = format_alpaca_prompt(instruction, input_text, "")
        
        response = ollama.chat(
            model='hf.co/hilalagtas/pufModel:latest',
            messages=[
                {
                    'role': 'user', 
                    'content': formatted_prompt
                }
            ],
            options={
                'temperature': 0.9,
                'num_ctx': 1024
            }
        )
        
        return response['message']['content']
        
    except Exception as e:
        print(f"Model hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model hatası: {str(e)}")

# OPTIONS endpoint'i ekleyin (CORS için gerekli)
@app.options("/create_scenario/")
async def options_create_scenario():
    return {"message": "OK"}

# POST endpointi: Senaryo oluşturma
@app.post("/create_scenario/")
async def create_scenario(ongoruler: Ongoruler):
    print(f"Gelen istek: {ongoruler.ongoruler}")  # Debug için
    
    if not ongoruler.ongoruler or not ongoruler.ongoruler.strip():
        raise HTTPException(status_code=400, detail="Öngörüler boş olamaz")
    
    try:
        cleaned_ongoruler = ongoruler.ongoruler.strip()
        senaryo = gelecek_senaryosu_olustur(cleaned_ongoruler)
        
        print(f"Oluşturulan senaryo: {senaryo[:100]}...")  # Debug için
        
        return {"scenario": senaryo, "status": "success"}
    
    except Exception as e:
        print(f"Hata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoint'i
@app.get("/test")
async def test():
    return {"message": "AI servisi çalışıyor", "model": "hilalagtas/pufModel:latest"}

# Sağlık kontrolü endpoint'i
@app.get("/health")
async def health_check():
    try:
        return {
            "status": "AI servisi çalışıyor",
            "model": "hilalagtas/pufModel:latest"
        }
    except Exception as e:
        return {
            "status": "Hata",
            "error": str(e)
        }

if __name__ == "__main__":
    print("Fine-tuned Gelecek Senaryosu AI Servisi başlatılıyor...")
    print("Model: hilalagtas/pufModel:latest")
    print("Port: 5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)  # 0.0.0.0 yapın