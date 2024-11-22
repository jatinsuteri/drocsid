from flask import Flask
from flask_bcrypt import Bcrypt
from .socket import socketio
from .extension import db, login_manager,migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
app.config['SECRET_KEY'] = 'jatinsuteri'
db.init_app(app)
migrate.init_app(app,db)
bcrypt = Bcrypt(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)
socketio.init_app(app)


from drocsid import routes