
def slugify(s:str)->str:
    return ''.join(c if c.isalnum() else '-' for c in s.lower()).strip('-')
