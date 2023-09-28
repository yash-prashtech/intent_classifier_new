# todo: clean it and make it professional if this feature properly need for now keep it raw
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# defining the scope of the application
scope_app = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'] 

#credentials to the account
# cred = ServiceAccountCredentials.from_json_keyfile_name('gsheets.json', scope_app) 

# authorize the clientsheet 
# client = gspread.authorize(cred)

# sheet = client.create("auto_optout_texts")
# sheet.share('ahmad@textdrip.com', perm_type='user', role='writer')


def add_text(text):
    # sheet = client.open("auto_optout_texts").sheet1
    # sheet.append_row([text, '', 'exact'])
    return True

