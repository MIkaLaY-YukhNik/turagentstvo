from flask import Flask
from flask_babel import Babel
from .config import load_config
from .translations import get_translation, get_current_language


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    load_config(app)
    
    # Configure Babel for internationalization
    babel = Babel(app)
    app.config['LANGUAGES'] = {
        'ru': 'Русский',
        'en': 'English', 
        'es': 'Español'
    }
    app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    
    # Make translation functions available in templates
    @app.context_processor
    def inject_translations():
        return {
            't': lambda key: get_translation(key, get_current_language()),
            'current_lang': get_current_language
        }

    # Blueprints
    from .blueprints.public import public_bp
    from .blueprints.admin import admin_bp
    from .blueprints.auth import auth_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app

