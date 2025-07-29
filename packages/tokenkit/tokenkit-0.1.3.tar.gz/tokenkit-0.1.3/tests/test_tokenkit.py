from transformers import AutoTokenizer
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tokenkit import *

##############################################################################################################################################################################################################################################################################
# Test `fertilize`
##############################################################################################################################################################################################################################################################################

def test_fertilize(): 
    text = 'This is a sentence for testing.'
    expected_tokens = ['This', 'Ġis', 'Ġa', 'Ġsentence', 'Ġfor', 'Ġtesting', '.']

    score, tokenized = fertilize(text)
    expected_score = len(tokenized) / len(text.split())

    assert isinstance(score, float)
    assert isinstance(tokenized, list)

    assert expected_tokens == tokenized
    assert score == expected_score


def test_fertilize_empty_text(): 
    text = "" 
    expected_tokens = []

    score, tokenized = fertilize(text)
    expected_score = float('inf')

    assert expected_tokens == tokenized 
    assert score == expected_score

##############################################################################################################################################################################################################################################################################
# Test `paritize`
##############################################################################################################################################################################################################################################################################

def test_paritize():
    sA = 'Kiû Lí hō͘ guá tì-huī, guá tsiū ē tsun-siú Lí ê lu̍t-huat, mā beh tsuan-sim lâi tsip-siú.'
    sB = 'Give me understanding, and I will keep your law. Yes, I will obey it with my whole heart.'
    parity = paritize(sA, sB)
    expected_parity = 2.4545454545454546
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    sA = 'Tabi̍t tuì Olnân kóng, Lí kā tsit-ê tiūⁿ-tiâⁿ ê tē hō͘ guá, hō͘ guá tī hia thang kā Siōngtsú khí tsi̍t tsō tuâⁿ, lí tio̍h tsiàu tsiok-gia̍h ê kè-tsînn bē guá, hō͘ un-i̍k suah, bô hāi-tio̍h jîn-bîn.'
    sB = 'Then David said to Ornan, Give me the place of this threshing floor, that I may build thereon an altar to Yahweh: for the full price shall you give it me, that the plague may be stayed from the people.'
    parity = paritize(sA, sB)
    expected_parity = 2.56
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    sA = ' Beh kā lín pun tē tsò sán-gia̍p ê lâng ê miâ-jī kì tī ē-té: Sī tsè-si Êlīatsal kah Nùn ê kiáⁿ Iosiúah.'
    sB = 'These are the names of the men who shall divide the land to you for inheritance: Eleazar the priest, and Joshua the son of Nun.'
    parity = paritize(sA, sB)
    expected_parity = 2.0344827586206895
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    sA = 'Siōngtè kā Iâkop kóng, Khí-lâi! Khì Bethel, tuà tī hia, koh tio̍h tī hia kā Siōngtè khí tsi̍t tsō tuâⁿ; to̍h-sī lí siám-phiah lí ê a-hiaⁿ Esáu ê bīn ê sî, tuì lí tshut-hiān ê hit uī.'
    sB = 'God said to Jacob, Arise, go up to Bethel, and live there. Make there an altar to God, who appeared to you when you fled from the face of Esau your brother.'
    parity = paritize(sA, sB)
    expected_parity = 2.5609756097560976
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    sA = 'Tng i teh sio hiuⁿ ê sî, huē-tsiòng kui tuā-tīn tī guā-bīn teh kî-tó.'
    sB = 'The whole multitude of the people were praying outside at the hour of incense.'
    parity = paritize(sA, sB)
    expected_parity = 2.4375
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    sA = 'kah tiàm tī Hesibóng tsò ông, Amô͘lī lâng ê ông Sihông tsiah-ê siâⁿ, kàu Ammóng lâng ê kau-kài;'
    sB = 'and all the cities of Sihon king of the Amorites, who reigned in Heshbon, to the border of the children of Ammon;'
    parity = paritize(sA, sB)
    expected_parity = 1.4545454545454546
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    tokenizer='google/gemma-2-9b'

    sA = 'kah tiàm tī Hesibóng tsò ông, Amô͘lī lâng ê ông Sihông tsiah-ê siâⁿ, kàu Ammóng lâng ê kau-kài;'
    sB = 'and all the cities of Sihon king of the Amorites, who reigned in Heshbon, to the border of the children of Ammon;'
    parity = paritize(sA, sB, tokenizer=tokenizer)
    expected_parity = 1.4137931034482758
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    sA = 'lí khuàⁿ, só͘-í, Guá beh tshuā guā-pang lâng, to̍h-sī lia̍t kok tiong kiông-pō ê lâng lâi lí tsia; in ē pue̍h to kong-kik lí tuì tì-huī só͘ tit-tio̍h ê hó mi̍h, kā lí ê îng-kng uè lah-sap.'
    sB = 'therefore, behold, I will bring strangers on you, the terrible of the nations; and they shall draw their swords against the beauty of your wisdom, and they shall defile your brightness.'
    parity = paritize(sA, sB, tokenizer=tokenizer)
    expected_parity = 2.4054054054054053
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    sA = 'In-uī lín uàn-hūn tì-sik, bô ài kìng-uì Siōngtsú.'
    sB = "Because they hated knowledge, And didn't choose the fear of Yahweh."
    parity = paritize(sA, sB, tokenizer=tokenizer)
    expected_parity = 2.066666666666667
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

def test_paritize_empty_text(): 
    sA = ''
    sB = ''
    parity = paritize(sA, sB)
    expected_parity = float('inf')
    print('Parity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

def test_paritize_missing_args(): 
    sA = ''
    sB = ''
    with pytest.raises(TypeError, match="missing 1 required positional argument: 'sB'"):
        paritize(sA)  # `sB` not given

##############################################################################################################################################################################################################################################################################
# Test certain LLMs/tokenizers
##############################################################################################################################################################################################################################################################################
texts = ["The sky is bright today.", 
        "I love classical music.", 
        "Data science is fascinating.", 
        "Could you pass the salt?", 
        "Baroque composers inspire my work.", 
        "What time is the meeting?", 
        "This coffee tastes really good.",
        "Purple is pretty"]

texts2 = ["Despite the heavy rain and strong winds, the team continued their hike up the steep mountain, determined to reach the summit before sunset.", 
            "In an effort to reduce carbon emissions and promote sustainability, many cities have started investing in renewable energy sources such as solar and wind power.",
            "Artificial intelligence is transforming the way we interact with technology.", 
            "If you want to live a happy life, tie it to a goal, not to people or things."]

def test_phi35(): 
    # Model: microsoft/Phi-3.5-mini-instruct
    global texts
    global texts2
    tokenizer = 'microsoft/Phi-3.5-mini-instruct'
    expected_tokens1 = [['▁The', '▁sky', '▁is', '▁bright', '▁today', '.'],
                        ['▁I', '▁love', '▁classical', '▁music', '.'],
                        ['▁Data', '▁science', '▁is', '▁fasc', 'in', 'ating', '.'],
                        ['▁Could', '▁you', '▁pass', '▁the', '▁salt', '?'],
                        ['▁Bar', 'o', 'que', '▁compos', 'ers', '▁insp', 'ire', '▁my', '▁work', '.'],
                        ['▁What', '▁time', '▁is', '▁the', '▁meeting', '?'],
                        ['▁This', '▁coffee', '▁t', 'ast', 'es', '▁really', '▁good', '.'],
                        ['▁Pur', 'ple', '▁is', '▁pretty']]
    expected_tokens2 = [['▁Despite', '▁the', '▁heavy', '▁rain', '▁and', '▁strong', '▁wind', 's', 
                            ',', '▁the', '▁team', '▁continued', '▁their', '▁hi', 'ke', '▁up', '▁the', 
                            '▁ste', 'ep', '▁mountain', ',', '▁determined', '▁to', '▁reach', '▁the', 
                            '▁sum', 'mit', '▁before', '▁sun', 'set', '.'], 
                            ['▁In', '▁an', '▁effort', '▁to', '▁reduce', '▁carbon', 
                            '▁em', 'issions', '▁and', '▁promote', '▁sust', 'ain', 
                            'ability', ',', '▁many', '▁cities', '▁have', '▁started', '▁invest', 
                            'ing', '▁in', '▁renew', 'able', '▁energy', '▁sources', '▁such', '▁as', 
                            '▁solar', '▁and', '▁wind', '▁power', '.'], ['▁Art', 'ific', 'ial', 
                            '▁intelligence', '▁is', '▁transform', 'ing', '▁the', '▁way', '▁we', 
                            '▁interact', '▁with', '▁technology', '.'], ['▁If', '▁you', '▁want', 
                            '▁to', '▁live', '▁a', '▁happy', '▁life', ',', '▁tie', '▁it', '▁to', 
                            '▁a', '▁goal', ',', '▁not', '▁to', '▁people', '▁or', '▁things', '.']]

    tokens1 = []
    for text in texts: 
        score, tokenized = fertilize(text, tokenizer=tokenizer)
        tokens1.append(tokenized)

    tokens2 = []
    for text in texts2: 
        score, tokenized = fertilize(text, tokenizer=tokenizer)
        tokens2.append(tokenized)

    assert expected_tokens1==tokens1
    assert expected_tokens2==tokens2


def test_flan_t5(): 
    global texts
    global texts2
    tokenizer = 'google/flan-t5-xxl'
    expected_tokens1 = [['▁The', '▁sky', '▁is', '▁bright', '▁today', '.'], 
                        ['▁I', '▁love', '▁classical', '▁music', '.'], 
                        ['▁Data', '▁science', '▁is', '▁fascinating', '.'], 
                        ['▁Could', '▁you', '▁pass', '▁the', '▁salt', '?'], 
                        ['▁Bar', 'o', 'que', '▁composer', 's', '▁inspire', '▁my', '▁work', '.'], 
                        ['▁What', '▁time', '▁is', '▁the', '▁meeting', '?'], 
                        ['▁This', '▁coffee', '▁tastes', '▁really', '▁good', '.'], 
                        ['▁Purple', '▁is', '▁pretty']]
    expected_tokens2 = [['▁', 'Despite', '▁the', '▁heavy', '▁rain', '▁and', '▁strong', '▁winds', ',', '▁the', '▁team', '▁continued', '▁their', '▁hike', '▁up', '▁the', '▁steep', '▁mountain', ',', '▁determined', '▁to', '▁reach', '▁the', '▁summit', '▁before', '▁sunset', '.'], 
                        ['▁In', '▁an', '▁effort', '▁to', '▁reduce', '▁carbon', '▁emissions', '▁and', '▁promote', '▁sustainability', ',', '▁many', '▁cities', '▁have', '▁started', '▁investing', '▁in', '▁renewable', '▁energy', '▁sources', '▁such', '▁as', '▁solar', '▁and', '▁wind', '▁power', '.'], 
                        ['▁Artificial', '▁intelligence', '▁is', '▁', 'transforming', '▁the', '▁way', '▁we', '▁interact', '▁with', '▁technology', '.'], 
                        ['▁If', '▁you', '▁want', '▁to', '▁live', '▁', 'a', '▁happy', '▁life', ',', '▁tie', '▁it', '▁to', '▁', 'a', '▁goal', ',', '▁not', '▁to', '▁people', '▁or', '▁things', '.']]


    tokens1 = []
    for text in texts: 
        score, tokenized = fertilize(text, tokenizer=tokenizer)
        tokens1.append(tokenized)

    tokens2 = []
    for text in texts2: 
        score, tokenized = fertilize(text, tokenizer=tokenizer)
        tokens2.append(tokenized)

    assert expected_tokens1==tokens1
    assert expected_tokens2==tokens2


def test_aya(): 
    # Model: CohereForAI/aya-101
    global texts
    global texts2
    tokenizer = 'CohereForAI/aya-101'
    expected_tokens1 = [['▁The', '▁sky', '▁is', '▁bright', '▁today', '.'], 
                        ['▁I', '▁love', '▁classic', 'al', '▁music', '.'], 
                        ['▁Data', '▁science', '▁is', '▁fascina', 'ting', '.'], 
                        ['▁Coul', 'd', '▁you', '▁pass', '▁the', '▁salt', '?'], 
                        ['▁Baro', 'que', '▁', 'composer', 's', '▁inspire', '▁my', '▁work', '.'], 
                        ['▁What', '▁time', '▁is', '▁the', '▁meeting', '?'], 
                        ['▁This', '▁coffee', '▁taste', 's', '▁', 'really', '▁good', '.'], 
                        ['▁Purple', '▁is', '▁', 'pretty']]
    expected_tokens2 = [['▁De', 'spite', '▁the', '▁', 'heavy', '▁rain', '▁and', '▁strong', '▁', 'winds', ',', '▁the', '▁team', '▁', 'continued', '▁', 'their', '▁', 'hike', '▁up', '▁the', '▁stee', 'p', '▁mountain', ',', '▁determin', 'ed', '▁to', '▁', 'reach', '▁the', '▁', 'summit', '▁before', '▁', 'sunset', '.'], 
                        ['▁In', '▁an', '▁', 'effort', '▁to', '▁reduce', '▁carbon', '▁', 'emissions', '▁and', '▁', 'promote', '▁', 'sustainability', ',', '▁many', '▁', 'cities', '▁have', '▁', 'started', '▁invest', 'ing', '▁in', '▁', 'renew', 'able', '▁energy', '▁', 'sources', '▁such', '▁as', '▁solar', '▁and', '▁wind', '▁power', '.'], 
                        ['▁', 'Artificial', '▁', 'intelligence', '▁is', '▁transform', 'ing', '▁the', '▁way', '▁we', '▁interact', '▁with', '▁technology', '.'], 
                        ['▁If', '▁you', '▁want', '▁to', '▁live', '▁', 'a', '▁happy', '▁life', ',', '▁tie', '▁it', '▁to', '▁', 'a', '▁goal', ',', '▁not', '▁to', '▁people', '▁or', '▁things', '.']]


    tokens1 = []
    for text in texts: 
        score, tokenized = fertilize(text, tokenizer=tokenizer)
        tokens1.append(tokenized)

    tokens2 = []
    for text in texts2: 
        score, tokenized = fertilize(text, tokenizer=tokenizer)
        tokens2.append(tokenized)

    assert expected_tokens1==tokens1
    assert expected_tokens2==tokens2


def test_bloomz(): 
    # Model: bigscience/bloomz-7b1
    global texts
    global texts2
    tokenizer = 'bigscience/bloomz-7b1'
    expected_tokens1 = [['The', 'Ġsky', 'Ġis', 'Ġbright', 'Ġtoday', '.'], 
                        ['I', 'Ġlove', 'Ġclassical', 'Ġmusic', '.'], 
                        ['Data', 'Ġscience', 'Ġis', 'Ġfascin', 'ating', '.'], 
                        ['Could', 'Ġyou', 'Ġpass', 'Ġthe', 'Ġsalt', '?'], 
                        ['B', 'aro', 'que', 'Ġcompos', 'ers', 'Ġinspire', 'Ġmy', 'Ġwork', '.'], 
                        ['What', 'Ġtime', 'Ġis', 'Ġthe', 'Ġmeeting', '?'], 
                        ['This', 'Ġcoffee', 'Ġt', 'astes', 'Ġreally', 'Ġgood', '.'], 
                        ['Pur', 'ple', 'Ġis', 'Ġpretty']]
    expected_tokens2 = [['Despite', 'Ġthe', 'Ġheavy', 'Ġrain', 'Ġand', 'Ġstrong', 'Ġwinds', ',', 'Ġthe', 'Ġteam', 'Ġcontinued', 'Ġtheir', 'Ġhike', 'Ġup', 'Ġthe', 'Ġsteep', 'Ġmountain', ',', 'Ġdetermined', 'Ġto', 'Ġreach', 'Ġthe', 'Ġsummit', 'Ġbefore', 'Ġsunset', '.'], 
                        ['In', 'Ġan', 'Ġeffort', 'Ġto', 'Ġreduce', 'Ġcarbon', 'Ġemissions', 'Ġand', 'Ġpromote', 'Ġsustainability', ',', 'Ġmany', 'Ġcities', 'Ġhave', 'Ġstarted', 'Ġinvest', 'ing', 'Ġin', 'Ġrenewable', 'Ġenergy', 'Ġsources', 'Ġsuch', 'Ġas', 'Ġsolar', 'Ġand', 'Ġwind', 'Ġpower', '.'], 
                        ['Art', 'ificial', 'Ġintelligence', 'Ġis', 'Ġtransforming', 'Ġthe', 'Ġway', 'Ġwe', 'Ġinteract', 'Ġwith', 'Ġtechnology', '.'], 
                        ['If', 'Ġyou', 'Ġwant', 'Ġto', 'Ġlive', 'Ġa', 'Ġhappy', 'Ġlife', ',', 'Ġtie', 'Ġit', 'Ġto', 'Ġa', 'Ġgoal', ',', 'Ġnot', 'Ġto', 'Ġpeople', 'Ġor', 'Ġthings', '.']]


    tokens1 = []
    for text in texts: 
        score, tokenized = fertilize(text, tokenizer=tokenizer)
        tokens1.append(tokenized)

    tokens2 = []
    for text in texts2: 
        score, tokenized = fertilize(text, tokenizer=tokenizer)
        tokens2.append(tokenized)

    assert expected_tokens1==tokens1
    assert expected_tokens2==tokens2

##############################################################################################################################################################################################################################################################################
# Test `TokenMetrics`
##############################################################################################################################################################################################################################################################################

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Test `help_fertilize` 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@pytest.fixture
def token_metrics():
    tokenizer = 'meta-llama/Llama-3.2-1B-Instruct'
    empty_df = pd.DataFrame(columns=["language", "text", "translation"])  
    return TokenMetrics(data=empty_df, tokenizer=tokenizer)

def test_help_fertilize(token_metrics):
    text = "This is a test sentence."
    score, tokens = token_metrics._help_fertilize(text)

    assert isinstance(score, float)
    assert isinstance(tokens, list)
    assert all(isinstance(token, str) for token in tokens)
    assert score > 0
    assert len(tokens) > 0
    assert np.isclose(score, len(tokens) / len(text.split()))

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Test `fertilize`
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@pytest.fixture
def token_metrics():
    tokenizer = 'meta-llama/Llama-3.2-1B-Instruct'
    test_df = pd.DataFrame({
        "language": ["English", "French", "Spanish"],
        "text": ["This is a test sentence.",
                 "Ceci est une phrase de test.",
                 "Esta es una oración de prueba."]})
    return TokenMetrics(data=test_df, tokenizer=tokenizer)

def test_fertilize(token_metrics):
    result = token_metrics.fertilize(text_col="text", language_col="language")

    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {"language", "corpus", "fertility", "tokens"}
    assert len(result) == 3  # Should match the number of languages

    for fertility in result["fertility"]:
        assert isinstance(fertility, float)
        assert fertility > 0

    for tokens in result["tokens"]:
        assert isinstance(tokens, list)
        assert all(isinstance(token, str) for token in tokens)

@pytest.fixture
def small_test_df():
    return pd.DataFrame({"lang": ["German", "Chinese"],
                         "sentence": ["Das ist ein Testsatz.", "这是一个测试句子。"]})

def test_fertilize2(token_metrics):
    result = token_metrics.fertilize(text_col="text", language_col="language")

    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {"language", "corpus", "fertility", "tokens"}
    assert len(result) == 3  # Should match the number of languages

def test_small_df(small_test_df):
    assert isinstance(small_test_df, pd.DataFrame)
    assert "lang" in small_test_df.columns
    assert "sentence" in small_test_df.columns
    assert len(small_test_df) == 2

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Test `visualize_fertilities`
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@pytest.fixture
def token_metrics():
    tokenizer = 'meta-llama/Llama-3.2-1B-Instruct'
    test_df = pd.DataFrame({"language": ["English", "French", "Spanish"],
                            "text": ["This is a test sentence.",
                                     "Ceci est une phrase de test.",
                                     "Esta es una oración de prueba."]})
    return TokenMetrics(data=test_df, tokenizer=tokenizer)

@pytest.fixture
def fertilized_data(token_metrics):
    return token_metrics.fertilize(text_col="text", language_col="language")

def test_visualize_fertilities(token_metrics, fertilized_data):
    try:
        token_metrics.visualize_fertilities(figsize=(4, 3), color="blue")
        assert True
    except Exception as e:
        pytest.fail(f"visualize_fertilities() raised an error: {e}")

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Test `help_paritize`
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def test_help_paritize():
    tokenizer = 'meta-llama/Llama-3.2-1B-Instruct'
    test_df = pd.DataFrame({"text": ["This is a test sentence.",
                                        "Ceci est une phrase de test.",
                                        "Esta es una oración de prueba."],
                            "translation": ["C'est une phrase de test.",
                                            "This is a test sentence.",
                                            "This is a trial sentence."]})
    token_metrics = TokenMetrics(data=test_df, tokenizer=tokenizer)

    row = test_df.iloc[0, :]
    parity = token_metrics._help_paritize(row, "text", "translation")
    expected_parity = 0.8571428571428571
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)


    row = test_df.iloc[1, :]
    parity = token_metrics._help_paritize(row, "text", "translation")
    expected_parity = 1.3333333333333333
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    row = test_df.iloc[2, :]
    parity = token_metrics._help_paritize(row, "text", "translation")
    expected_parity = 1.3333333333333333
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)


def test__help_paritize2():
    tokenizer = 'google/gemma-2-9b'
    test_df = pd.DataFrame({"text": ["Tī thinn-tíng khí I ê pâng-king, tī tē-tsiūⁿ hē kiong-tshong ê tē-ki, kiò hái tsuí lâi piàⁿ tī tē-ni̍h ê, I ê miâ kiò-tsò I-é-ho-bah.",
                                     "I koh tû-khì Iôtah lia̍t ông hiàn hō͘ ji̍t-thâu hiah-ê bé, tī ji̍p Siōngtsú tiān ê só͘-tsāi, tī thài-kàm Náthan Meli̍k uá-kīn mn̂g-lông ê tshù, koh īng hué sio ji̍t-thâu hiah-ê tshia.",
                                     "Tsú ê hiann-tī Iâkop í-guā, guá lóng bô kìⁿ-kuè kî-tha ê sù-tô͘."],
                            "translation": ["It is he who builds his chambers in the heavens, and has founded his vault on the earth; he who calls for the waters of the sea, and pours them out on the surface of the earth; Yahweh is his name.",
                                            "He took away the horses that the kings of Judah had given to the sun, at the entrance of the house of Yahweh, by the chamber of Nathan Melech the chamberlain, which was in the precincts; and he burned the chariots of the sun with fire.",
                                            "But of the other apostles I saw no one, except James, the Lord's brother."]})
    token_metrics = TokenMetrics(data=test_df, tokenizer=tokenizer)

    row = test_df.iloc[0, :]
    parity = token_metrics._help_paritize(row, "text", "translation")
    expected_parity = 1.5
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)


    row = test_df.iloc[1, :]
    parity = token_metrics._help_paritize(row, "text", "translation")
    expected_parity = 1.7169811320754718
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

    row = test_df.iloc[2, :]
    parity = token_metrics._help_paritize(row, "text", "translation")
    expected_parity = 2.0526315789473686
    print('\nParity:', parity)
    print('Expected parity:', expected_parity)
    assert isinstance(parity, float)
    assert np.isclose(parity, expected_parity)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Test `help_paritize`
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def test_paritize():
    tokenizer = 'google/gemma-2-9b'
    test_df = pd.DataFrame({"text": ["Tī guá lâi tsit ê hō͘-chū.",
                                     "I só͘-tshut ê sū sī tsiok gâu.",
                                     "Lí ē-tàng khòaⁿ guá ê tsheh."],
                            "translation": ["I came here for this reason.",
                                            "What he said was very clever.",
                                            "You can look at my book."]})
    token_metrics = TokenMetrics(data=test_df, tokenizer=tokenizer)
    parities_df = token_metrics.paritize("text", "translation")

    assert isinstance(parities_df, pd.DataFrame)
    assert set(parities_df.columns) == {"text", "translation", "parity"}
    assert len(parities_df) == 3

    for parity in parities_df["parity"]:
        assert isinstance(parity, float)
        assert parity > 0
    
    parities = parities_df["parity"].values
    expected_parities = np.array([2.285714, 2.142857, 2.142857])
    assert np.isclose(parities, expected_parities).all()
