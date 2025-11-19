# app/__init__.py

from flask import Flask
from .config import Config
from .services.s3_service import S3Service
from .exceptions import register_error_handlers

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize S3 Service and attach to app context
    s3_service = S3Service(config_class)
    app.s3_service = s3_service
    
    # Register error handlers
    register_error_handlers(app)

    # Import and register blueprints/routes
    from .api import bp as api_bp
    app.register_blueprint(api_bp)

    return app

# Runner to execute the application
if __name__ == '__main__':
    # Set this environment variable if not using a separate run command:
    # export LOCALSTACK_ENDPOINT_URL=http://localhost:4566
    
    app = create_app()
    app.run(host="0.0.0.0", port=5000)