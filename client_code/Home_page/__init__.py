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
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # If user is logged in, display the add button
    current_user = anvil.users.get_user()
    self.check_user_info()
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
    """This method is called when the button is clicked"""
    anvil.server.call('add_vocab',self.new_vocab_data)
    alert("Add Successful!!!")


  def check_user_info(self):
    curr_user = anvil.users.get_user()
    if curr_user and (not curr_user['first_name'] or not curr_user['last_name']):
      self.new_user = {}
      self.save_clicked = alert(
        content = User_form(item = self.new_user),
        title = "Edit Profile",
        large = True,
        buttons = [],
        dismissible = False
      )
      if self.save_clicked:
        open_form('Home_page')


    



