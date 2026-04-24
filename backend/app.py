#needed for github
from dotenv import load_dotenv
load_dotenv()

import os
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")



import os
print("RUNNING FROM:", os.path.abspath(__file__))

# Mariyah Marshall senior project
from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.message_routes import messages_bp
from routes.users_routes import users_bp

app = Flask(__name__)

# GLOBAL CORS — handles ALL routes and ALL blueprints
CORS(app, resources={r"/*": {"origins": "*"}})

#Register blueprints after enabling cors
app.register_blueprint(auth_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(users_bp)

@app.route("/test", methods=["GET", "OPTIONS"])
def test():
    return {"message": "CORS test"}

if __name__ == "__main__":
    app.run(debug=True)
