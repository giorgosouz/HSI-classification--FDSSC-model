# -*- coding: utf-8 -*-
#
#MHN VALEIS PYDOT KAI GRAPHZIN THA CRASHAREI TO PERIVALON AN THES NA VALEIS KANE PRWTA CLONE TO ENV
#
#
import numpy as np
import scipy.io as sio
from keras.utils.np_utils import to_categorical
from keras.optimizers import Adam, SGD, Adadelta, RMSprop, Nadam
import keras.callbacks as kcallbacks
from keras.utils import plot_model
import time
import datetime
import collections
from sklearn import metrics, preprocessing
from operator import truediv
from Utils import fdssc_model, record, extract_samll_cubic
import tensorflow as tf
import sklearn.model_selection



def our_model():
    model = fdssc_model.fdssc_model.build_fdssc((1, img_rows, img_cols, img_channels), nb_classes)
    rms = RMSprop(lr=0.00005)
    model.compile(loss='categorical_crossentropy', optimizer=rms, metrics=['accuracy'])

    return model


def geo(a):
    gt=np.load(a)    #unit8
    gt=gt.reshape(np.prod(gt.shape[:2]),)
    gt=np.nonzero(gt)
    if type(gt)==tuple:
        gt=gt[0]
    gt=list(gt)    #array
    np.random.shuffle(gt)
    return gt

def sampling(proportion, ground_truth):
    train = {}
    test = {}
    labels_loc = {}
    m = max(ground_truth)
    for i in range(m):
        indexes = [j for j, x in enumerate(ground_truth.ravel().tolist()) if x == i + 1]
        np.random.shuffle(indexes)
        labels_loc[i] = indexes
        nb_val = int(proportion * len(indexes))
        train[i] = indexes[:-nb_val]
        test[i] = indexes[-nb_val:]
    train_indexes = []
    test_indexes = []
    for i in range(m):
        train_indexes += train[i]
        test_indexes += test[i]
    np.random.shuffle(train_indexes)
    np.random.shuffle(test_indexes)
    return train_indexes, test_indexes


class LossHistory(kcallbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = []
        self.acc = []

    def on_epoch_end(self, epoch, logs={}):
        self.losses.append(logs.get('loss'))
        self.acc.append(0.1*logs.get('acc'))



class geo2(kcallbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        loss_and_metrics = self.evaluate(
        x_test.reshape(x_test.shape[0], x_test.shape[1], x_test.shape[2], x_test.shape[3], 1), y_test,
        batch_size=batch_size)
        print('Test score:', loss_and_metrics[0])
        print('Test accuracy:', loss_and_metrics[1])
        
        

def aa_and_each_accuracy(confusion_matrix):
    list_diag = np.diag(confusion_matrix)
    list_raw_sum = np.sum(confusion_matrix, axis=1)
    each_acc = np.nan_to_num(truediv(list_diag, list_raw_sum))
    average_acc = np.mean(each_acc)
    return each_acc, average_acc


print('-----Importing Dataset-----')

global Dataset  # UP,IN,KSC
#dataset = input('Please input the name of Dataset(IN, UP or KSC):')
#Dataset = dataset.upper()
Dataset = 'TEST'
if Dataset == 'IN':
    mat_data = sio.loadmat('datasets/Indian_pines_corrected.mat')
    data_hsi = mat_data['indian_pines_corrected']
    mat_gt = sio.loadmat('datasets/Indian_pines_gt.mat')
    gt_hsi = mat_gt['indian_pines_gt']
    TOTAL_SIZE = 10249
    TRAIN_SIZE = 2055
    VALIDATION_SPLIT = 0.8

if Dataset == 'UP':
    uPavia = sio.loadmat('datasets/PaviaU.mat')
    gt_uPavia = sio.loadmat('datasets/PaviaU_gt.mat')
    data_hsi = uPavia['paviaU']
    gt_hsi = gt_uPavia['paviaU_gt']
    TOTAL_SIZE = 42776
    TRAIN_SIZE = 4281
    VALIDATION_SPLIT = 0.9

if Dataset == 'KSC':
    KSC = sio.loadmat('datasets/KSC.mat')
    gt_KSC = sio.loadmat('datasets/KSC_gt.mat')
    data_hsi = KSC['KSC']
    gt_hsi = gt_KSC['KSC_gt']
    TOTAL_SIZE = 5211
    TRAIN_SIZE = 1048
    VALIDATION_SPLIT = 0.8
    
if Dataset == 'TEST':
  
    data_hsi = np.load('testolo.npy')
    # data1_hsi = np.load('testolo2.npy')
    gt_hsi = np.load('testologt.npy')
    # gt1_hsi = np.load('testologt2.npy')
    TOTAL_SIZE = np.count_nonzero(gt_hsi)
    TRAIN_SIZE = np.count_nonzero(gt_hsi)
    VALIDATION_SPLIT = 0.7    

print(data_hsi.shape)
data = data_hsi.reshape(np.prod(data_hsi.shape[:2]), np.prod(data_hsi.shape[2:]))
gt = gt_hsi.reshape(np.prod(gt_hsi.shape[:2]),)
# data1 = data1_hsi.reshape(np.prod(data1_hsi.shape[:2]), np.prod(data1_hsi.shape[2:]))
# gt = gt1_hsi.reshape(np.prod(gt1_hsi.shape[:2]),)

nb_classes = max(gt)
print('The class numbers of the HSI data is:', nb_classes)

print('-----Importing Setting Parameters-----')
batch_size = 256
nb_epoch = 20
ITER = 1
PATCH_LENGTH = 4

img_rows = 2*PATCH_LENGTH+1
img_cols = 2*PATCH_LENGTH+1
img_channels = data_hsi.shape[2]
INPUT_DIMENSION = data_hsi.shape[2]

# VAL_SIZE = int(0.5*TRAIN_SIZE)
# TEST_SIZE = TOTAL_SIZE - TRAIN_SIZE

data = preprocessing.scale(data)
data_ = data.reshape(data_hsi.shape[0], data_hsi.shape[1], data_hsi.shape[2])
whole_data = data_
padded_data = np.lib.pad(whole_data, ((PATCH_LENGTH, PATCH_LENGTH), (PATCH_LENGTH, PATCH_LENGTH), (0, 0)),
                         'constant', constant_values=0)

# data1 = preprocessing.scale(data1)
# data1_ = data1.reshape(data1_hsi.shape[0], data1_hsi.shape[1], data1_hsi.shape[2])
# whole_data1 = data1_
# padded_data1 = np.lib.pad(whole_data1, ((PATCH_LENGTH, PATCH_LENGTH), (PATCH_LENGTH, PATCH_LENGTH), (0, 0)),
#                          'constant', constant_values=0)


day = datetime.datetime.now()
day_str = day.strftime('%m_%d_%H_%M')

KAPPA = []
OA = []
AA = []
TRAINING_TIME = []
TESTING_TIME = []
ELEMENT_ACC = np.zeros((ITER, nb_classes))

seeds = [1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341]

for index_iter in range(ITER):
    print("-----Starting the  %d Iteration-----" % (index_iter + 1))
    best_weights_path = 'models/'+Dataset+'_FDSSC_'+day_str+'@'+str(index_iter+1)+'.hdf5'

    np.random.seed(seeds[index_iter])
    # train1_indices, test_indices = sampling(VALIDATION_SPLIT, gt)
    train_indices=geo('train0.2.npy')
    test_indices=geo('testologt2.npy')
    val_indices=geo('test0.2.npy')
    
    
    
    
    
    
    TRAIN_SIZE = len(train_indices)
    print('Train size: ', TRAIN_SIZE)
    TEST_SIZE = len(test_indices)
    print('Test size: ', TEST_SIZE)
    VAL_SIZE = len(val_indices)
    print('Validation size: ', VAL_SIZE)

    



    y_train = gt[train_indices]-1
    y_train = to_categorical(np.asarray(y_train))

    gt_ev=np.load('testologt2.npy')
    gt_ev = gt_ev.reshape(np.prod(gt_ev.shape[:2]),)
    y_test = gt_ev[test_indices]-1
    y_test = to_categorical(np.asarray(y_test))
    
    y_val = gt[val_indices]-1
    y_val = to_categorical(np.asarray(y_val))
 
    print('-----Selecting Small Pieces from the Original Cube Data-----')
    train_data = extract_samll_cubic.select_small_cubic(TRAIN_SIZE, train_indices, whole_data,
                                                        PATCH_LENGTH, padded_data, INPUT_DIMENSION)
    
    
    
    
    datatest_hsi=np.load('testolo2.npy')
    datatest = datatest_hsi.reshape(np.prod(datatest_hsi.shape[:2]), np.prod(datatest_hsi.shape[2:])) 
    datatest = preprocessing.scale(datatest)
    datatest_ = datatest.reshape(datatest_hsi.shape[0], datatest_hsi.shape[1], datatest_hsi.shape[2])
    whole_datatest = datatest_
    padded_datatest = np.lib.pad(whole_datatest, ((PATCH_LENGTH, PATCH_LENGTH), (PATCH_LENGTH, PATCH_LENGTH), (0, 0)),
                             'constant', constant_values=0)


    
    
    
    test_data = extract_samll_cubic.select_small_cubic(TEST_SIZE, test_indices, whole_datatest,
                                                       PATCH_LENGTH, padded_datatest, INPUT_DIMENSION)
    val_data = extract_samll_cubic.select_small_cubic(VAL_SIZE, val_indices, whole_data,
                                                       PATCH_LENGTH, padded_data, INPUT_DIMENSION)

    x_train = train_data.reshape(train_data.shape[0], train_data.shape[1], train_data.shape[2], INPUT_DIMENSION)
    x_test_all = test_data.reshape(test_data.shape[0], test_data.shape[1], test_data.shape[2], INPUT_DIMENSION)

    x_val = val_data.reshape(val_data.shape[0], val_data.shape[1], val_data.shape[2], INPUT_DIMENSION)
#    y_val = y_test[-VAL_SIZE:]

    x_test = x_test_all
#    y_test = y_test[:-VAL_SIZE]

    print("-----Importing Kcallback Functions and Training the FDSSC　Model-------")

    model_fdssc = our_model()
    # plot_model(model_fdssc, to_file='FDSSC_'+Dataset+'.png', show_shapes=True)
    early_Stopping = kcallbacks.EarlyStopping(monitor='val_loss', patience=50, verbose=1, mode='min')
    save_Best_Model = kcallbacks.ModelCheckpoint(best_weights_path, monitor='val_loss', verbose=1,
                                                 save_best_only=True, mode='auto')
    reduce_LR_On_Plateau = kcallbacks.ReduceLROnPlateau(monitor='val_acc', factor=0.5, patience=10, mode='auto',
                                                        verbose=1, min_lr=0)
    history = LossHistory()
#    geo2=geo2()
    tensor_board = kcallbacks.TensorBoard(log_dir='.\logs', histogram_freq=0, write_graph=True,
                                          write_images=True,
                                          embeddings_freq=0, embeddings_metadata=None)
    
    
    
    
    
    
    
    
    
                                          

    tic1 = time.clock()
    print(x_train.shape, x_test.shape)
    
    excel=np.zeros((nb_epoch,10), dtype=float) 
    for i in range(1,nb_epoch):
        tic1 = time.clock()
        best_weights_path = 'models/'+Dataset+'_FDSSC_'+day_str+'@'+str(i)+'.hdf5'
        history_fdssc = model_fdssc.fit(
            x_train.reshape(x_train.shape[0], x_train.shape[1], x_train.shape[2], x_train.shape[3], 1), y_train,
            validation_data=(x_val.reshape(x_val.shape[0], x_val.shape[1], x_val.shape[2], x_val.shape[3], 1), y_val),
            batch_size=batch_size, epochs=1, shuffle=True,
            callbacks=[early_Stopping, save_Best_Model, reduce_LR_On_Plateau, history, tensor_board])
        toc1 = time.clock()
    
        tic2 = time.clock()
        loss_and_metrics = model_fdssc.evaluate(
            x_test.reshape(x_test.shape[0], x_test.shape[1], x_test.shape[2], x_test.shape[3], 1), y_test,
            batch_size=batch_size)
        toc2 = time.clock()
    
        print(' Training Time: ', toc1 - tic1)
        print('Test time:', toc2 - tic2)
        print('Test score:', loss_and_metrics[0])
        print('Test accuracy:', loss_and_metrics[1])
        print(history_fdssc.history.keys())
        
        
        excel[i,0]=history_fdssc.history['loss'][0]
        excel[i,1]=history_fdssc.history['acc'][0]
        excel[i,2]=history_fdssc.history['val_loss'][0]
        excel[i,3]=history_fdssc.history['val_acc'][0]
        excel[i,4]=loss_and_metrics[0]
        excel[i,5]=loss_and_metrics[1]
        excel[i,6]=toc1 - tic1
        tic1=0.
        toc1=0.
        


        np.savetxt('data.csv', excel, delimiter=',')


        

        pred_test_fdssc = model_fdssc.predict(x_test.reshape(x_test.shape[0], x_test.shape[1], x_test.shape[2],
                                                              x_test.shape[3], 1)).argmax(axis=1)
        collections.Counter(pred_test_fdssc)
        gt_test = gt_ev[test_indices]-1
    
        overall_acc_fdssc = metrics.accuracy_score(pred_test_fdssc, gt_test)
        confusion_matrix_fdssc = metrics.confusion_matrix(pred_test_fdssc, gt_test)
        each_acc_fdssc, average_acc_fdssc = aa_and_each_accuracy(confusion_matrix_fdssc)
        kappa = metrics.cohen_kappa_score(pred_test_fdssc, gt_test)
    
        KAPPA.append(kappa)
        OA.append(overall_acc_fdssc)
        # AA.append(average_acc_fdssc)
        TRAINING_TIME.append(toc1 - tic1)
        TESTING_TIME.append(toc2 - tic2)
        # ELEMENT_ACC[index_iter, :] = each_acc_fdssc
    
        
        print("--------FDSSC Training Finished-----------")
        record.record_output(OA, AA, KAPPA, ELEMENT_ACC, TRAINING_TIME, TESTING_TIME,
                              'records/'+Dataset+'_fdssc_'+day_str+'.txt')
        print('The save mode is:'+Dataset+'_FDSSC_'+str(nb_epoch)+'.hdf5')
