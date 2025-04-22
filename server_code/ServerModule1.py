import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
import nltk

#https://anvil.works/forum/t/how-do-i-load-a-spacy-model/15279/5
#https://spacy.io/models/en#en_core_web_sm
import en_core_web_sm
nlp = en_core_web_sm.load()
#https://github.com/argilla-io/spacy-wordnet
nlp.add_pipe("spacy_wordnet", after='tagger')
# try:
#     nltk.download('wordnet', quiet=True)
#     nlp = spacy.load("en_core_web_sm")
#     nlp.add_pipe("wordnet", after="tagger")
# except:
#     import os
#     os.system("python -m spacy download en_core_web_sm")
#     nlp = spacy.load("en_core_web_sm")
#     nlp.add_pipe("wordnet", after="tagger")

@anvil.server.callable
def get_word_info(vocab_input):
    # if not vocab_input or not vocab_input.strip():
    #     return "Error: Please enter a valid word."
    doc = nlp(vocab_input.strip())
    result = []
    for synset in doc[0]._.wordnet.synsets():
        # print(dir(synset))
        result.append(f"POS: {synset.pos()}")
        result.append(f"Definition: {synset.definition()}")
        examples = synset.examples()
        result.append(f"Total Example: {len(examples)}")
        if examples:
            temp = "Examples:\n"
            for e in examples:
                temp += f"{e}\n"
              
            result.append(temp)
        else:
            result.append(f"No examples available")
        temp = "Synonyms: "
        for lemma in synset.lemma_names():
            temp += f"{lemma}, "
        result.append(temp)
        result.append("")
    
    if not result:
        return f"No synsets found for the word '{vocab_input}'."
    
    return "\n".join(result)