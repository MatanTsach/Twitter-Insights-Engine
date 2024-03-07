import requests, os, logging, json, random
from flask import Flask, request
from analyzer import analyze
from redis import Redis

INGESTOR_SERVICE_URL = f"http://{os.getenv('INGESTOR_SERVICE')}"

app = Flask(__name__)
redis_client =Redis(os.getenv('REDIS_SERVICE'), decode_responses=True)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_data_from_redis(key):
    # Fetch and deserialize data from Redis
    return [json.loads(row) for row in redis_client.lrange(key, 0, -1)]

def generate_analysis_key():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=25))

@app.route('/', methods=['GET'])
def get():
    if 'keyword' not in request.args or 'source' not in request.args:
        return "Missing keyword or source", 400
                        
    keyword = request.args.get('keyword')
    source = request.args.get('source')
    
    logging.info('Sending request to ingestor.')
    response = requests.get(INGESTOR_SERVICE_URL, params={'keyword': keyword, 'source': source})
    logging.info(f'Recieved response from ingestor')
    
    if response.status_code != 200:
        logging.warning('Warning: data ingestion failed')
        return "Data ingestion failed", 500
    
    key = f"{keyword}:{source}"
    data = fetch_data_from_redis(key)
    if not data:
        return "No Data found for keyword", 404

    logging.info(f'Beginning analysis of {keyword} from {source}')

    # Generate analysis key, will be saved in a folder in the mounted pvc with the same name
    analysis_key = generate_analysis_key()
    insights = analyze(keyword, data, analysis_key)
    logging.info(insights)
    logging.info('Analysis complete. Returning insights.')

    return [analysis_key, insights], 200
    

if __name__ == '__main__':
    logging.info('Analyzer service started.')
    app.run(host='0.0.0.0', port=2000)
