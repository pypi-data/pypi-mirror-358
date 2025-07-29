import os

from denodo_webservice import Client

DATABASE = os.environ["DENODO_DATABASE"]
VIEW = os.environ["DENODO_VIEW"]

client = Client(verify=False)
view = client.database(DATABASE).view(VIEW)

data = view.get()
