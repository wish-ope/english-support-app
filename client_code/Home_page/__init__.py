from ._anvil_designer import Home_pageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
f

class Home_page(Home_pageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.

  def input_text_change(self, **event_args):
    """This method is called when the text in this text area is edited"""

  def add_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('add_vocab')
    self.
    



