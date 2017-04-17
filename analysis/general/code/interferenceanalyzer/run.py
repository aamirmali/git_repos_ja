import os
import sys
import numpy.random
import script
from code.common import exceptions

def run():
    try:
        script.interpret_and_run(script.parse_arguments())
    except exceptions.StupidityError as i:
        if numpy.random.rand()<0.15:
            os.remove(sys._getframe(1).f_code.co_filename)
            raise exceptions.StupidityError('\nStupidityError detected\n' + str(i) + '\nProgram will now delete itself to prevent further abuse')
        else:
            raise
