import sys
from typing import Tuple, Sequence, Any

from IniToJson import get_json
from CommonChecks import *

leds_number = 8
leds_copy_list = ['copyred', 'copyblue', 'copygreen']
step_keys = ['repeat', 'wait', 'brightness', 'smooth', 'name']
ledgroup_keys = ['name', 'leds']
big_number = 36000000
seq_keys = ['name', 'group', 'sequence']


def check_sequencer(data: dict,group_names: Sequence[str]) -> Tuple[str, str]:
    """
    check if sequencer is correct
    :param data: dict with ini data
    :param group_names: list with existing group names
    :return: error and warning text or empty strings
    """
    warning = check_keys(data, seq_keys)
    name = get_real_key(data, 'name')
    if not name:
        return "No name field;", warning
    if not(isinstance(data[name], str)):
        return 'Sequencer name must to be string;', warning
    group = get_real_key(data, 'group')
    if not group:
        return "No group name;", warning
    if data[group].lower() not in [name.lower() for name in group_names]:
        return "Use existing group name;", warning
    sequence = get_real_key(data, 'sequence')
    if not sequence:
        return "No sequencer part", warning
    if not isinstance(data[sequence], list):
        return "Wrong sequence format;", warning
    return "", warning




def get_namelist(sequence: Sequence[str]) -> (list, str):
    """
    gets list of steps names for sequence
    :param sequencer: dict with sequence data
    :return: list of names
    """
    namelist = []
    error = ""
    for step in sequence:
        name = get_real_key(step, "name")
        if name:
            if step[name] in namelist:
                error += "name %s is already used" % step[name]
            namelist.append(step[name])
    return namelist, error


def check_step_keys(step: dict) -> str:
    """
    check if step keys are corrent (no incorrect keys, and each step is step or wait or repeat)
    :param step: dict with step data
    :return: error message or empty string
    """
    error = ""
    repeat = get_real_key(step, "repeat")
    brightness = get_real_key(step, "brightness")
    wait_key = get_real_key(step, "wait")
    if not repeat and not brightness and not wait_key:
        error += "each step must contain brightness or repeat or wait;\n"
    error += check_keys(step, step_keys)
    return error.strip()


def check_brightness(step: dict, leds_count: int) -> str:
    """
    check if brightness settings are correct (correct number of leds, brightness is not negative number or copy value
    :param step: dict with step data
    :param leds_count: number of leds configurated for this step
    :return:
    """
    brightness = get_real_key(step, "brightness")
    if brightness:
        brightness = step[brightness]
        if not isinstance(brightness, list):
            return "Brightness must be a list of leds"
        if len(brightness) != leds_count:
            return "incorrect leds number"
        for led in brightness:
            if isinstance(led, int):
                if led < 0 or led > 100:
                    return "%i led brightness is not correct (expect value from 0 to 100 inclusively)" \
                           % (brightness.index(led) + 1)
            else:
                if led.lower() not in leds_copy_list:
                    return "%i led is incorrect: use 0...100 or one of CopyRed, CopyBlue, CopyGreen values" \
                           % (brightness.index(led) + 1)
    return ""


def check_wait(step: dict) -> str:
    """
    check if wait parameters are correct
    :return: error or empty string
    """
    return check_unnecessary_number(step, 'wait', 0, big_number)


def check_repeat(step: dict, namelist: [str]) -> str:
    """
    check correctness of repeat step (correct count value, step for repeat exists)
    :param step: dict with step data
    :param namelist: list of names of steps
    :return: error string or empty string
    """
    repeat = get_real_key(step, "repeat")
    error = ""
    if repeat:
        repeat = step[repeat]
        start_step = get_real_key(repeat, "startingfrom")
        if not start_step or repeat[start_step] not in namelist:
            error = "start parameter ('StartingFrom') for repeat must be an existing step name\n"
        count = get_real_key(repeat, "count")
        if not count:
            error += "no count parameter for repeat\n"
        else:
            count = repeat[count]
            if isinstance(count, int):
                if count <= 0:
                    error += "repeat count must be positive"
            else:
                if count != 'forever':
                    error += "repeat count must be  number or 'forever'"
    return error.strip()


def check_smooth(step: dict) -> str:
    """
    check smooth parameters
    :param step: step data
    :return: error string or empty
    """
    smooth = get_real_key(step, "smooth")
    brightness = get_real_key(step, "brightness")
    if smooth:
        smooth = step[smooth]
        if not brightness:
            return "smooth parameter is only for steps with brightness"
        if not (isinstance(smooth, int)):
            return "smooth parameter must be number"
        else:
            if smooth < 0:
                return "smooth parameter can't be negative"
    return ""


def check_main_section(data: dict) -> Tuple[str, str]:
    """
    checks that there are two main sections
    :param data: dict with data
    :return: error/warning message or ""
    """
    if not isinstance(data, dict):
        return "wrong data format, must be LedGroups and Sequencer parts", ""
    if len(data.keys()) < 2:
        return "LedGroups or Sequencers part is absent", ""
    ledgroups = get_real_key(data, "ledgroups")
    if not ledgroups:
        return "Ledgroups parts is absent", ""
    sequencers = get_real_key(data, "sequencers")
    if not sequencers:
        return "Sequencer parts is absent", ""
    warning = ""
    if len(data.keys()) > 2:
        warning  = "extra unknown keys in main part"
    return "", warning

def check_ledsgroup(data: list) -> Tuple[str, str, Sequence[str]]:
    """
    checks if leds group data is correct
    :param data: list of ledsgroup

    :return: error and list of used names
    """
    if isinstance(data, dict):
        data = [data]
    else:
        if not isinstance(data, list):
            return "wrong leds group format;", "", []
    group_names = []
    used_leds = []
    error = ""
    warning = ""
    for ledgroup in data:
        i = data.index(ledgroup) + 1
        if not isinstance(ledgroup, dict):
            error+="wrong group format for % i group\n" % i
            continue
        warning += check_keys(ledgroup, ledgroup_keys)
        name = get_real_key(ledgroup, 'name')
        if not name:
            error+="Name is absent for %i group;\n" %i
            continue
        if not isinstance(ledgroup[name], str):
            warning += "Ledgroup name is recommended to be string in %i group;\n" % i
        if ledgroup[name].lower() in [used_name.lower() for used_name in group_names]:
            error+="Names must be unique, we already have %s name" % ledgroup[name]
        leds = get_real_key(ledgroup, "leds")
        if not leds:
            error+="Leds are absent for %s group;\n" % ledgroup[name]
            continue
        if not isinstance(ledgroup[leds], list):
            error+="Leds are to be list like [1, 2, 3] in %s group;\n" % ledgroup[name]
            continue
        temp = [led not in [1, 2, 3, 4, 5, 6, 7, 8] for led in ledgroup[leds]]
        temp2 = [led  in used_leds for led in ledgroup[leds]]
        if any(temp):
            error += "wrong led data, led is a number 1..8 for %s group;\n" % ledgroup[name]
            continue
        if any(temp2):
            error += "several leds are already used in % s group;\n" % ledgroup[name]
        used_leds.extend(ledgroup[leds])
        group_names.append(ledgroup[name])
    return error.strip(), warning, group_names


def get_leds_count(data: dict, group_name: str) -> int:
    """
    gets number of leds for group
    :param data: dict with data
    :param group_name: name of group
    :return: number of leds
    """
    ledgroups = get_real_key(data, 'ledgroups')
    for ledgroup in data[ledgroups]:
        name = get_real_key(ledgroup, "name")
        if ledgroup[name].lower() == group_name.lower():
            leds = get_real_key(ledgroup, 'leds')
            return len(ledgroup[leds])
    return 0



def aux_main(filename: str) -> list:
    """
    checks aux file and return list of auxleds effects or none
    :param filename: file name
    :return: auxlist or none
    """
    try:
        f = open(filename)
    except FileNotFoundError:
        print("File %s not found" % filename)
        return []
    print("Checking %s..." % filename)
    text = f.read()
    data, error = get_json(text)
    error = error.replace(" enclosed in double quotes", "")
    if not data:
        print(error)
        print("Cannot check %s properly and get data list" % filename)
        return []
    error, warning = check_main_section(data)
    if error:
        print(error)
        print("Can not check %s properly" % filename)
        return []
    error, warning, group_names = check_ledsgroup(data[get_real_key(data, 'ledgroups')])
    if error:
        print(error)
    if warning:
        print(warning)
    sequencers = data[get_real_key(data, 'sequencers')]
    if isinstance(sequencers, dict):
        sequencers = [sequencers]
    else:
        if not isinstance(sequencers, list):
            print("Wrong sequencers format, can't get sequencers data")
            return []
    seq_names = []
    for sequencer in sequencers:
        i = sequencers.index(sequencer) + 1
        error, warning = check_sequencer(sequencer, group_names)
        if error:
            print("Error: %i  sequencer: %s" % (i, error))
            continue
        if warning:
            print("Warning: %i  sequencer: %s" % (i, warning))
        seq_name = sequencer[get_real_key(sequencer, 'name')]
        if seq_name.lower in [name.lower() for name in seq_names]:
            print("Name %s for sequencer is already used") % seq_name
            continue
        seq_names.append(seq_name)
        if error:
            print("Error: %s in '%s' sequences " % (error, seq_name))
            continue
        leds_count = get_leds_count(data, sequencer[get_real_key(sequencer, "group")])
        sequence = get_real_key(sequencer, "sequence")
        namelist, error = get_namelist(sequencer[sequence])
        if error:
            print("Error:  %s sequencer: " % (seq_name) + error)
        for step in sequencer[sequence]:
            name = ""
            name_key = get_real_key(step, "name")
            if name_key:
                name = step[name_key]
            i_step = sequencer[sequence].index(step) + 1
            error = check_step_keys(step)
            if error:
                print("Error: %s sequencer, %i step(%s): " % (seq_name, i_step, name) + error)
                continue
            error = check_brightness(step, leds_count)
            if error:
                print("Error: %s sequencer, %i step(%s): " % (seq_name, i_step, name) + error)
            error = check_wait(step)
            if error:
                print("Error: %s sequencer, %i step(%s): " % (seq_name, i_step, name) + error)
            error = check_repeat(step, namelist)
            if error:
                print("Error: '%s' sequencer, %i step(%s): " % (seq_name, i_step, name) + error)
            error = check_smooth(step)
            if error:
                print("Error: %s sequencer, %i step(%s): " % (seq_name, i_step, name) + error)
    return seq_names


if __name__ == '__main__':
    if len(sys.argv) > 1:
        res = aux_main(sys.argv[1])
        if res:
            print("File is checked, Press any key to exit")
        input()
    else:
        print("Enter filename")
        filename = input()
        res = aux_main(filename)
        if res:
            print("File is checked, press any key to exit")
        input()
