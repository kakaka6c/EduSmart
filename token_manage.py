import random
import string
import databaseHelper
DB_HELPER = databaseHelper.DatabaseHelper('EduSmart.db')

def generate_token():
    prefix = "EAAAU"
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
    token = prefix + random_part
    return token

def revoke_token(token):
    return DB_HELPER.revoke_token(token)

