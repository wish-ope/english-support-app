import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
import nltk
from nltk.corpus import wordnet as wn

# Tải mô hình ngôn ngữ và WordNet
try:
  import en_core_web_sm
  # Đảm bảo tải wordnet và omw-1.4
  nltk.download('wordnet', quiet=True)
  nltk.download('omw-1.4', quiet=True)  # Tải Open Multilingual WordNet
  nltk.download('punkt', quiet=True)  # Tải tokenizer
  nltk.download('averaged_perceptron_tagger', quiet=True)  # Tải POS tagger
  nlp = en_core_web_sm.load()
  nlp.add_pipe("spacy_wordnet", after='tagger')
  # Kiểm tra xem wordnet đã tải thành công
  if not wn.synsets('dog'):  # Kiểm tra với một từ phổ biến
    raise Exception("Không thể tải WordNet từ NLTK. Vui lòng kiểm tra kết nối hoặc cài đặt lại.")
except Exception as e:
  raise Exception(f"Không thể tải mô hình ngôn ngữ hoặc WordNet: {str(e)}")

@anvil.server.callable
def get_word_relations(vocab_input):
  """Hàm lấy danh sách đồng nghĩa và trái nghĩa của từ"""
  if not vocab_input or not vocab_input.strip():
    raise ValueError("Từ nhập vào không hợp lệ")

  try:
    doc = nlp(vocab_input.strip())
    synonyms = set()
    antonyms = set()

    print(f"Đang xử lý từ: {vocab_input}")
    print(f"Tokens: {[token.text for token in doc]}")

    for token in doc:
      synsets = token._.wordnet.synsets()
      print(f"Synsets cho token '{token.text}': {len(synsets)}")
      for synset in synsets:
        # Lấy danh sách đồng nghĩa
        for lemma in synset.lemma_names():
          synonyms.add(lemma)
        # Lấy danh sách trái nghĩa
        for lemma in synset.lemmas():
          antonym_list = lemma.antonyms()
          for antonym in antonym_list:
            antonyms.add(antonym.name())

    print(f"Danh sách đồng nghĩa: {list(synonyms)}")
    print(f"Danh sách trái nghĩa: {list(antonyms)}")

    return {
      "synonyms": list(synonyms),
      "antonyms": list(antonyms)
    }
  except Exception as e:
    print(f"Lỗi trong get_word_relations: {str(e)}")
    raise Exception(f"Lỗi khi lấy đồng nghĩa và trái nghĩa: {str(e)}")

@anvil.server.callable
def get_hyponyms(vocab_input):
  """Hàm lấy danh sách các từ nghĩa hẹp (hyponyms) của từ"""
  if not vocab_input or not vocab_input.strip():
    raise ValueError("Từ nhập vào không hợp lệ")

  try:
    hyponyms = set()
    synsets = wn.synsets(vocab_input.strip())
    if not synsets:
      print(f"Không tìm thấy synsets cho từ '{vocab_input}'")
      return []

    for synset in synsets:
      for hyponym in synset.hyponyms():
        hyponyms.update(lemma.name() for lemma in hyponym.lemmas())

    print(f"Danh sách hyponyms: {list(hyponyms)}")
    return list(hyponyms)
  except Exception as e:
    print(f"Lỗi trong get_hyponyms: {str(e)}")
    raise Exception(f"Lỗi khi lấy hyponyms: {str(e)}")

@anvil.server.callable
def get_meronyms(vocab_input):
  """Hàm lấy danh sách các từ biểu thị quan hệ bộ phận-toàn phần (meronyms)"""
  if not vocab_input or not vocab_input.strip():
    raise ValueError("Từ nhập vào không hợp lệ")

  try:
    meronyms = set()
    synsets = wn.synsets(vocab_input.strip())
    if not synsets:
      print(f"Không tìm thấy synsets cho từ '{vocab_input}'")
      return []

    for synset in synsets:
      # Lấy meronyms (bộ phận của toàn phần)
      for meronym in synset.part_meronyms():
        meronyms.update(lemma.name() for lemma in meronym.lemmas())
      for meronym in synset.substance_meronyms():
        meronyms.update(lemma.name() for lemma in meronym.lemmas())

    print(f"Danh sách meronyms: {list(meronyms)}")
    return list(meronyms)
  except Exception as e:
    print(f"Lỗi trong get_meronyms: {str(e)}")
    raise Exception(f"Lỗi khi lấy meronyms: {str(e)}")

@anvil.server.callable
def analyze_sentence(sentence_input):
  """Hàm phân tích câu: token hóa, POS tagging và xác định vai trò từ"""
  if not sentence_input or not sentence_input.strip():
    raise ValueError("Câu nhập vào không hợp lệ")

  try:
    # Token hóa câu
    tokens = nltk.word_tokenize(sentence_input.strip())
    # POS tagging
    pos_tags = nltk.pos_tag(tokens)

    # Chuẩn bị kết quả
    result = []
    for word, pos in pos_tags:
      word_info = {
        "word": word,
        "pos": pos,
        "role": get_word_role(pos)
      }
      result.append(word_info)

    print(f"Kết quả phân tích câu: {result}")
    return result
  except Exception as e:
    print(f"Lỗi trong analyze_sentence: {str(e)}")
    raise Exception(f"Lỗi khi phân tích câu: {str(e)}")

def get_word_role(pos):
  """Hàm ánh xạ POS tag thành vai trò ngữ pháp dễ hiểu"""
  pos_roles = {
    'NN': 'Danh từ (Noun)',
    'NNS': 'Danh từ số nhiều (Plural Noun)',
    'NNP': 'Danh từ riêng (Proper Noun)',
    'NNPS': 'Danh từ riêng số nhiều (Plural Proper Noun)',
    'VB': 'Động từ (Verb)',
    'VBD': 'Động từ quá khứ (Past Verb)',
    'VBG': 'Động từ dạng V-ing (Gerund/Present Participle)',
    'VBN': 'Động từ phân từ quá khứ (Past Participle)',
    'VBP': 'Động từ hiện tại không ngôi thứ 3 (Present Verb, non-3rd person)',
    'VBZ': 'Động từ hiện tại ngôi thứ 3 (Present Verb, 3rd person)',
    'JJ': 'Tính từ (Adjective)',
    'JJR': 'Tính từ so sánh (Comparative Adjective)',
    'JJS': 'Tính từ cao nhất (Superlative Adjective)',
    'RB': 'Trạng từ (Adverb)',
    'RBR': 'Trạng từ so sánh (Comparative Adverb)',
    'RBS': 'Trạng từ cao nhất (Superlative Adverb)',
    'IN': 'Giới từ (Preposition)',
    'DT': 'Mạo từ (Determiner)',
    'PRP': 'Đại từ (Pronoun)',
    'PRP$': 'Đại từ sở hữu (Possessive Pronoun)',
    'CC': 'Liên từ (Conjunction)',
    'TO': 'Giới từ "to" hoặc dạng "to" của động từ',
    '.': 'Dấu câu (Punctuation)'
  }
  return pos_roles.get(pos, 'Không xác định')

@anvil.server.callable
def get_word_info(vocab_input):
  """Hàm lấy thông tin chi tiết của từ"""
  if not vocab_input or not vocab_input.strip():
    raise ValueError("Từ nhập vào không hợp lệ")

  try:
    doc = nlp(vocab_input.strip())
    result = []
    for synset in doc[0]._.wordnet.synsets():
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
        result.append(f"Không có ví dụ")
      temp = "Synonyms: "
      for lemma in synset.lemma_names():
        temp += f"{lemma}, "
      result.append(temp)
      result.append("")

    if not result:
      return f"Không tìm thấy thông tin cho từ '{vocab_input}'."

    return "\n".join(result)
  except Exception as e:
    raise Exception(f"Lỗi khi lấy thông tin chi tiết: {str(e)}")

@anvil.server.callable
def add_vocab(new_vocab_data):
  """Hàm thêm từ vào bảng vocab"""
  try:
    current_user = anvil.users.get_user()
    if current_user is not None:
      app_tables.vocab.add_row(
        Vocab=new_vocab_data["vocab_input"],
        Means=new_vocab_data["means_output"],
        User=current_user
      )
  except Exception as e:
    raise Exception(f"Lỗi khi thêm từ: {str(e)}")

@anvil.server.callable
def update_user(first_name, last_name, phone):
  """Hàm cập nhật thông tin người dùng"""
  try:
    curr_user = anvil.users.get_user()
    if curr_user:
      curr_user['first_name'] = first_name
      curr_user['last_name'] = last_name
      curr_user['phone'] = phone
  except Exception as e:
    raise Exception(f"Lỗi khi cập nhật thông tin người dùng: {str(e)}")

@anvil.server.callable
def get_curr_user_data():
  """Hàm lấy thông tin người dùng hiện tại"""
  try:
    curr_user = anvil.users.get_user()
    if curr_user:
      return {
        "first_name": curr_user['first_name'],
        "last_name": curr_user['last_name']
      }
  except Exception as e:
    raise Exception(f"Lỗi khi lấy thông tin người dùng: {str(e)}")