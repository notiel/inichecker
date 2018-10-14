import sys
from IniToJson import get_json
from CommonChecks import *


effects_keys = ['PowerOn', 'AfterWake', 'PowerOff', 'Flaming', 'Blade2', 'Lockup', 'Stab', 'Clash', 'Blaster',
                'Workingmode', 'Flickering']
workingmode_keys = ['color', "flaming", "flickeringalways", "auxledseffect"]
on_off_keys = ['blade', 'auxledseffect']
flaming_keys = ['size', 'speed', 'delay_ms', "colors", "auxledseffect"]
blade2_flaming_keys = ['size', 'speed', 'delay_ms', "colors", "auxledseffect", "alwayson"]
flickering_keys = ['time', 'brightness', "auxledseffect"]
blade2_flickering_keys = ['time', 'brightness', "auxledseffect", "alwayson"]
move_keys = ['color', 'duration_ms', 'sizepix', 'auxledseffect']
lockup_keys = ['flicker', 'flashes', 'auxledseffect']
lockup_flicker_keys = ['color', 'time', 'brightness']
lockup_flashes_keys = ['period', 'color', 'duration_ms', 'sizepix']
blade2_keys = ['flaming', 'workingmode', 'flickering', 'delaybeforeon']
big_number = 3600000


def check_auxleds(data: dict) -> str:
    """
    checks if auxledeffect string is correct
    :param data: dict with settings data
    :return: error message or  empty string
    """
    auxledseffect = get_real_key(data, "auxledseffect")
    if auxledseffect:
        if not isinstance(data[auxledseffect], str):
            return "auxleds effect must be string;\n"
    return ""


def check_afterwake(data: dict) -> str:
    """
    function chacks afterwake effect and returns error message or empty string
    :param data:dict with effect settings
    :return: error message or empty string
    """
    afterwake, error = check_existance(data, 'afterwake')
    if error:
        return error
    error += check_auxleds(afterwake)
    error += check_keys(afterwake, ['auxledseffect'])
    return error.strip()


def check_poweron(data: dict) -> str:
    """
    checks poweron effect
    :param data: data wit effect settings
    :return: error message or ""
    """
    poweron, error = check_existance(data, 'poweron')
    if error:
        return error
    error += check_auxleds(poweron)
    error += check_keys(poweron, on_off_keys)
    blade, error_blade = check_existance(poweron, 'blade')
    if blade:
        error_blade += check_number(blade, "speed", 0, big_number)
        error_blade += check_keys(blade, ['speed'])
    if error_blade:
        error += "Blade: " + error_blade
    return error.strip()


def check_workingmode(data: dict) -> (str, str):
    """
    checks if working mode settings are correct (all parameters exist and are of correct type and meaning,
    flaming effect exists if used
    flaming and flickering keys absent produce warning, other keys - error
    :param data: dict wit settings
    :return: error and warning messages (or empty strings)
    """
    warning = ""
    workingmode, error = check_existance(data, 'workingmode')
    if error:
        return error
    error += check_keys(workingmode, workingmode_keys)
    error += check_color(workingmode)
    error += check_bool(workingmode, 'flaming')
    error += check_bool(workingmode, 'flickeringalways')
    error += check_auxleds(workingmode)
    return error, warning


def check_poweroff(data: dict) -> str:
    """
    check poweroff settings (if setting for blade (speed, direction) and auxeffect are present and correct
    :param data: dict with poweroff settings
    :return: error message or empty string
    """
    poweroff, error = check_existance(data, 'poweroff')
    if error:
        return error
    error += check_keys(poweroff, on_off_keys)
    blade, error_blade = check_existance(poweroff, 'blade')
    if blade:
        error_blade += check_number(blade, 'speed', 0, big_number)
        error_blade += check_bool(blade, 'moveforward')
        error_blade += check_keys(blade, ['speed', 'moveforward'])
    error += check_auxleds(poweroff)
    if error_blade:
        error += 'Blade: ' + error_blade
    return error.strip()


def check_flaming(data: dict, keylist: list, led_number: int) -> str:
    """
    checks if flaming settings are correct
    :param data: dict with flaming settings
    :param keylist: list with keys for flaming effect
    :param led_number: number of leds in blade
    :return: error message or empty string
    """
    flaming, error  = check_existance(data, 'flaming')
    if error:
        return error
    error = check_keys(flaming, keylist)
    error += check_min_max_parameter(flaming, "size", 0, led_number)
    error += check_min_max_parameter(flaming, "speed", 0, big_number)
    error += check_min_max_parameter(flaming, "delay_ms", 0, big_number)
    error += check_color_from_list(flaming)
    error += check_auxleds(flaming)
    return error.strip()


def check_flickering(data: dict, keylist: list) -> str:
    """
    checks if flickering settings are cortect
    :param data: dict with flickering setting
    :param keylist: list of keys for flickering setting
    :return: error message or empty string
    """
    flickering, error = check_existance(data, 'flickering')
    if error:
        return error
    error += check_keys(flickering, keylist)
    error += check_min_max_parameter(flickering, "time", 0, big_number)
    error += check_min_max_parameter(flickering, "brightness", 0, 100)
    error += check_auxleds(flickering)
    return error.strip()


def check_movement(data: dict, leds_number: int, key: str) -> str:
    """
    checks if blaster/clash/stab effect is correct
    :param data: dict with settings
    :param key: type of mevement (blaster/clash/stab)
    :param leds_number: number or lades in blade
    :return:
    """
    move, error = check_existance(data, key.lower())
    if error:
        return error
    error += check_keys(move, move_keys)
    error += check_number(move, "duration_ms", 0, big_number)
    error += check_number(move, "sizepix", 0, leds_number)
    error += check_color(move)
    error += check_auxleds(move)
    return error.strip()


def check_flicker(data: dict) -> str:
    """
    checks flicker settings for lockup parameter
    :param data: dict with settings
    :return: error or empty message
    """
    flicker, error = check_existance(data, 'flicker')
    if error:
        return error
    error = check_keys(flicker, lockup_flicker_keys)
    error += check_color(flicker)
    error += check_min_max_parameter(flicker, 'time', 0, big_number)
    error += check_min_max_parameter(flicker, 'brightness', 0, 100)
    return error


def check_flashes(lockup: dict, leds_number: int) -> str:
    """
    checks flashes settings for lockup parameter
    :param data: dict with settings
    :param leds_number: number of leds
    :return: error or empty message
    """
    flashes, error = check_existance(lockup, 'flashes')
    if error:
        return error
    error = check_keys(flashes, lockup_flashes_keys)
    error += check_color(flashes)
    error += check_min_max_parameter(flashes, "period", 0, big_number)
    error += check_number(flashes, 'duration_ms', 0, big_number)
    error += check_number(flashes, 'sizepix', 0, leds_number)
    return error

def check_lockup(data: dict, leds_number: int) -> str:
    """
    checks of lockup effect settins are correct
    :param data: dict with data
    :param leds_number: number of leds in blade
    :return: error message or empty string
    """
    lockup, error = check_existance(data, 'lockup')
    error += check_keys(lockup, lockup_keys)
    error += check_auxleds(lockup)
    flicker_error = check_flicker(lockup)
    if flicker_error:
        error += 'Flicker: ' + flicker_error
    flashes_error = check_flashes(lockup, leds_number)
    if flashes_error:
        error += 'Flashes: ' + flashes_error
    return error.strip()


def check_blade2(data: dict, leds_number: int) -> str:
    """
    checks if blade2 settings are correct
    :param data: dict with settings of blade2
    :param leds_number: number of leds in blade
    :return:
    """
    blade2, error = check_existance(data, 'blade2')
    error = check_keys(blade2, blade2_keys)
    flickering = get_real_key(blade2, "flickering")
    if flickering:
        error_flickering = check_flickering(blade2, blade2_flickering_keys)
        flickering = blade2[flickering]
        if isinstance(flickering, dict):
            error_flickering += check_bool(flickering, "alwayson")
        if error_flickering:
            error += "flickering: %s" % error_flickering
    flaming = get_real_key(blade2, "flaming")
    if flaming:
        error_flaming = check_flaming(blade2, blade2_flaming_keys, leds_number)
        flaming = blade2[flaming]
        if isinstance(flaming, dict):
            error_flaming += check_bool(flaming, "alwayson")
        if error_flaming:
            error += "flaming: %s" % error_flaming
    error += check_number(blade2, "delaybeforeon", 0, big_number)
    workingmode, error_workingmode = check_existance(blade2, 'workingmode')
    if workingmode:
        error_workingmode = check_keys(workingmode, ['color'])
        error_workingmode += check_color(workingmode)
    if error_workingmode:
        error += "Working mode: %s" % error_workingmode
    return error.strip()


def main(filename: str, leds_number: int):

    try:
        f = open(filename)
    except FileNotFoundError:
        print("File %s not found" % filename)
        return -1
    text = f.read()
    data, error = get_json(text)
    error = error.replace(" enclosed in double quotes", "")
    if not data:
        print(error)
        return -1

    for profile in data.keys():
        if not isinstance(data[profile], dict):
            print("Wrong settings format for profile %s;" % profile)
            continue
        errors = {err: "" for err in effects_keys}
        error = check_keys(data[profile], [key.lower() for key in effects_keys])
        if error:
            print(error)
        errors['AfterWake'] = check_afterwake(data[profile])
        errors['PowerOn'] = check_poweron(data[profile])
        (error, warning) = check_workingmode(data[profile])
        errors['WorkingMode'] = error + "\nWarning: " + warning if warning else error
        errors['PowerOff'] = check_poweroff(data[profile])
        errors['Flaming'] = check_flaming(data[profile], flaming_keys, leds_number)
        errors['Flickering'] = check_flickering(data[profile], flickering_keys)
        errors['Blaster'] = check_movement(data[profile], leds_number, "Blaster")
        errors['Clash'] = check_movement(data[profile], leds_number, "Clash")
        errors['Stab'] = check_movement(data[profile], leds_number, "Stab")
        errors['Lockup'] = check_lockup(data[profile], leds_number)
        errors['Blade2'] = check_blade2(data[profile], leds_number)
        for key in errors.keys():
            if errors[key]:
                print("Error: %s profile %s effect:\n%s" % (profile, key, errors[key].strip()))
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 2:
        try:
            main(sys.argv[1], int(sys.argv[2]))
            print("File is checked. Press any key to exit")
            input()
        except ValueError:
            print("Second parameter (number of leds) must be number")
            input()
    else:
        print("Enter filename")
        user_filename = input()
        print("Enter leds number")
        user_leds_number = input()
        try:
            res = main(user_filename, int(user_leds_number))
            if res != -1:
                print("File is checked, press any key to exit")

        except ValueError:
            print("Leds number must be a number")
        input()
