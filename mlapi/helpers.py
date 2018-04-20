def err_tmplt(msg, code):
    '''Returns tuple of object with 'error' parameter and http status code.
    '''
    return {
        "error" : msg
    }, code