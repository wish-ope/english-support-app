from ._anvil_designer import About_usTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class About_us(About_usTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def login_btn_about_us_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.login_with_form()
    open_form('Form2')
   
