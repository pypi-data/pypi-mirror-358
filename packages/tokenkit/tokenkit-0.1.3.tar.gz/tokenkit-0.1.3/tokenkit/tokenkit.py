from transformers import AutoTokenizer
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Tuple

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
This is a library to calculate fertility and parity scores, as well as provide visualizations. 
The default model is `meta-llama/Llama-3.2-1B-Instruct`. 

Functions/Classes
-----------------
    - `fertilize`
    - `paritize`
    - `TokenMetrics`

Works Cited
-----------
Parity calculation from https://arxiv.org/abs/2305.15425 (page 3). 

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def fertilize(text: str, tokenizer='google/flan-t5-xxl') -> Tuple[float, List[str]]: 
    """ 
    Get the fertility score and tokens for a given text. 

    Parameters
    ----------
        - text (str): text for tokenization
        - tokenizer (tokenizer): model/tokenizer 
          (optional, defaults to `google/flan-t5-xxl`)

    Returns
    -------
        - score (float): fertility score
        - tokenized (list): list of tokens 
    """ 
    loaded_tokenizer = AutoTokenizer.from_pretrained(tokenizer)
    tokens = loaded_tokenizer.tokenize(text) 
    num_words = len(text.split())
    score = len(tokens) / num_words if num_words > 0 else float('inf')  
    return score, tokens


def paritize(sA: str, sB: str, tokenizer='google/flan-t5-xxl') -> float: 
    """ 
    Calculate parity score for a text and its translation. 
    "Premium" is the actual score, "parity" is when the score is ~1.    

    Parameters
    ----------
        - sA (string): sentence in language A    
        - sB (string): translation of `sA` in language B
        - tokenizer (tokenizer): model/tokenizer 
          (optional, defaults to `google/flan-t5-xxl`)

    Returns
    -------
        - parity (float): parity score for A relative to B (if this is ~1, it achieves parity)
    """
    loaded_tokenizer = AutoTokenizer.from_pretrained(tokenizer)

    sA_tokens = loaded_tokenizer.tokenize(sA)
    sB_tokens = loaded_tokenizer.tokenize(sB)
    return len(sA_tokens) / len(sB_tokens) if len(sB_tokens) > 0 else float('inf')


class TokenMetrics:
    """Get token metrics and visualizations for a dataset."""

    def __init__(self, data: pd.DataFrame, tokenizer='google/flan-t5-xxl'):
        """ 
        Initialize the `TokenMetrics` class.

        Parameters
        ----------
            - data (pd.DataFrame): Dataset of texts for tokenization
                                   Must contain only `language`, `text`, and `translation` columns,   
                                   where all columns are string-type. 
            - tokenizer (tokenizer): model/tokenizer 
                                     (optional, defaults to `google/flan-t5-xxl`) 

        Returns
        -------
        None. Initializes the class.        
        """
        data = data.fillna("")
        self.data = data
        self.loaded_tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self.fertilities = None
        self.parities = None

    def _help_fertilize(self, text: str) -> Tuple[float, List[str]]: 
        """ 
        Get the fertility score and tokens for a given text. Serves as helper function 
        for `fertilize`.

        Parameters
        ----------
            - text (str): text for tokenization

        Returns
        -------
            - score (float): fertility score
            - tokenized (list): list of tokens 
        """ 
        tokens = self.loaded_tokenizer.tokenize(text) 
        num_words = len(text.split())
        score = len(tokens) / num_words if num_words > 0 else float('inf') 
        return score, tokens

    def fertilize(self, text_col: str, language_col: str) -> pd.DataFrame: 
        """ 
        Get fertility scores and tokens for a dataset of texts in different languages. 

        Parameters
        ----------
            - text_col (str): column name containing the text
            - language_col (str): column name indicating the language

        Returns
        -------
            - scored (pd.DataFrame): DataFrame with `language`, `corpus`, `fertility`, and `tokens` columns
        """
        languages = list(self.data[language_col].unique())
        language2text = {}
        language2score = {}
        tokens = {}

        for language in languages:
            text = self.data[self.data[language_col] == language][text_col]
            corpus = " ".join(text)
            fertility_score, tokenized = self._help_fertilize(corpus)
            language2text[language] = corpus
            language2score[language] = fertility_score
            tokens[language] = tokenized

        scored = pd.DataFrame({
            'language': pd.Series(languages),
            'corpus': pd.Series(language2text.values()),
            'fertility': pd.Series(language2score.values()),
            'tokens': pd.Series(tokens.values())
        }) 
        self.fertilities = scored       
        return scored 

    def visualize_fertilities(self, figsize: Tuple[int, int] = (10, 6), color: str = 'purple') -> None: 
        """ 
        Make a bar plot visualizing fertilities by corpus/language. 

        Parameters
        ----------
            - figsize (tuple): Size of figure, default is (10, 6)
            - color (string): Color of bars

        Returns
        -------
        None. Plots fertilities by corpus/language.
        """
        if self.fertilities is None:
            raise ValueError("Fertilities not calculated. Call `fertilize()` first.")

        font_size = figsize[0] * 1.5
        data_sorted = self.fertilities.sort_values(by='fertility')

        plt.figure(figsize=figsize)
        plt.grid(axis='y', alpha=0.7, zorder=0)
        plt.bar(data_sorted['language'], data_sorted['fertility'], color=color, zorder=2)
        plt.xlabel('Language', fontsize=font_size)
        plt.ylabel('Fertility Score', fontsize=font_size)
        plt.title('Fertility Scores by Language', fontsize=font_size)
        plt.xticks(rotation=90, fontsize=font_size)
        plt.yticks(fontsize=font_size)
        plt.tight_layout()
        plt.show()

    def _help_paritize(self, row: pd.Series, text_col1: str, text_col2: str) -> float: 
        """ 
        Get the parity score for a given text. Serves as helper function 
        for `paritize`.

        Parameters
        ----------
            - row (pd.Series): one row from the DataFrame
            - text_col1 (str): name of column containing original text
            - text_col2 (str): name of column containing translation

        Returns
        -------
            - score (float): parity score
        """ 
        sA_tokens = self.loaded_tokenizer.tokenize(row[text_col1])
        sB_tokens = self.loaded_tokenizer.tokenize(row[text_col2])
        return len(sA_tokens) / len(sB_tokens) if len(sB_tokens) > 0 else float('inf')

    def paritize(self, text_col1: str, text_col2: str) -> pd.DataFrame: 
        """ 
        Get parity scores and tokens for a dataset of texts in different languages. 

        Parameters
        ----------
            - text_col1 (str): name of column with original text
            - text_col2 (str): name of column with translation

        Returns
        -------
            - scored (pd.DataFrame): DataFrame with `text`, `text2`, `parity` columns
        """
        scored = self.data[[text_col1, text_col2]].copy()
        scored['parity'] = scored.apply(
            lambda row: self._help_paritize(row, text_col1, text_col2), axis=1
        )
        self.parities = scored 
        return scored    
