from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Header
from fastapi.responses import FileResponse
import os
import uuid
from model.predict import BasketballActionClassifier
import mimetypes
from database import connection, mysql
from fastapi.staticfiles import StaticFiles
from encode import decode
import re

app = FastAPI(docs_url=None, redoc_url=None)

predictor = BasketballActionClassifier()

@app.get("/api-basketai")
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

async def get_bearer_token(authorization: str = Header(None)) -> str:
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    
    # Check if the header is of Bearer type
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    
    # Extract the token
    token = authorization[len("Bearer "):]

    return token

# Dummy function to validate token, replace with your logic
def validate_token(token: str) -> bool:
    # Implement your token validation logic
    # For example, check if the token is in a list of valid tokens
    valid_tokens = ["valid_token_example"]
    return token in valid_tokens


@app.post("/api-basketai/predict")
async def upload_file(
        video: UploadFile = File(),
        token: str = Depends(get_bearer_token)
    ):
    
    data = decode(token)

    if data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', data)
    
    username, datetime_str = None, None
    if match:
        # Get the start index of the datetime in the string
        datetime_start_index = match.start()
    
         # Slice the string
        username = data[:datetime_start_index]
        datetime_str = data[datetime_start_index:]
    
        print(f"Username: {username}")
        print(f"Datetime: {datetime_str}")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
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
    file_path = os.path.join('./videos', file_name)
    with open(file_path, "wb") as f:
        f.write(await video.read())

    # Panggil fungsi prediksi
    result, confidence = predictor.predict(file_path)
    
    insert_query = '''
        INSERT INTO activity (username, path, result, confidence, created_at)
        VALUES (%s, %s, %s, %s, %s)
    '''
    
    data = (username, file_name, result, float(confidence), datetime_str)

    connection.execute(insert_query, data)

    mysql.commit()

    print(confidence)
    return {
        'result': result,
        'confidence': confidence,
        'file_name': file_name
    }

@app.get("/api-basketai/history")
async def get_history(token: str = Depends(get_bearer_token)):
    # Decode the token to get data
    data = decode(token)

    if data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Extract username and datetime from the decoded token
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', data)
    
    if not match:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    datetime_start_index = match.start()
    username = data[:datetime_start_index]
    datetime_str = data[datetime_start_index:]

    # SQL query to get the history based on username
    sql = "SELECT * FROM activity WHERE username = %s ORDER BY id DESC"
    
    # Execute the query with the parameter
    connection.execute(sql, (username,))
    results = connection.fetchall()

    # Fetch column names from the cursor
    column_names = [column[0] for column in connection.description]

    # Convert each row into a dictionary
    history = []
    for row in results:
        row_dict = dict(zip(column_names, row))
        history.append(row_dict)

    return history

@app.get("/api-basketai/{file_name}")
async def get_result(file_name: str):
    file_path = f"./videos/{file_name}"
    return FileResponse(file_path)