# -*- coding: utf-8 -*-
"""sentiment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1goCnukbc87UA6IZWSI_qJAjdnXmOLPOv
"""

import tensorflow as tf
tf.enable_eager_execution()
import pandas as pd
import re
import numpy as np

stopwords = pd.read_csv("stopwords-bn.txt",header=None)
stopwords = stopwords.values

df = pd.read_excel('/content/Cricket.xlsx')
comm = df.Text
info = df.Polarity
data = df[['Text','Polarity']]
data = data.values
print(data)
for sent in data:
  sent[0] = sent[0].replace("।"," ")
  sent[0] = sent[0].replace("\xa0"," ")
  sent[0] = sent[0].replace("  "," ")
  sent[0] = re.sub(r'[১২৩৪৫৬৭৮৯০]',r'', sent[0])
  for word in stopwords:
    token = " " + word[0] + " "
    sent[0] = sent[0].replace(token, " ")
    sent[0] = sent[0].replace("  ", " ")
print(data)
df = pd.read_excel('/content/Restaurant.xlsx')
dt = df[['Text','Polarity']]
dt = dt.values
for sent in dt:
  sent[0] = sent[0].replace("।"," ")
  sent[0] = sent[0].replace("\xa0"," ")
  sent[0] = sent[0].replace("  "," ")
  sent[0] = re.sub(r'[১২৩৪৫৬৭৮৯০]',r'', sent[0])
  for word in stopwords:
    token = " " + word[0] + " "
    sent[0] = sent[0].replace(token, " ")
    sent[0] = sent[0].replace("  ", " ")
data = np.append(data,dt,axis=0)

'''
neg = pd.read_csv('/content/bangla_lexicon_neg.txt')
neg = neg.values.tolist()
for w in neg:
  w[0] = re.sub(r'[\x00-\xff]',r'', w[0])
  w.append('negative')
neg = np.asarray(neg)
np.append(data,neg,axis=0)
pos = pd.read_csv('/content/bangla_lexicon_pos.txt')
pos = pos.values.tolist()
for w in pos:
  w[0] = re.sub(r'[\x00-\xff]',r'', w[0])
  w.append('positive')
pos = np.asarray(pos)
data = np.append(data,pos,axis=0)
print(len(data))
'''

np.random.shuffle(data)
training, test = data[:3754,:], data[3754:,:]
print(test)

neg = pd.read_csv('/content/bangla_lexicon_neg.txt')
neg = neg.values.tolist()
for w in neg:
  w[0] = re.sub(r'[\x00-\xff]',r'', w[0])
  w.append('negative')
neg = np.asarray(neg)
training = np.append(training,neg,axis=0)
pos = pd.read_csv('/content/bangla_lexicon_pos.txt')
pos = pos.values.tolist()
for w in pos:
  w[0] = re.sub(r'[\x00-\xff]',r'', w[0])
  w.append('positive')
pos = np.asarray(pos)
training = np.append(training,pos,axis=0)

training_sent = []
training_label = []
testing_sent = []
testing_label = []
for s,l in training:
  training_sent.append(s)
  training_label.append(l)
for s,l in test:
  testing_sent.append(s)
  testing_label.append(l)

train_label = []
for l in training_label:
  if l == "negative":
    train_label.append(0)
  else:
    train_label.append(1)
test_label = []
for l in testing_label:
  if l == "negative":
    test_label.append(0)
  else:
    test_label.append(1)
train_label = np.array(train_label)
test_label = np.array(test_label)
print(len(test_label))

vocab = 8000
embedding_dim = 64
maxlen = 200
trunc_type = 'post'
oov_tok = '<OOV>'
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
tokenizer = Tokenizer(num_words = vocab, oov_token = oov_tok)
tokenizer.fit_on_texts(training_sent)
word_index = tokenizer.word_index

print(len(word_index))

print(word_index)
a = list(word_index.keys())
ids = a.index('<OOV>')
del(a[ids])
def listToDict(lst):
    op = { wrd : indx+1 for indx,wrd in enumerate(lst) }
    return op
with open("/content/file.txt", 'w') as f:
  for s in a:
      f.write(str(s) + '\n')

with open("/content/fileW.txt", 'r') as f:
  a = [line.rstrip('\n') for line in f]
a.insert(0,'<OOV>') 
word_index = listToDict(a)
print(word_index)
with open("/content/file2.txt", 'r') as f:
  a = [line.rstrip('\n') for line in f]
for w in range(len(a)):
  a[w] = a[w].replace("[","")
  a[w] = a[w].replace("]","")
  a[w] = a[w].replace("'","")
  a[w] = a[w].replace(" ","")
  a[w] = a[w].split(",")
print(a)
tokenizer.word_index = word_index
for s in range(len(training_sent)):
  for w in a:
    if w[0] in training_sent[s]:
      training_sent[s] = training_sent[s].replace(w[0],w[1])

sequence = tokenizer.texts_to_sequences(training_sent)
padded = pad_sequences(sequence,maxlen=maxlen,truncating=trunc_type)
testing_sequence = tokenizer.texts_to_sequences(testing_sent)
testing_padded = pad_sequences(testing_sequence,maxlen=maxlen,truncating=trunc_type)

model = tf.keras.Sequential([
                             tf.keras.layers.Embedding(vocab, embedding_dim, input_length=maxlen),
                             tf.keras.layers.Conv1D(32,3,activation='relu'),
                             tf.keras.layers.Conv1D(32,3,activation='relu'),
                             tf.keras.layers.Conv1D(32,3,activation='relu'),
                             tf.keras.layers.MaxPooling1D(2),
                             tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(512)),
                             tf.keras.layers.Dense(256, activation='relu'),
                             tf.keras.layers.Dropout(0.2),
                             tf.keras.layers.Dense(256, activation='relu'),
                             tf.keras.layers.Dropout(0.2),
                             tf.keras.layers.Dense(256, activation='relu'),
                             tf.keras.layers.Dropout(0.2),
                             tf.keras.layers.Dense(256, activation='relu'),
                             tf.keras.layers.Dropout(0.2),
                              tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
model.summary()

num_epochs = 10
history = model.fit(padded, train_label, epochs=num_epochs, validation_data=(testing_padded, test_label))

sent = ["খাবার"]
seq = tokenizer.texts_to_sequences(sent)
pad = pad_sequences(seq,maxlen=maxlen,truncating=trunc_type)
model.predict(pad)

model.save_weights("nlpmodel.h5")

print(history.history['val_loss'])
print(history.history['loss'])
re = [1.574427905,1.447600619,1.023229094,1.007175722,0.811034,0.896866817,0.673351567,0.262382034,0.119623855,0.451675643,]
print(re)

import matplotlib.pyplot as plt
acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']


epochs = range(len(acc))

plt.plot(epochs, acc, 'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()

plt.plot(epochs, loss, 'r', label='Training Loss')
plt.plot(epochs, val_loss, 'b', label='Validation Loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()

e = model.layers[0]
weights = e.get_weights()[0]
print(weights.shape)

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])
import io

out_v = io.open('vecsmlstm2.tsv', 'w', encoding='utf-8')
out_m = io.open('metamlstm2.tsv', 'w', encoding='utf-8')
for word_num in range(1, 7871):
  word = reverse_word_index[word_num]
  embeddings = weights[word_num]
  out_m.write(word + "\n")
  out_v.write('\t'.join([str(x) for x in embeddings]) + "\n")
out_v.close()
out_m.close()

try:
  from google.colab import files
except ImportError:
  pass
else:
  files.download('vecsmlstm2.tsv')
  files.download('metamlstm2.tsv')