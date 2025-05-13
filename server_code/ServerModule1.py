import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
import nltk
from nltk.corpus import wordnet as wn
import random
import anvil.http

# Tải mô hình ngôn ngữ và WordNet
try:
  import en_core_web_sm
  nltk.download('wordnet', quiet=True)
  #hỗ trợ các hàm như get_meronyms, get_hyponyms
  nltk.download('omw-1.4', quiet=True)
  nlp = en_core_web_sm.load()
  nlp.add_pipe("spacy_wordnet", after='tagger')
except Exception as e:
  raise Exception(f"Không thể tải mô hình ngôn ngữ hoặc WordNet: {str(e)}")

def get_image_url(word):
  """Hàm lấy URL ảnh minh họa từ Unsplash"""
  try:
    url = f"https://api.unsplash.com/search/photos?query={word}&per_page=1&client_id=xdz1FY6iYimqqxpSaE1KWgyW5LO6HphF-CHGI0Ty7mk"
    response = anvil.http.request(url, method="GET", json=True)
    if response.get('results'):
      return response['results'][0]['urls']['small']
    return None
  except Exception as e:
    print(f"Lỗi khi lấy ảnh: {str(e)}")
    return None

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
        for lemma in synset.lemma_names():
          synonyms.add(lemma)
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
def get_tokens(text):
  """Hàm trả về danh sách từ từ SpaCy Doc object"""
  if not text or not text.strip():
    raise ValueError("Văn bản nhập vào không hợp lệ")

  try:
    doc = nlp(text.strip())
    tokens = [token.text for token in doc]
    print(f"Danh sách từ: {tokens}")
    return tokens
  except Exception as e:
    print(f"Lỗi trong get_tokens: {str(e)}")
    raise Exception(f"Lỗi khi tách từ: {str(e)}")

@anvil.server.callable
def analyze_sentence(sentence_input):
  """Hàm phân tích câu: token hóa, POS tagging và xác định vai trò từ"""
  if not sentence_input or not sentence_input.strip():
    raise ValueError("Câu nhập vào không hợp lệ")

  try:
    doc = nlp(sentence_input.strip())
    result = []
    for token in doc:
      word_info = {
        "word": token.text,
        "pos": token.pos_,
        "role": get_word_role(token.pos_)
      }
      result.append(word_info)

    print(f"Kết quả phân tích câu: {result}")
    return result
  except Exception as e:
    print(f"Lỗi trong analyze_sentence: {str(e)}")
    raise Exception(f"Lỗi khi phân tích câu: {str(e)}")

def get_word_role(pos):
  """Hàm ánh xạ POS tag của SpaCy thành vai trò ngữ pháp dễ hiểu"""
  pos_roles = {
    'NOUN': 'Danh từ (Noun)',
    'VERB': 'Động từ (Verb)',
    'ADJ': 'Tính từ (Adjective)',
    'ADV': 'Trạng từ (Adverb)',
    'PRON': 'Đại từ (Pronoun)',
    'DET': 'Mạo từ (Determiner)',
    'ADP': 'Giới từ (Preposition)',
    'CONJ': 'Liên từ (Conjunction)',
    'PUNCT': 'Dấu câu (Punctuation)',
    'AUX': 'Trợ động từ (Auxiliary Verb)',
    'NUM': 'Số từ (Numeral)',
    'PART': 'Tiểu từ (Particle)',
    'SCONJ': 'Liên từ phụ thuộc (Subordinating Conjunction)'
  }
  return pos_roles.get(pos, 'Không xác định')

def get_pos_description(pos_code):
  """Hàm ánh xạ mã POS của WordNet thành mô tả dễ hiểu"""
  pos_descriptions = {
    'n': 'Danh từ (Noun)',
    'v': 'Động từ (Verb)',
    'a': 'Tính từ (Adjective)',
    'r': 'Trạng từ (Adverb)',
    's': 'Tính từ vệ tinh (Satellite Adjective)'
  }
  return pos_descriptions.get(pos_code, 'Không xác định')

@anvil.server.callable
def get_word_info(vocab_input):
  """Hàm lấy thông tin chi tiết của từ với nội dung mở rộng, bao gồm ảnh minh họa"""
  if not vocab_input or not vocab_input.strip():
    raise ValueError("Từ nhập vào không hợp lệ")

  try:
    doc = nlp(vocab_input.strip())
    result = []

    # Lấy tất cả synsets cho từ
    synsets = doc[0]._.wordnet.synsets()
    if not synsets:
      return f"Không tìm thấy thông tin cho từ '{vocab_input}'."

    # Thêm ảnh minh họa (URL)
    image_url = get_image_url(vocab_input)
    result.append(f"**Ảnh minh họa:** {image_url if image_url else 'Không tìm thấy ảnh'}")
    result.append("")

    # Xử lý từng synset
    for idx, synset in enumerate(synsets, 1):
      result.append(f"**Nghĩa {idx}:**")

      # POS và mô tả
      pos = synset.pos()
      pos_desc = get_pos_description(pos)
      result.append(f"Loại từ (POS): {pos_desc}")

      # Định nghĩa
      definition = synset.definition()
      result.append(f"Định nghĩa: {definition}")

      # Ví dụ
      examples = synset.examples()
      result.append(f"Số câu ví dụ: {len(examples)}")
      if examples:
        temp = "Câu ví dụ:\n"
        for e in examples[:3]:  # Giới hạn tối đa 3 ví dụ mỗi synset
          temp += f"- {e}\n"
        result.append(temp)
      else:
        result.append("Không có ví dụ")

      # Hypernyms (Từ nghĩa rộng)
      hypernyms = set()
      for hypernym in synset.hypernyms():
        hypernyms.update(lemma.name() for lemma in hypernym.lemmas())
      if hypernyms:
        temp = "Từ nghĩa rộng (Hypernyms): "
        temp += ", ".join(list(hypernyms)[:5])  # Giới hạn tối đa 5 từ
        result.append(temp)
      else:
        result.append("Không có từ nghĩa rộng")

      # Từ liên quan (Related Words)
      related_words = set()
      for lemma in synset.lemmas():
        for similar in lemma.similar_tos():
          related_words.add(similar.name())
        for derivation in lemma.derivationally_related_forms():
          related_words.add(derivation.name())
      if related_words:
        temp = "Từ liên quan (Related Words): "
        temp += ", ".join(list(related_words)[:5])
        result.append(temp)
      else:
        result.append("Không có từ liên quan")

      result.append("")  # Dòng trống để phân tách các nghĩa

    return "\n".join(result)
  except Exception as e:
    raise Exception(f"Lỗi khi lấy thông tin chi tiết: {str(e)}")

@anvil.server.callable
def get_word_of_the_day():
  """Hàm lấy từ của ngày với định nghĩa và ví dụ rõ ràng hơn"""
  try:
    all_synsets = list(wn.all_synsets())
    if not all_synsets:
      raise Exception("Không thể lấy danh sách từ từ WordNet.")

    random_synset = random.choice(all_synsets)
    word = random_synset.lemma_names()[0].replace('_', ' ')

    doc = nlp(word)
    result = []

    synsets = doc[0]._.wordnet.synsets()
    if not synsets:
      return f"Không tìm thấy thông tin cho từ '{word}'."

    for idx, synset in enumerate(synsets[:1], 1):
      result.append(f"**Từ của ngày: {word}**")

      pos = synset.pos()
      pos_desc = get_pos_description(pos)
      result.append(f"Loại từ (POS): {pos_desc}")

      definition = synset.definition()
      result.append(f"Định nghĩa: {definition}")

      # Cung cấp giải thích thêm cho định nghĩa
      if definition == "terminate" and pos == "v":
        result.append("Giải thích: Nghĩa là 'chấm dứt' hoặc 'kết thúc', thường dùng để chỉ việc dừng lại một hành động hoặc trạng thái, ví dụ: chấm dứt hợp đồng (break a contract).")

      examples = synset.examples()
      if examples:
        result.append("Câu ví dụ:")
        # Lọc ví dụ phù hợp hơn
        filtered_examples = [ex for ex in examples if "interrupt" not in ex.lower()]  # Loại bỏ ví dụ gây nhầm lẫn
        if filtered_examples:
          result.append(f"- {filtered_examples[0]}")
        else:
          # Thêm ví dụ tự tạo nếu không có ví dụ phù hợp
          if definition == "terminate" and pos == "v":
            result.append("- They decided to break the agreement.")
          else:
            result.append(f"- {examples[0]}")
      else:
        if definition == "terminate" and pos == "v":
          result.append("Câu ví dụ:")
          result.append("- They decided to break the agreement.")
        else:
          result.append("Không có ví dụ")

      result.append("")

    return "\n".join(result)
  except Exception as e:
    raise Exception(f"Lỗi khi lấy từ của ngày: {str(e)}")

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