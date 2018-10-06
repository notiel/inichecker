import json
import sys
import re

leds_number = 8
leds_copy_list = ['copyred', 'copyblue', 'copygreen']


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


def remove_comments(text: str)->(str, int):
    """
    function removes commentns from ini file and returns new text and number of deleted lines
    :param text: text from ini file
    :return: text without comments, number of removed strings
    """
    missed = 0
    while "/*" in text:
        start = text.find("/*")
        end = text.find('*/')
        if end == -1:
            print('Comment started with /* is not closed')
        missed = text.count('\n', start, end)
        new_text = text[:start] + text[end + 2:]
        text = new_text
    lines = text.split('\n')
    text = ""
    for line in lines:
        if r'//' in line:
            new_line = line[:line.index(r'//')]
            text = text + new_line + '\n'
        else:
            text = text + line + '\n'
    return text, missed


def prepare_text_for_json(text: str)->str:
    """
    remove extra commas, add { at the beginning anf } at the end of file, enclose keys in qoutes
    :param text: ini file text
    :return:  ini file text prepared for json converting
    """
    if r'"' in text:
        print(r'Not allowed symbol: "')
    text = '{' + text
    text = text + '}'
    #add qoutes
    text = re.sub(r'([A-Za-z]\w+)', r'"\1"', text)
    #remove tabulation
    text = text.replace("\t", "")
    #remove extra commas at },} and like this
    while re.findall(r"([\]\}]\s*),(\s*[\}\]])", text):
        text = re.sub(r"([\]\}]\s*),(\s*[\}\]])", r'\1\2', text)
    return text


def get_json(text: str, missed: int)->(dict, str):
    """
    funtions converts prepared text to json if possible
    :param text: ini file text
    :return: json (as dictionary) (or None), empty string or error text
    """
    try:
         data = json.loads(text)
         return data, ""
    except json.decoder.JSONDecodeError:
        e = sys.exc_info()[1]
        errors = e.args[0].split('line ')
        string_number = int(errors[1].split()[0])+ missed
        errors = errors[0]+'line '+ str(string_number)
        return None, errors

def check_sequencer (data, effect) -> str:
    """
    gets data dict and checks if any sequencers for effect and number of sequencers < leds_number
    :param data: dict with ini data
    :param effect: effect
    :param leds_number: number of leds in system
    :return: error text or empty string
    """
    if not data[effect]:
        return "Error: '%s' effect has no sequencers, this effect is skipped" % effect
    if len(data[effect]) >= leds_number:
        return "Error:'%s' effect: number of sequencers must be no more then %i, , this effect is skipped" % (effect, leds_number)
    return ""


def check_config(sequencer: dict, leds_used: list)->(str, int, list):
    """
    checks if sequencer config exists, is not empty, is correct (leds are not conflicting with used leds, leds are selected properly)
    :param sequencer: dictionary with sequencer data
    :param leds_used: list of used leds
    :return: error text or empty string
    """
    error = ""
    config = get_real_key(sequencer, "config")
    if not config:
        return "no Config string with leds list, , this sequencer is skipped", 0, leds_used
    if not isinstance(sequencer[config], list):
        return "config parameter must be list of LEDS (for example [Led1, Led2]), this sequencer is skipped", 0
    leds_count = len(sequencer[config])
    if leds_count == 0:
        return "0 LEDs selected, this sequencer is skipped ", 0, leds_used
    incorrect_leds = [led for led in sequencer[config] if
                      led.lower() not in ['led1', 'led2', 'led3', 'led4', 'led5', 'led6', 'led7', 'led8']]
    if incorrect_leds:
        error+= "incorrect led value, this sequencer is skipped\n"
    for led in sequencer[config]:
        if led in leds_used:
            error+="%s: this led is already used in other sequencer for this effect, this effect is skipped\n" % (led)
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
    if not sequence:
        return "no sequence steps, this sequencer is skipped"
    if not isinstance(sequencer[sequence], list):
        return "no steps, this sequencer is skipped"
    if len(sequencer[sequence]) == 0:
        return "no steps, this sequencer is skipped"
    return ""


def get_namelist(sequencer: dict) -> list:
    """
    gets list of steps names for sequence
    :param sequencer: dict with sequence data
    :return: list of names
    """
    namelist = []
    sequence = get_real_key(sequencer, "sequence")
    for step in sequencer[sequence]:
        name = get_real_key(step, "name")
        if name:
            namelist.append(step[name])
    return namelist


def check_step_keys(step: dict, )->str:
    """
    check if step keys are corrent (no incorrect keys, and each step is step or wait or repeat)
    :param step: dict with step data
    :return: error message or empty string
    """
    repeat = get_real_key(step, "repeat")
    brightness = get_real_key(step, "brightness")
    wait = get_real_key(step, "wait")
    if not repeat and not brightness and not wait:
        return "each step must contain brightness or repeat or wait, this sequencer is skipped"

    for key in step.keys():
        if key.lower() not in ['repeat', 'wait', 'brightness', 'smooth', 'name']:
           return "invalid keys for this step , this sequencer is skipped"
    return ""


def check_brightness(step: dict, leds_count: int)->str:
    """
    check if brightness settings are correct (correct number of leds, brightness is not negative number or copy value
    :param step: dict with step data
    :param leds_count: number of leds configurated for this step
    :return:
    """
    brightness = get_real_key(step, "brightness")
    if brightness:
        brightness = step[brightness]
        if len(brightness) != leds_count:
            return "incorrect leds number, this sequencer is skipped"
        for led in brightness:
            if isinstance(led, int):
                if led < 0 or led > 100:
                    return "%i led brightness is not correct (expect value from 0 to 100 inclusively, this sequencer is skipped" %  (brightness.index(led) + 1)
            else:
                if led.lower() not in leds_copy_list:
                    return "%i led is incorrect: use 0...100 or one of CopyRed, CopyBlue, CopyGreen values, this sequencer is skipped"% brightness.index(led)
    return ""


def check_wait(step: dict) -> str:
    """
    check if wait parameters are correct
    :return: error or empty string
    """
    wait = get_real_key(step, "wait")
    if wait:
        if not isinstance(step[wait], int) or step[wait] < 0:
            return "wait value must be positive number, this sequencer is skipped"
    return ""


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
           error = "start parameter ('StartingFrom') for repeat must be an existing step name, this sequencer is skipped\n"
        count = get_real_key(repeat, "count")
        if not count:
            error += "no count parameter for repeat, this sequencer is skipped]n"
        else:
            count = repeat[count]
            if isinstance(count, int):
                if count <= 0:
                   error+= "repeat count must be positive, this sequencer is skipped"
            else:
                if count != 'forever':
                   error+= "repeat count must be  number or 'forever', this sequencer is skipped"
    return error


def check_smooth(step: dict) -> str:
    """
    check smooth parameters
    :param dict: step data
    :return: error string or empty
    """
    smooth = get_real_key(step, "smooth")
    brightness = get_real_key(step, "brightness")
    if smooth:
        smooth = step[smooth]
        if not brightness:
           return "smooth parameter is only for steps with brightness, this sequencer is skipped"
        if not (isinstance(smooth, int)):
           return "smooth parameter must be number"
        else:
            if smooth < 0:
               return "smooth parameter can't be negative, this sequencer is skipped"
    return ""

def main(filename: str):
    f  = open(filename)
    text = f.read()
    text, missed = remove_comments(text)
    text = prepare_text_for_json(text)
    data, error = get_json(text, missed)
    error = error.replace(" enclosed in double quotes", "")
    if not data:
        print(error)
        return
    for effect in data.keys():
        error = check_sequencer(data, effect)
        if error:
            print("Error: '%s' effect, %i sequencer: " % (effect, i_seq) + error)
            continue
        leds_used = []
        for sequencer in data[effect]:
            i_seq = data[effect].index(sequencer) + 1
            error, leds_count, leds_used = check_config(sequencer, leds_used)
            if error:
                print("Error: '%s' effect, %i sequencer: " %(effect, i_seq) + error)
                continue
            error = check_sequence(sequencer)
            if error:
                print(("Error: '%s' effect, %i sequencer: " %(effect, i_seq) + error))
                continue
            namelist = get_namelist(sequencer)
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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("No ini file")
