import re

import nltk
from HanTa import HanoverTagger as ht
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("punkt")
nltk.download("stopwords")

with open("../data/stopwords-de.txt", "r") as file:
    stopwords_ger = file.read().split()

def tokenize_doc(doc):
    stopwords_en = stopwords.words("english")

    cleaned = re.sub(
        r"\b\w\b",
        "",
        re.sub(
            r"[\W](?=\w)",
            " ",
            doc.replace("\u200b", " ")
            .replace("\xad", "")
            .replace("-", " ")
            .replace("/", " ")
            .replace("·", " ")
            .replace("•", " ")
            .replace("…", " "),
        ),
    )
    tokenized = word_tokenize(cleaned, language="german")
    alphas = [w.lower() for w in tokenized if w.isalpha()]

    tagger = ht.HanoverTagger("morphmodel_ger.pgz")

    no_stops_de = [w for w in alphas if w not in stopwords_ger]
    no_stops_de_en = [w for w in no_stops_de if w not in stopwords_en]

    lemmatized = [tagger.analyze(token)[0].lower() for token in no_stops_de_en]

    return lemmatized