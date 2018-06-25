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
tf.app.flags.DEFINE_float("learning_rate",0.01,"learning rate")
tf.app.flags.DEFINE_integer("batch_size", 128, "Batch size for training/evaluating.") #批处理的大小 32-->128
tf.app.flags.DEFINE_integer("decay_steps", 50, "how many steps before decay learning rate.") #6000批处理的大小 32-->128
tf.app.flags.DEFINE_float("decay_rate", 0.5, "Rate of decay for learning rate.") #0.65一次衰减多少
#tf.app.flags.DEFINE_integer("num_sampled",50,"number of noise sampling") #100
tf.app.flags.DEFINE_string("ckpt_dir","model/","checkpoint location for the model")
tf.app.flags.DEFINE_integer("sentence_len",40,"max sentence length")
tf.app.flags.DEFINE_integer("embed_size",200,"embedding size")
tf.app.flags.DEFINE_boolean("is_training",True,"is traning.true:tranining,false:testing/inference")
tf.app.flags.DEFINE_integer("num_epochs",1,"number of epochs to run.")
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
        vocab_size = 2747
        trainX = np.load('nn/model_train.npy')
        trainY = np.load('nn/model_label_train.npy')
        validX = np.load('nn/model_valid.npy')
        validY = np.load('nn/model_label_valid.npy')
        
        trainX = pad_sequences(trainX,FLAGS.sentence_len)
        validX = pad_sequences(validX,FLAGS.sentence_len)

    #2.create session.
    config=tf.ConfigProto()
    config.gpu_options.allow_growth=True
    with tf.Session(config=config) as sess:
        #Instantiate Model
        textCNN=TextCNN(filter_sizes,FLAGS.num_filters,FLAGS.num_classes, FLAGS.learning_rate, FLAGS.batch_size, FLAGS.decay_steps,
                        FLAGS.decay_rate,FLAGS.sentence_len,vocab_size,FLAGS.embed_size,FLAGS.is_training,multi_label_flag=FLAGS.multi_label_flag)
        #Initialize Save
        saver=tf.train.Saver()
        if os.path.exists(FLAGS.ckpt_dir+"cs"):
            print("Restoring Variables from Checkpoint")
            saver.restore(sess,tf.train.latest_checkpoint(FLAGS.ckpt_dir))
        else:
            print('Initializing Variables')
            sess.run(tf.global_variables_initializer())
            if FLAGS.use_embedding: #load pre-trained word embedding
                assign_pretrained_word_embedding(sess,textCNN)
        curr_epoch=sess.run(textCNN.epoch_step)
        #3.feed data & training
        number_of_training_data=len(trainX)
        batch_size=FLAGS.batch_size
        for epoch in range(curr_epoch,FLAGS.num_epochs):
            loss, acc, counter = 0.0, 0.0, 0
            for start, end in zip(range(0, number_of_training_data, batch_size),range(batch_size, number_of_training_data, batch_size)):
                feed_dict = {textCNN.input_x: trainX[start:end],textCNN.dropout_keep_prob: 0.5}
                if not FLAGS.multi_label_flag:
                    feed_dict[textCNN.input_y] = trainY[start:end]
                else:
                    feed_dict[textCNN.input_y_multilabel]=trainY[start:end]
                    
                curr_loss,curr_acc,_=sess.run([textCNN.loss_val,textCNN.accuracy,textCNN.train_op],feed_dict) #curr_acc--->TextCNN.accuracy
                loss,counter,acc=loss+curr_loss,counter+1,acc+curr_acc
             
            print("Epoch %d\tBatch %d\tTrain Loss:%.3f\tTrain Accuracy:%.3f" %(epoch,counter,loss/float(counter),acc/float(counter)))
            print("going to increment epoch counter....")
            sess.run(textCNN.epoch_increment)

            # 4.validation
            print(epoch,FLAGS.validate_every,(epoch % FLAGS.validate_every==0))
            if epoch % FLAGS.validate_every==0:
                eval_acc=do_eval(sess,textCNN,validX,validY,batch_size)
                print("Epoch %d \tValidation Accuracy: %.3f" % (epoch,eval_acc))
                
                if best_valid_acc < eval_acc:
                    print('验证集准确度提高，保存模型！')
                    save_path=FLAGS.ckpt_dir+"model_label.ckpt"
                    saver.save(sess,save_path)
                    best_valid_acc = eval_acc
        
        print('训练完毕，保存模型！')
        save_path=FLAGS.ckpt_dir+"model_label_final.ckpt"
        saver.save(sess,save_path)

                    
def assign_pretrained_word_embedding(sess,textCNN):
    print("using pre-trained word emebedding")
    embedding_matrix = np.load('../../embedding_matrix.npy')
    embedding_matrix = tf.constant(embedding_matrix,tf.float32)
    t_assign_embedding = tf.assign(textCNN.Embedding,embedding_matrix)  # assign this value to our embedding variables of our model.
    sess.run(t_assign_embedding)
    #print("word. exists embedding:", count_exist, " ;word not exist embedding:", count_not_exist)
    print("using pre-trained word emebedding.ended...")

# 在验证集上做验证，报告损失、精确度
def do_eval(sess,textCNN,evalX,evalY,batch_size):
    number_examples=len(evalX)
    eval_acc,eval_counter=0.0,0
    
    for start,end in zip(range(0,number_examples,batch_size),range(batch_size,number_examples,batch_size)):
        curr_eval_acc= sess.run([textCNN.accuracy],#curr_eval_acc--->textCNN.accuracy
                                          feed_dict={textCNN.input_x: evalX[start:end],textCNN.input_y: evalY[start:end]
                                              ,textCNN.dropout_keep_prob:1})
        curr_eval_acc = curr_eval_acc[0]
        eval_counter,eval_acc=eval_counter+1,eval_acc+curr_eval_acc
        
    return eval_acc/float(eval_counter)


if __name__ == "__main__":
    tf.app.run()