import os
from flask import Flask
from app.models import db

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_12345')
    
    # Database path
    db_path = os.path.join(app.root_path, 'creditcard.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register Blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
    return app
