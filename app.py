from flask import Flask
from flask_cors import CORS
from components.config import FRONTEND_URL
from services.firebase import init_firebase
from routes import register_blueprints

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": FRONTEND_URL}}, supports_credentials=True)

# Initialize Firebase
init_firebase()

# Register all blueprints
register_blueprints(app)

@app.route("/")
def index():
    return "Flask app is running."

if __name__ == "__main__":
    app.run(debug=True)
