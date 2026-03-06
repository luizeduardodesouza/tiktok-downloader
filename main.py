from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# Permite acesso de qualquer lugar (necessário para o n8n)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/download")
async def download_video(url: str):
    """
    Recebe URL do TikTok/Instagram e retorna link do áudio
    """
    try:
        # Configuração do yt-dlp para extrair áudio
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrai informações sem baixar o arquivo
            info = ydl.extract_info(url, download=False)
            
            # Pega a URL do áudio/vídeo
            audio_url = info.get('url')
            
            if not audio_url:
                # Se não achar URL direta, pega do primeiro formato
                formats = info.get('formats', [])
                if formats:
                    audio_url = formats[0].get('url')
            
            return {
                "success": True,
                "url": audio_url,
                "title": info.get('title'),
                "duration": info.get('duration'),
                "platform": info.get('extractor', 'unknown')
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    """Página inicial para teste"""
    return {
        "status": "ok",
        "message": "TikTok/Instagram Downloader API",
        "endpoints": {
            "download": "POST /download?url=VIDEO_URL"
        }
    }

@app.get("/health")
async def health():
    """Verificação de saúde do serviço"""
    return {"status": "healthy"}
