from ._anvil_designer import ProfileTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..User_form import User_form


class Profile(ProfileTemplate):
  def __init__(self, layout = None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # anvil.server.call('get_curr_user_data')

    self.update_user_profile()

    # if current_user is not None:
    #   #Hiển thị từ vựng theo dữ liệu người dùng
    #   self.data_table.items = app_tables.users.search(
    #     User=current_user
    #   )
    # # Any code you write here will run before the form opens.

  def update_user_profile(self):
    current_user = anvil.users.get_user()
    if current_user['user_avatar']:
      self.avatar_show.source = current_user['user_avatar']
    else:
      self.avatar_show.source = "_/theme/picture/avatar.jpg"
    self.name_label.text = f"{current_user['first_name']} {current_user['last_name']}"
    self.email_label.text = current_user['email']
    self.phone_label.text = current_user['phone']
    
  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.new_user = {}
    self.form = User_form(layout = self.layout)
    self.save_clicked = alert(
      content = self.form,
      title = "Edit Profile",
      large = True,
      buttons = [],
      dismissible = False
    )
    if self.save_clicked:
      self.layout.update_user()
      self.update_user_profile()
  

