from ._anvil_designer import Anvil_page_layoutTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class Anvil_page_layout(Anvil_page_layoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    print(f"This user has logged in: {anvil.users.get_user()['email']}")
    self.init_components(**properties)
    
    self.logout_button.visible = False
    self.hide_user_bth()
    # Any code you write here will run before the form opens.

  def hide_user_bth(self, **event_args):
    self.profile_btn.visible = False
    self.notebook_btn.visible = False
  def show_user_bth(self, **event_args):
    self.profile_btn.visible = True
    self.notebook_btn.visible = True

    
  # function login when click button
  def login_button_click(self, **event_args):
    anvil.users.login_with_form()
    open_form('Home_page')
    self.logout_button.visible = True
    self.login_button.visible = False
    self.show_user_bth()
    
  #function log out
  def logout_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.logout()
    # show login btn and hide logout btn
    self.hide_user_bth()
    self.login_button.visible = True
    self.logout_button.visible = False 
    open_form('Home_page')
    anvil.alert("Log Out")

  def about_us_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('About_us')
    # self.login_button.visible = False

  def profile_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Profile')

  def home_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home_page')

  def notebook_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('NoteBook')

 
    



    
