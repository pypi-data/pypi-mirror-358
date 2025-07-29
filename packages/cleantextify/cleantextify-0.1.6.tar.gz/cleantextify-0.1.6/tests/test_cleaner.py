import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cleantextify import clean_text


def test_clean_text():
    text = "Hello World! Visit https://example.com 🌟<br> 123"
    cleaned = clean_text(text)
    assert 'http' not in cleaned
    assert '🌟' not in cleaned
    assert '123' not in cleaned
    assert '<' not in cleaned
    print("All tests passed!")

if __name__ == "__main__":
    test_clean_text()
