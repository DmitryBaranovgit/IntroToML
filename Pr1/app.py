from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load('model.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form.to_dict()
    df = pd.DataFrame([data])

    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass
    
    prediction = model.predict(df)[0]
    return jsonify({'prediction': '>50K' if prediction == 1 else '<=50K'})

if __name__ == '__main__':
    app.run(debug=True)