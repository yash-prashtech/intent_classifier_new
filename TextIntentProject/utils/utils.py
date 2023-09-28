import csv, json, requests
from django.utils.crypto import get_random_string
import string, os
import pandas as pd 
from django.core.validators import validate_email

import uuid


def generate_pdf_file_unique_id():
    return get_random_string(40, allowed_chars=string.digits + string.ascii_lowercase)


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def chunk_based_on_size(lst, n):
    for x in range(0, len(lst), n):
        each_chunk = lst[x: n+x]
        if len(each_chunk) < n:
            each_chunk = each_chunk + [None for y in range(n-len(each_chunk))]
        yield each_chunk



def generateAPIKEY():
    return get_random_string(40, allowed_chars=string.ascii_uppercase + string.digits + string.ascii_lowercase)


def generatePassword():
    return get_random_string(12, allowed_chars=string.ascii_uppercase + string.digits + string.ascii_lowercase)



def isValidEmailFormat(email):
    try:
        validate_email(email)
        return True
    except:
        return False
