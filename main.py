from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import uuid
from model.predict import BasketballActionClassifier
import mimetypes

app = FastAPI(docs_url=None, redoc_url=None)

predictor = BasketballActionClassifier()

@app.get("/")
def read_root():
    return {"Hello": "World"}

def get_file_extension(filename) -> str:
    _, extension = os.path.splitext(filename)
    return extension

# Fungsi untuk memeriksa tipe MIME video
def is_valid_video_mime(mime_type: str) -> bool:
    valid_video_mimes = [
        'video/mp4', 'video/x-matroska', 'video/x-msvideo', 'video/x-ms-wmv',
        'video/quicktime', 'video/x-flv', 'video/webm'
    ]
    return mime_type in valid_video_mimes

@app.post("/predict")
async def upload_file(video: UploadFile = File()):
    # Dapatkan ekstensi dan tipe MIME file
    extension = get_file_extension(video.filename)
    mime_type, _ = mimetypes.guess_type(video.filename)
    
    # Validasi ekstensi file
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    if extension not in valid_extensions:
        raise HTTPException(status_code=400, detail="Invalid file extension. Supported extensions are: .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm")
    
    # Validasi tipe MIME
    if not mime_type or not is_valid_video_mime(mime_type):
        raise HTTPException(status_code=400, detail="Invalid file type. Supported video MIME types are: video/mp4, video/x-matroska, video/x-msvideo, video/x-ms-wmv, video/quicktime, video/x-flv, video/webm")

    # Simpan file
    file_name = f"{str(uuid.uuid4())}{extension}"
    file_path = os.path.join('./tmp', file_name)
    with open(file_path, "wb") as f:
        f.write(await video.read())

    # Panggil fungsi prediksi
    results = predictor.predict(file_path)
    
    # Hapus file setelah prediksi
    os.remove(file_path)
    
    return {
        'result': results
    }
