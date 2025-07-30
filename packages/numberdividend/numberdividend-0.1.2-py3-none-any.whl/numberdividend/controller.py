def check_type_list(var_name, data):
    if isinstance(data, list):
        return True
    else:
        raise TypeError(f"Invalid type for {var_name}: expected list.")
    
def check_type_float(var_name, data):
    data = float(data)
    if isinstance(data, float):
        return True
    else:
        raise TypeError(f"Invalid type for {var_name}: expected float.")
    
def check_type_int(var_name, data):
    if isinstance(data, int):
        return True
    else:
        raise TypeError(f"Invalid type for {var_name}: expected int.")
