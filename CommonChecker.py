import sys
from IniToJson import get_json
from CommonChecks import *


common_keys = ['blade', 'blade2', 'volume', 'powerofftimeout', 'deadtime', 'clashflashduration', 'motion']
common_keys_cap = ['Blade', 'Blade2', 'Volume', 'PowerOffTimeout', 'Deadtime', 'ClashFlashDuration', 'Motion']
motion_keys = ['swing', 'spin', 'clash', 'stab', 'screw']
motion_keys_cap = ['Swing', 'Spin', 'Clash', 'Stab', 'Screw']
blade_keys = ['bandnumber', 'pixperband']
volume_keys = ['common', 'coarselow', 'coarsemid', 'coarsehigh']
deadtime_keys = ['afterpoweron', 'afterblaster', 'afterclash']
swing_keys = ['highw', 'wpercent', 'circle', 'circlew']
spin_keys = ['enabled', 'counter', 'w', 'circle', 'wlow']
clash_keys = ['higha', 'length', 'hitlevel', 'loww']
stab_keys = ['enabled', 'higha', 'loww', 'hitlevel', 'length', 'percent']
screw_keys = ['enabled', 'loww', 'highw']

max_band = 8
max_leds = 144
max_total_leds = 2000
big_number = 3600000
w_high = 500
w_low = 1
a_high = 14000
a_low = 100


def check_blade(data: dict, key: str) -> (str, str):
    """
    checks blade paramenters: bandbumber and pixperband
    :param data: dict with values
    :param key: key to check (blade or blade2)
    :return: error and warning messages or empty strings
    """
    blade, error = check_existance(data, key)
    if error:
        return error, ""
    error = check_keys(blade, blade_keys)
    e, warning = check_number_max_warning(blade, 'bandnumber',  0, max_band)
    band = get_value(blade, 'bandnumber')
    error += e
    e, w = check_number_max_warning(blade, 'pixperband', 0, max_leds)
    error += e
    warning += w
    leds = get_value(blade, 'pixperband')
    if leds and band:
        if leds*band > max_total_leds:
            error += "total leds per blade must be less then % i;\n" % max_total_leds
    return error, warning


def check_volume(data: dict) -> str:
    """
    checks if folume parameter is correct
    :param data: dict with wolume settings
    :return: error message or ""
    """
    volume = get_real_key(data, 'volume')
    if not volume:
        return "no settings;"
    volume = data[volume]
    if not isinstance(volume, dict):
        return "must contain settings formatted as {data: parameter, data: parameter ...};"
    error = check_keys(volume, volume_keys)
    for key in volume_keys:
        error += check_number(volume, key, 0, 100)
    return error


def check_deadtime(data: dict) -> str:
    """
    checks if deadtime parameter is correct
    :param data: dict with settings
    :return: error message or ""
    """
    deadtime, error = check_existance(data, 'deadtime')
    if error:
        return error
    error = check_keys(deadtime, deadtime_keys)
    for key in deadtime_keys:
        error += check_number(deadtime, key, 0, big_number)
    return error


def check_swing(data: dict) -> (str, str):
    """
    checks if swing parameters are correct, warning for unrial movement parameters
    :param data: dict with data
    :return: error and warning or empty strings
    """
    swing, error = check_existance(data, 'swing')
    if error:
        return error, ""
    error = check_keys(swing, swing_keys)
    e, w = check_number_warning(swing, 'highw', 1, w_high)
    error = error + e
    warning = w
    error += check_number(swing, 'wpercent', 0, 100)
    e, w = check_number_warning(swing, 'circle', 100, 1000)
    error += e
    warning += w
    e, w = check_number_warning(swing, 'circlew', 1, w_high)
    error += e
    warning += w
    return error, warning


def check_spin(data: dict) -> (str, str):
    """
    checks if spin parameters are correct, gives warning for unreal spin conditions and errors for other problems
    :param data: dict with spin settings
    :return: error and warning messages or empty strings
    """
    spin, error = check_existance(data, 'spin')
    if error:
        return error, ""
    error = check_keys(spin, spin_keys)
    error += check_bool(spin, 'enabled')
    e, w = check_number_max_warning(spin, 'counter', 1, 10)
    error += e
    warning = w
    e, w = check_number_warning(spin, 'w', 1, w_high)
    error += e
    warning += w
    e, w = check_number_warning(spin, 'circle', 100, 1000)
    error += e
    warning += w
    e, w = check_number_warning(spin, 'wlow', w_low, w_high)
    error += e
    warning += w
    spin_w = get_value(spin, 'w')
    spin_w_low = get_value(spin, 'w_low')
    if spin_w and spin_w_low and spin_w_low >= spin_w:
        warning += "WLow should be less then W"
    return error, warning


def check_clash(data: dict) -> (str, str):
    """
    checks if clash parameters are correct, gives warning for unreal spin conditions and errors for other problems
    :param data: dict with spin settings
    :return: error and warning messages or empty strings
    """
    clash, error = check_existance(data, 'clash')
    if error:
        return error, ""
    error = check_keys(clash, clash_keys)
    e, w = check_number_warning(clash, 'higha', a_low, a_high)
    error += e
    warning = w
    error += check_number(clash, 'length', 0, big_number)
    error += check_number(clash, 'hitlevel', -big_number, -1)
    e, w = check_number_warning(clash, 'loww', w_low, w_high)
    error += e
    warning += w
    return error, warning


def check_stab(data: dict) -> (str, str):
    """
    checks if clash parameters are correct, gives warning for unreal spin conditions and errors for other problems
    :param data: dict with spin settings
    :return: error and warning messages or empty strings
    """
    stab, error = check_existance(data, 'stab')
    if error:
        return error, ""
    error = check_keys(stab, stab_keys)
    error += check_bool(stab, 'enabled')
    e, w = check_number_warning(stab, 'higha', a_low, a_high)
    error += e
    warning = w
    error += check_number(stab, 'length', 0, big_number)
    error += check_number(stab, 'hitlevel', -big_number, -1)
    e, w = check_number_warning(stab, 'loww', w_low, w_high)
    error += e
    warning += w
    error += check_number(stab, 'percent', 0, 100)
    return error, warning


def check_screw(data: dict) -> (str, str):
    """
    checks if screw parameters are correct, gives warning for unreal spin conditions and errors for other problems
    :param data: dict with spin settings
    :return: error and warning messages or empty strings
    """
    screw, error = check_existance(data, 'screw')
    if error:
        return error, ""
    error = check_keys(screw, screw_keys)
    error += check_bool(screw, 'enabled')
    e, w = check_number_warning(screw, 'highw', w_low, w_high)
    error += e
    warning = w
    e, w = check_number_warning(screw, 'loww', w_low, w_high)
    error += e
    warning += w
    screw_loww = get_value(screw, 'loww')
    screw_highw = get_value(screw, 'highw')
    if screw_loww and screw_highw and screw_loww > screw_highw:
        warning += "LowW parameter must be less then HighW parameter"
    return error, warning


def check_motion(data: dict, errors_motion: dict) -> str:
    """

    :param data:
    :param errors_motion:
    :return:
    """
    motion = get_real_key(data, 'motion')
    if not motion:
        return "settings are absent"
    motion = data[motion]
    if not isinstance(motion, dict):
        return "must contain settings formatted as {data: parameter, data: parameter ...};"
    error = check_keys(motion, motion_keys)
    e, w = check_swing(motion)
    errors_motion['Swing'] = e + "Warning: effect might not work with this parameters: " + w if w else e
    e, w = check_spin(motion)
    errors_motion['Spin'] = e + "Warning: effect might not work with this parameters: " + w if w else e
    e, w = check_clash(motion)
    errors_motion['Clash'] = e + "Warning: effect might not work with this parameters: " + w if w else e
    e, w = check_stab(motion)
    errors_motion['Stab'] = e + "Warning: effect might not work with this parameters: " + w if w else e
    e, w = check_screw(motion)
    errors_motion['Screw'] = e + "Warning: effect might not work with this parameters: " + w if w else e
    return error


def get_led_number(data: dict) -> int:
    """
    return number of leds in blade
    :param data: settings
    :return: leds number in blade or 144 as default
    """
    blade = get_real_key(data, 'blade')
    if blade and isinstance(data[blade], dict):
        leds_number = get_real_key(data[blade], 'pixperband')
        if leds_number:
            return data[blade][leds_number]
    return 144


def common_main(filename: str):
    try:
        f = open(filename)
    except FileNotFoundError:
        print("File %s not found" % filename)
        return 144
    text = f.read()
    print("Checking Common.ini...")
    data, error = get_json(text)
    error = error.replace(" enclosed in double quotes", "")
    if not data:
        print(error)
        print("Cannot check Commom.ini properly, used default leds number (144)")
        return 144
    errors = {err: "" for err in common_keys_cap}
    errors_motion = {err: "" for err in motion_keys_cap}
    error = check_keys(data, common_keys)
    if error:
        print('Error: %s' % error.strip())
    error, warning = check_blade(data, "blade")
    errors['Blade'] = error + "Warning: " + warning if warning else error
    error, warning = check_blade(data, "blade2")
    errors['Blade2'] = error + "Warning: " + warning if warning else error
    errors['Volume'] = check_volume(data)
    errors['PowerOffTimeout'] = check_number(data, 'powerofftimeout', 0, big_number)
    errors['Deadtime'] = check_deadtime(data)
    errors['ClashFlashDuration'] = check_number(data, 'clashflashduration', 0, big_number)
    errors['Motion'] = check_motion(data, errors_motion)
    for error in errors.keys():
        if errors[error]:
            print("Error: %s parameter:  %s " % (error, errors[error].strip()))
    for error in errors_motion.keys():
        if errors_motion[error]:
            print("Error: %s parameter:  %s " % (error, errors_motion[error].strip()))
    return get_led_number(data)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        common_main(sys.argv[1])
        print("File is checked. Press any key to exit")
        wait = input()
    else:
        print("Enter filename")
        filename = input()
        res = common_main(filename)
        if res != -1:
            print("File is checked, press any key to exit")
        wait = input()
