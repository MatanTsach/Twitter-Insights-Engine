from redis import Redis
import json, os, logging
from flask import Flask, request, Response, stream_with_context
from ingestor import ingest_api, ingest_csv

app = Flask(__name__)
redis_client =Redis(os.getenv('REDIS_SERVICE'), decode_responses=True)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/', methods=['GET'])
def get():
    if 'keyword' not in request.args or 'source' not in request.args:
        return "Missing keyword or source", 400
                        
    keyword = request.args.get('keyword')
    source = request.args.get('source')
    logging.info(f'Recieved ingestion request for {keyword} from {source}')

    redis_key = f"{keyword}:{source}"
    if source == "API":
        redis_client.delete(redis_key)
        ingest_api(keyword, redis_key, redis_client)
    elif source == "CSV" and not redis_client.exists(redis_key):
        ingest_csv(keyword, redis_key, redis_client)

    logging.info('Ingestion complete.')
    return "Ingested Succesfully.", 200

if __name__ == '__main__':
    logging.info(f"Ingestor service started.")
    app.run(host='0.0.0.0', port=3000)