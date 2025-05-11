import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
import nltk

# Tải mô hình ngôn ngữ và WordNet
try:
  import en_core_web_sm
  nltk.download('wordnet', quiet=True)
  nlp = en_core_web_sm.load()
  nlp.add_pipe("spacy_wordnet", after='tagger')
except Exception as e:
  raise Exception(f"Không thể tải mô hình ngôn ngữ: {str(e)}")

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