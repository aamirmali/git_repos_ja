import os
import sys
import script
from code.common import exceptions

def run():
    try:
        script.interpret_and_run(script.parse_arguments())
    except exceptions.StupidityError as i:
        os.remove(sys._getframe(1).f_code.co_filename)
        raise exceptions.StupidityError('\nStupidityError detected\n' + str(i) + '\nProgram will now delete itself to prevent further abuse')
