from ._anvil_designer import Anvil_page_layoutTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class Anvil_page_layout(Anvil_page_layoutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    self.logout_button.visible = False
    self.profile_button.visible = False
    # Any code you write here will run before the form opens.

  # function login when click button
  def login_button_click(self, **event_args):
    anvil.users.login_with_form()
    self.logout_button.visible = True
    self.login_button.visible = False
    self.profile_button.visible = True
    
  #function log out
  def logout_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.logout()
    self.login_button.visible = True
    self.logout_button.visible = False 
    open_form('Form2')
    anvil.alert("Log Out")

  def about_us_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('About_us')
    self.login_button.visible = False

  def profile_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Profile')


  augment.set_event_handler(self.lbl_title, 'hover', self.lbl_title_hover)
  # equivalent to
  # augment.set_event_handler(self.link, 'mouseenter', self.link_hover)
  # augment.set_event_handler(self.link, 'mouseleave', self.link_hover)
  # or
  # augment.set_event_handler(self.link, 'mouseenter mouseleave', self.link_hover)
  
  def lbl_title_hover(self, **event_args):
    self.lbl_title.bold = 'enter' in event_args['event_type']
    
