from setuptools import setup, find_packages


def _install_reqs():
    with open('requirements.txt') as f:
        return f.read().split('\n')


setup(
    name='irc-porn',
    author="Cyril Roelandt",
    author_email="tipecaml@gmail.com",
    url="https://git.framasoft.org/Steap/irc-porn",
    version='0.1',
    install_requires = _install_reqs(),
    # Include data specified in MANIFEST.in
    include_package_data=True,
    packages = find_packages(),
    entry_points ={
        'console_scripts': ['irc-porn = irc_porn.irc_porn:main'],
    },
    test_suite="irc_porn.tests"
)
