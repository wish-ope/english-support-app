from ._anvil_designer import NoteBookTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class NoteBook(NoteBookTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #Displaying vocab data in grid table
    self.repeating_panel_1.items = app_tables.vocab.search()

