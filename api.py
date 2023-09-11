import os
import mimetypes
import concurrent.futures
from pprint import pprint
from handler import Create_Service
from googleapiclient.http import MediaFileUpload


CRENDS_FILE = "credentials.json"

API_NAME = "drive"

API_VERSION = "v3"

SCOPES = ["https://www.googleapis.com/auth/drive"]

root_id = "1GyWgVKNpDB6Pjm6a4HNC5PTmh4byS_IR"


# Convert bytes to mega bytes


def convert_bytes_to_megabytes(data_size):
    return data_size / (1024**2)


def convert_bytes_to_gigabytes(data_size):
    return data_size / (1024**3)


def search(service, query):
    # search for the file
    result = []
    page_token = None
    while True:
        response = (
            service.files()
            .list(
                supportsTeamDrives=True,
                includeTeamDriveItems=True,
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        # iterate over filtered files
        for file in response.get("files", []):
            result.append((file["id"], file["name"], file["mimeType"]))
        page_token = response.get("nextPageToken", None)
        if not page_token:
            # no more files
            break
    return result


def upload_progress(gfile, file):
    response = None

    while response is None:
        status, response = gfile.next_chunk()

        if status:
            data_size = convert_bytes_to_megabytes(status.progress())
            if data_size >= 1024:
                data_size /= 1024

            print(f"File Uploaded {data_size}%")
            time.sleep(2)
        if file:
            print(f"{file} Uploaded successfully")  # temp


#Getting information

def getAccountInfo() :
    service = Create_Service(CRENDS_FILE, API_NAME, API_VERSION, SCOPES)
    accInfo = service.about().get(fields="*").execute()

    storageQuota = accInfo["storageQuota"]

    used = convert_bytes_to_gigabytes(int(storageQuota["usage"])) 

    limit = convert_bytes_to_gigabytes(int(storageQuota["limit"]))

    trashUsedInDrive = convert_bytes_to_gigabytes(int(storageQuota["usageInDriveTrash"]))

    free = limit - used

    print("Used : {:.2f}GB of {}GB".format(used,limit) )
    print("Free : {:.2f}GB of {}GB".format(free,limit))
    print("Trash : {:.2f}GB of {:.2f}GB\n".format(trashUsedInDrive,used))
    print("Storage Used {:.2f}%".format((used/limit)*100))

    print("Storage Free {:.2f}%\n".format((free/limit)*100))




# Upload files


def uploadFile(path, rootFolderId=None):
    service = Create_Service(CRENDS_FILE, API_NAME, API_VERSION, SCOPES)
    """

    # create folder
    fileMetadata = {
        "name": os.path.split(path)[-1] if dirName == None else dirName,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [root_id] if dirName == None else [],
    }

    file = service.files().create(body=fileMetadata, fields="id").execute()

    # get the folder id
    folder_id = file.get("id")

"""

        fileMetadata = {"name": os.path.split(path)[-1], "parents": [root_id] if rootFolderId is None else rootFolderId }
        mimetype = mimetypes.guess_type(path)[0]
        print(mimetype)

        media = MediaFileUpload(path,mimetype=mimetype,resumable=True)
        gfile = (
            service.files()
            .create(body=fileMetadata, media_body=media, fields="id,name")
            .execute()
        )
        print("{gfile['name']}uploaded successfully... ")
        return

def uploadFolder(path,dirName=None):

    # create folder                                      
       fileMetadata = {                                         "name": os.path.split(path)[-1] if dirName == None else dirName,                                          "mimeType": "application/vnd.google-apps.folder",                                                         "parents": [root_id] if dirName == None else [],                                                      }                                                    
        file = service.files().create(body=fileMetadata, fields="id").execute()                                                                                        # get the folder id                            
        folder_id = file.get("id")

        os.chdir(path)
        resultFiles = os.listdir()
        #need to add env vars
        nestedFolderUpload = False

        if not nestedFolderUpload :
           resultFiles =  [file for file in resultFiles  if os.path.isfile(file)]


        with concurrent.futures.ThreadPoolExecuter() as executer :
            [executer.submit(uploadFile,*(file,folder_id))for file in resultFiles]






                """
                print(f"Uploading {file}...")
                fileMetadata = {"name": file, "parents": [folder_id]}
                mimetype = mimetypes.guess_type(file)[0]
                media = MediaFileUpload(file, mimetype=mimetype, resumable=True)
                gfile = (
                    service.files()
                    .create(body=fileMetadata, media_body=media, fields="id")
                    .execute()
                )
                if gfile:
                    print(f"{file} uploaded sucessfully")
"""

def cloneFile(real_file_id, root_folder_id=None):
    service = Create_Service(CRENDS_FILE, API_NAME, API_VERSION, SCOPES)

    metadata = service.files().get(fileId=real_file_id, fields="id,name").execute()

    fileMatadata = {
        "name": metadata["name"],
        "parents": [root_id] if root_folder_id is None else [root_folder_id],
    }
    file = service.files().copy(fileId=real_file_id, body=fileMatadata).execute()

    print(f"{metadata['name']} cloned successfully...")


def cloneFolder(real_file_id, root_folder_id=None):
    files = 0
    folders = 0
    service = Create_Service(CRENDS_FILE, API_NAME, API_VERSION, SCOPES)
    metadata = service.files().get(fileId=real_file_id, fields="id,name").execute()

    fileMetadata = {
        "name": metadata["name"],
        "parents": [root_id] if root_folder_id is None else [root_folder_id],
        "mimeType": "application/vnd.google-apps.folder",
    }

    folder = service.files().create(body=fileMetadata, fields="id").execute()

#    query = f"parents = '{real_file_id}'"
    query = f"'{real_file_id}' in parents"
    result = search(service, query)
    for file in result:
        if file[2] == "application/vnd.google-apps.folder":
            print(f"Cloning {file[1]}")
            cloneFolder(file[0], root_folder_id=folder["id"])
            folders += 1

        else:
            print(f"Cloning {file[1]}")
            cloneFile(file[0], root_folder_id=folder["id"])
            files += 1

   # print("{} folders {} files cloned successfully".format(folders, files))
