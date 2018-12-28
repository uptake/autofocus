import setuptools

with open('README.md', 'r') as f:
    my_long_description = f.read()


documentation_packages = []
regular_packages = [
    'boto3',
    'mlflow',
    'pandas',
    'pillow',
    'psutil',
    'tensorflow',
    'tensorflow_hub'
]
testing_packages = [
    'pytest'
]

setuptools.setup(
    name='autofocus',
    version='0.2.0',
    url='https://github.com/UptakeOpenSource/autofocus',
    python_requires='>=3.6.0',

    author='Greg Gandenberger',
    author_email='gsganden@gmail.com',

    description='Code for doing computer vision on camera trap images',
    long_description=my_long_description,

    packages=setuptools.find_packages(),
    test_suite='tests',

    install_requires=regular_packages,
    extras_require={
        'testing': testing_packages + regular_packages
    }
)
