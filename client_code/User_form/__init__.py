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
    self.cancel_btn.visible = False
    
    # Any code you write here will run before the form opens.

  def save_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    first = self.firstName_input.text
    last = self.lastName_input.text
    phone = self.phone_input.text
    if first and last:
      anvil.server.call('update_user',first, last, phone)
      self.raise_event('x-close-alert', value=True)
    
