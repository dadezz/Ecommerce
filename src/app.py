from flask import Flask
from extention import login_manager
from user import user_manager_bp
from product import product_page_bp
from search_and_filter import search_page_bp
from reviews import reviews_page_bp
from cart_and_history import cart_bp
"""
in app.py c'è il codice base per avviare l'applicazione
"""
def create_app():
    
    app = Flask(__name__,template_folder="../templates",static_folder='../static')
    app.config['SECRET_KEY'] = 'todo'
    login_manager.init_app(app)
    app.register_blueprint(user_manager_bp)
    app.register_blueprint(product_page_bp)
    app.register_blueprint(search_page_bp)
    app.register_blueprint(reviews_page_bp)
    app.register_blueprint(cart_bp)
    return app

if __name__ == "__main__":

    app = create_app()
    app.run(debug=True)
    
    