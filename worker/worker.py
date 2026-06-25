import os
import json
import pandas as pd
from dotenv import load_dotenv
from kafka import KafkaConsumer
from pymongo import MongoClient

# Pull configurations locally from the un-tracked .env file
load_dotenv()

def start_worker_daemon():
    # Read the connection URI securely from local environment runtime context
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    
    # Establish targets inside the ClearVue enterprise database
    db = mongo_client["clearvue_bi_system"]
    collection = db["operational_records"]

    consumer = KafkaConsumer(
        'excel-processing-tasks',
        bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    print("ClearVue background worker active. Listening for ingestion events...")
    
    for message in consumer:
        event = message.value
        file_path = event['storage_location']
        
        try:
            df = pd.read_excel(file_path)
            
            # String parsing for temporal variables to enforce clean document structure
            if 'Date' in df.columns:
                df['Date'] = df['Date'].astype(str)
            if 'TRANSACTION_DATE' in df.columns:
                df['TRANSACTION_DATE'] = df['TRANSACTION_DATE'].astype(str)
            
            records = df.to_dict(orient='records')
            
            if records:
                result = collection.insert_many(records)
                print(f"Successfully migrated {len(result.inserted_ids)} records to MongoDB Atlas.")
                
        except Exception as e:
            print(f"ETL operational pipeline failure: {str(e)}")

if __name__ == "__main__":
    start_worker_daemon()