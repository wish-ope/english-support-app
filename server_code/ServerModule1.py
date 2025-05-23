import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
import nltk
import random
import anvil.http
import json

try:
  import en_core_web_sm
  nltk.download('wordnet', quiet=True)
  nlp = en_core_web_sm.load()
  nlp.add_pipe("spacy_wordnet", after='tagger')
except Exception as e:
  raise Exception(f"Không thể tải mô hình ngôn ngữ hoặc WordNet: {str(e)}")

def get_image_url(word):
  try:
    url = f"https://api.unsplash.com/search/photos?query={word}&per_page=1&client_id=xdz1FY6iYimqqxpSaE1KWgyW5LO6HphF-CHGI0Ty7mk"
    response = anvil.http.request(url, method="GET", json=True)
    return response['results'][0]['urls']['small'] if response.get('results') else "Không tìm thấy ảnh"
  except:
    return "Không tìm thấy ảnh"

@anvil.server.callable
def process_input(text):
  if not text or not text.strip():
    raise ValueError("Văn bản nhập vào không hợp lệ")
  doc = nlp(text.strip())
  tokens = [token.text for token in doc]

  if len(tokens) == 1:
    word = tokens[0]
    word_data = get_word_data(word)
    if word_data:
      return {"type": "word", "word": word, "relations": word_data["relations"]}

    synonyms, antonyms, hyponyms, meronyms = set(), set(), set(), set()
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
    detailed_info = get_word_info(word)
    save_word_data(word, relations, detailed_info["detailed_info"], detailed_info["image_url"])
    return {"type": "word", "word": word, "relations": relations}
  else:
    result = [{"word": token.text, "pos": token.pos_, "role": get_word_role(token.pos_)} for token in doc]
    return {"type": "sentence", "sentence_analysis": result}

def get_word_role(pos):
  pos_roles = {
    'NOUN': 'Danh từ', 'VERB': 'Động từ', 'ADJ': 'Tính từ', 'ADV': 'Trạng từ',
    'PRON': 'Đại từ', 'DET': 'Mạo từ', 'ADP': 'Giới từ', 'CONJ': 'Liên từ',
    'PUNCT': 'Dấu câu', 'AUX': 'Trợ động từ', 'NUM': 'Số từ', 'PART': 'Tiểu từ',
    'SCONJ': 'Liên từ phụ thuộc'
  }
  return pos_roles.get(pos, 'Không xác định')

@anvil.server.callable
def get_word_info(vocab_input):
  if not vocab_input or not vocab_input.strip():
    raise ValueError("Từ nhập vào không hợp lệ")
  try:
    doc = nlp(vocab_input.strip())
    synsets = doc[0]._.wordnet.synsets()
    if not synsets:
      return {"detailed_info": f"Không tìm thấy thông tin cho từ '{vocab_input}'.", "image_url": "Không tìm thấy ảnh"}

    image_url = get_image_url(vocab_input)
    result = []
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
  try:
    current_user = anvil.users.get_user()
    if not current_user:
      return "Không có người dùng đăng nhập."

    vocab_rows = app_tables.vocab.search(User=current_user)
    if not vocab_rows:
      return "Không có từ nào trong cơ sở dữ liệu."

    random_row = random.choice(list(vocab_rows))
    word = random_row['Vocab']
    detailed_info = random_row['DetailedInfo'] or get_word_info(word)["detailed_info"]
    return f"**Từ của ngày: {word}**\n\n{detailed_info}"
  except Exception as e:
    raise Exception(f"Lỗi khi lấy từ của ngày: {str(e)}")

@anvil.server.callable
def save_word_data(word, relations, detailed_info, image_url):
  try:
    current_user = anvil.users.get_user()
    if not current_user:
      return
    row = app_tables.vocab.get(Vocab=word, User=current_user)
    if row:
      if not row['ImageUrl'] or not row['Synonyms']:
        row.update(
          Synonyms=json.dumps(relations["synonyms"]),
          Antonyms=json.dumps(relations["antonyms"]),
          Hyponyms=json.dumps(relations["hyponyms"]),
          Meronyms=json.dumps(relations["meronyms"]),
          DetailedInfo=detailed_info,
          ImageUrl=image_url
        )
      return
    app_tables.vocab.add_row(
      Vocab=word,
      Synonyms=json.dumps(relations["synonyms"]),
      Antonyms=json.dumps(relations["antonyms"]),
      Hyponyms=json.dumps(relations["hyponyms"]),
      Meronyms=json.dumps(relations["meronyms"]),
      DetailedInfo=detailed_info,
      ImageUrl=image_url,
      User=current_user
    )
  except:
    pass

@anvil.server.callable
def get_word_data(word):
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
        }
      }
    return None
  except:
    return None

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
  try:
    current_user = anvil.users.get_user()
    if current_user:
      app_tables.vocab.add_row(
        Vocab=new_vocab_data["vocab_input"],
        DetailedInfo=new_vocab_data["means_output"],
        User=current_user
      )
  except Exception as e:
    raise Exception(f"Lỗi khi thêm từ: {str(e)}")

@anvil.server.callable
def update_user(first_name, last_name, phone):
  try:
    curr_user = anvil.users.get_user()
    if curr_user:
      curr_user.update(first_name=first_name, last_name=last_name, phone=phone)
  except Exception as e:
    raise Exception(f"Lỗi khi cập nhật thông tin người dùng: {str(e)}")

@anvil.server.callable
def get_curr_user_data():
  try:
    curr_user = anvil.users.get_user()
    if curr_user:
      return {
        "first_name": curr_user['first_name'],
        "last_name": curr_user['last_name']
      }
  except Exception as e:
    raise Exception(f"Lỗi khi lấy thông tin người dùng: {str(e)}")