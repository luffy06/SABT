# -*- coding: utf-8 -*-
#training the model.
#process--->1.load data(X:list of lint,y:int). 2.create session. 3.feed data. 4.training (5.validation) ,(6.prediction)
import sys
import tensorflow as tf
import numpy as np
from model import TextCNN
from keras.preprocessing.sequence import pad_sequences
import os
#import word2vec
#import pickle

#configuration
FLAGS=tf.app.flags.FLAGS
tf.app.flags.DEFINE_integer("num_classes",2,"number of label")
tf.app.flags.DEFINE_float("learning_rate",0.0001,"learning rate")
tf.app.flags.DEFINE_integer("batch_size", 128, "Batch size for training/evaluating.") #批处理的大小 32-->128
tf.app.flags.DEFINE_integer("decay_steps", 50, "how many steps before decay learning rate.") #6000批处理的大小 32-->128
tf.app.flags.DEFINE_float("decay_rate", 0.5, "Rate of decay for learning rate.") #0.65一次衰减多少
#tf.app.flags.DEFINE_integer("num_sampled",50,"number of noise sampling") #100
tf.app.flags.DEFINE_string("ckpt_dir","model/","checkpoint location for the model")
tf.app.flags.DEFINE_integer("sentence_len",40,"max sentence length")
tf.app.flags.DEFINE_integer("embed_size",200,"embedding size")
tf.app.flags.DEFINE_boolean("is_training",True,"is traning.true:tranining,false:testing/inference")
tf.app.flags.DEFINE_integer("num_epochs",100,"number of epochs to run.")
tf.app.flags.DEFINE_integer("validate_every", 1, "Validate every validate_every epochs.") #每10轮做一次验证
tf.app.flags.DEFINE_boolean("use_embedding",False,"whether to use embedding or not.")
#tf.app.flags.DEFINE_string("cache_path","text_cnn_checkpoint/data_cache.pik","checkpoint location for the model")
#train-zhihu4-only-title-all.txt
tf.app.flags.DEFINE_string("traning_data_path","train-zhihu4-only-title-all.txt","path of traning data.") #O.K.train-zhihu4-only-title-all.txt-->training-data/test-zhihu4-only-title.txt--->'training-data/train-zhihu5-only-title-multilabel.txt'
tf.app.flags.DEFINE_integer("num_filters", 128, "number of filters") #256--->512
tf.app.flags.DEFINE_string("word2vec_model_path","zhihu-word2vec-title-desc.bin-100","word2vec's vocabulary and vectors") #zhihu-word2vec.bin-100-->zhihu-word2vec-multilabel-minicount15.bin-100
tf.app.flags.DEFINE_boolean("multi_label_flag",False,"use multi label or single label.")
filter_sizes=[1,2,3,4,5,6,7] #[1,2,3,4,5,6,7]
#1.load data(X:list of lint,y:int). 2.create session. 3.feed data. 4.training (5.validation) ,(6.prediction)
best_valid_acc = 0
def main(_):
    global best_valid_acc
    if 1==1:
        trainX, trainY, testX, testY = None, None, None, None
        vocabulary_word2index, vocabulary_index2word = None,None
        vocabulary_word2index_label,vocabulary_index2word_label = None,None
        vocab_size = 12046
        
        testX = np.load('nn/model_test.npy')
        testX = pad_sequences(testX,FLAGS.sentence_len)
        print('testX shape {}'.format(testX.shape))

    #2.create session.
    config=tf.ConfigProto()
    config.gpu_options.allow_growth=True
    with tf.Session(config=config) as sess:
        #Instantiate Model
        textCNN=TextCNN(filter_sizes,FLAGS.num_filters,FLAGS.num_classes, FLAGS.learning_rate, FLAGS.batch_size, FLAGS.decay_steps,
                        FLAGS.decay_rate,FLAGS.sentence_len,vocab_size,FLAGS.embed_size,FLAGS.is_training,multi_label_flag=FLAGS.multi_label_flag)
        #Initialize Save
        saver=tf.train.Saver()
        if os.path.exists(FLAGS.ckpt_dir):
            print("Restoring Variables from Checkpoint")
            saver.restore(sess,FLAGS.ckpt_dir+"model.ckpt")
        else:
            print('Initializing Variables')
            sess.run(tf.global_variables_initializer())
            if FLAGS.use_embedding: #load pre-trained word embedding
                assign_pretrained_word_embedding(sess,textCNN)
        curr_epoch=sess.run(textCNN.epoch_step)
        #3.feed data & training
        number_of_training_data=len(testX)+1
        batch_size=FLAGS.batch_size
       
        result = []
        for start, end in zip(range(0, number_of_training_data, batch_size),range(batch_size, number_of_training_data, batch_size)):
            feed_dict = {textCNN.input_x: testX[start:end],textCNN.dropout_keep_prob: 1}

            predictions = sess.run([textCNN.predictions],feed_dict) #curr_acc--->TextCNN.accuracy
            predictions = np.array(predictions).reshape([-1,1])
            result.extend(predictions)
        result = np.array(result)
        print(result[:5])
        print(result.shape)
        np.save('nn/anls_result.npy',result)
#         print(result[:5])
#         print(result.shape)

if __name__ == "__main__":
    tf.app.run()