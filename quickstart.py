# DO THE FIRST 2 STEPS OF THIS SETUP for this to work

# https://developers.google.com/drive/v3/web/quickstart/python

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def fileNametoID(BigfileList, fileName):

    for fileList in BigfileList:
        for item in fileList:
            if(item['name'] == fileName and item['trashed'] == False):
                return item['id']
    return "nofile"

def update_file(service,file_path, fileId):
    media_body = MediaFileUpload(file_path, mimetype="text/html")
    results = service.files().update(fileId=fileId, media_body=media_body).execute()
    return results


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    results = service.files().list(
        pageSize=1000,fields="nextPageToken, files(id, name, trashed)").execute()
    itemlist = []    
    items= results.get('files', [])
    itemlist.append(items)
    token = results.get('nextPageToken', None)
    while(token != None) :
        results = service.files().list(
            pageSize=1000,pageToken = token,fields="nextPageToken, files(id, name, trashed)").execute()
        itemlist.append(results.get('files', []))
        token = results.get('nextPageToken', None)
    if itemlist.count == 0:
        print('No files found.')
    else:
        print('Files:')
        for iteml in itemlist:
            for item in iteml:
                 print('name:{0}, id: {1}, trashed: {2} '.format(item['name'], item['id'], item['trashed']))
    # assuming unique file names, updating the checker file that was created by the android app
    myID =fileNametoID(itemlist, "123test")
    #update the file on Drive with contents of a local file
    if(myID != "nofile"):         
        update_file(service,"Deauth.txt",myID)
        print("update should have succeeded")
        
    else:
        print("No file with that name was found")

if __name__ == '__main__':
    main()