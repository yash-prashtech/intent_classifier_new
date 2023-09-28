from django.db.models import Q
import pickle, re, os
from urlextract import URLExtract

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from .helpling_function import data_preprocessing

from intents_app.models import TextIntent, TrainModel, OptoutTexts
from utils.intents_app.handle_cleantext import CLEANTEXT 
cleantext_obj = CLEANTEXT()
extractor = URLExtract()
import joblib


class AiTextIntentPredictionModel:
    def __init__(self) -> None: 
        self.model_files_path = "model_files"
        self.unique_intents =  ['interested_general', 'neutral']

    
    # as util method to get only intent instead of full details
    def getOnlyIntent(self, text):
        return self.getPrediction(text)['Intent']
    
    
    #function to handle main logic and other supportive methods
    def getPrediction(self, text):
        check_text = str(text).strip().lower()
        return_dict = {'Text':check_text, "Intent": None, "IntentDetails":{'interested_general': 0.0000, 'neutral': 0.0000, 'opt_out': 0.0000}}
        #check if text has zip code - return interested_general
        if self.is_zip_code(check_text):
            return_dict['Intent'] = 'interested_general'
            return_dict['IntentDetails']['interested_general'] = 1.0000
            return return_dict
        
        #check if text has url - return neutral
        if self.is_url_found_in_text(check_text):
            return_dict['Intent'] = 'neutral'
            return_dict['IntentDetails']['neutral'] =  1.0000
            return return_dict
        
        # need clean text if above both conditions not true
        clean_text = cleantext_obj.getCleanText(check_text)
        clean_text = data_preprocessing(check_text)
    
        print("CLEAN TEXT", clean_text)
        
        # # # check text if under opt_out
        if self.is_optout_text_found(check_text, clean_text):
            return_dict['Intent'] = 'opt_out'
            return_dict['IntentDetails']['opt_out'] =  1.0000
            return return_dict
                
        ## check under text model to see if text match with other intents
        db_qs = TextIntent.objects.values('intent').filter(intent__in=['interested_general',
                                                                       'neutral']).filter(is_approved=True).filter(clean_text__iexact=clean_text).first()
        if db_qs:
            db_intent = db_qs['intent']
            return_dict['Intent'] = db_intent
            if db_intent == 'interested_general':
                return_dict['IntentDetails']['interested_general'] =  1.0000
            elif return_dict['Intent'] == 'neutral':
                return_dict['IntentDetails']['neutral'] =  1.0000
            return return_dict
        
        #last step to check against trained models
        train_model_obj = TrainModel.objects.values('uid', 'model_info').filter(active=True).order_by('-updated')

        if train_model_obj:
            train_model_obj = train_model_obj.first()
            uid = train_model_obj['uid']
            tf_model, tf_tokenizer = self.loadTFModel(uid)
            sk_model, sk_vectorizer = self.loadSKModel(uid)
            #tf_max_length = train_model_obj['model_info']['tf_max_length']
        else:
            sk_model, sk_vectorizer, tf_model, tf_tokenizer = self.loadDefaultModels()
            #tf_max_length = 154 # for default tf model - it will be changed if you replace default model files
        
        try:
            _extra, tf_max_length = tf_model._build_input_shape
            new_seq = tf_tokenizer.texts_to_sequences([check_text])
            padded_new_seq = pad_sequences(new_seq, maxlen=tf_max_length)
            predicted_class_prob = tf_model.predict(padded_new_seq)
            predictions = [round(_, 4) for _ in predicted_class_prob[0]]
            prediction = dict(zip(self.unique_intents, predictions))
            new_prediction_dict = {}
            for key, value in prediction.items():
                new_prediction_dict[key] = float(round(value.item(), 4)) 
            prediction = new_prediction_dict

            predict_intent = max(prediction, key=prediction.get)
            max_prediction_value = prediction[predict_intent] #float(round(prediction[predict_intent].item(), 4))

            if max_prediction_value > 0.70:
                return_dict['Intent'] = predict_intent
                return_dict['IntentDetails'] = new_prediction_dict
                return_dict['IntentDetails']['opt_out'] = 0.0000
                return return_dict
        except:
            pass
        
        # #load SK Model - process the text
        text_vector = sk_vectorizer.transform([check_text])
        prediction = sk_model.predict_proba(text_vector)
        predictions = [round(_, 4) for _ in prediction[0]]
        prediction = dict(zip(sk_model.classes_, predictions))
        return_dict['Intent'] = max(prediction, key=prediction.get)
        return_dict['IntentDetails'] = prediction
        return_dict['IntentDetails']['opt_out'] = 0.0000
        return return_dict

     
        
    #load default sk or tf models incase if no custom models found
    def loadDefaultModels(self):
        with open( f"voting_vectorizer_with_stopwords.pkl", 'rb') as fobj:
            sk_vectorizer = joblib.load(fobj)
        
        
        with open(f"voting_classifier_with_stopwords.pkl", 'rb') as fobj:
            sk_model = joblib.load(fobj)
        
        with open( f"{self.model_files_path}/tf_tokenizer.pkl", 'rb') as fobj:
            tf_tokenizer = pickle.load(fobj)
    
        tf_model = load_model(f"{self.model_files_path}/tf_model.h5")
        # print("model loaded successfully")
        # print("Predict", sk_model.predict(sk_vectorizer.transform("Hello")))
        return sk_model, sk_vectorizer, tf_model, tf_tokenizer        


    # method to load TF model - trained one or default one
    def loadTFModel(self, uid):
        model_fp = f"{ self.model_files_path}/{uid}_tf_model.h5"
        tokenizer_fp = f"{ self.model_files_path}/{uid}_tf_tokenizer.pkl"
        if os.path.exists(model_fp) and os.path.exists(tokenizer_fp):
            tf_model =  load_model(model_fp)
            tf_tokenizer = pickle.load(open(tokenizer_fp, 'rb')) 
            return tf_model, tf_tokenizer

        sk_model, sk_vectorizer, tf_model, tf_tokenizer = self.loadDefaultModels()
        return tf_model, tf_tokenizer
     
    
    # method to load SK model - trained one or default one
    def loadSKModel(self, uid):
        model_fp = f"model_files/{uid}_sk_model.pkl"
        vectorizer_fp = f"model_files/{uid}_sk_vectorizer.pkl"
        if os.path.exists(model_fp) and os.path.exists(vectorizer_fp):
            sk_model = pickle.load(open(model_fp, 'rb')) 
            sk_vectorizer = pickle.load(open(vectorizer_fp, 'rb')) 
            return  sk_model, sk_vectorizer
        
        sk_model, sk_vectorizer, tf_model, tf_tokenizer = self.loadDefaultModels()
        return sk_model, sk_vectorizer
     

    #used to see, if text is opt_out or not
    def is_optout_text_found(self, text, clean_text):
        opt_out_qs = list(OptoutTexts.objects.filter(status=True).values_list('text', 'filter_type'))
        all_clean_texts = []
        all_clean_texts.extend([t[0] for t in opt_out_qs])
        all_clean_texts = set(all_clean_texts)
        matching_elements = {clean_text} & all_clean_texts
        if bool(matching_elements): 
            return True

        contains_values =  []
        contains_values.extend([t[0] for t in opt_out_qs if t[1]=='contains'])
        if any(val in text for val in contains_values):
            return True

        return False
    
    #helping util
    def is_url_found_in_text(self, text):
        urls = extractor.find_urls(text)
        return True if len(urls) > 0 else False

    #helping util
    def is_zip_code(self, text):
        zip_code_pattern = re.compile(r'\b\d{5}(?:[-\s]\d{4})?\b')
        return True if zip_code_pattern.search(text) else False
        
        