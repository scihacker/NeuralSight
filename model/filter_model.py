import numpy as np
import matplotlib.pyplot as plt
import os
from keras import backend as K

image_path = "./static/upload/"
'''
I copied A Keras Example of kernel visualization here. 
'''
def compute_filter(model, layer_id, out_path, size=(224, 224)):
    if os.path.exists(out_path + "ok"):
        return
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    layer = model.layers[layer_id]
    im_width, im_height = model.input_shape[2:4] if model.input_shape[2] and model.input_shape[3] else size

    def deprocess_image(x):
        x -= x.mean()
        x /= (x.std() + 1e-5)
        x *= 0.1
        x += 0.5
        x = np.clip(x, 0, 1)
        x *= 255
        x = x.transpose((1, 2, 0))
        x = np.clip(x, 0, 255).astype('uint8')
        return x

    input_img = model.input

    def normalize(x):
        return x / (K.sqrt(K.mean(K.square(x))) + 1e-5)

    filters = []
    for filter_index in range(layer.output_shape[1]):
        layer_output = layer.output
        loss = K.mean(layer_output[:, filter_index])
        grads = K.gradients(loss, input_img)[0]
        grads = normalize(grads)

        iterate = K.function([input_img, K.learning_phase()], [loss, grads])
        step = 1.
        input_img_data = np.random.random((1, 3, im_width, im_height))

        # last_loss_value, last_diff, stop_mult = 0, -np.inf, False
        for i in range(50):
            loss_value, grads_value = iterate([input_img_data, 0])
            input_img_data += grads_value * step
            """
            if i == 1:
                step *= 2
            if i > 1 and not stop_mult:
                if (loss_value - last_loss_value > last_diff) and step < 100000: 
                    step *= 2
                elif i >= 5:
                    step /= 2
                    stop_mult = True

            if i >= 1:
                last_diff = loss_value - last_loss_value
            last_loss_value = loss_value
            """
            print('Current loss value:', loss_value, 'step:', step)

        img = deprocess_image(input_img_data[0])
        plt.imsave(out_path + str(filter_index + 1) + ".png", img)
        filters.append((img, loss_value))
        print('Filter %d processed' % (filter_index))
    with open(out_path + "ok", 'w') as f:
        f.write("ok")

def compute_all_filter(model, out_path):
    a = list(enumerate(model.layers))
    for i, layer in a:
        if layer.__class__.__name__ == "Convolution2D":
            print "Current:", i
            compute_filter(model, i, out_path + layer.name + "/")