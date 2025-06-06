from ._anvil_designer import Home_pageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
from ..User_form import User_form

class WordRelations:
  def __init__(self, synonyms=None, antonyms=None, hyponyms=None, meronyms=None):
    self.synonyms = synonyms or []
    self.antonyms = antonyms or []
    self.hyponyms = hyponyms or []
    self.meronyms = meronyms or []

  def get_relations(self, relation_type):
    return getattr(self, relation_type, [])

  def has_data(self, relation_type):
    return bool(self.get_relations(relation_type))

class Home_page(Home_pageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.input_words = []
    self.word_relations_dict = {}
    self.current_word = None

    self._init_user()
    self._init_defaults_()
    self._init_dropdown_()
    self._init_word_of_day_()

  def _init_user(self):
    self.curr_user = anvil.users.get_user()
    self.check_user_info()
    self.add_btn.visible = bool(self.curr_user)

  def _init_defaults_(self):
    self.result_panel.clear()
    self.relation_panel.clear()
    self.detail_label.text = "Chọn một từ hoặc cụm từ để xem chi tiết."
    self.word_image.visible = False
    self.search_result_panel.visible = False

  def _init_dropdown_(self):
    self.dropdown_items = [
      ("Đồng nghĩa", "synonyms"),
      ("Trái nghĩa", "antonyms"),
      ("Hyponyms", "hyponyms"),
      ("Meronyms", "meronyms")
    ]
    self.category_dropdown.items = self.dropdown_items
    self.category_dropdown.selected_value = "synonyms"
    self.category_dropdown.add_event_handler('change', self.category_dropdown_change)

    if not hasattr(self, 'word_dropdown'):
      self.word_dropdown = DropDown(name="word_dropdown")
      self.add_component(self.word_dropdown)
    self.word_dropdown.items = []
    self.word_dropdown.add_event_handler('change', self.word_dropdown_change)

  def _init_word_of_day_(self):
    try:
      self.word_of_day_content.text = anvil.server.call('get_word_of_the_day')
    except Exception as e:
      self.word_of_day_content.text = f"Lỗi khi lấy từ của ngày: {str(e)}"

  def clear_all(self):
    self.result_panel.clear()

  def clear_relations(self):
    self.relation_panel.clear()

  def analyze_word_btn_click(self, **event_args):
    input_text = self.input_text.text.strip()
    if not input_text:
      alert("Vui lòng nhập một từ hoặc cụm từ hợp lệ!")
      return

    words = [w.strip() for w in input_text.split('/') if w.strip()]
    if not words:
      alert("Đầu vào không hợp lệ! Vui lòng nhập ít nhất một từ hoặc cụm từ.")
      return

    try:
      result = anvil.server.call('process_input', words, is_word=True)
      self.input_words = result["words"]
      self.word_relations_dict.clear()
      for word, relations in result["relations"].items():
        self.word_relations_dict[word] = WordRelations(
          synonyms=relations.get("synonyms", []),
          antonyms=relations.get("antonyms", []),
          hyponyms=relations.get("hyponyms", []),
          meronyms=relations.get("meronyms", [])
        )
      self.current_word = self.input_words[0] if self.input_words else None
      self.update_word_dropdown()
      self.update_dropdown_options()
      self.update_relation_panel()
      if self.current_word:
        self.update_word_details(self.current_word)
      self.search_result_panel.visible = True
    except Exception as e:
      alert(f"Lỗi khi xử lý: {str(e)}")

  def analyze_sentence_btn_click(self, **event_args):
    input_text = self.input_text.text.strip()
    if not input_text:
      alert("Vui lòng nhập một câu hợp lệ!")
      return

    try:
      result = anvil.server.call('process_input', input_text, is_word=False)
      if result["type"] == "sentence":
        self.input_words = []
        self.word_relations_dict.clear()
        self.analyze_sentence(result["sentence_analysis"])
        self.detail_label.text = "Chọn một từ hoặc cụm từ để xem chi tiết."
        self.clear_relations()
        self.word_dropdown.items = []
        self.search_result_panel.visible = True
      else:
        alert("Đầu vào không phải là một câu hợp lệ!")
    except Exception as e:
      alert(f"Lỗi khi xử lý: {str(e)}")

  def update_word_dropdown(self):
    self.word_dropdown.items = [(w, w) for w in self.input_words]
    self.word_dropdown.selected_value = self.current_word

  def word_dropdown_change(self, **event_args):
    self.current_word = self.word_dropdown.selected_value
    if self.current_word:
      self.update_dropdown_options()
      self.update_relation_panel()
      self.update_word_details(self.current_word)

  def update_dropdown_options(self):
    if not self.current_word or not self.word_relations_dict.get(self.current_word):
      self.category_dropdown.items = [("Không có dữ liệu", "none")]
      self.category_dropdown.selected_value = "none"
      return
    enabled_items = [(text, value) for text, value in self.dropdown_items
                     if self.word_relations_dict[self.current_word].has_data(value)]
    self.category_dropdown.items = enabled_items or [("Không có dữ liệu", "none")]
    if self.category_dropdown.selected_value not in [item[1] for item in self.category_dropdown.items]:
      self.category_dropdown.selected_value = enabled_items[0][1] if enabled_items else "none"
      self.update_relation_panel()

  def update_relation_panel(self):
    value = self.category_dropdown.selected_value
    self.clear_relations()
    if self.current_word and value != "none" and self.current_word in self.word_relations_dict:
      result = self.word_relations_dict[self.current_word].get_relations(value)
      if result:
        links = [Link(text=str(item), role="default", spacing_above="small", spacing_below="small")
                 for item in result]
        for link in links:
          link.tag.word = link.text
          link.add_event_handler('click', self.result_word_click)
        for link in links:
          self.relation_panel.add_component(link)

  def category_dropdown_change(self, **event_args):
    self.update_relation_panel()

  def analyze_sentence(self, sentence_analysis):
    self.clear_all()
    links = [Link(text=f"{word_info['word']} ({word_info['role']})", role="default",
                  spacing_above="small", spacing_below="small")
             for word_info in sentence_analysis]
    for link in links:
      link.tag.word = link.text.split(" (")[0]
      link.add_event_handler('click', self.sentence_word_click)
    for link in links:
      self.result_panel.add_component(link)

  def result_word_click(self, sender, **event_args):
    word = sender.tag.word
    self.current_word = word
    try:
      result = anvil.server.call('process_input', [word], is_word=True)
      if result["type"] == "word":
        if not any(result["relations"][word].values()):
          self.detail_label.text = "Không tìm thấy dữ liệu quan hệ cho từ này."
          self.clear_relations()
          return
        self.word_relations_dict[word] = WordRelations(
          synonyms=result["relations"][word].get("synonyms", []),
          antonyms=result["relations"][word].get("antonyms", []),
          hyponyms=result["relations"][word].get("hyponyms", []),
          meronyms=result["relations"][word].get("meronyms", [])
        )
        detailed_info_data = anvil.server.call('get_detailed_info', word)
        if not detailed_info_data:
          detailed_info_data = anvil.server.call('get_word_info', word)
        anvil.server.call('save_word_data', word, result["relations"][word],
                          detailed_info_data["detailed_info"], detailed_info_data["image_url"])
        self.input_words.append(word)
        self.update_word_dropdown()
        self.update_dropdown_options()
        self.update_relation_panel()
        self.update_word_details(word)
      else:
        self.detail_label.text = "Từ không được xử lý đúng."
        self.clear_relations()
    except Exception as e:
      alert(f"Lỗi khi xử lý từ: {str(e)}")

  def sentence_word_click(self, sender, **event_args):
    word = sender.tag.word
    self.current_word = word
    try:
      result = anvil.server.call('process_input', [word], is_word=True)
      if result["type"] == "word":
        if not any(result["relations"][word].values()):
          self.detail_label.text = "Không tìm thấy dữ liệu quan hệ cho từ này."
          self.clear_relations()
          return
        self.word_relations_dict[word] = WordRelations(
          synonyms=result["relations"][word].get("synonyms", []),
          antonyms=result["relations"][word].get("antonyms", []),
          hyponyms=result["relations"][word].get("hyponyms", []),
          meronyms=result["relations"][word].get("meronyms", [])
        )
        detailed_info_data = anvil.server.call('get_detailed_info', word)
        if not detailed_info_data:
          detailed_info_data = anvil.server.call('get_word_info', word)
        anvil.server.call('save_word_data', word, result["relations"][word],
                          detailed_info_data["detailed_info"], detailed_info_data["image_url"])
        self.input_words.append(word)
        self.update_word_dropdown()
        self.update_dropdown_options()
        self.update_relation_panel()
        self.update_word_details(word)
      else:
        self.detail_label.text = "Từ không được xử lý đúng."
        self.clear_relations()
    except Exception as e:
      alert(f"Lỗi khi xử lý từ: {str(e)}")

  def update_word_details(self, word):
    if not word:
      self.detail_label.text = "Không có từ hoặc cụm từ nào được chọn."
      self.word_image.visible = False
      return
    try:
      detailed_info_data = anvil.server.call('get_detailed_info', word)
      if not detailed_info_data:
        detailed_info_data = anvil.server.call('get_word_info', word)
      self.detail_label.text = detailed_info_data["detailed_info"]
      image_url = detailed_info_data["image_url"]
      self.word_image.source = image_url if image_url and image_url != "Không tìm thấy ảnh" else None
      self.word_image.visible = bool(self.word_image.source)
    except Exception as e:
      self.detail_label.text = f"Có lỗi khi lấy thông tin chi tiết: {str(e)}"
      self.word_image.visible = False

  def add_btn_click(self, **event_args):
    vocab_input = self.input_text.text.strip()
    means_output = self.detail_label.text
    if not vocab_input or means_output == "Chọn một từ hoặc cụm từ để xem chi tiết.":
      alert("Vui lòng tìm kiếm và chọn một từ hoặc cụm từ trước!")
      return
    try:
      anvil.server.call('add_vocab', {"vocab_input": vocab_input, "means_output": means_output})
      alert("Thêm từ thành công!")
    except Exception as e:
      alert(f"Lỗi khi thêm từ: {str(e)}")

  def check_user_info(self):
    curr_user = anvil.users.get_user()
    if curr_user and (not curr_user['first_name'] or not curr_user['last_name']):
      self.new_user = {}
      self.save_clicked = alert(
        content=User_form(item=self.new_user),
        title="Chỉnh sửa hồ sơ",
        large=True,
        buttons=[],
        dismissible=False
      )
      if self.save_clicked:
        open_form('Home_page')

  def input_text_pressed_enter(self, **event_args):
    self.analyze_word_btn_click()

  def search_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
