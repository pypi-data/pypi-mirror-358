# custom_pyvi/ViTokenizer.py

import os
import codecs
import pickle
import re
import string
import unicodedata

class ViTokenizer:
    # --- 1. Tải tài nguyên một lần duy nhất khi khởi tạo ---
    try:
        _current_dir = os.path.dirname(os.path.abspath(__file__))
        _model_path = os.path.join(_current_dir, 'models/pyvi3.pkl')
        with open(_model_path, 'rb') as f:
            model = pickle.load(f)

        _words_path = os.path.join(_current_dir, 'models/words.txt')
        mono_grams = set()
        bi_grams = set()
        tri_grams = set()
        with codecs.open(_words_path, 'r', encoding='utf-8') as f:
            for token in f.read().split('\n'):
                token = token.strip()
                n = len(token.split(' '))
                if n == 1:
                    mono_grams.add(token)
                elif n == 2:
                    bi_grams.add(token)
                elif n == 3:
                    tri_grams.add(token)
    except FileNotFoundError as e:
        raise IOError(f"Lỗi nghiêm trọng: Không tìm thấy file model hoặc words.txt. "
                      f"Hãy đảm bảo thư mục 'models' chứa 'pyvi3.pkl' và 'words.txt'. Lỗi: {e}")
    except Exception as e:
        raise IOError(f"Lỗi không xác định khi tải model của ViTokenizer: {e}")

    @staticmethod
    def sylabelize(text: str) -> list:
        text = unicodedata.normalize('NFC', text)
        product_codes = r"\b([bB]{1}[bB]?\d{2}|[tT]ogo)\b"
        datetime_pattern = r"\d{1,2}/\d{1,2}(/\d{2,4})?"
        email = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        web = r"\w+://[^\s]+"
        word = r"\w+"
        non_word = r"[^\w\s]"
        patterns = [product_codes, web, email, datetime_pattern, word, non_word]
        patterns_re = re.compile("(" + "|".join(patterns) + ")", re.UNICODE)
        return [match[0] if isinstance(match, tuple) else match for match in patterns_re.findall(text)]

    @staticmethod
    def word2features(sent: list, i: int) -> dict:
        word = sent[i]
        prev_word = sent[i-1] if i > 0 else "#"
        next_word = sent[i+1] if i < len(sent)-1 else "#"
        prev2_word = sent[i-2] if i > 1 else "#"
        next2_word = sent[i+2] if i < len(sent)-2 else "#"

        bigram_prev = ' '.join([prev_word, word]).lower()
        bigram_next = ' '.join([word, next_word]).lower()
        trigram = ' '.join([prev_word, word, next_word]).lower()

        features = {
            'bias': 1.0,
            'word.lower()': word.lower(),
            'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(),
            'word.isdigit()': word.isdigit(),

            'prev_word.lower()': prev_word.lower(),
            'prev_word.istitle()': prev_word.istitle(),

            'next_word.lower()': next_word.lower(),
            'next_word.istitle()': next_word.istitle(),

            'is_mono_gram': word.lower() in ViTokenizer.mono_grams,
            'is_bi_gram_prev': bigram_prev in ViTokenizer.bi_grams,
            'is_bi_gram_next': bigram_next in ViTokenizer.bi_grams,
            'is_tri_gram': trigram in ViTokenizer.tri_grams,
        }
        return features

    @staticmethod
    def sent2features(sent: list) -> list:
        return [ViTokenizer.word2features(sent, i) for i in range(len(sent))]

    @staticmethod
    def tokenize(text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        syllables = ViTokenizer.sylabelize(text)
        if not syllables:
            return text
        features = ViTokenizer.sent2features(syllables)
        labels = ViTokenizer.model.predict([features])[0]
        output = syllables[0]
        for i in range(1, len(syllables)):
            if (labels[i] == 'I_W') and (syllables[i] not in string.punctuation):
                output += '_' + syllables[i]
            else:
                output += ' ' + syllables[i]
        return output
