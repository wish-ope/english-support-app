from ._anvil_designer import Anvil_pageTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class Anvil_page(Anvil_pageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.logout_button.visible = False
    # Any code you write here will run before the form opens.

  def login_button_click(self, **event_args):
    anvil.users.login_with_form()
    self.logout_button.visible = True
    self.login_button.visible = False
    

  def logout_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.logout()
    self.login_button.visible = True
    self.logout_button.visible = False 
    open_form('Form2')
    anvil.alert("Log Out")

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('About_us')


    
