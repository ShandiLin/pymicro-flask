import os
import sys

# add this line to avoid No module named 'pymicro_flask', make pytest happy :)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import helpers
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

unset_list = list()
for env in os.environ:
    if env.startswith("PYMICRO") and env not in ["PYMICRO_DATADIR", "PYMICRO_CONFIG"]:
        unset_list.append(env)
for unset_env in unset_list:
    del os.environ[unset_env]
