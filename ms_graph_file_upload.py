import ms_graph_file_upload_config
import requests
import json
import os
import logging
import sys
import time

logging.basicConfig(format='%(asctime)s %(process)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG, stream=sys.stdout)

# Decorator to handle the response, including refreshing the token and retrying the function (if needed).
def handle_response(request_type):
    def inner_decorator(func):
        def wrapper_handle_response(*args, **kwargs):
            logging.debug("wrapper_handle_response called. "+func.__name__+" with "+str(args)+" and "+str(kwargs))
            try:
                r = func(*args, **kwargs)
            except Exception:
                logging.exception("An exception occurred while running "+func.__name__+" with "+str(args)+" and "+str(kwargs)+" so we will wait 60 seconds and try again.")
                time.sleep(60)
                return wrapper_handle_response(*args, **kwargs)
            if (r.status_code - 400 >= 0 and (request_type=="token" or request_type=="upload" and r.status_code != 401)):
                logging.error(str(r.status_code)+" response when calling "+func.__name__+" with "+str(args)+" and "+str(kwargs))
                logging.error(r.text)
                logging.error(r.headers)
                if(r.status_code == 400):
                    r.raise_for_status() # Stop the program if the request is bad
                else:
                    logging.error("We will wait 60 seconds and try again.")
                    time.sleep(60)
                    return wrapper_handle_response(*args, **kwargs)
            elif (r.status_code == 401):
                logging.debug("401 response when calling "+func.__name__+" with "+str(args)+" and "+str(kwargs)+", we will get refresh token and try again.")
                logging.debug(r.text)
                logging.debug(r.headers)
                refresh_token()
                return func(*args, **kwargs)
            else:
                logging.debug("Good response when calling " +func.__name__+" with "+str(args)+" and "+str(kwargs))
                return r

        return wrapper_handle_response
    return inner_decorator

# Make a request to get a new access token
@handle_response("token")
def get_new_access_token():

    f = open("authcode")
    code = f.read()
    f.close()

    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    data = {"client_id": ms_graph_file_upload_config.config["client_id"],
            "scope": ms_graph_file_upload_config.config["scope"],
            "code": code,
            "redirect_uri": ms_graph_file_upload_config.config["redirect_uri"],
            "grant_type": ms_graph_file_upload_config.config["grant_type"],
            "client_secret": ms_graph_file_upload_config.config["secret"]
            }
    url = ms_graph_file_upload_config.config["authority"]+"/oauth2/v2.0/token"
    logging.debug("attempting to get an access token")
    r = requests.post(url, data=data, headers=headers)
    return r

# Get the access token, returning the one saved to disk (if exists), or getting a new one
def get_access_token():
    if(os.path.exists("access_token")):
        logging.debug("access code exists")
        f = open("access_token","r")
        access_code = f.read()
        f.close()
        logging.debug('returning access_code from file')
        return json.loads(access_code)

    r = get_new_access_token()
    f = open("access_token","w")
    f.write(r.text)
    f.close()
    return json.loads(r.text)

# Make a request to refresh a token.
@handle_response("token")
def get_refresh_token():
    f = open("access_token","r")
    access_code = json.loads(f.read())
    f.close()

    f = open("authcode")
    code = f.read()
    f.close()
    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    data = {"client_id": ms_graph_file_upload_config.config["client_id"],
        "scope": ms_graph_file_upload_config.config["scope"],
        "redirect_uri": ms_graph_file_upload_config.config["redirect_uri"],
        "grant_type": "refresh_token",
        "client_secret": ms_graph_file_upload_config.config["secret"],
        "refresh_token": access_code["refresh_token"]
        }
    url = ms_graph_file_upload_config.config["authority"]+"/oauth2/v2.0/token"

    r = requests.post(url, data=data, headers=headers)
    return r

# Get the refreshed token
def refresh_token():
    token = get_refresh_token().text
    f = open("access_token","w")
    f.write(token)
    f.close()
    return json.loads(token)

# Make the request to create an upload session
@handle_response("upload")
def post_createUploadSession(filename):
    url = ms_graph_file_upload_config.config["endpoint"] + \
            "drives/"+ms_graph_file_upload_config.config["drive_id"] + \
            "/root:"+ms_graph_file_upload_config.config["folder"]+ \
            "/"+filename+":/createUploadSession"

    logging.debug("Creating upload session at "+url)
    access_token = get_access_token()
    headers = { "Authorization": "Bearer "+access_token["access_token"] }
    r = requests.post(url, headers=headers)
    return r

# Create an upload session
def create_upload_session(filename):
    return json.loads(post_createUploadSession(filename).text)

# Upload large file
@handle_response("upload")
def upload_file_with_session(upload_session, filename):
    access_token = get_access_token()
    url = upload_session["uploadUrl"]
    logging.info("uploading "+filename+" to "+url)
    file_stats = os.stat(filename)
    headers = {"Authorization": "Bearer "+access_token["access_token"],
            "Content-Range": "bytes 0-"+str(file_stats.st_size-1)+"/"+str(file_stats.st_size),
            "Content-Length": str(file_stats.st_size)
            }
    f = open(filename,'rb')
    file_data = f.read()
    f.close()
    r = requests.put(url, headers=headers, data=file_data)
    return r

# Create upload session and upload the file
def upload_file(filename):
    upload_session = create_upload_session(filename)
    upload_file_with_session(upload_session, filename)

upload_file('file_to_upload.txt')


