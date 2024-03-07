from flask import Flask, render_template, request
import os, requests, logging
from displayUtils import visualize_insights

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

ANALYZER_SERVICE_URL = f"http://{os.getenv('ANALYZER_SERVICE')}"
SOURCES = ['API', 'CSV']

@app.route('/', methods=['POST'])
def post():
    if 'keywords' not in request.form or 'source' not in request.form:
        return "Missing keyword or source", 400
    
    keywords = request.form['keywords']
    source = request.form['source']

    if source not in SOURCES:
        logging.info('Invalid source')
        return "Invalid source", 400
    
    if keywords and all(char in ['.', ';', ':'] for char in keywords):
        logging.info('Invalid keywords')
        return "Keywords should contain valid characters", 400
    
    logging.info(f'Sending to Analyzer with {keywords} and {source}')
    response = requests.get(ANALYZER_SERVICE_URL, params={'keyword': keywords, 'source': source})

    logging.info(f'Recieved from analyzer. Starting to display insights')
    if response.status_code != 200:
        return "Error fetching insights", 500
    
    insights = response.json()
    
    analysis_key = insights[0]
    insights = insights[1]
    insights_html = visualize_insights(analysis_key, insights, keywords, source)
    
    return render_template('insights.html', insights=insights_html)

@app.route('/', methods=['GET'])
def get():
    return render_template('index.html')


if __name__ == '__main__':
    logging.info('Webapp service started.')
    app.run(host='0.0.0.0', port=1000)
