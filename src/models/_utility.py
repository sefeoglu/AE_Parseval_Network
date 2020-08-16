from tensorflow.keras.callbacks import LearningRateScheduler

def lr_sch(epoch):

    """ Helper funtion to use different learning rate on the different number of the epochs

    Returns:
        [type]: [description]
    """    
    if epoch < 60:
        return 0.1
    elif epoch < 120:
        return 0.02
    elif epoch < 160:
        return 0.004
    else:
        return 0.0008

# Learning rate scheduler callback
lr_scheduler = LearningRateScheduler(lr_sch)
