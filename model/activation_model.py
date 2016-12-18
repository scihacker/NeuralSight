from theano import function
from scipy.misc import imread, imresize
import numpy as np
import matplotlib.pyplot as plt
import os
from keras import backend as K

image_path = "./static/upload/"
def compute_activation(model, layer_id, image, out_path, size=(224, 224)):
    if os.path.exists(out_path):
        return len(os.listdir(out_path))
    layer = model.layers[layer_id]
    f = function([model.input, K.learning_phase()], layer.output, on_unused_input='ignore')
    # hopefully this is a colored image
    im = imread(image_path + image, mode='RGB') / 255.
    print "im:", im.shape
    imsize = model.input_shape[2:4] if model.input_shape[2] and model.input_shape[3] else size
    im = imresize(im, imsize)
    if len(im.shape) == 3:
        im = im.transpose(2, 0, 1)[np.newaxis, :]
    else:
        im = im[np.newaxis, np.newaxis, :]
    result = f(im, 0.)[0]
    os.mkdir(out_path)
    if len(result.shape) == 3:
        for k in range(result.shape[0]):
            plt.imsave(out_path + str(k + 1) + ".png", result[k])
        return result.shape[0]
    elif len(result.shape) == 1:
        # histogram
        fig = plt.figure(figsize=(20, 10))
        plt.xlim([0, result.shape[0]])
        plt.bar(np.arange(result.shape[0]), result, width=1)
        fig.savefig(out_path + "1.png")
        return 1