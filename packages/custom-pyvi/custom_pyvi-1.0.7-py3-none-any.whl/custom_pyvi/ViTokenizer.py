# -*- coding: utf-8 -*-

"""
ViTokenizer.py: Một thư viện tách từ Tiếng Việt tùy chỉnh dựa trên mô hình CRF.

Module này cung cấp một công cụ tách từ Tiếng Việt mạnh mẽ. Nó sử dụng mô hình
Hồi quy Điều kiện Ngẫu nhiên (Conditional Random Fields - CRF) được huấn luyện
với một bộ từ điển tùy chỉnh để thực hiện việc tách từ.
"""

import os
import codecs
import pickle
import re
import string
import unicodedata as ud
from typing import List, Dict, Tuple, Set

# Thư viện này cần được cài đặt qua pip: pip install sklearn-crfsuite
try:
    import sklearn_crfsuite
except ImportError:
    raise ImportError(
        "Thư viện sklearn-crfsuite chưa được cài đặt. Vui lòng chạy lệnh: "
        "'pip install sklearn-crfsuite'"
    )


class ViUtils:
    """
    Một tập hợp các hàm tiện ích để xử lý văn bản Tiếng Việt.
    """

    @staticmethod
    def remove_accents(text: str) -> str:
        """
        Loại bỏ dấu câu Tiếng Việt khỏi một chuỗi văn bản.

        Tham số:
            text (str): Chuỗi văn bản đầu vào (có dấu).

        Trả về:
            str: Chuỗi văn bản đã được loại bỏ dấu.
        """
        normalized_text = ud.normalize('NFD', text)
        s = ''.join(c for c in normalized_text if ud.category(c) != 'Mn')
        s = s.replace('đ', 'd').replace('Đ', 'D')
        return s


class ViTokenizer:
    """
    Lớp (class) Tách từ Tiếng Việt.
    """

    def __init__(self, model_path: str = None, words_path: str = None):
        """
        Hàm khởi tạo của ViTokenizer.

        Tham số:
            model_path (str, tùy chọn): Đường dẫn tới file model (.pkl). 
                Mặc định là 'custom_pyvi/models/custom_pyvi3.pkl'.
            words_path (str, tùy chọn): Đường dẫn tới file từ điển.
                Mặc định là 'custom_pyvi/models/custom_words.txt'.
        """
        _current_dir = os.path.dirname(os.path.abspath(__file__))

        if model_path is None:
            model_path = os.path.join(_current_dir, 'models', 'custom_pyvi3.pkl')
        
        if words_path is None:
            words_path = os.path.join(_current_dir, 'models', 'custom_words.txt')

        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Không tìm thấy file model tại: {model_path}")
        except Exception as e:
            raise IOError(f"Lỗi khi nạp file model: {e}")

        self.mono_grams, self.bi_grams, self.tri_grams = self._load_words(words_path)

    def _load_words(self, path: str) -> Tuple[Set[str], Set[str], Set[str]]:
        """Nạp các từ và cụm từ từ file từ điển vào bộ nhớ."""
        mono_grams, bi_grams, tri_grams = set(), set(), set()
        try:
            with codecs.open(path, 'r', encoding='utf-8') as f:
                for token in f:
                    token = token.strip().lower()
                    if not token:
                        continue
                    n_words = token.count(' ') + 1
                    if n_words == 1: mono_grams.add(token)
                    elif n_words == 2: bi_grams.add(token)
                    elif n_words == 3: tri_grams.add(token)
        except FileNotFoundError:
            print(f"Cảnh báo: Không tìm thấy file từ điển tại {path}. "
                  "Bộ tách từ sẽ chỉ dựa vào mô hình.")
        return mono_grams, bi_grams, tri_grams

    def _word2features(self, sent: List[str], i: int) -> Dict[str, any]:
        """Trích xuất các đặc trưng cho một âm tiết trong câu."""
        word = sent[i]
        prev_word = sent[i-1] if i > 0 else "#"
        next_word = sent[i+1] if i < len(sent)-1 else "#"
        prev_2_word = sent[i-2] if i > 1 else "#"
        next_2_word = sent[i+2] if i < len(sent)-2 else "#"
        bigram_prev = ' '.join([prev_word, word]).lower()
        bigram_next = ' '.join([word, next_word]).lower()
        trigram = ' '.join([prev_word, word, next_word]).lower()
        
        features = {
            'bias': 1.0, 'word.lower()': word.lower(), 'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(), 'word.isdigit()': word.isdigit(),
            'prev_word.lower()': prev_word.lower(), 'next_word.lower()': next_word.lower(),
            'prev_2_word.lower()': prev_2_word.lower(), 'next_2_word.lower()': next_2_word.lower(),
            'is_mono_gram': word.lower() in self.mono_grams,
            'is_bi_gram_prev': bigram_prev in self.bi_grams,
            'is_bi_gram_next': bigram_next in self.bi_grams,
            'is_tri_gram': trigram in self.tri_grams,
        }
        if i == 0: features['BOS'] = True
        if i == len(sent) - 1: features['EOS'] = True
        return features

    def _sent2features(self, sent: List[str]) -> List[Dict[str, any]]:
        """Chuyển đổi cả một câu thành một chuỗi các bộ đặc trưng."""
        return [self._word2features(sent, i) for i in range(len(sent))]

    @staticmethod
    def sylabelize(text: str) -> List[str]:
        """Thực hiện việc tách âm tiết, chia văn bản thành các âm tiết cơ bản."""
        text = ud.normalize('NFC', text)
        vietnamese_chars = "a-zA-Z0-9àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíỉĩịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỷỹỵ"
        product_codes = r"\b(bb\d{2}|b\d{2}|togo)\b"
        web = r"https?://[^\s]+"
        email = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        word = f"[{vietnamese_chars}]+"
        non_word = r"[^\w\s]"
        patterns = [web, email, product_codes, word, non_word]
        patterns_re = re.compile("|".join(patterns), re.UNICODE | re.IGNORECASE)
        syllables = [match.group(0) for match in patterns_re.finditer(text)]
        return [s.strip() for s in syllables if s.strip()]

    def tokenize(self, text: str) -> str:
        """
        Thực hiện việc tách từ trên một chuỗi văn bản Tiếng Việt.
        """
        if not isinstance(text, str) or not text.strip():
            return ""
        
        syllables = self.sylabelize(text)
        if not syllables:
            return text

        features = self._sent2features(syllables)
        labels = self.model.predict([features])[0]
        
        output_tokens = [syllables[0]]
        for i in range(1, len(syllables)):
            if (labels[i] == 'I_W') and (syllables[i] not in string.punctuation):
                output_tokens[-1] += '_' + syllables[i]
            else:
                output_tokens.append(syllables[i])
        
        # *** PHẦN CẢI TIẾN BẮT ĐẦU TỪ ĐÂY ***
        
        # Ghép các token lại với nhau bằng khoảng trắng
        raw_output = ' '.join(output_tokens)
        
        # Hậu xử lý để loại bỏ khoảng trắng thừa trước các dấu câu phổ biến
        # Ví dụ: "cảm ơn nhiều ." -> "cảm ơn nhiều."
        #        "hàng , sản phẩm" -> "hàng, sản phẩm"
        processed_output = re.sub(r'\s+([,.?!])', r'\1', raw_output)
        
        return processed_output

if __name__ == '__main__':
    print("--- THƯ VIỆN ViTokenizer & ViUtils (BẢN CHUẨN HÓA) ---")
    try:
        tokenizer = ViTokenizer()
        print("\n[ViTokenizer] Khởi tạo thành công.")
        
        test_sentence_1 = "Shop tư vấn cho mình với nhé, cảm ơn nhiều."
        tokenized_sentence_1 = tokenizer.tokenize(test_sentence_1)
        
        print("\n[ViTokenizer] Ví dụ về chức năng tách từ:")
        print(f"  - Câu gốc:        '{test_sentence_1}'")
        print(f"  - Câu đã tách từ: '{tokenized_sentence_1}'")
    except Exception as e:
        print(f"\nLỗi khi chạy ví dụ của ViTokenizer: {e}")
