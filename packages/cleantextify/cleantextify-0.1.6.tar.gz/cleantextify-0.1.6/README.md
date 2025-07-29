# cleantextify 🧹✨

[![PyPI version](https://img.shields.io/pypi/v/cleantextify.svg)](https://pypi.org/project/cleantextify/)
[![Downloads](https://pepy.tech/badge/cleantextify)](https://pepy.tech/project/cleantextify)

A lightweight, customizable Python package for cleaning text data.  
Removes URLs, HTML tags, emojis, numbers, punctuation, and normalizes whitespace — perfect for text preprocessing in NLP, data cleaning, and web scraping projects.

---

## 📦 Installation

Install from PyPI:
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
- ! Remove punctuations

---

## 📖 Usage

### Basic Example:
```python
from cleantextify import clean_text

text = "Hello world! 🌟 Visit https://example.com <br> 123"
cleaned = clean_text(text)

print(cleaned)
# Output: Hello world Visit
```
**Output:**
```
Hello world Visit
```
---

## 🔧 Customizable Options

| Parameter         | Type    | Default | Description                                   |
|:-----------------|:--------|:----------|:------------------------------------------------|
| `remove_urls`     | `bool`  | `True`   | Remove URLs from text.                         |
| `remove_html`     | `bool`  | `True`   | Remove HTML tags and entities.                 |
| `remove_emojis`   | `bool`  | `True`   | Remove emojis.                                 |
| `remove_numbers`  | `bool`  | `True`   | Remove numbers.                                |
| `remove_punct`    | `bool`  | `True`   | Remove punctuation marks.                      |
| `normalize_spaces`| `bool`  | `True`   | Replace multiple spaces with a single space.   |

---

## 📚 Full Usage Examples:

### Remove only URLs and Emojis:
```python
from cleantextify import clean_text

text = "Check this out! 😃 https://example.com"
cleaned = clean_text(text, remove_urls=True, remove_emojis=True, remove_numbers=False, remove_punct=False, normalize_spaces=True)

print(cleaned)

```
**Output:**
```
Check this out
```

---
### Remove All but Keep Numbers:
```python
from cleantextify import clean_text

text = "Score: 99! 🎉 Visit: https://test.com"
cleaned = clean_text(text, remove_numbers=False)

print(cleaned)

```
**Output:**
```
Score 99 Visit
```
---

### Only Normalize Spaces:
```python
from cleantextify import clean_text

text = "This    is    a    test."
cleaned = clean_text(text, remove_urls=False, remove_html=False, remove_emojis=False, remove_numbers=False, remove_punct=False, normalize_spaces=True)

print(cleaned)

```
**Output:**
```
This is a test.
```
---



## 📜 License
MIT License

---

## 📞 Author
**Rajdeep Pandhere**  
[rajdeeppandhere36coc@gmail.com](mailto:rajdeeppandhere36coc@gmail.com)

---

## 📦 PyPI Link
[https://pypi.org/project/cleantextify/](https://pypi.org/project/cleantextify/)
