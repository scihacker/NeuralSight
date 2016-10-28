import os
from Crypto.Hash import SHA
import base64

content_path = "./static/content/"
def folder_adapter(name):
    import re
    return re.sub("[/]", "A", name)

def get_hash_by_code(code):
    sha = SHA.new()
    sha.update(code)
    return folder_adapter(sha.hexdigest())

def get_path_by_code(code, act):
    path = content_path + act + "/" + get_hash_by_code(code)
    if not os.path.exists(path):
        os.mkdir(path)
    return path + "/"

'''
Neural Network Visualizations Below
'''
def get_architecture(code):
    path = get_path_by_code(code, "structure")
    if os.path.exists(path) and os.path.exists(path + "arch.png"):
        return path + "arch.png"
    return False

# Suppose all activation image in a layer is named from 1 ~ n
def get_activation(code, image, layers):
    path = get_path_by_code(code, "activation")
    path = path + image[:-4]
    result = [0] * len(layers)
    if not os.path.exists(path):
        os.mkdir(path)
        return path + "/", result
    for layer in layers:
        if os.path.exists(path + "/" + layer[1]):
            layer[2] = True
            result[layer[0]] = len(os.listdir(path + "/" + layer[1]))
    return path + "/", result
