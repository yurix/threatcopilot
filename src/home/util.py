
def safe_is_empty_list(input_list):
    if input_list is None:
        return True
    elif not isinstance(input_list, list):
        return True
    elif not len(input_list) > 0:
        return True
    else: 
        return False

def safe_is_not_empty_list(input_list):
    return not safe_is_empty_list(input_list)

def safe_list_len_neomodel(input_list):
    if input_list is None:
        return 0
    elif safe_is_empty_list(input_list):
        return 0
    else:
        return len(input_list[0])