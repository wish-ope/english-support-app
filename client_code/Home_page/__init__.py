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
    self.synonym_panel.clear()  # Xóa nội dung ban đầu của ColumnPanel
    self.antonym_panel.clear()
    self.detail_label.text = "Chọn một từ để xem chi tiết."

    # Đảm bảo panel hiển thị
    self.synonym_panel.visible = True
    self.antonym_panel.visible = True

  def search_btn_click(self, **event_args):
    """Xử lý khi nút tìm kiếm được nhấn"""
    vocab_input = self.input_text.text.strip()
    if not vocab_input:
      alert("Vui lòng nhập một từ hợp lệ!")
      return

    try:
      # Gọi server để lấy danh sách đồng nghĩa và trái nghĩa
      result = anvil.server.call('get_word_relations', vocab_input)

      print(f"Kết quả từ server: {result}")

      # Kiểm tra kết quả trả về
      if not result["synonyms"] and not result["antonyms"]:
        alert(f"Không tìm thấy đồng nghĩa hoặc trái nghĩa cho từ '{vocab_input}'.")
        self.synonym_panel.clear()
        self.antonym_panel.clear()
        self.detail_label.text = "Chọn một từ để xem chi tiết."
        return

      # Xóa nội dung cũ trong ColumnPanel
      self.synonym_panel.clear()
      self.antonym_panel.clear()

      # Thêm từ đồng nghĩa vào synonym_panel
      for word in result["synonyms"]:
        link = Link(text=word, role="default", spacing_above="small", spacing_below="small")
        link.tag.word = word  # Lưu từ để sử dụng trong sự kiện click
        link.add_event_handler('click', self.synonym_word_click)
        self.synonym_panel.add_component(link)

      # Thêm từ trái nghĩa vào antonym_panel
      for word in result["antonyms"]:
        link = Link(text=word, role="default", spacing_above="small", spacing_below="small")
        link.tag.word = word
        link.add_event_handler('click', self.antonym_word_click)
        self.antonym_panel.add_component(link)

      self.detail_label.text = "Chọn một từ để xem chi tiết."

    except Exception as e:
      alert(f"Có lỗi xảy ra: {str(e)}")
      print(f"Error in search_btn_click: {str(e)}")

  def synonym_word_click(self, sender, **event_args):
    """Xử lý khi nhấp vào một từ đồng nghĩa"""
    word = sender.tag.word  # Lấy từ từ tag
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

  def add_btn_click(self, **event_args):
    """Xử lý khi nút thêm từ được nhấn"""
    vocab_input = self.input_text.text.strip()
    means_output = self.detail_label.text
    if not vocab_input or not means_output or means_output == "Chọn một từ để xem chi tiết.":
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