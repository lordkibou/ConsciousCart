from flask import Flask, request, jsonify
from flask_cors import CORS
from joblib import load
from biodegradable import calculate_normalized_good_score_and_list_materials
from harmscore import calculate_normalized_harmfulness_score_and_list_materials
from brandscore import brand_score

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        clf = load('sentiment_logistic_regression_model.joblib') 
        tfidf_vectorizer = load('sentiment_tfidf_vectorizer.joblib')
        
        data = request.json
        title = data.get('title', '')
        about = data.get('about', '')

        sentence_tfidf = tfidf_vectorizer.transform([title + about])
        probabilities = clf.predict_proba(sentence_tfidf)
        sent_score = str(probabilities[0][1])
        bio_score, materials = calculate_normalized_good_score_and_list_materials(title + about)
        harm_score, chemicals = calculate_normalized_harmfulness_score_and_list_materials(title + about)
        return jsonify({'sent_score': sent_score, 'bio_score': bio_score, 'materials': list(materials), 'harm_score': harm_score, 'chemicals': list(chemicals)})
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)