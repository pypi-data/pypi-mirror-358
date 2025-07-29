import re
import openai
import json
from datetime import datetime, timedelta
from dateutil.parser import parse

def find_gender_from_back(text):
    gender = ''
    gender_pattern = r'(\d)([A-Za-z])(\d)'
    gender_match = re.search(gender_pattern, text)
    if gender_match:
        gender = gender_match.group(2)

    if not gender:
        gender_pattern = r'(\d)([MFmf])(\d)'
        gender_match = re.search(gender_pattern, text)
        if gender_match:
            gender = gender_match.group(2)

    return gender


def is_valid_date(date_str):
    """Returns True if the string can be parsed as a valid date, regardless of format."""
    try:
        parse(date_str, fuzzy=False)
        return True
    except (ValueError, TypeError):
        return False

def is_expiry_issue_diff_valid(issue_date_str, expiry_date_str, time_period):
    """Check if expiry date = issue date + 5 years - 1 day"""
    if is_valid_date(issue_date_str) and is_valid_date(expiry_date_str):
        issue_date = datetime.strptime(issue_date_str, "%Y/%m/%d")
        expiry_date = datetime.strptime(expiry_date_str, "%Y/%m/%d")
        expected_expiry = issue_date.replace(year=issue_date.year + time_period) - timedelta(days=1)
        return expiry_date == expected_expiry
    return False

def is_mrz_dob_mrz_field_match(dob_str, mrz_line2):
    """Check if DOB in MRZ matches the printed DOB"""
    dob = datetime.strptime(dob_str, "%Y/%m/%d")
    mrz_dob_raw = mrz_line2[:6]  # First 6 characters (YYMMDD)
    current_year_last2 = int(str(datetime.today().year)[-2:])
    year_prefix = "19" if int(mrz_dob_raw[:2]) > current_year_last2 else "20"
    mrz_dob = datetime.strptime(year_prefix + mrz_dob_raw, "%Y%m%d")
    return mrz_dob == dob

def is_age_18_above(dob_str):
    """Check if the person is 18 or older as of today"""
    dob = datetime.strptime(dob_str, "%Y/%m/%d")
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age >= 18


from datetime import datetime


def is_expired_id(expiry_date):
    """
    Checks if an ID is expired.

    Parameters:
    expiry_date (str): Expiry date in 'YYYY-MM-DD', 'DD.MM.YYYY', or 'YYYY/MM/DD' format.

    Returns:
    bool: True if the passport is expired, False otherwise.
    """
    date_formats = ["%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"]

    for fmt in date_formats:
        try:
            expiry = datetime.strptime(expiry_date, fmt).date()
            today = datetime.today().date()
            return expiry < today
        except ValueError:
            continue

    raise ValueError("Invalid date format. Expected 'YYYY-MM-DD', 'DD.MM.YYYY', or 'YYYY/MM/DD'.")



from datetime import datetime


def parse_yymmdd(yymmdd_str):
    """
    Converts a 'YYMMDD' string to a 'YYYY-MM-DD' formatted string.
    Assumes years < 50 are 2000s, otherwise 1900s.

    Parameters:
    yymmdd_str (str): A string in 'YYMMDD' format.

    Returns:
    str: A date string in 'YYYY-MM-DD' format.
    """
    if len(yymmdd_str) != 6 or not yymmdd_str.isdigit():
        raise ValueError("Invalid YYMMDD format")

    try:
        parsed_date = datetime.strptime(yymmdd_str, "%y%m%d")
        if parsed_date.year < 1950:
            parsed_date = parsed_date.replace(year=parsed_date.year + 100)
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Could not parse YYMMDD string: {yymmdd_str}")



from pydantic import BaseModel, Field
from typing import Type

from pydantic import BaseModel
from typing import Type

def convert_pydantic_to_openai_function2(
    model: Type[BaseModel]
) -> dict:
    """
    Convert a Pydantic model into OpenAI function calling format,
    inferring the function name and description from the model.

    - Function name is derived from the class name in snake_case.
    - Description is taken from the class docstring.

    Args:
        model (BaseModel): The Pydantic model class.

    Returns:
        dict: A dictionary formatted for OpenAI function calling.
    """
    import re

    def camel_to_snake(name: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    return {
        "name": camel_to_snake(model.__name__),
        "description": model.__doc__ or "No description provided.",
        "parameters": model.schema()
    }

