"""Py-TestUI setup module"""

import pathlib
from setuptools import find_packages, setup


root_path = pathlib.Path(__file__).parent.resolve()
long_description = (root_path / "README.md").read_text(encoding="utf-8")


setup(
    name="python-testui",
    version="1.2.0",
    description="Browser and Mobile automation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/testdevlab/Py-TestUI",
    author="Alvaro Santos Laserna Lopez",
    license="Apache LICENSE 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="Py-TestUI,mobile automation,browser automation",
    project_urls={
        "Source": "https://github.com/testdevlab/Py-TestUI",
        "Tracker": "https://github.com/testdevlab/Py-TestUI/issues",
        "TestDevLab": "https://www.testdevlab.com/",
    },
    packages=find_packages(),
    python_requires=">=3.6, <4",
    install_requires=[
        "pytest<=8.0.1",
        "Appium-Python-Client~=3.1.1",
        "opencv-python>=4.8.1,<4.10.0",
        "geckodriver-autoinstaller==0.1.0",
        "pytest-xdist~=2.5.0",
        "pytest-testrail~=2.9.0",
        "pure-python-adb==0.3.0.dev0",
        "webdriver-manager~=4.0.1",
        "numpy~=1.26",
        "imutils~=0.5.4",
    ],
)
