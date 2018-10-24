
import numpy as np
import tensorflow as tf


def load_graph(model_file):
    """
    Load a tensorflow graph from a path
    Args:
        model_file(str): path to a tensorflow.pb file

    Returns:
        graph(tf.Graph): tensorflow graph

    """
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file(file_name,
                                input_height=224,
                                input_width=224,
                                input_mean=0,
                                input_std=255):
    """
    Read in an image file as a tensor and convert height, width, mean and std.

    Must have one of the following extensions:
    .bmp, .jpeg, .gif, .png


    Args:
        file_name(str): path to an image file
        input_height(int): height of image that is output
        input_width(int): width of image that is output
        input_mean(int): mean of image that is output
        input_std(int): std of image that is output

    Returns:
        result(tf.Tensor): image converted to a tensor

    """
    input_name = "file_reader"
    file_reader = tf.read_file(file_name, input_name)
    try:
        if file_name.endswith(".png"):
            image_reader = tf.image.decode_png(
                file_reader, channels=3, name="png_reader")
        elif file_name.endswith(".gif"):
            image_reader = tf.squeeze(
                tf.image.decode_gif(file_reader, name="gif_reader"))
        elif file_name.endswith(".bmp"):
            image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
        elif file_name.endswith(".jpeg"):
            image_reader = tf.image.decode_jpeg(
                file_reader, channels=3, name="jpeg_reader")
    except ValueError:
        print("File Must have one of the following extensions: .bmp, .jpeg, .gif, .png!")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result

def load_labels(label_file):
    """
    Load a file with labels in as a tf.gfile

    Label file should have 1 label per line.

    Args:
        label_file(str): path to label file

    Returns:
        label(tf.gfile): label as tf.gfile

    """
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label


def predict_single(graph, file_name, labels):
    """
    Create predictions from a graph for a single file.

    Args:
        graph: tensorflow graph of model
        file_name (str): path to file name
        labels (list): list of labels that correspond to order of labels for training / prediction

    Returns:
        predictions: dictionary of results with label:probability

    """


    input_layer = "Placeholder"#"input"
    output_layer = "final_result"#"InceptionV3/Predictions/Reshape_1"

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    input_tensor = input_operation.values()[0]

    input_height = int(input_tensor.shape[1])
    input_width = int(input_tensor.shape[2])
    input_mean = 0
    input_std = 255

    t = read_tensor_from_image_file(
        file_name,
        input_height=input_height,
        input_width=input_width,
        input_mean=input_mean,
        input_std=input_std)



    with tf.Session(graph=graph) as sess:
        results = sess.run(output_operation.outputs[0], {
            input_operation.outputs[0]: t
        })
    results = np.squeeze(results)

    out_dict = {}
    out_dict['filename'] = file_name
    preds = dict(zip(labels, results))
    out_dict.update(preds)

    return(out_dict)



def predict_multiple(graph, file_list, labels):
    """
    Create predictions from a graph for multiple files at once.

    Args:
        graph: tensorflow graph of model
        file_name (str): path to file name
        labels (list): list of labels that correspond to order of labels for training / prediction

    Returns:
        predictions: dictionary of results with label:probability

    """

    all_results = []
    input_layer = "Placeholder"#"input"
    output_layer = "final_result"#"InceptionV3/Predictions/Reshape_1"

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    input_tensor = input_operation.values()[0]

    input_height = int(input_tensor.shape[1])
    input_width = int(input_tensor.shape[2])
    input_mean = 0
    input_std = 255

    with tf.Session(graph=graph) as sess:
        for file_name in file_list:
            t = read_tensor_from_image_file(
                file_name,
                input_height=input_height,
                input_width=input_width,
                input_mean=input_mean,
                input_std=input_std)

            results = sess.run(output_operation.outputs[0], {
                input_operation.outputs[0]: t
            })
            results = np.squeeze(results)

            out_dict = {}
            out_dict['filename'] = file_name
            preds = dict(zip(labels, results))
            out_dict.update(preds)

            all_results.append(out_dict)

    return(all_results)
