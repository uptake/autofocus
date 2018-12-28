import setuptools

with open('README.md', 'r') as f:
    my_long_description = f.read()

setuptools.setup(
    name="autofocus",
    version="0.2.0",
    url="https://github.com/UptakeOpenSource/autofocus",

    author="Greg Gandenberger",
    author_email="gsganden@gmail.com",

    description="Code for doing computer vision on camera trap images",
    long_description=my_long_description,

    packages=setuptools.find_packages(),

    install_requires=[
        'boto3',
        'mlflow',
        'pandas',
        'pillow',
        'psutil',
        'tensorflow',
        'tensorflow_hub'
    ]
)
