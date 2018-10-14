import sys
from IniToJson import get_json
from CommonChecks import *

leds_number = 8
leds_copy_list = ['copyred', 'copyblue', 'copygreen']
step_keys = ['repeat', 'wait', 'brightness', 'smooth', 'name']
bignumber = 36000000


def check_sequencer(data, effect) -> str:
    """
    gets data dict and checks if any sequencers for effect and number of sequencers < leds_number
    :param data: dict with ini data
    :param effect: effect
    :return: error text or empty string
    """
    if not data[effect] or not isinstance(data[effect], list):
        return "Error: '%s' effect has no sequencers;" % effect
    if len(data[effect]) >= leds_number:
        return "Error:'%s' effect: number of sequencers must be no more then %i;" \
               % (effect, leds_number)
    return ""


def check_config(sequencer: dict, leds_used: list) -> (str, int, list):
    """
    checks if sequencer config exists, is not empty, is correct
    (leds are not conflicting with used leds, leds are selected properly)
    :param sequencer: dictionary with sequencer data
    :param leds_used: list of used leds
    :return: error text or empty string
    """
    error = ""
    config = get_real_key(sequencer, "config")
    if not config:
        return "no Config string with leds list;", 0, leds_used
    if not isinstance(sequencer[config], list):
        return "config parameter must be list of LEDS (for example [Led1, Led2]);", 0
    leds_count = len(sequencer[config])
    if leds_count == 0:
        return "0 LEDs selected", 0, leds_used
    incorrect_leds = [led for led in sequencer[config] if
                      led.lower() not in ['led1', 'led2', 'led3', 'led4', 'led5', 'led6', 'led7', 'led8']]
    if incorrect_leds:
        error += "incorrect led value;\n"
    for led in sequencer[config]:
        if led in leds_used:
            error += "%s: this led is already used in other sequencer for this effect;\n" % led
        else:
            leds_used.append(led)
    return error.strip(), leds_count, leds_used


def check_sequence(sequencer: dict) -> str:
    """
    checks is sequence exists, if sequences are an array and this array is not empty
    :param sequencer: sequencer dict
    :return: error empty string
    """
    sequence = get_real_key(sequencer, "sequence")
    if not sequence or not isinstance(sequencer[sequence], list):
        return "no steps"
    if len(sequencer[sequence]) == 0:
        return "no steps"
    return ""


def get_namelist(sequencer: dict) -> (list, str):
    """
    gets list of steps names for sequence
    :param sequencer: dict with sequence data
    :return: list of names
    """
    namelist = []
    error = ""
    sequence = get_real_key(sequencer, "sequence")
    for step in sequencer[sequence]:
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
                           % brightness.index(led) + 1
            else:
                if led.lower() not in leds_copy_list:
                    return "%i led is incorrect: use 0...100 or one of CopyRed, CopyBlue, CopyGreen values" \
                           % brightness.index(led) + 1
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


def main(filename: str):

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

    for effect in data.keys():
        error = check_sequencer(data, effect)
        if error:
            print("Error: '%s' effect: " % effect + error)
            continue

        leds_used = []
        for sequencer in data[effect]:
            i_seq = data[effect].index(sequencer) + 1
            error, leds_count, leds_used = check_config(sequencer, leds_used)
            if error:
                print("Error: '%s' effect, %i sequencer: " % (effect, i_seq) + error)
                continue
            error = check_sequence(sequencer)
            if error:
                print(("Error: '%s' effect, %i sequencer: " % (effect, i_seq) + error))
                continue
            namelist, error = get_namelist(sequencer)
            if error:
                print("Error: '%s' effect, %i sequencer: " % (effect, i_seq) + error)
            sequence = get_real_key(sequencer, "sequence")

            for step in sequencer[sequence]:
                name = ""
                name_key = get_real_key(step, "name")
                if name_key:
                    name = step[name_key]
                i_step = sequencer[sequence].index(step) + 1
                error = check_step_keys(step)
                if error:
                    print("Error: '%s' effect, %i sequencer, %i step(%s): " % (effect, i_seq, i_step, name) + error)
                    continue
                error = check_brightness(step, leds_count)
                if error:
                    print("Error: '%s' effect, %i sequencer, %i step(%s): " % (effect, i_seq, i_step, name) + error)

                error = check_wait(step)
                if error:
                    print("Error: '%s' effect, %i sequencer, %i step(%s): " % (effect, i_seq, i_step, name) + error)

                error = check_repeat(step, namelist)
                if error:
                    print("Error: '%s' effect, %i sequencer, %i step(%s): " % (effect, i_seq, i_step, name) + error)

                error = check_smooth(step)
                if error:
                    print("Error: '%s' effect, %i sequencer, %i step(%s): " % (effect, i_seq, i_step, name) + error)
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1:
        res = main(sys.argv[1])
        if res != -1:
            print("File is checked, Press any key to exit")
        wait = input()
    else:
        print("Enter filename")
        filename = input()
        res = main(filename)
        if res != -1:
            print("File is checked, press any key to exit")
        wait = input()
