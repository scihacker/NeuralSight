from model import code_model
from model import content_model
from keras.models import load_model as keras_load_model
model_dict = {}

def load_model(code, data):
    hash = content_model.get_hash_by_code(code)
    if model_dict.has_key(hash):
        return model_dict[hash]
    try:
        model_dict[hash] = keras_load_model(data)
        return model_dict[hash]
    except IOError:
        return None

def dispose_model(code):
    hash = content_model.get_hash_by_code(code)
    if model_dict.has_key(hash):
        model_dict.pop(hash)
        return True
    else:
        return False