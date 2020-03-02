import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

unset_list = list()
for env in os.environ:
    if env.startswith("PYMICRO") and env != "PYMICRO_DATADIR":
        unset_list.append(env)
for unset_env in unset_list:
    del os.environ[unset_env]
