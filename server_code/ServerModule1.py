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
    result.append('Definition: ' + synset.definition())
    
    # Kiểm tra xem có ví dụ hay không
    examples = synset.examples()
    result.append('Total Example: ' + str(len(examples)))
    if examples:  # Nếu danh sách ví dụ không rỗng
        result.append('Example: ' + examples[0])
    else:
        result.append('Example: No examples available')
    
    # In các lemma (từ đồng nghĩa)
    for lemma in synset.lemma_names():
       result.append('Synonym: ' + lemma)
    result.append("")
  # Nếu không có synset, trả về thông báo
if not result:
        return f"No synsets found for the word '{word}'."
    
    # Kết hợp tất cả kết quả thành một chuỗi
return "\n".join(result)
