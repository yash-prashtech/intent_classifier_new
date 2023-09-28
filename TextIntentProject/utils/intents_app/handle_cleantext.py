import re, string, contractions
from urlextract import URLExtract


contractions.add('mychange', 'my change')
contractions.add('&', 'and')
string_punctuation_custom = string.punctuation.replace('"', '').replace("'", "").replace("'", "").replace('"', '')
extractor = URLExtract()


class CLEANTEXT:
    def __init__(self) -> None:
        pass

    # done
    def quickClean(self, text):
        text = " ".join(str(text).strip().lower().split())
        text = text.encode("ascii", "ignore").decode()
        return text
    
    # done
    def replaceEscapeCharacters(self, text):
        escape_characters = ['\\a', '\\b', '\\f', '\\n', '\\r', '\\t', '\\v', '\\', '\0', '\\0', '\0']
        pattern = '|\\'.join(escape_characters)
        return re.sub(pattern, '', text)

    # done
    def removeURLS(self, text):
        urls = extractor.find_urls(text)
        patterns = [re.compile(r'\b({})\b'.format(string)) for string in urls]
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        return text

    #done
    def removeEmojis(self, text):
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        emoji_set = set(emoji_pattern.findall(text))
        translate_table = dict.fromkeys(map(ord, emoji_set), None)
        return text.translate(translate_table)

    # done
    def removePunctuation(self, text):
        translate_table = text.maketrans("", "", "'\"`")
        text = text.translate(translate_table)
        text = text.replace('.', '. ')
        return text

    # done
    def fixcontractions(self, text):
        return contractions.fix(text)


    def getCleanText(self, clean_text):
        clean_text = self.quickClean(clean_text)
        clean_text = self.removeURLS(clean_text)
        clean_text = re.sub(r'[^\x00-\x7F]+', '', clean_text)
        clean_text = self.replaceEscapeCharacters(clean_text)
        clean_text = self.removeEmojis(clean_text)
        clean_text = self.fixcontractions(clean_text)
        clean_text = self.removePunctuation(clean_text)
        clean_text = " ".join(str(clean_text).strip().lower().split())
        return clean_text



