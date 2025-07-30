# -*- coding: utf-8 -*-
"""
custom_pyvi/ViTokenizer.py – phiên bản 1.0.9
================================================
Các điểm mới:
1. **reconstruct_words()** – Ghép token dựa nhãn IOB, tái sử dụng nhiều chỗ.
2. **tokenize_return_list()** – Trả về list token đã ghép (không có dấu cách dư).
3. **tokenize_with_labels()** – Trả tuple (tokens, labels, words) để debug.
4. Cho phép **override từ điển** khi khởi tạo (`dict_override_path`).
5. Regex syllable splitter chuyển sang **raw‑string** tránh warning.
6. Giữ tương thích hoàn toàn với mô hình CRF hiện tại.
"""
import os, pickle, re, unicodedata as ud
from typing import List, Dict, Tuple, Set, Optional

_DEFAULT_MODEL = os.path.join(os.path.dirname(__file__), "models", "custom_pyvi3.pkl")
_DEFAULT_DICT  = os.path.join(os.path.dirname(__file__), "models", "custom_words.txt")

class ViUtils:
    @staticmethod
    def remove_accents(text: str) -> str:
        return "".join(c for c in ud.normalize("NFD", text) if ud.category(c) != "Mn")

class ViTokenizer:
    """Tokenizer Tiếng Việt dựa vào CRF + từ điển tuỳ chỉnh."""

    def __init__(self,
                 model_path: str = _DEFAULT_MODEL,
                 dict_path: str  = _DEFAULT_DICT,
                 dict_override_path: Optional[str] = None):
        """Khởi tạo tokenizer.
        dict_override_path: Nếu truyền, sẽ load thêm từ điển cụm từ ở path này."""
        # --- Load model ---
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Không tìm thấy model tại {model_path}")
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        # --- Load words ---
        self.mono_grams: Set[str] = set()
        self.bi_grams:   Set[str] = set()
        self.tri_grams:  Set[str] = set()
        self._load_words(dict_path)
        if dict_override_path:
            self._load_words(dict_override_path)

    # ------------------------------------------------------------------
    def _load_words(self, path: str):
        if not os.path.isfile(path):
            print(f"[⚠] Không tìm thấy từ điển: {path}")
            return
        with open(path, encoding="utf-8") as f:
            for line in f:
                token = line.strip().lower()
                if not token: continue
                n = len(token.split())
                if n == 1:
                    self.mono_grams.add(token)
                elif n == 2:
                    self.bi_grams.add(token)
                else:
                    self.tri_grams.add(token)

    # ------------------------------------------------------------------
    @staticmethod
    def sylabelize(text: str) -> List[str]:
        text = ud.normalize("NFC", text)
        vn = ("a-zA-Z0-9àáãạảăắằẳẵặâấầẩẫậ"
              "èéẹẻẽêềếểễệđìíỉĩịòóõọỏôốồổỗộ"
              "ơớờởỡợùúũụủưứừửữựỳýỷỹỵ")
        pattern = re.compile(rf"[{vn}]+|\S", re.UNICODE)
        return [m.group(0) for m in pattern.finditer(text)]

    # ------------------------------------------------------------------
    def _word2features(self, sent: List[str], i: int) -> Dict[str, object]:
        w  = sent[i]
        lw = w.lower()
        pw = sent[i-1].lower() if i > 0 else "<BOS>"
        nw = sent[i+1].lower() if i < len(sent)-1 else "<EOS>"
        feats = {
            'bias': 1.0,
            'w.lower': lw,
            'w.isupper': w.isupper(),
            'w.isdigit': w.isdigit(),
            '-1:lower': pw,
            '+1:lower': nw,
            'in_uni': lw in self.mono_grams,
            'bi_prev': f"{pw} {lw}" in self.bi_grams,
            'bi_next': f"{lw} {nw}" in self.bi_grams,
            'BOS': i == 0,
            'EOS': i == len(sent)-1,
        }
        return feats

    def sent2features(self, sent: List[str]):
        return [self._word2features(sent, i) for i in range(len(sent))]

    # ------------------------------------------------------------------
    def reconstruct_words(self, tokens: List[str], labels: List[str]) -> List[str]:
        """Ghép token thành cụm dựa nhãn IOB."""
        words, buf = [], []
        for tok, lab in zip(tokens, labels):
            if lab == "B_W":
                if buf: words.append("_".join(buf))
                buf = [tok]
            elif lab == "I_W":
                buf.append(tok)
            else:
                if buf: words.append("_".join(buf)); buf = []
                words.append(tok)
        if buf:
            words.append("_".join(buf))
        return words

    # ------------------------------------------------------------------
    def tokenize_return_list(self, text: str) -> List[str]:
        """Trả về danh sách token (đã ghép) thay vì chuỗi."""
        if not isinstance(text, str) or not text.strip():
            return []
        tokens = self.sylabelize(text)
        if not tokens:
            return [text]
        labels = self.model.predict([self.sent2features(tokens)])[0]
        return self.reconstruct_words(tokens, labels)

    def tokenize(self, text: str) -> str:
        words = self.tokenize_return_list(text)
        raw  = " ".join(words)
        return re.sub(r"\s+([,.?!])", r"\1", raw)

    def tokenize_with_labels(self, text: str) -> Tuple[List[str], List[str], List[str]]:
        """Trả về (tokens, labels, words) để debug mô hình."""
        tokens = self.sylabelize(text)
        labels = self.model.predict([self.sent2features(tokens)])[0] if tokens else []
        words  = self.reconstruct_words(tokens, labels)
        return tokens, labels, words

# ----------------------------------------------------------------------
if __name__ == "__main__":
    sample = "Shop ơi ghế thư giãn BB04 có ship về Hà Nội không?"
    vk = ViTokenizer()
    print("➡  Chuỗi gốc :", sample)
    toks, labs, wrds = vk.tokenize_with_labels(sample)
    print("➡  Tokens    :", toks)
    print("➡  Labels    :", labs)
    print("➡  Ghép words:", " ".join(wrds))
