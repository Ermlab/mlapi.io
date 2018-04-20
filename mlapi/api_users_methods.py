import logging
from flask import request
from flask_api import status, exceptions
from flask_jwt import jwt_required, current_identity

from mlapi.helpers import err_tmplt

def check_if_authorized(dbc):
    '''Checks whether the user is authorized to send admin request
    '''
    if current_identity and request:
        if dbc.is_admin(current_identity['user_id']):
            return True
        else:
            logging.warning("Not admin!")
    else:
        logging.warning("No identity or null request.")
    return False
    

def create_user(dbc, email, uses, is_admin):
    '''Creates new user in database

    Parameters
    ----------
    dbc: db.DbConnectionClass
        Active DB connection class 
    email: str
        Users email
    uses: int
        The amount of uses (POST request to API)
    is_admin: int, pseudo-bool (0 or 1)
        Whether the admin has admin rights

    Returns
    -------
    str
        JSON formatted response with login and password fields.
    '''
    if check_if_authorized(dbc):
        if not dbc.check_if_email_exists(email):
            password = dbc.create_user(email, uses, is_admin)
            return {
            "login" : email,
            "password" : password
        }, status.HTTP_201_CREATED
        else:
            logging.debug("Duplicated email given")
            return err_tmplt("This email is already registered.", status.HTTP_409_CONFLICT)
    else:
        return err_tmplt("You are not authorized to create users.", status.HTTP_403_FORBIDDEN)

def update_user(dbc,):
    '''TODO
    '''
    pass

def delete_user(id):
    '''TODO
    '''
    # if check_if_authorized(dbc):
    #     user_to_delete = User.query.filter_by(id=id)
    # else:
    #     return err_tmplt("You are not authorized to delete users.", status.HTTP_403_FORBIDDEN)
    pass
