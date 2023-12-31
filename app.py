from flask import Flask, request, jsonify
from flask_cors import CORS
from joblib import load
from biodegradable import calculate_normalized_good_score_and_list_materials
from harmscore import calculate_normalized_harmfulness_score_and_list_materials

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        try:
            data = request.get_json(force=True)  # Explicitly set content type
            text_content = ''
            if data.get('title', '') != '':
                title = data.get('title', '')
                about = data.get('about', '')
                text_content = title + about
            else:
                text_content = data.get('description', '')

            clf = load('sentiment_logistic_regression_model.joblib')
            tfidf_vectorizer = load('sentiment_tfidf_vectorizer.joblib')

            sentence_tfidf = tfidf_vectorizer.transform([text_content])
            probabilities = clf.predict_proba(sentence_tfidf)
            sent_score = probabilities[0][1]
            bio_score, materials = calculate_normalized_good_score_and_list_materials(text_content)
            harm_score, chemicals = calculate_normalized_harmfulness_score_and_list_materials(text_content)
            env = sent_score * 2.5
            if env >= 1:
                env = 0.99
            safety = 2*bio_score - 3*harm_score
            safety = int(safety * 100)
            if safety <= 5:
                safety = 10
            elif safety <=35:
                safety = 40
            elif safety <=80:
                safety = 75
            else:
                safety = 90
            env = int(env * 100)
            return jsonify({'env_score': env, 'safety_score': safety})
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # Return the error message with 500 status code

    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
