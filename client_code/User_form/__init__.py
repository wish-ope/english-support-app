from ._anvil_designer import User_formTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class User_form(User_formTemplate):
  def __init__(self,layout = None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout = layout
    self.selected_avatar = None
    current_user = anvil.users.get_user()
    self.avatar_image.source = current_user['user_avatar']
    if current_user and not current_user['first_name'] and not current_user['last_name']:
      self.cancel_btn.visible = False
    else:
      self.cancel_btn.visible = True
    # Any code you write here will run before the form opens.

  def save_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    avatar = self.selected_avatar
    first = self.firstName_input.text
    last = self.lastName_input.text
    phone = self.phone_input.text

    # if first and last:
    anvil.server.call('update_user', avatar, first, last, phone)d
    self.raise_event('x-close-alert', value=True)


  def image_uploader_change(self, file, **event_args):
    """Khi người dùng chọn một file ảnh"""
    if file:
      self.avatar_image.source = file  # Hiển thị ảnh lên Image component
      self.selected_avatar = file      # Lưu file vào biến tạm (instance variable)
    

  def cancel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    answer = confirm("Are you sure?", Buttons = [("Yes", True), ("No", False)])
    if answer:
      self.raise_event("x-close-alert")
    
    
