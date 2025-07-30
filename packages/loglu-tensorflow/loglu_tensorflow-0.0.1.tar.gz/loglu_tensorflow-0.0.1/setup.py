
from setuptools import setup, find_packages

setup(
    name='loglu-tensorflow',  
    version='0.0.1',
    description='LogLU Activation Function - TensorFlow',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Rishi Chaitanya',
    author_email='rishichaitanya888@gmail.com',
    url='https://github.com/XenReZ/LogLU-TensorFlow',
    packages=find_packages(),
    license="Apache-2.0",
    install_requires=[     
        'tensorflow>=2.10.0',
        'keras>=2.10.0'       
    ],
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research', 
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.6',
)
