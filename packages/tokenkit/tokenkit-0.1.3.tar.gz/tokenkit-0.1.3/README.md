<h1 align="center">TokenKit</h1>

**TokenKit** is a Python library for computing **fertility** and **parity** metrics using large language model (LLM) tokenizers like LLaMA, T5, Gemma, and more. It helps you quantify and visualize how many tokens a sentence breaks into and how aligned a translation is in length across languages. **Model-agnostic** for any Hugging Face AutoTokenizer. Ideal for NLP evaluation, translation research, or just exploring how tokenizers behave across models.

---

## Installation
In the terminal:
```bash
pip install tokenkit
```

Import:
```python
from tokenkit import fertilize, paritize, TokenMetrics
# or
from tokenkit import *
```

---

## Examples

```python
# Fertility score: tokens per word
score, tokens = fertilize("I love classical music.")
print(score)
print(tokens)

# Parity score: token length ratio between original + translation
parity = paritize("Bonjour tout le monde", "Hello everyone")
print(parity)
```

```python
# Token metrics across a dataset
import pandas as pd
df = pd.DataFrame({
    "language": ["English", "French"],
    "text": ["This is a test sentence.", "Ceci est une phrase de test."],
    "translation": ["C'est une phrase de test.", "This is a test sentence."]
})

tm = TokenMetrics(data=df)
tm.fertilize(text_col="text", language_col="language")
tm.visualize_fertilities()
tm.paritize(text_col1="text", text_col2="translation")
```

Note that can use any Hugging Face AutoTokenizer:

```python
from transformers import AutoTokenizer
custom_tok = AutoTokenizer.from_pretrained("google/flan-t5-xxl")
fertilize("Tokenizing with a custom model.", tokenizer=custom_tok)
```

---

## License

MIT License © Bill & Melinda Gates Foundation 

Ada Zhang, Nihal Karim, Hamza Louzan, Victor Wei, Cody Carroll, Jessica Lundin
