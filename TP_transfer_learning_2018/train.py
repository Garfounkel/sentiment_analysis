from collections import Counter
#from preprocessing import standardization, data_preprocessing
import sys
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
from gensim.models import KeyedVectors
from keras.layers.embeddings import Embedding
from keras.models import Sequential, Model
from keras.utils.np_utils import to_categorical
from sklearn.model_selection import train_test_split
from keras.layers import LSTM, Dropout, Dense, Bidirectional,  Flatten, Input, GRU
import matplotlib as mpl
from keras.optimizers import Adam
import pandas as pd
import numpy

#mpl.use('TkAgg')  # or whatever other backend that you want
#import matplotlib.pyplot as plt
np.random.seed(7)
from keras.models import load_model

from preprocessing import data_preprocessing, data_preprocessing_test

EMBEDDING_FILE="/home/abdou/Téléchargements/GoogleNews-vectors-negative300.bin"
EMBEDDING_DIM=300

corpora_train_3="/home/abdou/Documents/TP_transfer_learning_2018/data/task_A/data_train_3.csv"
corpora_train_7="/home/abdou/Documents/TP_transfer_learning_2018/data/task_A/data_train_7.csv"
corpora_test_7="/home/abdou/Documents/TP_transfer_learning_2018/data/task_A/data_test_7.csv"



tweets_train_3, sentiments_train_3 =  data_preprocessing(corpora_train_3,'train')
tweets_train_7, sentiments_train_7 =  data_preprocessing(corpora_train_7,'test')

all_tweet = tweets_train_3.append(tweets_train_7)


tokenizer = Tokenizer(filters=' ')
tokenizer.fit_on_texts(all_tweet)
word_index = tokenizer.word_index



sequences_train_3 = tokenizer.texts_to_sequences(tweets_train_3)
sequences_train_7 = tokenizer.texts_to_sequences(tweets_train_7)
sequences = sequences_train_3 + sequences_train_7

MAX_SEQUENCE_LENGTH = 0
for elt in sequences:
	if len(elt) > MAX_SEQUENCE_LENGTH:
		MAX_SEQUENCE_LENGTH = len(elt)

print(MAX_SEQUENCE_LENGTH)

data_train_3 = pad_sequences(sequences_train_3, maxlen=MAX_SEQUENCE_LENGTH)
data_train_7 = pad_sequences(sequences_train_7, maxlen=MAX_SEQUENCE_LENGTH)


indices_train_3 = np.arange(data_train_3.shape[0])
data_train_3 = data_train_3[indices_train_3]

indices_train_7 = np.arange(data_train_7.shape[0])
data_train_7 = data_train_7[indices_train_7]

labels_train_3 = to_categorical(np.asarray(sentiments_train_3), 3)
labels_train_3 = labels_train_3[indices_train_3]


nb_words=len(word_index)+1

embedding_matrix = np.zeros((nb_words, EMBEDDING_DIM))
word2vec = KeyedVectors.load_word2vec_format(EMBEDDING_FILE, binary=True)

oov=[]
oov.append((np.random.rand(EMBEDDING_DIM) * 2.0) - 1.0)
oov = oov / np.linalg.norm(oov)


for word, i in word_index.items():
    if word in word2vec.vocab:
        embedding_matrix[i] = word2vec.word_vec(word)
    else:
        embedding_matrix[i] = oov


split_idx = int(len(data_train_3)*0.70)
x_train_3, x_val_3 = data_train_3[:split_idx], data_train_3[split_idx:]
y_train_3, y_val_3 = labels_train_3 [:split_idx], labels_train_3[split_idx:]




print('training set: ' + str(len(x_train_3)) + ' samples')
print('validation set: ' + str(len(x_val_3)) + ' samples')
# print('test set: ' + str(len(x_test)) + ' samples')



embedding_layer = Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=MAX_SEQUENCE_LENGTH,
                            trainable=False, name='embedding_layer')


print('x_train', x_train_3.shape)
print('y_train', y_train_3.shape)


def model1(x_train_3, y_train_3,x_val_3, y_val_3, embedding_layer):

	model1 = Sequential()
	model1.add(embedding_layer)
	model1.add(LSTM(32))
	model1.add(Dropout(0.2))
	model1.add(Dense(32, activation='relu'))
	model1.add(Dropout(0.2))
	model1.add(Dense(3, activation='softmax'))
	model1.compile(loss='categorical_crossentropy',
			      optimizer='Adam',
			      metrics=['acc'])
	model1.summary()
	history=model1.fit(x_train_3, y_train_3, validation_data=(x_val_3, y_val_3),epochs=6, batch_size=50)
	model1.save("./model1.h5")



def model2(x_train_3, y_train_3,x_val_3, y_val_3, embedding_layer,epochs, batch_size):
	model2 = Sequential()
	model2.add(embedding_layer)
	model2.add(GRU(32))
	model2.add(Dropout(0.2))
	model2.add(Dense(3, activation='softmax'))
	model2.compile(loss='categorical_crossentropy',
			      optimizer='rmsprop',
			      metrics=['acc'])
	model2.summary()
	history=model2.fit(x_train_3, y_train_3, validation_data=(x_val_3, y_val_3),epochs=6, batch_size=50)
	model1.save("./model2.h5")


model1(x_train_3, y_train_3,x_val_3, y_val_3, embedding_layer)


# ========================================================================


labels_train_7 = to_categorical(np.asarray(sentiments_train_7), 7)
labels_train_7 = labels_train_7[indices_train_7]


split_idx = int(len(data_train_7)*0.85
)
x_train_7, x_val_7 = data_train_7[:split_idx], data_train_7[split_idx:]
y_train_7, y_val_7 = labels_train_7 [:split_idx], labels_train_7[split_idx:]


print('x_train', x_train_7.shape)
print('y_train', y_train_7.shape)

#, y_train_7, x_val_7,y_train_7)

model=load_model("./model1.h5")
model.summary()
model.layers.pop()
model.layers.pop()
#model.outputs = [model.layers[-1].output]
model.add(Dense(150,activation='relu',name='dense1'))
model.add(Dense(64,activation='relu',name='dense2'))
model.add(Dense(7,activation='softmax',name='dense3'))
model.summary()
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=["accuracy"])
history = model.fit(x_train_7, y_train_7,   validation_data=(x_val_7,y_val_7), epochs=11, batch_size=50)
model.save("./model3.h5")



# ======================================================================

tweets_test_7 =  data_preprocessing_test(corpora_test_7)
sequences_test_7 = tokenizer.texts_to_sequences(tweets_test_7)
data_train_7 = pad_sequences(sequences_test_7, maxlen=MAX_SEQUENCE_LENGTH)
r =model.predict(data_train_7)
data = pd.read_csv("/home/abdou/Documents/datastories-semeval2017-task4-master/dataset/Subtask_A/gold/2018-Valence-oc-En-test-gold.txt", sep='\t', encoding='utf-8')

for i in range(len(r)):
	data['Intensity Class'][i]=["-1: slightly negative emotional state can be inferred",
			            "-2: moderately negative emotional state can be inferred",
			            "-3: very negative emotional state can be inferred",
			            "0: neutral or mixed emotional state can be inferred",
			            "1: slightly positive emotional state can be inferred",
			            "2: moderately positive emotional state can be inferred",
			            "3: very positive emotional state can be inferred"][numpy.argmax(r[i])]

f = open("./submission_after.csv", "w")
f.write("ID	Tweet	Affect Dimension	Intensity Class\n")

for d in range(len(data)):
	f.write(data['ID'][d]+"\t"+data['Tweet'][d]+"\tvalence\t"+data['Intensity Class'][d] + "\n")

f.close()










