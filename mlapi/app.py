import json
# import sqlite3
import os
import logging
import coloredlogs
coloredlogs.install(level='DEBUG', format='%(levelname)s%(asctime)s:%(message)s',)

from flask import request, url_for, Response, jsonify, g, redirect
from flask_api import FlaskAPI, status, exceptions
from flask_api.decorators import set_parsers
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
# from mlapi.modelRouter import ModelRouterClass

from mlapi.api_users_methods import create_user, delete_user, update_user
from mlapi.helpers import err_tmplt

from flask_api.parsers import JSONParser, URLEncodedParser, MultiPartParser
from mlapi.parsers.imageParser import JpegImageParser, PngImageParser

# from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt
from .images import ImageStorage
from models.modelsHolder import ModelsHolderClass
from flask_sqlalchemy import SQLAlchemy

from .shellColors import ShellColors

bcrypt = ""
database = ""
app = ""
jwt = ""
MODELS_DIR = "./models/computed/"
white_list = [
    'http://localhost:3000', 'http://localhost:8000',
    'https://api.mlapi.io', 'https://demo.mlapi.io']

if os.popen('stty size', 'r').read():
    rows, columns = os.popen('stty size', 'r').read().split()
    columns = int(columns)
    print('\n' + columns * "=")
    print(((columns-len(__name__))//2) * "=" + ShellColors.HEADER + __name__ + ShellColors.ENDC + ((columns -1 - len(__name__))//2 + 1) * "=")
    print(columns * "=" + '\n')
else:
    print("======MLAPI.IO=======")

def reduce_uses(fn):
    '''A decorator function that invokes the DB uses-reducing function.
    '''
    def W1(*args, **kwargs):
        errors = []
        if current_identity and request:
            if dbc.get_users_available_uses(current_identity['user_id']) == 0:
                errors.append("No token uses left for this user")
            else:
                dbc.reduce_uses(current_identity['user_id'])
        return fn(errors=errors, *args,**kwargs)
    W1.__name__ = fn.__name__
    return W1

def save_request(response, data_type=None, data=None):
    '''Function invoking request saving in database
    '''
    try:
        dbc.save_request(
                    request_type=request.method,
                    request_url=request.url,
                    response = response,
                    user_id = current_identity['user_id'] if current_identity else 0,
                    is_xhr = request.is_xhr,
                    headers = str(request.headers),
                    data_type = data_type,
                    data = data)
    except:
        logging.warning("There was an error while saving request data to DB. {}".format(request))

def errors_handler(errors=None):
    '''Wrapper for logging errors
    '''
    if errors:
        for e in errors:
            logging.error(e)
    return errors


def create_app(image_storage):
    '''Function returning Flask app instance
    '''
    global bcrypt, database, jwt, app, dbc
    
    app = FlaskAPI(__name__)
    CORS(app, origins=white_list)

    models_holder_instance = ModelsHolderClass(MODELS_DIR)
    app_settings = os.getenv('APP_SETTINGS','db.config.DevelopmentConfig')
    app.config.from_object(app_settings)
    logging.info("Using {} settings.".format(app_settings))

    bcrypt = Bcrypt(app)
    try:
        database = SQLAlchemy(app)
    except Exception:
        logging.critical("Couldn't connect to DB!")

    from db.dbConnection import DbConnectionClass
    dbc = DbConnectionClass(database, app.config)
    jwt = JWT(app, dbc.authenticate, dbc.identity)


    @app.route('/')
    def slash():
        return redirect(url_for('root'))

    @app.route('/v2/', methods=['GET'])
    def root():
        '''Function responding to request to "/v2/" route.
        Returns a list of possible routes.
        '''
        text = {
            'available_routes': [ 
                "api.mlapi.io/v2/token - Check current token balance status [POST]",
                "api.mlapi.io/v2/test1 - Car recognition NN[GET, POST]",
                ]
        }
        return text
        
    @app.route('/v2/token', methods=['GET'])    
    @jwt_required()
    def token():
        '''Retrieve description of route or amount of uses left on token
        '''
        return {
            "uses_left": str(dbc.get_users_available_uses(current_identity['user_id']))
        }
    
    @app.route('/v2/user', methods=['POST', 'PATCH', 'DELETE'])
    @set_parsers(JSONParser)
    @jwt_required()
    def user():
        '''Manage users.
        '''
        #################################
        #### METHODS FOR ADMIN USERS ONLY

        if request.method == 'POST':
            req = request.data
            logging.debug(req)
            uses = req['uses'] if 'uses' in req else 100
            isa = req['is_admin'] if "is_admin" in req else False
            if 'email' not in req:
                return {
                    'error' : "No email given"
                }, status.HTTP_400_BAD_REQUEST

            return create_user(dbc, req['email'], uses, isa)

        elif request.method == 'DELETE':
            id = request.user_id
            return delete_user(id)
        #### METHODS FOR ADMIN USERS ONLY
        #################################

        elif request.method == 'GET':
            pass
        elif request.method == 'PUT':
            pass
    
    ## Needed for unathorized pre-requests
    @app.route('/v2/test1', methods=['OPTIONS'])
    def test1_opt():
        return ""

    @app.route('/v2/test1', methods=['GET', 'POST'])
    @jwt_required()
    @set_parsers(JSONParser, JpegImageParser, PngImageParser, MultiPartParser)
    @reduce_uses  
    def test1(errors=None):
        '''Responds with predictions on the sent image on POST. Returns description on GET request.
        Accepted formats: image/jpeg, image/png, application/json with an image in Base64 format.
        '''
        if errors:
            return {"result":errors_handler(errors)}
        model_name = 'test1'
        logging.debug("REQUEST: {}".format(repr(request)))
        if request.method == 'GET':
            return {
                "description" : "Make an authenticated POST request for predicting the image. POST binary file with proper header or { 'image' : 'BASE64 image' }",
                "accepted_content_type" : [
                    "image/jpeg",
                    "image/png",
                    "application/json"
                ]
            }
        elif request.method == 'POST':
            # logging.debug("Got files from client: >>> {} <<<".format(request.files))
            if request.files:
                val = request.files['file']
                path = image_storage.save(val, request.headers['Content-Type'])
                response = {
                    "result" : models_holder_instance.sendRequest(model_name, path)
                } 
                save_request(
                    response = str(response['result']), 
                    data_type = "I",
                    data = path)

                return response
            elif request.data:
                path = image_storage.save(request.data, request.headers['Content-Type'])
                response = {
                    "result" : models_holder_instance.sendRequest(model_name, path)
                } 
                save_request(
                    response = str(response['result']), 
                    data_type = "I",
                    data = path)

                return response
            else:
                return {
                "result":"You provided no data"
            }

    return app, bcrypt, database, image_storage, jwt


def get_app():
    image_storage = ImageStorage(storage_path = "./images/")
    return create_app(image_storage)

if __name__ == "mlapi.app":
    
    app, bcrypt, database, image_storage, jwt = application, bcrypt, database, image_storage, jwt = get_app()
