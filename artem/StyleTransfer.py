# from __future__ import print_function, division
from builtins import range, input

import os
os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"

from keras.layers import Input, Lambda, Dense, Flatten
from keras.layers import AveragePooling2D, MaxPooling2D
from keras.layers.convolutional import Conv2D
from keras.models import Model, Sequential
from keras.applications.vgg19 import VGG19
from keras.applications.vgg19 import preprocess_input
from keras.preprocessing import image
from skimage.transform import resize
from keras.preprocessing.image import save_img
from datetime import datetime
import keras.backend as K
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin_l_bfgs_b
from Utils import Utils

utils = Utils(600, 600)

def VGGPool(shape):
    vgg = VGG19(input_shape=shape, weights='imagenet', include_top=False)
    vgg.trainable = False

    model = Sequential()
    for layer in vgg.layers:
        if layer.__class__ == MaxPooling2D:
            model.add(AveragePooling2D())
        else:
            model.add(layer)

    return model


def gram_matrix(img):
    Y = K.batch_flatten(K.permute_dimensions(img, (2, 0, 1)))
    G = K.dot(Y, K.transpose(Y))/ (img.shape.dims[0]*img.shape.dims[1]*img.shape.dims[2])
    return G


def style_loss(style, combo):
    s = gram_matrix(style)
    c = gram_matrix(combo)
    return K.mean(K.square(s - c))


def content_loss(base, combo):
    return K.mean(K.square(base - combo))


def minimize(fn, epochs, batch_shape):
    t0 = datetime.now()
    losses = []
    x = np.random.randn(np.prod(batch_shape))
    for i in range(epochs):
        x, l, _ = fmin_l_bfgs_b(
            func=fn,
            x0=x,
            maxfun=20
        )
        x = np.clip(x, -127, 127)
        print("iter=%s, loss=%s" % (i, l))
        losses.append(l)

    print("duration:", datetime.now() - t0)

    newimg = x.reshape(*batch_shape)
    final_img = utils.unpreprocess(newimg)
    return final_img[0]


def total_variation_loss(x, rows, cols):
    a = K.square(
        x[:, : rows - 1, : cols - 1, :] - x[:, 1:, : cols - 1, :]
    )
    b = K.square(
        x[:, : rows - 1, : cols - 1, :] - x[:, : rows - 1, 1:, :]
    )
    return K.reduce_sum(K.pow(a + b, 1.25))


def transfer_style( content_path, style_path, save_path, 
                    size=None, style_weight=None, content_weight=None, epochs=10):
    # Set size
    if size:
        global utils
        utils = Utils(size[0], size[1])
    
    # Import style and style images
    content_img = utils.preprocessImage(content_path)
    h, w = content_img.shape[1:3]
    style_img = utils.preprocessImage(style_path)

    batch_shape = content_img.shape
    shape = content_img.shape[1:]
    vgg = VGGPool(shape)

    # Layers
    content_layers = [
        layer.get_output_at(1) for layer in vgg.layers if layer.name.endswith('block5_conv1')
    ]

    content_model = Model(vgg.input, content_layers)
    content_model.summary()
    content_target = K.variable(content_model.predict(content_img))

    symbolic_conv_outputs = [
        layer.get_output_at(1) for layer in vgg.layers if layer.name.endswith('conv1')
    ]

    style_model = Model(vgg.input, symbolic_conv_outputs)
    style_layers_predicts = [K.variable(y) for y in style_model.predict(style_img)]

    if style_weight == None:
        style_weight=1e-2
    
    if content_weight == None:
        content_weight=1e4

    loss = K.mean(K.square(content_model.output - content_target))
    
    for symbolic, actual in zip(symbolic_conv_outputs, style_layers_predicts):
        loss += style_weight * style_loss(symbolic[0], actual[0])

    grads = K.gradients(loss, vgg.input)
    get_loss_and_grads = K.function(
        inputs=[vgg.input],
        outputs=[loss] + grads
    )

    def get_loss_and_grads_wrapper(x_vec):
        l, g = get_loss_and_grads([x_vec.reshape(*batch_shape)])
        return l.astype(np.float64), g.flatten().astype(np.float64)

    final_img = minimize(get_loss_and_grads_wrapper, epochs, batch_shape)
    plt.imshow(utils.scaleImage(final_img))

    save_img(save_path, final_img)


if __name__ == "__main__":
    from datetime import datetime

    temp_name = datetime.now().strftime("%Y-%m-%d")

    content_path = '/Users/Tommy/Documents/School/CHEMENG 4H03/Project/Resources/neural-style-tf/content_images/canoe.jpg'
    style_path     = '/Users/Tommy/Documents/School/CHEMENG 4H03/Project/Resources/neural-style-tf/style_images/album_5.jpeg'

    content_img = utils.preprocessImage(content_path)
    h, w = content_img.shape[1:3]

    transfer_style(content_path, style_path, "stylized/" + temp_name + ".jpg", size=(h,w))