import os
from Crypto.Hash import SHA
import base64

content_path = "./content/"
def folder_adapter(name):
    import re
    return re.sub("[/]", "A", name)

def get_hash_by_code(code):
    sha = SHA.new()
    sha.update(code)
    return folder_adapter(base64.encodestring(sha.digest()).rstrip())

def get_path_by_code(code, act):
    path = content_path + act + "/" + get_hash_by_code(code)
    if not os.path.exists(path):
        os.mkdir(path)
    return path + "/"

'''
Neural Network Visualizations Below
'''
def architecture_exist(code):
    path = get_path_by_code(code, "structure")
    if os.path.exists(path) and os.path.exists(path + "arch.png"):
        return os.path.exists(path + "arch.png")
    return False