from ._anvil_designer import Home_pageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..User_form import User_form

class WordRelations:
  """Class để lưu trữ các mối quan hệ từ vựng"""
  def __init__(self, synonyms=None, antonyms=None, hyponyms=None, meronyms=None):
    self.synonyms = synonyms if synonyms is not None else []
    self.antonyms = antonyms if antonyms is not None else []
    self.hyponyms = hyponyms if hyponyms is not None else []
    self.meronyms = meronyms if meronyms is not None else []

  def get_relations(self, relation_type):
    """Lấy dữ liệu dựa trên loại mối quan hệ"""
    if relation_type == "synonyms":
      return self.synonyms
    elif relation_type == "antonyms":
      return self.antonyms
    elif relation_type == "hyponyms":
      return self.hyponyms
    elif relation_type == "meronyms":
      return self.meronyms
    return []

  def has_data(self, relation_type):
    """Kiểm tra xem loại mối quan hệ có dữ liệu không"""
    return len(self.get_relations(relation_type)) > 0

class Home_page(Home_pageTemplate):
  def __init__(self, **properties):
    # Khởi tạo giao diện
    self.init_components(**properties)

    # Kiểm tra người dùng
    self.curr_user = anvil.users.get_user()
    self.check_user_info()
    self.add_btn.visible = self.curr_user is not None

    # Thiết lập ban đầu
    self.result_panel.clear()
    self.relation_panel.clear()  # Xóa panel mối quan hệ ban đầu
    self.detail_label.text = "Chọn một từ hoặc câu để xem chi tiết."
    self.word_image.visible = False

    # Cấu hình dropdown
    self.category_dropdown.items = [
      ("Đồng nghĩa", "synonyms"),
      ("Trái nghĩa", "antonyms"),
      ("Hyponyms", "hyponyms"),
      ("Meronyms", "meronyms")
    ]
    self.category_dropdown.selected_value = "synonyms"
    self.category_dropdown.add_event_handler('change', self.category_dropdown_change)

    # Hiển thị từ của ngày
    try:
      word_of_day = anvil.server.call('get_word_of_the_day')
      self.word_of_day_content.text = word_of_day
    except Exception as e:
      self.word_of_day_content.text = f"Lỗi khi lấy từ của ngày: {str(e)}"

  def clear_all(self):
    """Xóa nội dung panel kết quả"""
    self.result_panel.clear()

  def clear_relations(self):
    """Xóa nội dung panel mối quan hệ"""
    self.relation_panel.clear()

  def search_btn_click(self, **event_args):
    """Xử lý khi nút tìm kiếm được nhấn"""
    input_text = self.input_text.text.strip()
    if not input_text:
      alert("Vui lòng nhập một từ hoặc câu hợp lệ!")
      return

    try:
      # Sử dụng SpaCy để tách từ
      tokens = anvil.server.call('get_tokens', input_text)
      if len(tokens) == 1:
        self.current_word = input_text
        # Kiểm tra cơ sở dữ liệu trước
        word_data = anvil.server.call('get_word_data', input_text)
        if word_data:
          print(f"Lấy dữ liệu từ cơ sở dữ liệu cho từ '{input_text}'")
          self.word_relations = WordRelations(
            synonyms=word_data["relations"]["synonyms"],
            antonyms=word_data["relations"]["antonyms"],
            hyponyms=word_data["relations"]["hyponyms"],
            meronyms=word_data["relations"]["meronyms"]
          )
        else:
          print(f"Không tìm thấy từ '{input_text}' trong cơ sở dữ liệu, gọi server...")
          relations_data = anvil.server.call('get_all_word_relations', input_text)
          self.word_relations = WordRelations(
            synonyms=relations_data["synonyms"],
            antonyms=relations_data["antonyms"],
            hyponyms=relations_data["hyponyms"],
            meronyms=relations_data["meronyms"]
          )
          # Lấy nghĩa chi tiết và lưu vào cơ sở dữ liệu
          detailed_info = anvil.server.call('get_word_info', input_text)
          anvil.server.call('save_word_data', input_text, relations_data, detailed_info)

        self.update_dropdown_options()
        self.update_relation_panel()  # Cập nhật panel mối quan hệ
        self.update_word_details(input_text)  # Hiển thị nghĩa chi tiết
      else:
        self.analyze_sentence(input_text)
        self.detail_label.text = "Chọn một từ hoặc câu để xem chi tiết."
        self.clear_relations()  # Xóa panel mối quan hệ khi phân tích câu

    except Exception as e:
      alert(f"Có lỗi xảy ra: {str(e)}")
      print(f"Error in search_btn_click: {str(e)}")

  def update_dropdown_options(self):
    """Cập nhật trạng thái của dropdown dựa trên từ nhập vào"""
    if not hasattr(self, 'word_relations'):
      self.category_dropdown.items = [("Không có dữ liệu", "none")]
      return

    # Tạo danh sách tùy chọn, loại bỏ các mục không có dữ liệu
    enabled_items = []
    for text, value in [
      ("Đồng nghĩa", "synonyms"),
      ("Trái nghĩa", "antonyms"),
      ("Hyponyms", "hyponyms"),
      ("Meronyms", "meronyms")
    ]:
      if self.word_relations.has_data(value):
        enabled_items.append((text, value))

    # Nếu không có tùy chọn nào, thêm tùy chọn mặc định
    if not enabled_items:
      enabled_items = [("Không có dữ liệu", "none")]

    self.category_dropdown.items = enabled_items
    # Đảm bảo giá trị đã chọn vẫn hợp lệ
    current_value = self.category_dropdown.selected_value
    if current_value not in [item[1] for item in enabled_items]:
      self.category_dropdown.selected_value = enabled_items[0][1] if enabled_items else "none"
      self.update_relation_panel()

  def update_relation_panel(self):
    """Cập nhật panel mối quan hệ dựa trên lựa chọn trong dropdown"""
    if not hasattr(self, 'current_word') or not hasattr(self, 'word_relations'):
      return

    value = self.category_dropdown.selected_value
    self.clear_relations()

    try:
      if value == "none":
        result = []
      else:
        result = self.word_relations.get_relations(value)

      if result:
        for item in result:
          link = Link(text=item, role="default", spacing_above="small", spacing_below="small")
          link.tag.word = item
          link.add_event_handler('click', self.result_word_click)
          self.relation_panel.add_component(link)
      else:
        self.relation_panel.add_component(Label(text="Không có dữ liệu cho loại này."))

    except Exception as e:
      self.relation_panel.add_component(Label(text=f"Lỗi: {str(e)}"))

  def category_dropdown_change(self, **event_args):
    """Xử lý khi thay đổi lựa chọn trong dropdown, tự động cập nhật panel"""
    if hasattr(self, 'word_relations'):
      self.update_relation_panel()
    else:
      self.clear_relations()
      self.relation_panel.add_component(Label(text="Vui lòng tìm kiếm trước!"))

  def analyze_sentence(self, sentence):
    """Phân tích một câu: token hóa, POS tagging, vai trò ngữ pháp"""
    self.clear_all()

    try:
      sentence_analysis = anvil.server.call('analyze_sentence', sentence)
      for word_info in sentence_analysis:
        word = word_info["word"]
        role = word_info["role"]
        link = Link(text=f"{word} ({role})", role="default", spacing_above="small", spacing_below="small")
        link.tag.word = word
        link.add_event_handler('click', self.sentence_word_click)
        self.result_panel.add_component(link)
    except Exception as e:
      self.result_panel.add_component(Label(text=f"Lỗi: {str(e)}"))

  def result_word_click(self, sender, **event_args):
    """Xử lý khi nhấp vào một từ trong panel mối quan hệ"""
    word = sender.tag.word
    self.update_word_details(word)

  def sentence_word_click(self, sender, **event_args):
    """Xử lý khi nhấp vào một từ trong phân tích câu"""
    word = sender.tag.word
    self.current_word = word
    # Kiểm tra cơ sở dữ liệu trước
    word_data = anvil.server.call('get_word_data', word)
    if word_data:
      print(f"Lấy dữ liệu từ cơ sở dữ liệu cho từ '{word}'")
      self.word_relations = WordRelations(
        synonyms=word_data["relations"]["synonyms"],
        antonyms=word_data["relations"]["antonyms"],
        hyponyms=word_data["relations"]["hyponyms"],
        meronyms=word_data["relations"]["meronyms"]
      )
    else:
      print(f"Không tìm thấy từ '{word}' trong cơ sở dữ liệu, gọi server...")
      relations_data = anvil.server.call('get_all_word_relations', word)
      self.word_relations = WordRelations(
        synonyms=relations_data["synonyms"],
        antonyms=relations_data["antonyms"],
        hyponyms=relations_data["hyponyms"],
        meronyms=relations_data["meronyms"]
      )
      # Lấy nghĩa chi tiết và lưu vào cơ sở dữ liệu
      detailed_info = anvil.server.call('get_word_info', word)
      anvil.server.call('save_word_data', word, relations_data, detailed_info)

    # Hiển thị nghĩa chi tiết trước
    self.update_word_details(word)
    self.update_dropdown_options()
    self.update_relation_panel()  # Cập nhật panel mối quan hệ, giữ nguyên result_panel

  def update_word_details(self, word):
    """Cập nhật thông tin chi tiết và hiển thị ảnh"""
    try:
      # Kiểm tra cơ sở dữ liệu trước
      detailed_info = anvil.server.call('get_detailed_info', word)
      if detailed_info:
        print(f"Lấy nghĩa chi tiết từ cơ sở dữ liệu cho từ '{word}'")
      else:
        print(f"Không tìm thấy nghĩa chi tiết cho từ '{word}' trong cơ sở dữ liệu, gọi server...")
        detailed_info = anvil.server.call('get_word_info', word)
        anvil.server.call('save_detailed_info', word, detailed_info)

      lines = detailed_info.split('\n')
      self.detail_label.text = "\n".join(line for line in lines if not line.startswith('**Ảnh minh họa:**'))

      # Hiển thị ảnh
      image_url_line = next((line for line in lines if line.startswith('**Ảnh minh họa:**')), None)
      if image_url_line:
        image_url = image_url_line.replace('**Ảnh minh họa:** ', '').strip()
        if image_url != "Không tìm thấy ảnh" and image_url:
          self.word_image.source = image_url
          self.word_image.visible = True
        else:
          self.word_image.visible = False
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