from deepboard.gui.utils import smart_round
from datetime import datetime

def format_value(value, decimals: int = 4):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(value, float):
        return smart_round(value, decimals)
    return value