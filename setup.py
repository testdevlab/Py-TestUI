from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="py_testui",
    author="Alvaro Santos Laserna Lopez",
    version="1.0.9",
    url="https://testdevlab.com",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        "pytest", 'Appium-Python-Client', 'selenium', 'opencv-python', 'geckodriver-autoinstaller',
        'value', "pytest-xdist", "pytest-testrail", "pure-python-adb", "webdriver-manager", 'numpy', 'imutils'
    ],
    python_requires='>=3.6',
)
