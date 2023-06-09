# -*- coding: utf-8 -*-
"""VGG-19.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ao_uR8iWNP3HSdTuG8kPdHrJMRobs57L
"""

import os
import cv2
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import keras
import tensorflow

from tensorflow.keras.models import Model
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.applications import VGG19
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Input, Lambda, Dense, Flatten, Dropout, BatchNormalization, Activation

from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, recall_score, precision_score, f1_score

from google.colab import drive

drive.mount('/content/drive')

train_path = '/content/drive/MyDrive/Colab Notebooks/DATA(VGG-19)/train2.0'
test_path = '/content/drive/MyDrive/Colab Notebooks/DATA(VGG-19)/test'
val_path = '/content/drive/MyDrive/Colab Notebooks/DATA(VGG-19)/val'

val_path

os.listdir(train_path)

for folder in os.listdir(train_path):
    sub_path = train_path + "/" + folder
    print(folder)
    # img = os.listdir(sub_path)
    # print(img)
    
    for i in range(2):
        temp_path = os.listdir(sub_path)[i]
        temp_path = sub_path + "/" + temp_path
        print(temp_path)
        img = mpimg.imread(temp_path)
        imgplot = plt.imshow(img)
        plt.show()

def imagearray(path, size):
    data = []
    for folder in os.listdir(path):
        sub_path=path+"/"+folder
        print(sub_path)

        for img in os.listdir(sub_path):
            image_path=sub_path+"/"+img
            img_arr=cv2.imread(image_path)
            img_arr=cv2.resize(img_arr, size)
            data.append(img_arr)
            
    return data

# for folder in os.listdir(test_path):
#         sub_path=test_path+"/"+folder
#         # print(sub_path)
#         for img in os.listdir(sub_path):
#             image_path=sub_path+"/"+img
#             # print(image_path)
#             img_arr=cv2.imread(image_path)
#             print(img_arr)

size = (250,250)

train = imagearray(train_path, size)
test = imagearray(test_path, size)
val = imagearray(val_path, size)

x_train = np.array(train)
x_test = np.array(test)
x_val = np.array(val)

x_val

x_train = x_train/255.0
x_test = x_test/255.0
x_val = x_val/255.0

x_test

def data_class(data_path, size, class_mode):
    datagen = ImageDataGenerator(rescale = 1./255)
    classes = datagen.flow_from_directory(data_path,
                                          target_size = size,
                                          batch_size = 32,
                                          class_mode = class_mode)
    return classes

train_class = data_class(train_path, size, 'sparse')
test_class = data_class(test_path, size, 'sparse')
val_class = data_class(val_path, size, 'sparse')

train_class.classes

y_train = train_class.classes
y_test = test_class.classes
y_val = val_class.classes

y_test

train_class.class_indices

y_train.shape,y_test.shape,y_val.shape

x_train.shape,x_test.shape,x_val.shape

vgg = VGG19(input_shape = (250, 250, 3), weights = 'imagenet', include_top = False)

for layer in vgg.layers:
    layer.trainable = False

x = Flatten()(vgg.output)
prediction = Dense(5, activation='softmax')(x)

model = Model(inputs=vgg.input, outputs=prediction)
model.summary()
model.compile(
  loss='sparse_categorical_crossentropy',
  optimizer="adam",
  metrics=['accuracy']
)

plot_model(model=model, show_shapes=True)

early_stop = EarlyStopping(monitor = 'val_loss', mode='min', verbose = 1, patience = 5)

history = model.fit(x_train, y_train, validation_data = (x_val, y_val), epochs = 10, callbacks=[early_stop], batch_size = 30,
                    shuffle=True)

plt.figure(figsize=(5, 5))
plt.plot(history.history['accuracy'], label='train acc')
plt.plot(history.history['val_accuracy'], label='val acc')
plt.legend()
plt.title('Accuracy')
plt.show()

plt.figure(figsize=(5, 5))
plt.plot(history.history['loss'], label='train loss')
plt.plot(history.history['val_loss'], label='val loss')
plt.legend()
plt.title('Loss')
plt.show()

model.evaluate(x_test, y_test, batch_size=32)

y_pred = model.predict(x_test)

y_pred=np.argmax(y_pred,axis=1)

print(classification_report(y_pred,y_test))

cm = confusion_matrix(y_pred,y_test)

plt.figure(figsize=(5, 3))
ax = plt.subplot()
sns.set(font_scale=2.0)
sns.heatmap(cm, annot=True, fmt='g', cmap="Blues", ax=ax); 

# labels, title and ticks
ax.set_xlabel('Predicted labels', fontsize=20);ax.set_ylabel('True labels', fontsize=20); 
ax.set_title('Confusion Matrix', fontsize=20); 
# ax.xaxis.set_ticklabels(['Grade-A', 'Grade-B', 'Grade-C'], fontsize=20); ax.yaxis.set_ticklabels(['Grade-A', 'Grade-B', 'Grade-C'], fontsize=20);

