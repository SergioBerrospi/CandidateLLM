
import pandas as pd
import json
import re


def slugify(text):
    """
    Convert text into a slug (e.g., "Exitosa Radio" -> "exitosa_radio").
    """
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')
