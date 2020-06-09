from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Add, Activation, Dropout, Flatten, Dense
from tensorflow.keras.layers import Convolution2D, MaxPooling2D, AveragePooling2D
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.regularizers import l2
from tensorflow.keras import backend as K
from tensorflow.keras.optimizers import SGD
import warnings

warnings.filterwarnings("ignore")

class WideResidualNetwork(object):

    def __init__(self):
        pass

    def initial_conv(self, input):
    
        x = Convolution2D(16, (3, 3), padding='same', kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(input)

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(x)
        x = Activation('relu')(x)
        return x


    def expand_conv(self, init, base, k, strides=(1, 1)):
        x = Convolution2D(base * k, (3, 3), padding='same', strides=strides, kernel_initializer='he_normal', kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(init)

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(x)
        x = Activation('relu')(x)

        x = Convolution2D(base * k, (3, 3), padding='same', kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(x)

        skip = Convolution2D(base * k, (1, 1), padding='same', strides=strides, kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(init)

        m = Add()([x, skip])

        return m


    def conv1_block(self, input, k=1, dropout=0.0):
        init = input

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(input)
        x = Activation('relu')(x)
        x = Convolution2D(16 * k, (3, 3), padding='same', kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(x)

        if dropout > 0.0: x = Dropout(dropout)(x)

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(x)
        x = Activation('relu')(x)
        x = Convolution2D(16 * k, (3, 3), padding='same', kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(x)

        m = Add()([init, x])
        return m

    def conv2_block(self, input, k=1, dropout=0.0):
        init = input

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1
        print("conv2:channel:  {}".format(channel_axis))
        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(input)
        x = Activation('relu')(x)
        x = Convolution2D(32 * k, (3, 3), padding='same', kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(x)

        if dropout > 0.0: x = Dropout(dropout)(x)

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(x)
        x = Activation('relu')(x)
        x = Convolution2D(32 * k, (3, 3), padding='same', kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(x)

        m = Add()([init, x])
        return m

    def conv3_block(self, input, k=1, dropout=0.0):
        init = input

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(input)
        x = Activation('relu')(x)
        x = Convolution2D(64 * k, (3, 3), padding='same', kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(x)

        if dropout > 0.0: x = Dropout(dropout)(x)

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(x)
        x = Activation('relu')(x)
        x = Convolution2D(64 * k, (3, 3), padding='same', kernel_initializer='he_normal',
                        kernel_regularizer=l2(self.weight_decay),
                        use_bias=False)(x)

        m = Add()([init, x])
        return m

    def create_wide_residual_network(self,weight_decay, lr, input_dim, nb_classes=100, N=2, k=1, dropout=0.0, verbose=1):
        """
        Creates a Wide Residual Network with specified parameters

        :param input: Input Keras object
        :param nb_classes: Number of output classes
        :param N: Depth of the network. Compute N = (n - 4) / 6.
                Example : For a depth of 16, n = 16, N = (16 - 4) / 6 = 2
                Example2: For a depth of 28, n = 28, N = (28 - 4) / 6 = 4
                Example3: For a depth of 40, n = 40, N = (40 - 4) / 6 = 6
        :param k: Width of the network.
        :param dropout: Adds dropout if value is greater than 0.0
        :param verbose: Debug info to describe created WRN
        :return:
        """
        channel_axis = 1 if K.image_data_format() == "channels_first" else -1
        self.weight_decay = weight_decay
        self.lr = lr
        ip = Input(shape=input_dim)

        x = self.initial_conv(ip)
        nb_conv = 4

        x = self.expand_conv(x, 16, k)
        nb_conv += 2

        for i in range(N - 1):
            x = self.conv1_block(x, k, dropout)
            nb_conv += 2

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(x)
        x = Activation('relu')(x)

        x = self.expand_conv(x, 32, k, strides=(2, 2))
        nb_conv += 2

        for i in range(N - 1):
            x = self.conv2_block(x, k, dropout)
            nb_conv += 2

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(x)
        x = Activation('relu')(x)

        x = self.expand_conv(x, 64, k, strides=(2, 2))
        nb_conv += 2

        for i in range(N - 1):
            x = self.conv3_block(x, k, dropout)
            nb_conv += 2

        x = BatchNormalization(axis=channel_axis, momentum=0.1, epsilon=1e-5, gamma_initializer='uniform')(x)
        x = Activation('relu')(x)

        x = AveragePooling2D((8, 8))(x)
        x = Flatten()(x)

        x = Dense(nb_classes, kernel_regularizer=l2(self.weight_decay), activation='softmax')(x)

        model = Model(ip, x)
        sgd = SGD(lr=self.lr, momentum=0.9)
        # model.summary()
        model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["acc"])
        if verbose: print("Wide Residual Network-%d-%d created." % (nb_conv, k))
        return model

if __name__ == "__main__":
    wrn = WideResidualNetwork()
    init = (68, 100,1)
    model = wrn.create_wide_residual_network(0.0005, 0.1, init, nb_classes=4, N=2, k=2, dropout=0.3)