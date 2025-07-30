
from setuptools import setup, find_packages

setup(
    name='zengrad-tensorflow',  
    version='0.0.2',
    description='ZenGrad Optimizer - TensorFlow',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Murumuri Naga Poorni',
    author_email='poorni.m0405@gmail.com',
    packages=find_packages(),
    url='https://github.com/XenReZ/ZenGrad-TensorFlow',
    license="Apache-2.0",
    install_requires=[     
        'tensorflow>=2.10.0',
        'keras>=2.10.0',
    ],
    classifiers=[
    'Programming Language :: Python :: 3',
    "License :: OSI Approved :: Apache Software License",
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research', 
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.6',
)
