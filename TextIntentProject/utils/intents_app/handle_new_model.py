import joblib, re, os


def loadNewModel():
    with open( f"voting_vectorizer_with_stopwords.pkl", 'rb') as fobj:
        sk_vectorizer = joblib.load(fobj)
        
    print("Vectorizer loaded", sk_vectorizer)



 #load default sk or tf models incase if no custom models found
def loadDefaultModels(self):
    with open( f"voting_vectorizer_with_stopwords.pkl", 'rb') as fobj:
        sk_vectorizer = joblib.load(fobj)
    
    with open(f"voting_classifier_with_stopwords.pkl", 'rb') as fobj:
        sk_model = joblib.load(fobj)
 