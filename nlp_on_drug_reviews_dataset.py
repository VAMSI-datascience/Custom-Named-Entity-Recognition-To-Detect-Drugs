# -*- coding: utf-8 -*-
"""NLP on Drug Reviews Dataset.ipynb

### NLP on Drug Reviews with Python
+ Sentiment Analysis
+ Named Entity Recognition
"""

# Load Pkgs
import pandas as pd
import numpy as np

# Load NLP Pkgs
import spacy
from wordcloud import WordCloud, STOPWORDS
from spacy.util import minibatch, compounding

import matplotlib.pyplot as plt
import re
import random

# Load Dataset
df = pd.read_csv("drug_review_dataset_with_sentiment.csv")

df.head()

# NER
nlp0 = spacy.load('en_core_web_sm')

# Get All Components of this NLP Object
nlp0.pipe_names

ner0 = nlp0.get_pipe('ner')

ner0.add_label()

# Example
ex1 = "James went to London to buy Ibuprofen last year 2019"

docx = nlp0(ex1)

type(docx)

# Check for entities
for entity in docx.ents:
  print(entity,entity.label_)



"""#### Preparing the data
+ Training data must be a tuple

TRAIN_DATA = [
    ("Who is Shaka Khan?", {"entities": [(START, STOP, "LABEL")]})
]

TRAIN_DATA = [
    ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
    ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
]
"""

def process_review(review):
    processed_token = []
    for token in review.split():
        token = ''.join(e.lower() for e in token if e.isalnum())
        processed_token.append(token)
    return ' '.join(processed_token)

# Drugs Names
all_drugs = df['drugName'].unique().tolist()

all_drugs = [x.lower() for x in all_drugs]

all_drugs

df['review']

count = 0
TRAIN_DATA = []
for _, item in df.iterrows():
    ent_dict = {}
    if count < 1000:
        review = process_review(item['review'])
        #Locate drugs and their positions once and add to the visited items.
        visited_items = []
        entities = []
        for token in review.split():
            if token in all_drugs:
                for i in re.finditer(token, review):
                    if token not in visited_items:
                        entity = (i.span()[0], i.span()[1], 'DRUG')
                        visited_items.append(token)
                        entities.append(entity)
        if len(entities) > 0:
            ent_dict['entities'] = entities
            train_item = (review, ent_dict)
            TRAIN_DATA.append(train_item)
            count+=1

TRAIN_DATA

"""### Training the NER Model"""



n_iter = 10
def train_ner(training_data):
    """Steps
    Create a Blank NLP  model object
    Create and add NER to the NLP model
    Add Labels from your training data
    Train  
    """
    TRAIN_DATA = training_data
    nlp = spacy.blank("en")  # create blank Language class
    print("Created blank 'en' model")
    
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")
        
    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
            
    nlp.begin_training()
    for itn in range(n_iter):
        random.shuffle(TRAIN_DATA)
        losses = {}
        # batch up the examples using spaCy's minibatch
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            nlp.update(
                texts,  # batch of texts
                annotations,  # batch of annotations
                drop=0.5,  # dropout - make it harder to memorise data
                losses=losses,
            )
        print("Losses", losses)
    return nlp

# Let training
nlp2 = train_ner(TRAIN_DATA)

ex1

docx2 = nlp2(ex1)

for entity in docx2.ents:
  print(entity,entity.label_)

# Test
for text,_ in TRAIN_DATA[:5]:
  doc = nlp2(text)
  result = [(ent,ent.label_) for ent in doc.ents]
  print(result)

def extract_drug_entity(text):
  docx =  nlp2(text)
  result = [(ent,ent.label_) for ent in docx.ents]
  return result

df['review'][0:10]

df['review'][0:10].apply(extract_drug_entity)

