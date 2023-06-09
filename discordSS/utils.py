
from string import Formatter
def is_fstring(string):
    if "{" not in string:
        return False
    if "}" not in string:
        return False
    try:
        Formatter().parse(string)
        
    except ValueError:
        return False
    else:
        return True

    
    