from setuptools import find_packages, setup

setup(
    name="py_testui",
    author="Alvaro Santos Laserna Lopez",
    version="1.1.1",
    url="https://testdevlab.com",
    packages=find_packages(),
    install_requires=[
        "pytest==6.2.5",
        "Appium-Python-Client==2.6.0",
        "selenium==4.1.0",
        "opencv-python==4.6.0.66",
        "geckodriver-autoinstaller==0.1.0",
        "value==0.1.0",
        "pytest-xdist==2.5.0",
        "pytest-testrail==2.9.0",
        "pure-python-adb==0.3.0.dev0",
        "webdriver-manager==3.6.3",
        "numpy==1.21.6",
        "imutils==0.5.4",
    ],
    python_requires=">=3.6",
)
