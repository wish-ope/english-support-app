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
def get_word_info(word):
  if not word or not word.strip():
    return "Error: Please enter a valid word."
    
