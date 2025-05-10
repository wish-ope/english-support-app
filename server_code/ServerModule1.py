import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def add_vocab(vocab_data):
  app_tables.vocab.add_row(Vocab=vocab_data["vocab_input"], Means=vocab_data["means_input"])

@anvil.server.callable
def update_user(first_name, last_name, phone):
  curr_user = anvil.users.get_user()
  if user:
    user['first_name'] = first_name
    user['last_name'] = last_name
    user['phone'] = phone
# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
