import os
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='views')

    # Chave de segurança para a sessão
    app.secret_key = os.environ.get('SECRET_KEY', 'Tropa_Xavantes_Kairos_513')

    from app.controllers.auth_controller import auth_bp
    from app.controllers.home_controller import home_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)

    return app