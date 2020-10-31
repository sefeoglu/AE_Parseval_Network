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
    def __init__(self,
                 weight_decay,
                 input_dim,
                 momentum,
                 nb_classes=100,
                 N=2,
                 k=1,
                 dropout=0.0,
                 verbose=1):
        """[Assign the initial parameters of the wide residual network]

        Args:
            weight_decay ([float]): [description]
            input_dim ([tuple]): [input dimension]
            nb_classes (int, optional): [output class]. Defaults to 100.
            N (int, optional): [the number of blocks]. Defaults to 2.
            k (int, optional): [network width]. Defaults to 1.
            dropout (float, optional): [dropout value to prevent overfitting]. Defaults to 0.0.
            verbose (int, optional): [description]. Defaults to 1.

        Returns:
            [Model]: [wideresnet]
        """
        self.weight_decay = weight_decay
        self.input_dim = input_dim
        self.nb_classes = nb_classes
        self.N = N
        self.k = k
        self.dropout = dropout
        self.verbose = verbose

    def initial_conv(self, input):
        """[summary]

        Args:
            input ([type]): [description]

        Returns:
            [type]: [description]
        """
        x = Convolution2D(16, (3, 3),
                          padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(input)

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(x)
        x = Activation('relu')(x)
        return x

    def expand_conv(self, init, base, k, strides=(1, 1)):
        """[summary]

        Args:
            init ([type]): [description]
            base ([type]): [description]
            k ([type]): [description]
            strides (tuple, optional): [description]. Defaults to (1, 1).

        Returns:
            [type]: [description]
        """
        x = Convolution2D(base * k, (3, 3),
                          padding='same',
                          strides=strides,
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(init)

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(x)
        x = Activation('relu')(x)

        x = Convolution2D(base * k, (3, 3),
                          padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(x)

        skip = Convolution2D(base * k, (1, 1),
                             padding='same',
                             strides=strides,
                             kernel_initializer='he_normal',
                             kernel_regularizer=l2(self.weight_decay),
                             use_bias=False)(init)

        m = Add()([x, skip])

        return m

    def conv1_block(self, input, k=1, dropout=0.0):
        """[summary]

        Args:
            input ([type]): [description]
            k (int, optional): [description]. Defaults to 1.
            dropout (float, optional): [description]. Defaults to 0.0.

        Returns:
            [type]: [description]
        """
        init = input

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(input)
        x = Activation('relu')(x)
        x = Convolution2D(16 * k, (3, 3),
                          padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(x)

        if dropout > 0.0: x = Dropout(dropout)(x)

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(x)
        x = Activation('relu')(x)
        x = Convolution2D(16 * k, (3, 3),
                          padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(x)

        m = Add()([init, x])
        return m

    def conv2_block(self, input, k=1, dropout=0.0):
        """[summary]

        Args:
            input ([type]): [description]
            k (int, optional): [description]. Defaults to 1.
            dropout (float, optional): [description]. Defaults to 0.0.

        Returns:
            [type]: [description]
        """
        init = input

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1
        print("conv2:channel:  {}".format(channel_axis))
        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(input)
        x = Activation('relu')(x)
        x = Convolution2D(32 * k, (3, 3),
                          padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(x)

        if dropout > 0.0: x = Dropout(dropout)(x)

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(x)
        x = Activation('relu')(x)
        x = Convolution2D(32 * k, (3, 3),
                          padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(x)

        m = Add()([init, x])
        return m

    def conv3_block(self, input, k=1, dropout=0.0):
        """[summary]

        Args:
            input ([type]): [description]
            k (int, optional): [description]. Defaults to 1.
            dropout (float, optional): [description]. Defaults to 0.0.

        Returns:
            [type]: [description]
        """
        init = input

        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(input)
        x = Activation('relu')(x)
        x = Convolution2D(64 * k, (3, 3),
                          padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(x)

        if dropout > 0.0: x = Dropout(dropout)(x)

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(x)
        x = Activation('relu')(x)
        x = Convolution2D(64 * k, (3, 3),
                          padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(self.weight_decay),
                          use_bias=False)(x)

        m = Add()([init, x])
        return m

    def create_wide_residual_network(self):
        """create a wide residual network model


        Returns:
            [Model]: [wide residual network]
        """
        channel_axis = 1 if K.image_data_format() == "channels_first" else -1

        ip = Input(shape=self.input_dim)

        x = self.initial_conv(ip)
        nb_conv = 4

        x = self.expand_conv(x, 16, self.k)
        nb_conv += 2

        for i in range(self.N - 1):
            x = self.conv1_block(x, self.k, self.dropout)
            nb_conv += 2

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(x)
        x = Activation('relu')(x)

        x = self.expand_conv(x, 32, self.k, strides=(2, 2))
        nb_conv += 2

        for i in range(self.N - 1):
            x = self.conv2_block(x, self.k, self.dropout)
            nb_conv += 2

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(x)
        x = Activation('relu')(x)

        x = self.expand_conv(x, 64, self.k, strides=(2, 2))
        nb_conv += 2

        for i in range(self.N - 1):
            x = self.conv3_block(x, self.k, self.dropout)
            nb_conv += 2

        x = BatchNormalization(axis=channel_axis,
                               momentum=0.1,
                               epsilon=1e-5,
                               gamma_initializer='uniform')(x)
        x = Activation('relu')(x)

        x = AveragePooling2D((8, 8))(x)
        x = Flatten()(x)

        x = Dense(self.nb_classes,
                  kernel_regularizer=l2(self.weight_decay),
                  activation='softmax')(x)

        model = Model(ip, x)

        if self.verbose:
            print("Wide Residual Network-%d-%d created." % (nb_conv, self.k))
        return model


if __name__ == "__main__":
    
    init = (32, 32, 1)

    wrn = WideResidualNetwork(0.0005,
                              init,
                              0.9,
                              nb_classes=4,
                              N=2,
                              k=2,
                              dropout=0.3)
    
    model = wrn.create_wide_residual_network()
