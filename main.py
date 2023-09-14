import os
import sys
from api import (
    uploadFile,
    uploadFolder,
    cloneFolder,
    cloneFile,
    getAccountInfo,
    downloadFile,
    downloadFolder,
)


def driveInfo():
    getAccountInfo()


def getDriveLinkId(url: str):

    try:
        #For folder link
        if "folders" in url:
            return ("dir", url.split("/")[-1])
        #for Download link
        elif "file" in url and "export" in url:
            return ("file", url.split("?")[-1].split("&")[0][3:])

        #For Webview link
        elif "file" in url and "view" in url:
            return ("file", url.split("/")[-2])
    except IndexError:
        print("Invalid link")
        return -1

    except Exception as e:
        print("Something went wrong", e)
        return -1


def driveUpload(path: str):
    if os.path.isfile(path):
        uploadFile(path=path)
    if os.path.isdir(path):
        uploadFolder(path=path)


def driveDownload(url: str):

    link_data = getDriveLinkId(url)

    if link_data == -1:
        return

    if link_data[0] == "dir":
        downloadFolder(link_data[1])

    elif link_data[0] == "file":
        downloadFile(link_data[1])


def driveClone(url: str):

    link_data = getDriveLinkId(url)

    if link_data == -1:
        return

    if link_data[0] == "dir":
        cloneFolder(link_data[1])

    elif link_data[0] == "file":
        cloneFile(link_data[1])


def cli():

    while True:

        print("drive CLI Tool ")

        print(
            """
     1 => Get Account Information
     2 => Upload to drive
     3 => Download from drive
     4 => Clone files
     5 => Exit
       """
        )
        try:
            ch = int(input())

            if ch == 1:
                driveInfo()
            elif ch == 2:
                path = input("Enter folder/file path ")
                if not (os.path.exists(path)):
                    raise FileNotFoundError
                driveUpload(path)
            elif ch == 3:
                url = input("Enter Drive Link ")
                driveDownload(url)
            elif ch == 4:
                url = input("Enter Drive Link ")
                driveClone(url)
            elif ch == 5:
                exit()
            else:
                print("Invalid input...")
        except FileNotFoundError:
            print("File/Folder doesnt exist")

        except ValueError:
            print("Value must be integer")

        except Exception as e:
            print("Something went wrong", e)


def main():
    args = list(sys.argv)
    try:

        if "-d" in args or "--download" in args:
            index = (
                args.index("-d") if args.count("-d") == 1 else args.index("--download")
            )
            link = args[index + 1]

            driveDownload(link)
        elif "-u" in args or "--upload" in args:
            index = (
                args.index("-u") if args.count("-u") == 1 else args.index("--upload")
            )
            path = args[index + 1]

            if not os.path.exists(path):
                raise FileNotFoundError

            driveUpload(path)

        elif "-c" in args or "--clone" in args:
            index = (
                args.index("-c") if args.count("-c") == 1 else args.index("--clone")
            )
            link = args[index + 1]

            driveClone(link)

        elif "-g" in args or "--get" in args:
            index = args.index("-g") if args.count("-g") == 1 else args.index("--get")
            # link = args[index+1]

            driveInfo()

        else:
            cli()

    except FileNotFoundError:
        print("Invalid Path")

    except IndexError:
        print("Wrong Input")

    except Exception as e:
        print("Something went wrong...", e)


if __name__ == "__main__":
    main()
