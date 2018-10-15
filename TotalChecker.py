from Auxchecker import *
from ProfileChecker import *
from CommonChecker import *
import os


def main():
    aux_ok = os.path.exists("Auxleds.ini")
    profile_ok = os.path.exists("Profiles.ini")
    common_ok = os.path.exists("Common.ini")
    if aux_ok:
        aux_list = aux_main("Auxleds.ini")
    else:
        aux_list = []
        print("Auxleds.ini is absent")
    if common_ok:
        leds_number = common_main("Common.ini")
    else:
        leds_number = 144
        print("Common.ini is absent, default leds number (144) is used")
    if profile_ok:
        profile_main("Profiles.ini", leds_number, aux_list)
    else:
        print("Profiles.ini is absent")
    print("All found files are checked")


if __name__ == '__main__':
    main()
    input()