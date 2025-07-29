# setup.py

from setuptools import setup, find_packages

setup(
    name='cognitive_sdk_plus',
    version='1.0.0.post2',
    description='Cognitive SDK Plus',
    author='Turan Abdullah',
    author_email='abdullah@habs.ai',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'cognitive_sdk_plus': ['presets/*.json'],
    },
    install_requires=[
        'loguru',
        'zmq==0.0.0',
        'pyyaml',
        'numpy==2.2.4',
        'brainflow==5.16.0',
        'httpx==0.28.1',
        'pika==1.3.2',
        'pandas',
        'requests'
    ],
    python_requires='>=3.10',
    include_package_data=True,
    zip_safe=False,
)