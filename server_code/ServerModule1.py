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
nltk.download('wordnet', quiet=True)
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

@anvil.server.callable
def add_vocab(new_vocab_data):
  current_user = anvil.users.get_user()
  if current_user is not None:
    app_tables.vocab.add_row(
      Vocab=new_vocab_data["vocab_input"],
      Means=new_vocab_data["means_output"],
      User=current_user
    )
def update_user(first_name, last_name, phone):
  curr_user = anvil.users.get_user()
  if curr_user:
    curr_user['first_name'] = first_name
    curr_user['last_name'] = last_name
    curr_user['phone'] = phone
# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
