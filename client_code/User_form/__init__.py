from ._anvil_designer import User_formTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class User_form(User_formTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    current_user = anvil.users.get_user()
    if current_user and not current_user['first_name'] and not current_user['last_name']:
      self.cancel_btn.visible = False
    else:
      self.cancel_btn.visible = True
    # Any code you write here will run before the form opens.

  def save_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    first = self.firstName_input.text
    last = self.lastName_input.text
    phone = self.phone_input.text
    if first and last:
      anvil.server.call('update_user',first, last, phone)
      self.raise_event('x-close-alert', value=True)


  def image_uploader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    self.item['image'] = file

  def cancel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    answer = confirm("Are you sure?", Buttons = [("Yes", True), ("No", False)])
    if answer:
      self.raise_event("x-close-alert")
    
    
