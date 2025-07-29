from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 6 - Mature',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='DysonPythonHack',
    version='0.0.3.2',
    description='Controlling Dyson Fan. For more information check out my website:https://pypi.org/project/DysonPythonHack/ and my github: https://github.com/Kill0geR/DysonPythonHack',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Fawaz Bashiru',
    author_email='fawazbashiru@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='Keylogger',
    packages=find_packages(),
    install_requires=["BetterPrinting", "python-dotenv", "paho-mqtt", "Pytheas22"]
)