import pandas as pd 
from django.db.models import Count
from django.utils import timezone

import numpy as np

import tensorflow as tf #2.11.0
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import nltk
import numpy as np
import pickle
from nltk.metrics import accuracy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import f1_score, accuracy_score, classification_report
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import  MLPClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

from intents_app.models import TextIntent
from intents_app.models import TextIntent, TrainModel


class IntentTrainModel:
    def __init__(self, uid) -> None: 
        self.uid = uid
        self.model_files_path = 'model_files'
        self.unique_intents =  ['interested_general', 'neutral']
        
    def train_model(self):
        train_model_obj, texts_list, clean_texts_list, intents_list = self.return_data_from_db()
        model_info = {
                "tf_loss": "",
                "tf_accuracy": "",
                "tf_max_length": "",
                "sk_accuracy": ""
            }
        
        sk_accuracy = self.trainSKModel(texts_list, intents_list)
        tf_dict = self.trainTFModel(texts_list, intents_list)
        model_info['sk_accuracy'] = round(sk_accuracy, 4)
        model_info['tf_loss'] = round(tf_dict['tf_loss'], 4)
        model_info['tf_accuracy'] = round(tf_dict['tf_accuracy'], 4)
        model_info['tf_max_length'] = tf_dict['tf_max_length']

        # save the database obj
        train_model_obj.model_status = 'trained'
        train_model_obj.model_info = model_info
        if train_model_obj.active:
            TrainModel.objects.exclude(uid=self.uid).update(active=False, updated=timezone.now())
        train_model_obj.save()
        return None
    
    #method to load data from database, split and return
    def return_data_from_db(self):
        intents_list = [TextIntent.TEXT_INTENT.INTERESTED_GENERAL, TextIntent.TEXT_INTENT.Neutral]
        train_model_obj = TrainModel.objects.get(uid=self.uid)
        train_on = train_model_obj.train_on
        textintent_qs = TextIntent.objects.filter(intent__in=intents_list).filter(is_approved=True).values_list('text', 'clean_text', 'intent')

        if train_on == 'full':
            textintent_qs = TextIntent.objects.filter(intent__in=intents_list).filter(is_approved=True).values_list('text', 'clean_text', 'intent')
        else:
            minimum_intent_objects_number = TextIntent.objects.filter(intent__in=intents_list).filter(is_approved=True).values('intent').annotate(count=Count('id')).order_by()
            minimum_intent_objects_number = min(minimum_intent_objects_number, key=lambda x:x['count'])['count']
            interested_general_qs = TextIntent.objects.filter(intent=intents_list[0]).filter(is_approved=True).values_list('text', 'clean_text', 'intent')[:minimum_intent_objects_number]
            neutral_qs = TextIntent.objects.filter(intent=intents_list[1]).filter(is_approved=True).values_list('text', 'clean_text', 'intent')[:minimum_intent_objects_number]
            textintent_qs = interested_general_qs.union(neutral_qs)
            
        texts_list = []
        clean_texts_list = []
        intents_list = []

        for _ in textintent_qs:
            words_len =  len(_[1].split())
            if words_len > 1:
                texts_list.append(_[0])
                clean_texts_list.append(_[1])
                intents_list.append(_[2])
                
        
        return train_model_obj, texts_list, clean_texts_list, intents_list
    
    
    #method to train SK model and save into pickle files for later use
    def trainSKModel(self, texts_list, intents_list):
        # vectorizer = CountVectorizer()
        # vectorizer.fit(texts_list)
        # X_vectors = vectorizer.transform(texts_list)
        # model = LogisticRegression(max_iter=999)
        # model.fit(X_vectors, intents_list)
        
        vectorizer = TfidfVectorizer()
        vectorizer.fit(texts_list)
        X_vectors = vectorizer.transform(texts_list)
        classifier = LogisticRegression(penalty="l2", C=10, max_iter=999)
        rf_classifier = RandomForestClassifier(n_estimators=500)
        svm = SVC(kernel="rbf",C=50, probability=True)
        dt_classifier = DecisionTreeClassifier()
        mlp_classifier_ = MLPClassifier(epsilon=0.001, hidden_layer_sizes=500, activation="relu")

        estimator = [("LR", classifier), ("RF", rf_classifier), ("MLP", mlp_classifier_), ("SVM", svm), ("DT", dt_classifier)]
        model = VotingClassifier(estimators=estimator, voting="soft",)
        model.fit(X_vectors, intents_list)
        #saving data
        pickle.dump(vectorizer, open(f"{self.model_files_path}/{self.uid}_sk_vectorizer.pkl", 'wb'))
        pickle.dump(model, open(f"{self.model_files_path}/{self.uid}_sk_model.pkl", 'wb'))
        
        # Evaluate classifier
        predictions = model.predict(X_vectors)
        accuracy = accuracy_score(intents_list, predictions)
        print("Accuracy:", accuracy)
        return accuracy

    
    #method to train TF model and save into pickle/h5 files for later use
    def trainTFModel(self, texts_list, intents_list):
        # Tokenize text
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(texts_list)
        sequences = tokenizer.texts_to_sequences(texts_list)

        # Pad sequences
        max_length = max([len(seq) for seq in sequences])
        padded_sequences = pad_sequences(sequences, maxlen=max_length)
        #print(max_length, len(padded_sequences))

        # Split dataset into training and testing sets
        train_size = int(len(texts_list) * 0.80)
        X_train = padded_sequences[:train_size]
        X_test = padded_sequences[train_size:]

        # Create labels
        intents = intents_list
        unique_intents = self.unique_intents

        # unique_intents = list(set(intents))
        num_intents = len(unique_intents)
        y_train = np.array([unique_intents.index(intent) for intent in intents[:train_size]])
        y_test = np.array([unique_intents.index(intent) for intent in intents[train_size:]])
        # print(y_train, y_test)
        # print(len(tokenizer.word_index))

        # Define model architecture
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=2, input_length=max_length),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(units=num_intents, activation='softmax')
        ])

        # Compile the model  such as 'adam' 'adagrad', 'adadelta', 'rmsprop',
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        model.fit(X_train, y_train, epochs=8, batch_size=32, verbose=0)

        # Evaluate the model on the test set
        test_loss, test_acc = model.evaluate(X_test, y_test)
        print('loss | accuracy:', test_loss, test_acc )

        
        #saving model and tokenizer
        model.save(f"{self.model_files_path}/{self.uid}_tf_model.h5")
                    
        with open(f"{self.model_files_path}/{self.uid}_tf_tokenizer.pkl", 'wb') as handle:
            pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        return {
                "tf_loss": test_loss,
                "tf_accuracy": test_acc,
                "tf_max_length": max_length
            }


    #text method - check it later if it can improve then replace with main method
    def trainAndSaveModel_test(self, texts_list, intents_list):
        test_data = list(zip(texts_list[4000:4300], intents_list[4000:4300]))

        texts_list = texts_list[:4000]
        intents_list = intents_list[:4000]
        training_data = list(zip(texts_list, intents_list))
        
        # Tokenize the text and extract relevant features
        stop_words = set(stopwords.words('english'))
        training_data = [(word_tokenize(text.lower()), intent) for text, intent in training_data]
        training_data = [([word for word in text if word not in stop_words], intent) for text, intent in training_data]

        # Convert the data into a format that can be used for training
        texts, intents = zip(*training_data)
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform([' '.join(text) for text in texts])

        # Train the model
        classifier = MultinomialNB()
        classifier.fit(X, intents)
        
        test_texts, test_intents = zip(*test_data)
        X_test = vectorizer.transform(test_texts)
        test_predictions = classifier.predict(X_test)

        # Calculate the accuracy score
        accuracy = accuracy_score(test_intents, test_predictions)
        #print("Accuracy:", accuracy)
