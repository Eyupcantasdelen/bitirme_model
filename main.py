import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Proje dizini oluşturma
proje_dizini = './gelecek_senaryosu_projesi'
os.makedirs(proje_dizini, exist_ok=True)

# Modelfile içeriğini oluşturma
modelfile_content = """FROM llama3.1

# Gelecek Senaryosu Yazım Sistemi Prompt'u
SYSTEM \"\"\"
Sen profesyonel bir gelecek senaryosu yazarsın. Verilen öngörülerden:
- 2050 yılına dair, inandırıcı ve tutarlı bir senaryo yaz
- Politik, ekonomik, teknolojik, sosyal ve çevresel dinamikleri hesaba kat
- Net, yaratıcı ve özgün senaryolar oluştur
- Hikaye formatında, olay örgüsüne sahip bir senaryo oluştur
- Metin 1 veya 2 paragraflık olmalı
- Başlık içermemeli, sadece hikayeye odaklanmalı
- Akıcı, yaratıcı ve tutarlı bir anlatım olmalı
\"\"\"

# Model Parametreleri
PARAMETER temperature 0.8
PARAMETER num_ctx 1024
"""

# Modelfile'ı kaydetme
with open(os.path.join(proje_dizini, 'Modelfile'), 'w') as f:
    f.write(modelfile_content)

print(f"Model dosyası başarıyla oluşturuldu: {os.path.join(proje_dizini, 'Modelfile')}")

# Modeli oluşturma
os.system(f"ollama create gelecek-senaryosu4 -f {os.path.join(proje_dizini, 'Modelfile')}")

print("Özel model başarıyla oluşturuldu!")

# FastAPI uygulaması
app = FastAPI()

# CORS yapılandırması
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Bunu güvenlik için özelleştirebilirsiniz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Öngörüleri alacak veri yapısı
class Ongoruler(BaseModel):
    ongoruler: str  # Kullanıcının girdiği öngörülerin metni

# Gelecek senaryosunu oluşturacak fonksiyon
def gelecek_senaryosu_olustur(ongoruler):
    try:
        response = ollama.chat(
            model='gelecek-senaryosu4',
            messages=[
                {
                    'role': 'user', 
                    'content': f"""Aşağıdaki öngörülerden 2050 yılına dair bir gelecek senaryosu yaz:
                    {ongoruler}
                    
                    Senaryoyu şu yapıda kur:
                    1. Başlık
                    2. Senaryo
                    """
                }
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

# POST endpointi: Senaryo oluşturma
@app.post("/create_scenario/")
async def create_scenario(ongoruler: Ongoruler):
    scenario_text = ongoruler.ongoruler.strip().replace("\n", " - ")  # Satır başlarına - ekle
    senaryo = gelecek_senaryosu_olustur(scenario_text)
    return {"scenario": senaryo}

# Uvicorn sunucusunu başlatma
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)