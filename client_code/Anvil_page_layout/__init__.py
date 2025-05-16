from ._anvil_designer import Anvil_page_layoutTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from ..User_form import User_form


class Anvil_page_layout(Anvil_page_layoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.

    self.init_components(**properties)
    self.curr_user = anvil.users.get_user()
    
    if not self.curr_user:
      self.hide_user_bth() 
    else:
      self.show_user_bth()
      self.update_user()


    # Any code you write here will run before the form opens.
  def update_user(self):
    current_user = anvil.users.get_user()
    if current_user:
      self.avatar.source = current_user['user_avatar']
      self.user_name.text = f"{current_user['first_name']} {current_user['last_name']}"

  
  
          
          
  def hide_user_bth(self, **event_args):
    self.login_button.visible = True
    self.logout_button.visible = False
    self.profile_btn.visible = False
    self.notebook_btn.visible = False
    self.user.visible = False

    
  def show_user_bth(self, **event_args):
    self.login_button.visible = False
    self.logout_button.visible = True
    self.profile_btn.visible = True
    self.notebook_btn.visible = True
    self.user.visible = True


    
  # function login when click button
  def login_button_click(self, **event_args):
    anvil.users.login_with_form(allow_cancel=True, allow_remembered = True)
    self.curr_user = anvil.users.get_user()
    if self.curr_user is not None:
      self.show_user_bth()
      self.update_user()
      open_form('Home_page')
      
    
    
    
  #function log out
  def logout_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.logout()
    # show login btn and hide logout btn
    self.curr_user = None
    self.hide_user_bth()
    open_form('Home_page')
    anvil.alert("Log Out")

  def about_us_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('About_us')

  def profile_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Profile')

  def home_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home_page')

  def notebook_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('NoteBook')

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
    
  def user_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('Profile')
 
    



    
