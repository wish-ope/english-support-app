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
import json

# Tải mô hình ngôn ngữ và WordNet
try:
  import en_core_web_sm
  nltk.download('wordnet', quiet=True)
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
def process_input(input_data, mode = True):
  """Hàm xử lý đầu vào: phân biệt từ/câu và trả về kết quả tương ứng"""
  if not input_data:
    raise ValueError("Văn bản nhập vào không hợp lệ")
  
  if mode:
    # Xử lý từ hoặc cụm từ
    if not isinstance(input_data, list):
      input_data = [input_data.strip()]
    words = [w.strip() for w in input_data if w.strip()]
    if not words:
      raise ValueError("Danh sách từ không hợp lệ")

    relations_dict = {}
    for word in words:
      word_data = get_word_data(word)
      if word_data:
        relations_dict[word] = word_data["relations"]
        continue

      doc = nlp(word)
      # Phát hiện cụm danh từ
      noun_phrases = [chunk.text for chunk in doc.noun_chunks]
      is_phrase = len(noun_phrases) == 1 and noun_phrases[0] == word
      synonyms, antonyms, hyponyms, meronyms = set(), set(), set(), set()
      if is_phrase:
        # Lấy synset cho head noun (từ cuối)
        head_noun = doc[-1].text
        head_doc = nlp(head_noun)
        for synset in head_doc[0]._.wordnet.synsets():
          synonyms.update(synset.lemma_names())
          antonyms.update(lemma.antonyms()[0].name() for lemma in synset.lemmas() if lemma.antonyms())
          hyponyms.update(lemma.name() for hyponym in synset.hyponyms() for lemma in hyponym.lemmas())
          meronyms.update(lemma.name() for meronym in synset.part_meronyms() + synset.substance_meronyms() for lemma in meronym.lemmas())
      else:
        for synset in doc[0]._.wordnet.synsets():
          synonyms.update(synset.lemma_names())
          antonyms.update(lemma.antonyms()[0].name() for lemma in synset.lemmas() if lemma.antonyms())
          hyponyms.update(lemma.name() for hyponym in synset.hyponyms() for lemma in hyponym.lemmas())
          meronyms.update(lemma.name() for meronym in synset.part_meronyms() + synset.substance_meronyms() for lemma in meronym.lemmas())

      relations = {
        "synonyms": list(synonyms),
        "antonyms": list(antonyms),
        "hyponyms": list(hyponyms),
        "meronyms": list(meronyms)
      }
      relations_dict[word] = relations
      detailed_info = get_word_info(word)
      save_word_data(word, relations, detailed_info["detailed_info"], detailed_info["image_url"])
    return {"type": "word", "words": words, "relations": relations_dict}
  else:
    # Xử lý câu
    doc = nlp(input_data.strip())
    tokens = [token.text for token in doc]
    if len(tokens) < 2:
      raise ValueError("Vui lòng nhập một câu hoàn chỉnh!")
    result = [{"word": token.text, "pos": token.pos_, "role": get_word_role(token.pos_)} for token in doc]
    return {"type": "sentence", "sentence_analysis": result}

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
  if not vocab_input or not vocab_input.strip():
    raise ValueError("Từ nhập vào không hợp lệ")
  try:
    doc = nlp(vocab_input.strip())
    # Phát hiện cụm danh từ
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
    is_phrase = len(noun_phrases) == 1 and noun_phrases[0] == vocab_input
    synsets = doc[0]._.wordnet.synsets() if not is_phrase else []
    if is_phrase and not synsets:
      # Thử lấy synset cho head noun
      head_noun = doc[-1].text
      head_doc = nlp(head_noun)
      synsets = head_doc[0]._.wordnet.synsets()

    if not synsets:
      return {
        "detailed_info": f"Không tìm thấy thông tin chi tiết cho '{vocab_input}'.",
        "image_url": get_image_url(vocab_input)
      }

    image_url = get_image_url(vocab_input)
    result = []
    if is_phrase:
      result.append(f"**Cụm danh từ: {vocab_input}**")
    for idx, synset in enumerate(synsets, 1):
      result.append(f"**Nghĩa {idx}:**")
      pos_desc = {'n': 'Danh từ', 'v': 'Động từ', 'a': 'Tính từ', 'r': 'Trạng từ', 's': 'Tính từ vệ tinh'}.get(synset.pos(), 'Không xác định')
      result.append(f"Loại từ (POS): {pos_desc}")
      result.append(f"Định nghĩa: {synset.definition()}")
      examples = synset.examples()
      result.append(f"Số câu ví dụ: {len(examples)}")
      if examples:
        result.append("Câu ví dụ:\n" + "\n".join(f"- {e}" for e in examples[:3]))
      else:
        result.append("Không có ví dụ")
      result.append("")

    return {"detailed_info": "\n".join(result), "image_url": image_url}
  except Exception as e:
    raise Exception(f"Lỗi khi lấy thông tin chi tiết: {str(e)}")

@anvil.server.callable
def get_word_of_the_day():
  """Hàm lấy từ của ngày từ cơ sở dữ liệu"""
  try:
    current_user = anvil.users.get_user()
    if not current_user:
      print("Không có người dùng đăng nhập, lấy từ ngẫu nhiên từ WordNet.")
      all_synsets = list(wn.all_synsets())
      if not all_synsets:
        raise Exception("Không thể lấy danh sách từ từ WordNet.")

      random_synset = random.choice(all_synsets)
      word = random_synset.lemma_names()[0].replace('_', ' ')
      detailed_info = get_word_info(word)
      return f"**Từ của ngày: {word}**\n\n{detailed_info}"

    vocab_rows = app_tables.vocab.search(User=current_user)
    if not vocab_rows:
      print("Không có từ nào trong cơ sở dữ liệu, lấy từ ngẫu nhiên từ WordNet.")
      all_synsets = list(wn.all_synsets())
      if not all_synsets:
        raise Exception("Không thể lấy danh sách từ từ WordNet.")

      random_synset = random.choice(all_synsets)
      word = random_synset.lemma_names()[0].replace('_', ' ')
      detailed_info = get_word_info(word)
      return f"**Từ của ngày: {word}**\n\n{detailed_info}"

    vocab_list = list(vocab_rows)
    random_row = random.choice(vocab_list)
    word = random_row['Vocab']
    detailed_info = random_row['DetailedInfo']

    if not detailed_info:
      print(f"Không có DetailedInfo cho từ '{word}', lấy từ WordNet.")
      detailed_info = get_word_info(word)
      random_row.update(DetailedInfo=detailed_info)

    return f"**Từ của ngày: {word}**\n\n{detailed_info}"
  except Exception as e:
    raise Exception(f"Lỗi khi lấy từ của ngày: {str(e)}")

@anvil.server.callable
def save_word_data(word, relations, detailed_info):
  """Hàm lưu từ, các mối quan hệ từ vựng và nghĩa chi tiết vào bảng vocab"""
  try:
    current_user = anvil.users.get_user()
    if not current_user:
      print("Không có người dùng đăng nhập, không lưu vào cơ sở dữ liệu.")
      return

    existing_row = app_tables.vocab.get(Vocab=word, User=current_user)
    if existing_row:
      existing_row.update(
        Synonyms=json.dumps(relations["synonyms"]),
        Antonyms=json.dumps(relations["antonyms"]),
        Hyponyms=json.dumps(relations["hyponyms"]),
        Meronyms=json.dumps(relations["meronyms"]),
        Means=detailed_info,
        DetailedInfo=detailed_info
      )
    else:
      app_tables.vocab.add_row(
        Vocab=word,
        Synonyms=json.dumps(relations["synonyms"]),
        Antonyms=json.dumps(relations["antonyms"]),
        Hyponyms=json.dumps(relations["hyponyms"]),
        Meronyms=json.dumps(relations["meronyms"]),
        Means=detailed_info,
        DetailedInfo=detailed_info,
        User=current_user
      )
    print(f"Đã lưu từ '{word}' vào cơ sở dữ liệu.")
  except Exception as e:
    print(f"Lỗi khi lưu từ '{word}' vào cơ sở dữ liệu: {str(e)}")

@anvil.server.callable
def get_word_data(word):
  """Hàm lấy dữ liệu từ vựng từ cơ sở dữ liệu"""
  try:
    current_user = anvil.users.get_user()
    if not current_user:
      return None

    row = app_tables.vocab.get(Vocab=word, User=current_user)
    if row:
      return {
        "relations": {
          "synonyms": json.loads(row['Synonyms']) if row['Synonyms'] else [],
          "antonyms": json.loads(row['Antonyms']) if row['Antonyms'] else [],
          "hyponyms": json.loads(row['Hyponyms']) if row['Hyponyms'] else [],
          "meronyms": json.loads(row['Meronyms']) if row['Meronyms'] else []
        },
        "detailed_info": row['DetailedInfo']
      }
    return None
  except Exception as e:
    print(f"Lỗi khi lấy dữ liệu từ cơ sở dữ liệu cho từ '{word}': {str(e)}")
    return None

@anvil.server.callable
def save_detailed_info(word, detailed_info):
  """Hàm lưu nghĩa chi tiết của từ vào cơ sở dữ liệu"""
  try:
    current_user = anvil.users.get_user()
    if not current_user:
      print("Không có người dùng đăng nhập, không lưu vào cơ sở dữ liệu.")
      return

    row = app_tables.vocab.get(Vocab=word, User=current_user)
    if row:
      # row.update(DetailedInfo=detailed_info, Means=detailed_info)
      return  # Từ đã tồn tại, bỏ qua.
    else:
      app_tables.vocab.add_row(
        Vocab=word,
        Synonyms=json.dumps([]),
        Antonyms=json.dumps([]),
        Hyponyms=json.dumps([]),
        Meronyms=json.dumps([]),
        Means=detailed_info,
        DetailedInfo=detailed_info,
        User=current_user
      )
    print(f"Đã lưu nghĩa chi tiết cho từ '{word}' vào cơ sở dữ liệu.")
  except Exception as e:
    print(f"Lỗi khi lưu nghĩa chi tiết cho từ '{word}': {str(e)}")

@anvil.server.callable
def get_detailed_info(word):
  try:
    current_user = anvil.users.get_user()
    if not current_user:
      return None
    row = app_tables.vocab.get(Vocab=word, User=current_user)
    if row:
      return {"detailed_info": row['DetailedInfo'], "image_url": row['ImageUrl']}
    return None
  except:
    return None


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