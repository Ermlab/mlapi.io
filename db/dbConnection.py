import logging
import uuid

database=""

DEBUG_T = "[DbConnection] "


class DbConnectionClass:
    '''Class containing methods for DB management

    Methods
    -------
    verify
    identity
    is_admin
    check_if_email_exists
    create_user
    authenticate
    get_users_available_uses
    reduce_uses
    save_request
    '''
    def __init__(self, dbi, config):
        global database
        database = dbi
        self.__app_config = config
        self.__db_URI = config["SQLALCHEMY_DATABASE_URI"]
        
    
    def verify(self, email, password):
        '''Verifies the credentials.

        Parameters
        ----------
        email: str
            Users email.
        password: str
            Users password.

        Returns
        -------
        db.dbModels.User or None
        '''
        if not (email and password):
            return False
        return self.authenticate(email, password)

    # def close(self):
    #     self.__connection.close()
    def identity(self, payload):
        '''Returns an object with user_id field.

        Parameters
        ----------
        payload: list

        Returns
        -------
        dict
        '''
        user_id = payload['identity']
        return {"user_id": user_id}

    def is_admin(self, identity):
        '''Returns 1 if the user with given id has administrative rights.
        
        Parameters
        ----------
        identity: int
            Users ID.

        Returns
        -------
        bool
        '''
        user = User.query.filter_by(id=identity).first()
        isa = bool(user.is_admin)
        return isa

    def check_if_email_exists(self, email):
        '''Returns true if email already exists in DB.

        Parameters
        ----------
        email: str
            Email to check.

        Returns
        -------
        bool
        '''
        result= User.query.filter_by(email=email).first()

        if result:
            return True
        else:
            return False

    def create_user(self, email, uses, is_admin):
        '''Creates a new user.

        Parameters
        ----------
        email: str
            Users email.
        uses: int
            Users uses.
        is_admin: int
            Bool cast. 1 if the user has to be admin.
        '''
        password = str(uuid.uuid4()).replace("-","")
        user = User(email = email, password = password, uses = uses, is_admin = is_admin)
        database.session.add(user)
        database.session.commit()

        return password

    def authenticate(self, email, password):
        '''Returns User object if proper credentials. Otherwise returns None.

        Parameters
        ----------
        email: str
            Users email.
        password: str
            Users password.
        '''
        result= User.query.filter_by(email=email).first()
        if bcrypt.check_password_hash(result.password, password):
            return result
        else:
            return None

    def get_users_available_uses(self, id):
        '''Returns amount of available POST requests for given user's id.
        
        Parameters
        ----------
        id: int
            Users ID.

        Returns
        -------
        int
        '''
        result = User.query.filter_by(id=id).first()
        return result.get_uses()
    
    def reduce_uses(self, id):
        '''Reduces available user's uses by 1.

        Parameters
        ----------
        id: int
            Users ID.

        Returns
        -------
        int
        '''
        result = User.query.filter_by(id=id).first()
        return result.subtract_use()

    def save_request(self, request_type, request_url, response, user_id, headers, is_xhr, data_type, data):
        '''Saves request details in DB.

        Parameters
        ----------
        request_type: str
            Request type (POST, PUT etc.) 
        request_url: str
            Requests URL e.g http://localhost:8000/v2/test1
        response: str
            Models response to the request
        user_id: int
            ID of user that sent request
        headers: str
            Headers sent with the request
        is_xhr: bool
            Was the request a XHR request.
        data_type: char
            Type of data sent 'I' - image etc.
        data: str
            Path to saved image or text.

        '''
        request_url = (request_url[:64] + '..') if len(request_url) > 64 else request_url
        response = (response[:1024] + '..') if len(response) > 1024 else response
        headers = (headers[:1024] + '..') if len(headers) > 1024 else headers
        data = (data[:1024] + '..') if len(data) > 1024 else data

        request_entry = Request(
            request_type=request_type, 
            request_url=request_url, 
            response=response, 
            user_id=user_id, 
            headers=headers, 
            is_xhr=is_xhr, 
            data_type=data_type, 
            data=data)
        database.session.add(request_entry)
        database.session.commit()

from mlapi.app import bcrypt
from db.dbModels import User
from db.dbModels import Request