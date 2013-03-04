#MACROS Speicfy location of DB, relative path
import os
DB_PATH = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'NIH.db')

