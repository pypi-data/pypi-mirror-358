#!/usr/bin/env python3
import os
from setuptools import setup


BASEDIR = os.path.abspath(os.path.dirname(__file__))
PLUGIN_ENTRY_POINT = 'ovos-stt-plugin-whispercppserver = ovos_stt_plugin_whispercppserver:OVOSWCPPSSTT'

def get_version():
    """ Find the version of the package"""
    version = None
    version_file = os.path.join(BASEDIR, 'ovos_stt_plugin_whispercppserver', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def required(requirements_file):
    pass
#    """ Read requirements file and remove comments and empty lines. """
#    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
#        requirements = f.read().splitlines()
#        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
#            print('USING LOOSE REQUIREMENTS!')
#            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
#        return [pkg for pkg in requirements
#                if pkg.strip() and not pkg.startswith("#")]


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name='ovos-stt-plugin-whispercppserver',
    version=get_version(),
    description='ovos stt plugin for whisper.cpp server',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ser/ovos-stt-whispercppserver-plugin',
    author='ser',
    author_email='ovos+github@sergevictor.eu',
    license='Apache-2.0',
    packages=['ovos_stt_plugin_whispercppserver'],
    install_requires=required("requirements.txt"),
    package_data={'': package_files('ovos_stt_plugin_whispercppserver')},
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='mycroft OpenVoiceOS OVOS plugin stt whisper.cpp whisper',
    entry_points={'mycroft.plugin.stt': PLUGIN_ENTRY_POINT}
)
