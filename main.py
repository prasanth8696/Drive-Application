import os
from api import uploadFile, uploadFolder, cloneFolder, cloneFile, getAccountInfo


def driveInfo():
    getAccountInfo()


def driveUpload():
    path = input("Enter folder/file path")
    if not (os.path.exists(path)):
        print("Invalid path... ")
        return
    else:
        if os.path.isfile(path):
            uploadFile(path=path)
        if os.path.isdir(path):
            uploadFolder(path=path)


def driveDownload():
    pass


def driveClone():
    file_type = None
    file_link = input("Enter Drive Link ")

    if file_link.find("folders") != -1:
        file_id = file_link.split("/")[-1]
        cloneFolder(file_id)

    elif file_link.find("file") != -1:
        file_id = file_link.split("/")[-2]
        cloneFile(file_id)


while True:

    print("drive CLI Tool ")

    print(
        """
     1 => Get Account Information
     2 => Upload to drive
     3 => Download from drive
     4 => Clone files
       """
    )
    try:
        ch = int(input())
    except ValueError:
        print("Invalid input")

    if ch == 1:
        driveInfo()
    elif ch == 2:
        driveUpload()
    elif ch == 3:
        driveDownload()
    elif ch == 4:
        driveClone()
    else:
        print("Invalid input...")
