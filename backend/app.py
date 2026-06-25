import os
import json
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
from kafka import KafkaProducer

# Pull configurations locally from the un-tracked .env file
load_dotenv()

app = FastAPI(title="ClearVue Ingestion Web Server")

try:
    producer = KafkaProducer(
        bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except Exception as e:
    print(f"Kafka message broker connection offline: {str(e)}")
    producer = None

@app.post("/upload-excel/")
async def upload_excel_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid extension format.")
    
    file_id = f"CV-{uuid.uuid4().hex[:8].upper()}"
    upload_dir = os.getenv("UPLOAD_DIR", "./storage")
    os.makedirs(upload_dir, exist_ok=True)
    
    saved_file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    
    try:
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File system failure: {str(e)}")
        
    if producer:
        event_payload = {
            "event_type": "FILE_UPLOADED",
            "file_id": file_id,
            "storage_location": saved_file_path,
            "original_name": file.filename
        }
        producer.send('excel-processing-tasks', value=event_payload)
        producer.flush()

    return {
        "status": "Success",
        "file_id": file_id,
        "message": "ClearVue operational file queued successfully."
    }