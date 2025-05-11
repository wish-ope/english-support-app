from ._anvil_designer import Home_pageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..User_form import User_form

class Home_page(Home_pageTemplate):
  def __init__(self, **properties):
    # Khởi tạo giao diện
    self.init_components(**properties)

    # Kiểm tra người dùng
    self.curr_user = anvil.users.get_user()
    self.check_user_info()
    self.add_btn.visible = self.curr_user is not None

    # Thiết lập ban đầu cho các panel
    self.clear_all_panels()
    self.detail_label.text = "Chọn một từ hoặc câu để xem chi tiết."

    # Đảm bảo panel hiển thị
    self.synonym_panel.visible = True
    self.antonym_panel.visible = True
    self.hyponym_panel.visible = True
    self.meronym_panel.visible = True
    self.sentence_analysis_panel.visible = True

  def clear_all_panels(self):
    """Xóa nội dung của tất cả các panel"""
    self.synonym_panel.clear()
    self.antonym_panel.clear()
    self.hyponym_panel.clear()
    self.meronym_panel.clear()
    self.sentence_analysis_panel.clear()

  def search_btn_click(self, **event_args):
    """Xử lý khi nút tìm kiếm được nhấn"""
    input_text = self.input_text.text.strip()
    if not input_text:
      alert("Vui lòng nhập một từ hoặc câu hợp lệ!")
      return

    try:
      # Kiểm tra xem input là một từ hay một câu (dựa trên số lượng từ)
      tokens = input_text.split()
      if len(tokens) == 1:
        # Xử lý cho một từ
        self.analyze_single_word(input_text)
      else:
        # Xử lý cho một câu
        self.analyze_sentence(input_text)

      self.detail_label.text = "Chọn một từ để xem chi tiết."

    except Exception as e:
      alert(f"Có lỗi xảy ra: {str(e)}")
      print(f"Error in search_btn_click: {str(e)}")

  def analyze_single_word(self, word):
    """Phân tích một từ: đồng nghĩa, trái nghĩa, hyponyms, meronyms"""
    result = anvil.server.call('get_word_relations', word)

    print(f"Kết quả từ server: {result}")

    self.clear_all_panels()

    if not result["synonyms"] and not result["antonyms"]:
      alert(f"Không tìm thấy đồng nghĩa hoặc trái nghĩa cho từ '{word}'.")
      return

    # Đồng nghĩa
    for syn in result["synonyms"]:
      link = Link(text=syn, role="default", spacing_above="small", spacing_below="small")
      link.tag.word = syn
      link.add_event_handler('click', self.synonym_word_click)
      self.synonym_panel.add_component(link)

    # Trái nghĩa
    for ant in result["antonyms"]:
      link = Link(text=ant, role="default", spacing_above="small", spacing_below="small")
      link.tag.word = ant
      link.add_event_handler('click', self.antonym_word_click)
      self.antonym_panel.add_component(link)

    # Hyponyms
    hyponyms = anvil.server.call('get_hyponyms', word)
    for hyp in hyponyms:
      link = Link(text=hyp, role="default", spacing_above="small", spacing_below="small")
      link.tag.word = hyp
      link.add_event_handler('click', self.hyponym_word_click)
      self.hyponym_panel.add_component(link)

    # Meronyms
    meronyms = anvil.server.call('get_meronyms', word)
    for mer in meronyms:
      link = Link(text=mer, role="default", spacing_above="small", spacing_below="small")
      link.tag.word = mer
      link.add_event_handler('click', self.meronym_word_click)
      self.meronym_panel.add_component(link)

  def analyze_sentence(self, sentence):
    """Phân tích một câu: token hóa, POS tagging, vai trò ngữ pháp"""
    self.clear_all_panels()

    # Gọi server để phân tích câu
    sentence_analysis = anvil.server.call('analyze_sentence', sentence)

    print(f"Kết quả phân tích câu: {sentence_analysis}")

    # Hiển thị kết quả phân tích câu với từ là Link
    for word_info in sentence_analysis:
      word = word_info["word"]
      role = word_info["role"]
      link = Link(text=f"{word} ({role})", role="default", spacing_above="small", spacing_below="small")
      link.tag.word = word
      link.add_event_handler('click', self.sentence_word_click)
      self.sentence_analysis_panel.add_component(link)

  def synonym_word_click(self, sender, **event_args):
    """Xử lý khi nhấp vào một từ đồng nghĩa"""
    word = sender.tag.word
    try:
      result = anvil.server.call('get_word_info', word)
      self.detail_label.text = result
    except Exception as e:
      alert(f"Có lỗi khi lấy thông tin từ: {str(e)}")

  def antonym_word_click(self, sender, **event_args):
    """Xử lý khi nhấp vào một từ trái nghĩa"""
    word = sender.tag.word
    try:
      result = anvil.server.call('get_word_info', word)
      self.detail_label.text = result
    except Exception as e:
      alert(f"Có lỗi khi lấy thông tin từ: {str(e)}")

  def hyponym_word_click(self, sender, **event_args):
    """Xử lý khi nhấp vào một từ hyponym"""
    word = sender.tag.word
    try:
      result = anvil.server.call('get_word_info', word)
      self.detail_label.text = result
    except Exception as e:
      alert(f"Có lỗi khi lấy thông tin từ: {str(e)}")

  def meronym_word_click(self, sender, **event_args):
    """Xử lý khi nhấp vào một từ meronym"""
    word = sender.tag.word
    try:
      result = anvil.server.call('get_word_info', word)
      self.detail_label.text = result
    except Exception as e:
      alert(f"Có lỗi khi lấy thông tin từ: {str(e)}")

  def sentence_word_click(self, sender, **event_args):
    """Xử lý khi nhấp vào một từ trong phân tích câu"""
    word = sender.tag.word
    try:
      result = anvil.server.call('get_word_info', word)
      self.detail_label.text = result
    except Exception as e:
      alert(f"Có lỗi khi lấy thông tin từ: {str(e)}")

  def add_btn_click(self, **event_args):
    """Xử lý khi nút thêm từ được nhấn"""
    vocab_input = self.input_text.text.strip()
    means_output = self.detail_label.text
    if not vocab_input or not means_output or means_output == "Chọn một từ hoặc câu để xem chi tiết.":
      alert("Vui lòng tìm kiếm và chọn một từ trước khi thêm!")
      return

    try:
      self.new_vocab_data = {
        "vocab_input": vocab_input,
        "means_output": means_output
      }
      anvil.server.call('add_vocab', self.new_vocab_data)
      alert("Thêm từ thành công!")
    except Exception as e:
      alert(f"Có lỗi khi thêm từ: {str(e)}")

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