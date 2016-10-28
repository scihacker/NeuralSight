try:
    import pydot_ng as pydot
except ImportError:
    import pydot
if not pydot.find_graphviz():
    raise RuntimeError('Failed to import pydot. You must install pydot'
                       ' and graphviz for `pydotprint` to work.')

'''
I copied Keras Network Architecture Visualization Code here. 
Just add some essential information.
'''
def model_to_dot(model, show_shapes=False, show_layer_names=True):
    dot = pydot.Dot()
    dot.set('rankdir', 'TB')
    dot.set('concentrate', True)
    dot.set_node_defaults(shape='record')

    if model.__class__.__name__ == 'Sequential':
        if not model.built:
            model.build()
        model = model.model
    layers = model.layers

    # first, populate the nodes of the graph
    for layer in layers:
        layer_id = str(id(layer))
        if show_layer_names:
            label = str(layer.name) + ' (' + layer.__class__.__name__ + ')'
        else:
            label = layer.__class__.__name__
        # Why not add something more here?
        if layer.__class__.__name__ == "Convolution2D":
            label += "\nFilters: %d * (%d * %d) %s" % (layer.nb_filter, layer.nb_row, layer.nb_col, layer.border_mode)
            label += "\n|Params:\n%d" % (layer.count_params())
        elif layer.__class__.__name__ == "Activation":
            label += "\n%s" % (layer.get_config()['activation'].capitalize())
        elif layer.__class__.__name__ == "MaxPooling2D":
            label += "\nPooling: %s Stride: %s" % (str(layer.pool_size), str(layer.strides[0]) if layer.strides[0] == layer.strides[1] else str(layer.strides))
        elif layer.__class__.__name__ == "Dropout":
            label += "\nDropout: %f" % (layer.p, )
        elif layer.__class__.__name__ == "Dense":
            label += "\n|Params:\n%d" % (layer.count_params())
        
        if show_shapes:
            # Build the label that will actually contain a table with the
            # input/output
            try:
                outputlabels = str(layer.output_shape)
            except:
                outputlabels = 'multiple'
            if hasattr(layer, 'input_shape'):
                inputlabels = str(layer.input_shape)
            elif hasattr(layer, 'input_shapes'):
                inputlabels = ', '.join(
                    [str(ishape) for ishape in layer.input_shapes])
            else:
                inputlabels = 'multiple'
            label = '%s\n|{input:|output:}|{{%s}|{%s}}' % (label, inputlabels, outputlabels)

        node = pydot.Node(layer_id, label=label)
        dot.add_node(node)

    # second, add the edges
    for layer in layers:
        layer_id = str(id(layer))
        for i, node in enumerate(layer.inbound_nodes):
            node_key = layer.name + '_ib-' + str(i)
            if node_key in model.container_nodes:
                # add edges
                for inbound_layer in node.inbound_layers:
                    inbound_layer_id = str(id(inbound_layer))
                    layer_id = str(id(layer))
                    dot.add_edge(pydot.Edge(inbound_layer_id, layer_id))
    return dot


def plot(model, to_file='model.png', show_shapes=False, show_layer_names=True):
    dot = model_to_dot(model, show_shapes, show_layer_names)
    dot.write_png(to_file)

def output_architecture(model, out_path):
    plot(model, to_file=out_path, show_shapes=True)
