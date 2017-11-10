import os
from os.path import dirname
import sys
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf


# hide Tensorflow GPU warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


"""
The MNIST dataset:
- is a dataset of handwritten digits
- 55,000 images for training and 10,000 images for testing (include labels for each image)
- each image has the dimension of 28x28 pixels (-> 1D array: 784 pixels)
- each pixel has value from 0 - 255 (0: black, 255: white) to display a specific color -> 256 values can occur

Reference:
- http://www.cs.nyu.edu/~roweis/data/mnist_train2.jpg
- https://media.licdn.com/mpr/mpr/AAEAAQAAAAAAAAoYAAAAJDI5OGU3NDYwLTEzNWItNGVmZS1hMzVhLWIxYTI0MmU5MDFmYQ.png
- https://www.simplicity.be/articles/recognizing-handwritten-digits/img/matrix.jpg
- https://www.youtube.com/watch?v=aircAruvnKk&list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi
"""


def show_info():
    train_images = mnist.train.images
    train_labels = mnist.train.labels
    test_images = mnist.test.images
    test_labels = mnist.test.labels

    print '\n..::Overview::..'
    print '- Type of mnist data is ', type(mnist)
    print '- Number of train data is ', mnist.train.num_examples
    print '- Number of test data is ', mnist.test.num_examples
    print '- Training images: type {}, shape {}'.format(type(train_images), train_images.shape)
    print '- Training labels: type {}, shape {} '.format(type(train_labels), train_labels.shape)
    print '- Test images: type {}, shape {}'.format(type(test_images), test_images.shape)
    print '- Test labels: type {}, shape {}'.format(type(test_labels), test_labels.shape)

    # take 3 random elements from the training images dataset
    print 'Show random images and its labels...'
    random_indexes = np.random.randint(train_images.shape[0], size=3)
    for i in random_indexes:
        img = np.reshape(train_images[i, :], (28, 28))
        label = np.argmax(train_labels[i, :])

        # use matplotlib to show 3 random elements and its label visually
        plt.matshow(img, cmap=plt.get_cmap('gray'))
        plt.title('item ' + str(i) + 'th was labeled ' + str(label))
        plt.show()

    print '\n'


def training():
    learning_rate = 0.0001
    training_epochs = 100
    batch_size = 128  # people usually use batch size number as a power of 2 for better memory usage (64, 128, 256...)
    total_batches_need_to_run = int(mnist.train.num_examples / batch_size)  # also called "iterations"
    display_step = 10
    losses = []

    # init input layer
    input_nodes = 784  # 28x28 pixels
    X = tf.placeholder(tf.float32, shape=[None, input_nodes])

    # init hidden layer 1
    # hidden layer 1 = weight_1 * X + bias_1
    hidden_1_nodes = 256  # each pixel has value from 0 - 255 (0: black, 255: white) -> 256 values can occur
    weight_1 = tf.Variable(tf.random_normal([input_nodes, hidden_1_nodes]), name='weight_1')
    bias_1 = tf.Variable(tf.random_normal([hidden_1_nodes]), name='bias_1')
    hidden_layer_1 = tf.add(tf.matmul(X, weight_1), bias_1)

    # init hidden layer 2
    # hidden layer 2 = weight_2 * output from hidden layer 1 + bias_2
    hidden_2_nodes = 256  # each pixel has value from 0 - 255 (0: black, 255: white) -> 256 values can occur
    weight_2 = tf.Variable(tf.random_normal([hidden_1_nodes, hidden_2_nodes]), name='weight_2')
    bias_2 = tf.Variable(tf.random_normal([hidden_2_nodes]), name='bias_2')
    hidden_layer_2 = tf.add(tf.matmul(hidden_layer_1, weight_2), bias_2)

    # init output layer
    # output layer = weight_output * output from hidden layer 2 + bias_output
    output_nodes = 10
    Y = tf.placeholder(tf.float32, shape=[None, output_nodes])
    weight_output = tf.Variable(tf.random_normal([hidden_2_nodes, output_nodes]), name='weight_output')
    bias_output = tf.Variable(tf.random_normal([output_nodes]), name='bias_output')
    output_layer = tf.add(tf.matmul(hidden_layer_2, weight_output), bias_output)

    # reduce loss
    loss_output = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=output_layer, labels=Y))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_output = optimizer.minimize(loss_output)
    accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(output_layer, 1), tf.argmax(Y, 1)), tf.float32))

    print '..::Model training::..'
    with tf.Session() as session:
        session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()

        """
        Epoch: when an entire dataset is passed through the network.
        Batch: small portion of the dataset are passed through the network.

        Ex:
        Current MNIST dataset has 55,000 training examples with batch size = 128
        -> when entire 55,000 examples are passed through the network, you have done 1 epoch.
        -> total batches (iterations) need to run to complete 1 epoch = int(55,000 / 128) = 429
           + 1st iteration (batch 1): {X1: Y1}, ..., {X128: Y128}
           + 2nd iteration (batch 2): {X129: Y129}, ..., {X256: Y256}
           + ...
           + 429th iteration (batch 429): ...

        Why need ?
        - Your fancy computer machine has limited resources to be able to train entire dataset in 1 time.
        - Optimization (via the gradient descent) will has less accuracy when you train the dataset only 1 time.
        """
        for epoch in range(training_epochs):
            for batch in range(total_batches_need_to_run):
                batch_x, batch_y = mnist.train.next_batch(batch_size)
                _train, _loss, _accuracy = session.run([train_output, loss_output, accuracy], feed_dict={X: batch_x, Y: batch_y})
                losses.append(_loss)

            if epoch % display_step == 0:
                print 'Epoch ' + str(epoch) + ', minibatch loss= ' + '{:.4f}'.format(_loss) + ', training accuracy= ' + '{:.3f}'.format(_accuracy)

        print 'Training finished!!!'
        print 'Learning rate: ', learning_rate
        print 'Batch size: ', batch_size
        print 'Testing accuracy: ', session.run(accuracy, feed_dict={X: mnist.test.images, Y: mnist.test.labels})
        print '\n'

        # save the variables to disk
        save_path = saver.save(session, dirname(__file__) + "trained_models/mnist-nn/model")
        print 'The trained model has been saved in path: ', save_path

        # export model graph to Tensorboard
        writer = tf.summary.FileWriter(dirname(__file__) + 'tensorboard/mnist-nn', session.graph)
        writer.close()
        print 'The tensorboard graph has been saved in path: tensorboard/mnist-nn'
        print 'You can execute this command in terminal to see the graph: tensorboard --logdir="./tensorboard/mnist-nn"'
        print '\n'

        # draw loss diagram
        plt.title('The loss diagram after trained')
        plt.plot(losses[:])
        plt.savefig('diagrams/diagram_of_loss_values_after_trained')
        plt.show()


# run the program
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('data/mnist', one_hot=True)
show_info()
training()

