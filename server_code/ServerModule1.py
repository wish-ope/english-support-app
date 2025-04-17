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
    
doc = nlp(word.strip())
result = []
for synset in doc[0]._.wordnet.synsets():
  result.append(f"Definition: {synset.definition()}")
  examples = synset.examples()
  result.append(f"Total Example: {len(examples)}")
  if examples:
    result.append(f"Example: {examples[0]}")
  else:
    result.append("Example: No examples available")
  
  # Thêm synonyms
  for lemma in synset.lemma_names():
    result.append(f"Synonym: {lemma}")
  
  result.append("")  # Thêm dòng trống giữa các synsets
  if not result:
    return f"No synsets found for the word '{word}'."
# Nếu không có synset, trả về thông báo
  return "\n".join(result)
 