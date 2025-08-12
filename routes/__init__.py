from .upload_routes import upload_bp
from .chat_routes import chat_bp
from .chat_titles_routes import chat_titles_bp
from .get_chat_routes import get_chat_bp

def register_blueprints(app):
    app.register_blueprint(upload_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(chat_titles_bp)
    app.register_blueprint(get_chat_bp)