from ._anvil_designer import Form2Template
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Form2(Form2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.canvas_size = 500
    self.canvas_1.height = self.canvas_size
    self.canvas_1.reset_context()

  def canvas_1_reset(self, **event_args):
    """This method is called when the canvas is reset and cleared, such as when the window resizes, or the canvas is added to a form."""
    # Adjust these coordinates if you want the drawing area to not be centered
    self.canvas_offset = (self.canvas_1.get_width() - self.canvas_size)/2
    self.canvas_1.translate(self.canvas_offset, 0)

    # Restrict drawing to the section that we want visible
    self.canvas_1.begin_path()
    self.canvas_1.move_to(0, 0)
    self.canvas_1.line_to(self.canvas_size, 0)
    self.canvas_1.line_to(self.canvas_size,self.canvas_size)
    self.canvas_1.line_to(0, self.canvas_size)
    self.canvas_1.close_path()
    self.canvas_1.clip()
    
    # Draw a square
    self.canvas_1.begin_path()
    self.canvas_1.move_to(100, 100)
    self.canvas_1.line_to(150, 100)
    self.canvas_1.line_to(150, 150)
    self.canvas_1.line_to(100, 150)
    self.canvas_1.close_path()
    self.canvas_1.stroke() 
    self.canvas_1.fill()

    # Draw a circle
    self.canvas_1.begin_path()
    self.canvas_1.arc(300, 100, 50)
    self.canvas_1.close_path()
    self.canvas_1.stroke()
    self.canvas_1.fill()
    


