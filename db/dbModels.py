# API/db/dbModels.py
from mlapi.app import database, app, bcrypt
import datetime

class User(database.Model):
    ''' User Model for storing user related details

    Attributes
    ----------
    id: int
    email: str(255)
    password: str(255)
    uses: int
    is_admin: int

    Methods
    -------
    set_uses
    get_uses
    subtract_use
    '''
    __tablename__ = "users"

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    email = database.Column(database.String(255), unique=True, nullable=False)
    password = database.Column(database.String(255), nullable=False)
    uses = database.Column(database.Integer, nullable=False)
    is_admin = database.Column(database.Integer, nullable=True)

    def __init__(self, email, password, uses=100, is_admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.uses = uses #Default amount of uses 100
        self.is_admin = is_admin

    def __repr__(self):
        return '<User {}> {}, uses: {}'.format(self.email, "Admin" if self.is_admin else "", self.uses)
    
    def set_uses(self, uses):
        '''Sets uses.
        '''
        self.uses = uses
    
    def get_uses(self):
        '''Returns uses.
        '''
        return self.uses
    
    def subtract_use(self):
        '''Subtracts uses.
        '''
        if self.uses > 0:
            self.uses -= 1
        else:
            self.uses = 0
        database.session.commit()
        return self.uses

class BlacklistToken(database.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    token = database.Column(database.String(500), unique=True, nullable=False)
    blacklisted_on = database.Column(database.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

class Request(database.Model):
    '''Model for storing user requests.

    Attributes
    ----------
    request_type: str of max 6 chars
        GET, POST, OPTIONS etc..
    request_url: str of max 64 chars
    response: str of max 1024 chars
    user_id: int
        Foreign key from `users` table
    headers: str of max 1024 chars
    is_xhr: bool (int cast)
        1 if the request was triggered via a JavaScript XMLHttpRequest.
    data_type: char
        Type of data sent. I - image, T - text
    data: str of max 1024 chars
        Contains path to file on server or plain text.
    '''
    __tablename__ = 'requests'

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    request_type = database.Column(database.String(6), nullable=False)
    request_url = database.Column(database.String(64), nullable=False)
    response = database.Column(database.String(1024), unique=False, nullable=False)
    date = database.Column(database.DateTime, nullable=False)
    headers = database.Column(database.String(1024), nullable=False)
    is_xhr = database.Column(database.Integer)
    user_id = database.Column(database.Integer, database.ForeignKey('users.id'), nullable=True)

    data_type = database.Column(database.String(1), nullable=True)
    # Saves path to image or text data
    data = database.Column(database.String(1024), unique=False, nullable=True)

    def __init__(self, request_type, request_url, response, user_id, is_xhr, headers, data_type=False, data=False):
        self.request_type = request_type
        self.request_url = request_url
        self.user_id = user_id
        self.headers = headers
        self.response = response
        self.is_xhr = is_xhr
        self.date = datetime.datetime.now()
        self.data_type = data_type
        self.data = data
        
