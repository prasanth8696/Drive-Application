import os
import io
import mimetypes
from pprint import pprint
import tqdm
from handler import Create_Service,picInfo
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload



CRENDS_FILE = "/data/data/com.termux/files/home/newproject/credentials.json"

API_NAME = "drive"

API_VERSION = "v3"

SCOPES = ["https://www.googleapis.com/auth/drive"]

root_id = "1GyWgVKNpDB6Pjm6a4HNC5PTmh4byS_IR"

SAVE_PATH = os.environ.get("HOME") + "/gdriveFiles"


if not os.path.exists(SAVE_PATH):
    os.mkdir(SAVE_PATH)


class Drive:
    def __init__(self):
        self._service = Create_Service(CRENDS_FILE, API_NAME, API_VERSION, SCOPES)

    # Convert bytes to mega bytes
    def convert_bytes_to_megabytes(self, data_size: int):
        return data_size / (1024**2)

    def convert_bytes_to_gigabytes(self, data_size: int) -> float:
        return data_size / (1024**3)

    def clear(self):
        clear_cmd = "cls" if os.name == "nt" else "clear"
        os.system(clear_cmd)


    def search(self, service, query):
        # search for the file
        result = []
        page_token = None
        while True:
            response = (
                self._service.files()
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

    def uploadProgress(self, gfile):
        response = None

        while not response:
            status, response = gfile.next_chunk()

            if status:
                clear()
                print(f"Uploaded {status.progress()}")
        if gfile:
            print(f"{gfile['name']} Uploaded successfully")  # temp

    # Getting information

    def getAccountInfo(self):

        accInfo = self._service.about().get(fields="*").execute()

        storageQuota = accInfo["storageQuota"]
        user = accInfo["user"]

        used = self.convert_bytes_to_gigabytes(int(storageQuota["usage"]))

        limit = self.convert_bytes_to_gigabytes(int(storageQuota["limit"]))

        trashUsedInDrive = self.convert_bytes_to_gigabytes(
            int(storageQuota["usageInDriveTrash"])
        )

        free = limit - used
        self.clear()

        print(f"Owner : {user['displayName']}")
        print(f"Email Address : {user['emailAddress']}\n")
        print("$$$$STORAGE DETAILS$$$$\n")
        print(picInfo((used / limit) * 100) + "\n")
        print("Used : {:.2f}GB of {}GB".format(used, limit))
        print("Free : {:.2f}GB of {}GB".format(free, limit))
        print("Trash : {:.2f}GB of {:.2f}GB\n".format(trashUsedInDrive, used))
        print("Storage Used {:.2f}%".format((used / limit) * 100))

        print("Storage Free {:.2f}%\n".format((free / limit) * 100))

    # Upload files

    def uploadFile(self, path, rootFolderId=None):

        fileMetadata = {
            "name": os.path.split(path)[-1],
            "parents": [root_id] if rootFolderId is None else [rootFolderId],
        }

        mimetype = mimetypes.guess_type(path)[0]

        media = MediaFileUpload(path, mimetype=mimetype, resumable=True)
        gfile = (
            self._service.files()
            .create(body=fileMetadata, media_body=media, fields="id,name")
            .execute()
        )

        print(f"{gfile['name']} uploaded successfully")
        return

    def uploadFolder(self, path, dirName=None):

        fileMetadata = {
            "name": os.path.split(path)[-1] if dirName == None else dirName,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [root_id] if dirName == None else [],
        }
        file = self._service.files().create(body=fileMetadata, fields="id").execute()

        folder_id = file.get("id")

        resultFiles = os.listdir(path)
        # need to add env vars
        nestedFolderUpload = False

        if not nestedFolderUpload:
            resultFiles = [
                os.path.join(path, file)
                for file in resultFiles
                if os.path.isfile(os.path.join(path, file))
            ]

        for file in resultFiles:

            if os.path.isdir(file):
                print("under contruction")
            elif os.path.isfile(file):
                self.uploadFile(file, folder_id)

    def cloneFile(self, real_file_id, root_folder_id=None):

        metadata = (
            self._service.files().get(fileId=real_file_id, fields="id,name").execute()
        )

        fileMatadata = {
            "name": metadata["name"],
            "parents": [root_id] if root_folder_id is None else [root_folder_id],
        }
        file = (
            self._service.files().copy(fileId=real_file_id, body=fileMatadata).execute()
        )

        print(f"{metadata['name']} cloned successfully...")

    def cloneFolder(self, real_file_id, root_folder_id=None):
        files = 0
        folders = 0

        metadata = (
            self._service.files().get(fileId=real_file_id, fields="id,name").execute()
        )

        fileMetadata = {
            "name": metadata["name"],
            "parents": [root_id] if root_folder_id is None else [root_folder_id],
            "mimeType": "application/vnd.google-apps.folder",
        }

        folder = self._service.files().create(body=fileMetadata, fields="id").execute()

        #    query = f"parents = '{real_file_id}'"
        query = f"'{real_file_id}' in parents"
        result = self.search(self._service, query)
        for file in result:
            if file[2] == "application/vnd.google-apps.folder":
                print(f"Cloning {file[1]}")
                self.cloneFolder(file[0], root_folder_id=folder["id"])
                folders += 1

            else:
                print(f"Cloning {file[1]}")
                self.cloneFile(file[0], root_folder_id=folder["id"])
                files += 1

    # print("{} folders {} files cloned successfully".format(folders, files))

    def downloadFile(self, realFileId: str, savePath: str = SAVE_PATH):

        file_metadata = (
            self._service.files().get(fileId=realFileId, fields="id,name").execute()
        )

        request = self._service.files().get_media(fileId=realFileId)

        fh = io.BytesIO()

        downloader = MediaIoBaseDownload(fd=fh, request=request)

        response = None

        while not response:
            status, response = downloader.next_chunk()

            print(status.progress() * 100)

        with open(os.path.join(savePath, file_metadata["name"]), "wb") as file:
            file.write(fh.getvalue())

        print(f"{file_metadata['name']} downloaded successfully")

    def downloadFolder(self, realFileId: str, savePath: str = SAVE_PATH):

        fileMetadata = (
            self._service.files().get(fileId=realFileId, fields="id,name").execute()
        )

        query = f"'{realFileId}' in parents"
        getResults = self.search(self._service, query)

        cur_path = os.path.join(savePath, fileMetadata["name"])
        if not os.path.exists(cur_path):
            os.mkdir(cur_path)

        for file in getResults:
            if file[2] == "application/vnd.google-apps.folder":
                self.downloadFolder(file[0], cur_path)
            else:
                self.downloadFile(file[0], cur_path)
