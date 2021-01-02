def estr(str1, str2):
    if not (type(str1) == str and type(str2) == str):
        return False

    str1 = str1.strip().lower()
    str2 = str2.strip().lower()

    return str1 == str2
