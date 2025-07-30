# Custom-Pyvi v1.0.5

Một phiên bản tùy chỉnh, gọn nhẹ của thư viện `pyvi`, tập trung vào chức năng **Tách từ (Word Segmentation)** và được tối ưu hóa cho các dự án cần xử lý Tiếng Việt chuyên ngành.

## Tính năng chính

* **Gọn nhẹ:** Loại bỏ các module không cần thiết như Gán nhãn từ loại (POS Tagging), Thêm dấu (Diacritics), chỉ giữ lại phần cốt lõi là `ViTokenizer`.
* **Tùy biến cao:** Dễ dàng "dạy" thêm từ vựng mới bằng cách chỉnh sửa file `models/words.txt` để tăng độ chính xác cho lĩnh vực của bạn (ví dụ: thương mại điện tử, y tế, pháp luật...).
* **Hiệu quả:** Kế thừa "bộ não" CRF mạnh mẽ từ `pyvi` gốc để đảm bảo khả năng tách từ ghép chính xác.

## Cài đặt

```bash
pip install custom-pyvi
```

## Sử dụng cơ bản

```python
from custom_pyvi import ViTokenizer

text = "ghế bập bênh giá bao nhiêu?"
tokenized_text = ViTokenizer.tokenize(text)

print(tokenized_text)
# Kết quả mong đợi: ghế_bập_bênh giá bao_nhiêu ?
```

## Tùy biến

Để cải thiện độ chính xác cho dự án của bạn, hãy mở file `custom_pyvi/models/words.txt` và thêm vào các từ ghép, thuật ngữ, tên sản phẩm... mà bạn muốn thư viện nhận diện. Mỗi cụm từ trên một dòng và các từ đơn cách nhau bằng dấu cách.

**Ví dụ:**
```
khung thép carbon
sơn tĩnh điện
da pu cao cấp
```

## Lời Cảm Ơn (Acknowledgments)

Thư viện này được tinh chỉnh và tùy biến dựa trên mã nguồn mở của thư viện `pyvi` gốc. Xin chân thành cảm ơn tác giả **trungtv** đã tạo ra và chia sẻ một công cụ xử lý Tiếng Việt vô cùng hữu ích cho cộng đồng.

* **PyPI gốc:** [https://pypi.org/project/pyvi/](https://pypi.org/project/pyvi/)
* **Tác giả:** `trungtv`