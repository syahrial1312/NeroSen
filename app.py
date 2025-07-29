from flask import Flask,request,jsonify, render_template
import pickle
import numpy as np
import firebase_admin
from firebase_admin import db, credentials

suggestion={
    'Normal':'Tetap jaga pola hidup sehat dengan istirahat cukup, konsumsi makanan bergizi, dan berolahraga secara teratur. Luangkan waktu untuk aktivitas yang menyenangkan, seperti hobi atau berkumpul dengan orang terdekat. Pertahankan gaya hidup yang seimbang dan jangan abaikan tanda-tanda awal stres. Lakukan teknik relaksasi seperti meditasi atau pernapasan dalam secara rutin untuk menjaga kondisi tetap optimal.',
    'Sedang':'Identifikasi sumber stres dan coba atasi secara bertahap. Berkomunikasilah dengan orang yang dipercaya, seperti teman, keluarga, atau konselor, untuk mendapatkan dukungan. Kurangi konsumsi kafein, rokok, atau hal lain yang dapat meningkatkan ketegangan. Luangkan waktu lebih untuk relaksasi dan perawatan diri. Jangan ragu untuk mencari bantuan profesional jika stres mulai memengaruhi aktivitas harian atau kualitas hidup.',
    'Tinggi':'Segera cari bantuan profesional, seperti psikolog atau dokter, untuk mendapatkan penanganan yang sesuai. Fokus pada pemulihan diri dengan menghentikan aktivitas yang terlalu membebani. Prioritaskan istirahat dan perbaikan pola hidup. Jangan abaikan tingkat stres tinggi karena dapat berdampak serius pada kesehatan fisik dan mental. Ikuti panduan dari tenaga medis atau profesional untuk mengelola stres dengan tepat. Jangan ragu untuk berbagi perasaan dan meminta dukungan dari orang-orang terdekat.'
}

#autentikasi kepada database
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL" : "https://iot-x-ml-default-rtdb.asia-southeast1.firebasedatabase.app/"})

ref=db.reference("/")
LABEL= ["Tinggi", "Sedang", "Normal"]
ref.get()
data=db.reference("/Sensor/heart_rate/now").get()

#Create FLask App
app=Flask(__name__,static_url_path='/static')

# Load the model
with open("model.pkl","rb") as model_file:
    model = pickle.load(model_file)

# Global variables for storing session data
session_data = {
    "heart_rate": [],
    "body_temperature": []
}

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/prediksi")
def prediksi():
    data=db.reference("/Sensor/heart_rate/now").get()
    hr_features=[float(data)]
    new_data=[hr_features]
    prediction=model.predict(new_data)              
    output=LABEL[prediction[0]]
    return render_template("prediksi.html",prediction_text="Kondisi {}".format(output), heart_rate=data)

@app.route('/start_session', methods=["POST"])
def start_session():
    """Clears session data to start a new recording."""
    session_data["heart_rate"].clear()
    session_data["body_temperature"].clear()
    return jsonify({"message": "Session started"}), 200

@app.route('/get_realtime_data', methods=["GET"])
def get_realtime_data():
    try:
        # Fetch data from Firebase
        heart_rate = db.reference("/Sensor/heart_rate/now").get() or "No Data"
        body_temperature = db.reference("/Sensor/body_temperature/now").get() or "No Data"

        # Add data to session if it's valid
        if heart_rate != "No Data" and body_temperature != "No Data":
            session_data["heart_rate"].append(float(heart_rate))
            session_data["body_temperature"].append(float(body_temperature))
            print(session_data["body_temperature"])
            print(session_data["heart_rate"])

        return jsonify({
            "heart_rate": heart_rate,
            "body_temperature": body_temperature
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop_session', methods=["POST"])
def stop_session():
    """Calculate averages and stop session."""
    try:
        if not session_data["heart_rate"] or not session_data["body_temperature"]:
            return jsonify({"error": "Tidak ada data"}), 400

        avg_heart_rate = sum(session_data["heart_rate"]) / len(session_data["heart_rate"])
        avg_body_temperature = sum(session_data["body_temperature"]) / len(session_data["body_temperature"])
        print(avg_body_temperature)
        print(avg_heart_rate)
        
        if avg_heart_rate != "No Data":
            hr_features = [[float(avg_heart_rate)]]
            prediction = model.predict(hr_features)
            prediction_text = LABEL[prediction[0]]
        else:
            prediction_text = "Unknown"
        
        # db.reference("/Sensor/heart_rate").set({"now": 80 })
        LED=prediction[0]
        db.reference("/").update({"Hasil":int(LED)})
        
        session_data["heart_rate"].clear()
        session_data["body_temperature"].clear()
        
        return jsonify({
            "avg_heart_rate": round(avg_heart_rate, 0),
            "avg_body_temperature": round(avg_body_temperature, 0),
            "predict": (prediction_text),
            "suggest": (suggestion[prediction_text])
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)})

    
if __name__ == '__main__':
    app.run(port=5000,debug=True)
