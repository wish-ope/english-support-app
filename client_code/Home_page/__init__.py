from ._anvil_designer import Home_pageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Home_page(Home_pageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # If user is logged in, display the add button
    current_user = anvil.users.get_user()
    if current_user == None:
      self.add_btn.visible = False
    else:
      self.add_btn.visible = True
      
  def input_text_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    vocab_input = self.input_text.text
    means_input = self.output_text.content
    self.new_vocab_data = {
      "vocab_input": vocab_input,
      "means_input": means_input
    }

  def add_btn_click(self, **event_args):
     # Lấy
        word = self.input_text.text
        
        # Gọi hàm server để lấy thông tin
        result = anvil.server.call('get_word_info', word)
        
        # Hiển thị kết quả
        self.output_text.text = result
    # """This method is called when the button is clicked"""
    # anvil.server.call('add_vocab',self.new_vocab_data)
    # alert("Add Successful!!!")


    
    



