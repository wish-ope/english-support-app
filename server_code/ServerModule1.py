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
    
# doc = nlp("dog")
# for synset in doc[0]._.wordnet.synsets():
#     print('Definition: ' + synset.definition())
    
#     # Kiểm tra xem có ví dụ hay không
#     examples = synset.examples()
#     print('Total Example: ' + str(len(examples)))
#     if examples:  # Nếu danh sách ví dụ không rỗng
#         print('Example: ' + examples[0])
#     else:
#         print('Example: No examples available')
    
#     # In các lemma (từ đồng nghĩa)
#     for lemma in synset.lemma_names():
#         print('Synonym: ' + lemma)
  
  doc = nlp(word.strip())
    
    # Thu thập kết quả vào một chuỗi
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
    
    # Nếu không có synset, trả về thông báo
  if not result:
        return f"No synsets found for the word '{word}'."
    
    # Kết hợp tất cả kết quả thành một chuỗi
  return "\n".join(result)