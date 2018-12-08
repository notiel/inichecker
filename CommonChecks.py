"""this module contains common checks for lightsaber project ini file
List of functions
-get_real_key (data, key):                        gets real key for lowercase string (key in dictionary may be written
                                                  like Blade, or blade, or BLADE)
-check_existance(data, key):                      checks if key is valid and key data is a dict too
-check_number(data, key, min, max):               checks that key exists, its value is a correct number
-check_unnessesary_number(data, key, min, max):   like check_number but just warning if number is absent
-check_number_max_warning(data, key, min, max):   checks that key exists, its value is a correct number,
                                                  but if it > max you get warning, not error
-check_number_min_warning(data, key, min, max):   checks that key exists, its value is a correct number,
                                                  but if it < min you get warning, not error
-check_number_warning(data, key, min, max):       checks that key exists, its value is a correct number,
                                                  but if it > max or < min you get warning, not error
-check_bool(data, key):                           checks that key exists and its value is 0 or 1
-check_keys(data, list):                          checks if all data keys are in list of keys
-check_min_max_parameter:                         checks if key exists and has min and max keys and their values are correct
-check_color(data):                               checks color (if key exists and color is random or in rgb model)
-check_color_list(data):                          checks color list, uts existance and correctness of all colors
-get_value(data, key):                            gets value if it exists or None
"""


def get_real_key(data: dict, template: str) -> str:
    """
    gets real dictionary key
    :param data: dictionary with data
    :param template: template for a key to find
    :return: real dictionary key
    """
    for key in data.keys():
        if key.lower() == template:
            return key
    return ""


#def key_correct(data: dict, old_key: str, new_key: str, path:dict)
#    """
#    change old_key to new_key
#    :param data: dictionary
#    :param old_key: key to change
##    :param new_key: modern key
#   :param path: keys to reach
#    :return: 
#    """
#    for i in len(path):
#        pass
#    data[new_key] = data[oldkey]

def check_existance(data: dict, param: str) -> (dict, str):
    """
    checks if key exists and its value is a dict
    :param data: dict with settings
    :param param: key
    :return: data or none and error message or empty string
    """
    key = get_real_key(data, param)
    if not key:
        return None, "setting are absent"
    data = data[key]
    if not isinstance(data, dict):
        return None, "must contain settings formatted as {data: parameter, data: parameter ...};"
    return data, ""


def check_number(data: dict, param: str, min_value: int, max_value: int)->str:
    """
    checks if number parameter is correct
    :param data: data with settings
    :param param: key for checing
    :param min_value: min parameter value
    :param max_value: max parameter value
    :return: error message ot empty
    """
    error = ""
    key = get_real_key(data, param)
    if not key:
        error = "%s parameter is absent;\n" % param
    else:
        value = data[key]
        if not isinstance(value, int) or value < min_value or value > max_value:
            return "%s parameter must be number in %i...%i;\n" % (param, min_value, max_value)
    return error


def check_unnecessary_number(data: dict, param: str, min_value: int, max_value: int)->str:
    """
    checks if number parameter is correct (number may be absent)
    :param data: data with settings
    :param param: key for checing
    :param min_value: min parameter value
    :param max_value: max parameter value
    :return: error message ot empty
    """
    error = ""
    key = get_real_key(data, param)
    if key:
        value = data[key]
        if not isinstance(value, int) or value < min_value or value > max_value:
            return "%s parameter must be number in %i...%i;\n" % (param, min_value, max_value)
    return error


def check_number_max_warning(data: dict, param: str, min_value: int, max_value: int) -> (str, str):
    """
    checks if number parameter is correct, if number>max you get warning, for other problem - error
    :param data: data with settings
    :param param: key for checing
    :param min_value: min parameter value
    :param max_value: max parameter value
    :return: error and warning message ot empty
    """
    error = ""
    warning = ""
    key = get_real_key(data, param)
    if not key:
        error = "%s parameter is absent;\n" % param
    else:
        value = data[key]
        if not isinstance(value, int) or value < min_value:
            error += "%s parameter must be number more then %i;\n" % (param, min_value)
        if isinstance(value, int) and value > max_value:
            warning = "%s parameter should be less then %i;\n" % (param, max_value)
    return error, warning


def check_number_min_warning(data: dict, param: str, min_value: int, max_value: int) -> (str, str):
    """
    checks if number parameter is correct, if number>max you get warning, for other problem - error
    :param data: data with settings
    :param param: key for checing
    :param min_value: min parameter value
    :param max_value: max parameter value
    :return: error and warning message ot empty
    """
    error = ""
    warning = ""
    key = get_real_key(data, param)
    if not key:
        error = "%s parameter is absent;\n" % param
    else:
        value = data[key]
        if not isinstance(value, int) or value > max_value:
            error += "%s parameter must be number less then %i;\n" % (param, max_value)
        if isinstance(value, int) and value < min_value:
            warning = "%s parameter should be more then %i;\n" % (param, min_value)
    return error, warning


def check_number_warning(data: dict, param: str, min_value: int, max_value: int) -> (str, str):
    """
    checks if number parameter is correct, if number>max or < min you get warning, for other problem - error
    :param data: data with settings
    :param param: key for checing
    :param min_value: min parameter value
    :param max_value: max parameter value
    :return: error and warning message ot empty
    """
    error = ""
    warning = ""
    key = get_real_key(data, param)
    if not key:
        error = "%s parameter is absent;\n" % param
    else:
        value = data[key]
        if not isinstance(value, int):
            error += "%s parameter must be number;\n" % param
        else:
            if value > max_value or value < min_value:
                warning = "%s parameter is recommended to be in %i...%i;\n" % (param, min_value, max_value)
    return error, warning


def check_bool(data, param) -> str:
    """
    checks boolean param (0 or 1)
    :param data: dict with settings
    :param param: key for checking
    :return: error message or empty str
    """
    error = ""
    key = get_real_key(data, param)
    if not key:
        error = "%s setting is absent;\n" % param
    else:
        data = data[key]
        if not isinstance(data, int) or (data != 1 and data != 0):
            return "%s must be 0 or 1;\n" % param
    return error


def check_min_max_parameter(data: dict, param: str, lower: int, upper: int) -> str:
    """
    checks pair of parameters that set min and max values for param key
    :param data: dict with settings
    :param param: key to check
    :param lower: lower border for parameter
    :param upper: upper border for parameter
    :return:
    """
    error = ""
    param_key = get_real_key(data, param)
    if not param_key:
        return "%s parameter is absent;\n" % param
    if not isinstance(data[param_key], dict):
        return "%s settings must be in {min:... , max: ...} format;\n" % param
    for key in data[param_key]:
        if key.lower() not in ["min", "max"]:
            error += "unknown parameter %s in %s settings;\n" % (key, param)
    min_value = get_real_key(data[param_key], 'min')
    max_value = get_real_key(data[param_key], 'max')
    if not min_value or not max_value:
        error += "min and max %s parameters must present;\n" % param
    else:
        min_value = data[param_key][min_value]
        max_value = data[param_key][max_value]
        if not isinstance(min_value, int) or min_value < lower or not isinstance(max_value, int) or max_value < min_value or max_value > upper:
            error += "min and max %s parameters must be numbers in %i...%i, max>=min;\n" % (param, lower, upper)
    return error


def check_color(data: dict) -> str:
    """
    checks if color is correct (list of three numbers 0...255 or random string)
    :param data: dict with setting
    :return:
    """
    error = ""
    color = get_real_key(data, "color")
    if not color:
        return "color settings are absent\n"
    color = data[color]
    if isinstance(color, str):
        if color.lower() != 'random':
            return "oolor settings must be array of three numbers or 'random' string;\n"
    else:
        if not isinstance(color, list) or len(color) != 3:
            error += "color settings must be array of three numbers, example:([255, 255, 0]);\n"
        else:
            for part in color:
                if not isinstance(part, int) or (part < 0) or part > 255:
                    error += "color must be positive number (max 255);\n"
    return error


def check_color_from_list(data) -> str:
    """
    checks if color is correct (list of three numbers 0...255 or random string)
    :param data: colors settings
    :return:
    """
    colors = get_real_key(data, 'colors')
    if not colors:
        return "colors settings are absent;\n"
    colors = data[colors]
    if not isinstance(colors, list) or len(colors) == 0:
        return "colors must contain not empty list of colors;\n"
    error = ""
    for color in colors:
        if isinstance(color, str):
            if color.lower() != 'random':
                error += "oolor settings must be array of three numbers or 'random' string;\n"
        else:
            if not isinstance(color, list) or len(color) != 3:
                error += "color settings must be array of three numbers ([255, 255, 0]);\n"
            else:
                for part in color:
                    if not isinstance(part, int) or (part < 0) or part > 255:
                        error += "color must be positive number (max 255);\n"
    return error


def check_keys(data: dict, key_list: list) -> str:
    """
    checks if all keys are correct
    :param data: dict with settings
    :param key_list: list with keus
    :return: error message ot empty string
    """
    error = ""
    for key in data.keys():
        if key.lower() not in key_list:
            error += "unknown parameter % s;\n" % key
    return error


def get_value(data: dict, key: str) -> object:
    """
    checks if key is correct and gets value
    :param data: settings
    :param key: key
    :return: value or None
    """
    key = get_real_key(data, key)
    if not key:
        return None
    else:
        return data[key]


