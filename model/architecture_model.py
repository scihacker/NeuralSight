from model import content_model
from keras.utils.visualize_util import plot

def output_architecture(model, out_path):
    plot(model, to_file=out_path, show_shapes=True)