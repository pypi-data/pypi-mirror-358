
# cleantextify 🧹✨

[![PyPI version](https://img.shields.io/pypi/v/cleantextify.svg)](https://pypi.org/project/cleantextify/)
[![Downloads](https://pepy.tech/badge/cleantextify)](https://pepy.tech/project/cleantextify)

A lightweight, plug-and-play Python package for cleaning text data.  
Remove URLs, HTML tags, emojis, numbers, and normalize spaces — all in a single function.

---

## 📦 Installation

```bash
pip install cleantextify
```

---

## ✨ Features

- 🚀 Remove URLs
- 🧼 Remove HTML tags
- 😂 Remove emojis
- 🔢 Remove numbers
- 📏 Normalize whitespace

---

## 📖 Usage

```python
from cleantextify import clean_text

text = "Hello world! 🌟 Visit https://example.com <br> 123"
cleaned = clean_text(text)
print(cleaned)
```

**Output:**
```
Hello world! Visit
```

---

## 📄 License

[MIT License](LICENSE)

---

## 👨‍💻 Author

**Rajdeep18**



---
