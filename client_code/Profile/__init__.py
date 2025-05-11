from ._anvil_designer import ProfileTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..User_form import User_form


class Profile(ProfileTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # anvil.server.call('get_curr_user_data')
    current_user = anvil.users.get_user()
    
    self.name_label.text = f"{current_user['first_name']} {current_user['last_name']}"
    self.email_label.text = current_user['email']
    self.phone_label.text = current_user['phone']
    # if current_user is not None:
    #   #Hiển thị từ vựng theo dữ liệu người dùng
    #   self.data_table.items = app_tables.users.search(
    #     User=current_user
    #   )
    # # Any code you write here will run before the form opens.

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.new_user = {}
    self.save_clicked = alert(
      content = User_form(item = self.new_user),
      title = "Edit Profile",
      large = True,
      buttons = [("Save", True), ("Cancel", False)],
      dismissible = False
    )
    if self.save_clicked:
      anvil.server.call('add_user', self.new_user)
      # anvil.server.call('update_user', self.new_user)
      open_form('Profile')
  

