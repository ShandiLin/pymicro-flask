import os
import sys
from io import open

from setuptools import setup, Command, find_packages


root_dirpath = os.path.dirname(os.path.abspath(__file__))


class Clean(Command):
    """
        custom clean command
        usage:
            python setup.py clean [-e|--egg]
    """
    description = "Cleans build files"
    user_options = [('egg', 'e', "Arguments to clean with .eggs folder")]

    def initialize_options(self):
        self.egg = None

    def finalize_options(self):
        if self.egg is None:
            print('not deleting .eggs folder')

    def run(self):
        cmd = dict(
            build="rm -rf {p}/build".format(p=root_dirpath),
            egg_info="find {p} -name '*.egg-info' -exec rm -rf {{}} +".format(p=root_dirpath),
            dist="rm -rf {p}/dist".format(p=root_dirpath),
            pytest_cache="find {p} -name '.pytest_cache' -exec rm -rf {{}} +".format(p=root_dirpath),
            pycache="find {p} -name '__pycache__' -exec rm -rf {{}} +".format(p=root_dirpath)
        )
        if self.egg is not None:
            cmd['eggs'] = "find {p} -name '.eggs' -exec rm -rf {{}} +".format(p=root_dirpath)

        for key in cmd:
            print('remove {d} folder with command below:\n  {c}'.format(d=key, c=cmd[key]))
            os.system(cmd[key])


python_2 = sys.version_info[0] == 2
app_home = os.path.dirname(os.path.abspath(__file__))


def get_requirements(fname):
    def read(fname):
        with open(fname, 'rU' if python_2 else 'r') as f:
            return f.read()
    fpath = os.path.join(app_home, fname)
    return [req.strip() for req in read(fpath).splitlines() if req.strip()]

with open(os.path.join(app_home, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_require = get_requirements('docs/requirements.txt')
test_require = get_requirements('docs/requirements-test.txt')

setup(
    name="pymicro_flask",
    version="1.0",
    author="",
    description="python flask micro service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    packages=find_packages(where='pymicro_flask'),
    package_dir={
        '': 'pymicro_flask',
    },
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
    include_package_data=True,
    data_files=[
        ("conf", [
            "conf/service.toml",
            "conf/logging_config.ini",
            "conf/uwsgi.ini",
        ])
    ],
    install_requires=install_require,
    tests_require=test_require,
    zip_safe=False,
    scripts=[
        "bin/pymicro_server",
        "bin/pymicro_uwsgi"
    ],
    cmdclass={'clean': Clean}
)
