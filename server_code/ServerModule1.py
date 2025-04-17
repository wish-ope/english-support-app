import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 
import nltk
import en_core_web_sm
nltk.download('wordnet') 
nlp = en_core_web_sm.load()
nlp.add_pipe("spacy_wordnet", after='tagger')

@anvil.server.callable
def add_vocab(vocab_data):
  app_tables.vocab.add_row(Vocab=vocab_data["vocab_input"], Means=vocab_data["means_input"])
doc = nlp("dog")
# for token in doc:
#      print(token.text, token.lemma_, token.pos_,token._.wordnet.synsets(),
#      token._.wordnet.lemmas()
#            )

for synset in doc[0]._.wordnet.synsets():
    print('Definition: ' + synset.definition())
    
    # Kiểm tra xem có ví dụ hay không
    examples = synset.examples()
    print('Total Example: ' + str(len(examples)))
    if examples:  # Nếu danh sách ví dụ không rỗng
        print('Example: ' + examples[0])
    else:
        print('Example: No examples available')
    
    # In các lemma (từ đồng nghĩa)
    for lemma in synset.lemma_names():
        print('Synonym: ' + lemma)
  
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
