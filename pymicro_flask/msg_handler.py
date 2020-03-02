
import time
import random

from pymicro_flask.ret_code import *


def process_message(data):
    result = {KEY_S_TIME: time.time()}
    random_int = random.randint(1,10)
    if random_int % 3 == 0:
        result.update({KEY_RET: RET_FAILED})
    else:
        result.update({KEY_RET: RET_SUCCESS})
    result.update({KEY_E_TIME: time.time()})
    return result
