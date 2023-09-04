#!/bin/bash
echo "Realizando o download das bases de dados para processamento natural de texto..."
python -m nltk.downloader wordnet
python -m nltk.downloader omw
python -m nltk.downloader wordnet_ic
python -m nltk.downloader stopwords
python -m nltk.downloader rslp
python -m nltk.downloader punkt