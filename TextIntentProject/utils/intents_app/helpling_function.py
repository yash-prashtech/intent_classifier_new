import re
import contractions
import string
# import spacy


# nlp= spacy.load('en_core_web_sm', disable=["parser", "ner"])
# spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
exclude=string.punctuation

def is_valid_zip_code(zip_code):
    # Define regular expressions for 5-digit and 9-digit ZIP codes
    zip_code_pattern = r'\d{5}'
    
    result = re.sub(zip_code_pattern, "zip_code", zip_code)
    return result

def replace_urls_with_placeholder(text):
    # Define a regular expression pattern for URLs
    url_pattern = r'(https?://\S+|www\.\S+)'

    # Use re.sub() to replace URLs with "<URL>"
    result_text = re.sub(url_pattern, '<url>', text)

    return result_text

def replace_emails_with_placeholder(text):
    # Define a regular expression pattern for email addresses
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    # email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    # Use re.sub() to replace email addresses with "<email>"
    result_text = re.sub(email_pattern, '<email>', text)

    return result_text

    
def replace_mobile_numbers_with_placeholder(text):
    # Define a regular expression pattern for mobile numbers starting with "001"
    mobile_number_pattern = r'(001|\+1|\+001)( ?\d{10}|\s?\(\d{3}\)\s?\d{3}-\d{4})'

    # Use re.sub() to replace mobile numbers with "<mobile_num>"
    result_text = re.sub(mobile_number_pattern, '<mobile_num>', text)

    return result_text



def replace_time_with_placeholder(text):
    # Define regular expression pattern for time or time ranges
    time_pattern = r'(\d{1,2}(?: ?(?:am|pm))?)(?: ?- ?(\d{1,2}(?: ?(?:am|pm))))?'

    # Use re.sub() to find and replace times with "<time>"
    result_text = re.sub(time_pattern, '<time>', text)

    return result_text

def replace_prices_with_placeholder(text):
    # Define a regular expression pattern for prices or price ranges with decimal values
    price_pattern = r'\$\d+(\.\d{1,2})?(?:\s?-?\s?\$\d+(\.\d{1,2})?)?'

    # Use re.sub() to find and replace prices with "<PRICE>"
    result_text = re.sub(price_pattern, '<price>', text)

    return result_text


    
def replace_dates_with_placeholder(date_str):
    # Define a regular expression pattern for all supported date formats
    date_pattern = r'\b\d{1,2}[-/| ]\d{1,2}[-/| ](?:\d{2}|\d{4})\b|\b\d{6}\b'
    
    # Use re.sub() to find and replace all date formats with "date"
    result_str = re.sub(date_pattern, '<date>', date_str)
    
    return result_str

def expand_words(text):
    converted_text = contractions.fix(text)
    return converted_text
  
# words_to_remove = {"against","nor","call","me", "no", "not", "out", "please" , "myself", "alone", "both", "neither", "nothing", "never", "do", "me", "mine", "my" ,"already", "too", "much"}
# for words in words_to_remove:
#     spacy_stopwords.remove(words)

def remove_emojis(text):
    # Define a regular expression pattern to match emojis
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # Emojis from emoticons
                               u"\U0001F300-\U0001F5FF"  # Miscellaneous symbols and pictographs
                               u"\U0001F680-\U0001F6FF"  # Transport and map symbols
                               u"\U0001F700-\U0001F77F"  # Alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric shapes
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U0001F004-\U0001F0CF"  # Additional emoticons
                               u"\U0001F170-\U0001F251"  # Enclosed characters
                               "]+", flags=re.UNICODE)

    # Use the sub method to replace all matching emojis with an empty string
    text_without_emojis = emoji_pattern.sub(r'', text)
    
    return text_without_emojis

def data_preprocessing(data):

    #Lowering text
    data = data.lower().strip()

    data = expand_words(data)
    

    data = remove_emojis(data)
    # print("DATA==> ", data)
    data = replace_emails_with_placeholder(data)
    data = replace_urls_with_placeholder(data)
    
    data = replace_mobile_numbers_with_placeholder(data)
    data = replace_dates_with_placeholder(data)
    data = replace_prices_with_placeholder(data)
    data = is_valid_zip_code(data)
    data = replace_time_with_placeholder(data)

    data = replace_prices_with_placeholder(data)

    #remove punctuation
    data = data.translate(str.maketrans('','',exclude))


    ## remove stopwords
    # data = " ".join([word for word in str(data).split() if word not in spacy_stopwords])

    
    #tokenization & numbers will be removed
    only_letters = re.sub("[^a-zA-Z]", " ",data)

    return only_letters.replace("  ","").strip()


# print(data_preprocessing("+1 (727) 365-6019"))
