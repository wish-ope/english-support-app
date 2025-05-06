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
    self.curr_user = anvil.users.get_user()
    if self.curr_user is not None:
      self.add_btn.visible = True
    else:
      self.add_btn.visible = False
      
  def input_text_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    # vocab_input = self.input_text.text
    # means_input = self.output_text.text
    # self.new_vocab_data = {
    #   "vocab_input": vocab_input,
    #   "means_input": means_input
    # }




  def search_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Lấy input
    vocab_input = self.input_text.text
    if not vocab_input:
      alert("Error: Please enter a valid word.")    
    # Gọi hàm server để lấy thông tin
    else:
      result = anvil.server.call('get_word_info', vocab_input)
      # Hiển thị kết quả
      self.output_text.text = result

  def add_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    vocab_input = self.input_text.text
    means_output = self.output_text.text
    self.new_vocab_data = {
      "vocab_input":vocab_input,
      "means_output":means_output
    }
    if not self.output_text.text:
      alert("Input not valid!")
    else:
      anvil.server.call('add_vocab',self.new_vocab_data)
      alert("Successful")


 


    
    



