import pathlib

import setuptools

setuptools.setup(
    name='EVENT_PACKAGE',
    version='0.2.9',
    packages=setuptools.find_packages(),
    install_requires=['matplotlib', 'numpy', 'pandas'],
    discription='''This is a hydrologic based event analysis package it also gives the following:
    A. Event duration
    B. Event start time
    C. Event end time
    D. Event FLOW WEIGHTED CONCENTRATION (FWC)
    E. EVENT MEAN WATER TABLE DEPTH (MWTD)
    F. EVENT MEAN TEMPERATURE (EMT)
    ''',
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/jorelix/Event_analysis_code',
    author='Emeka Aniekwensi',
    author_email='felixaniekwensi@gmail.com; aniekwen@msu.edu',
    license='''MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.''',
    classifiers= [
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],
    python_requires='>=3.4',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'event_analysis=EVENT_PACKAGE.cli:main',
        ],
    },
    )