import setuptools
import os

long_description = ""
if os.path.isfile("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setuptools.setup(
    name="phisher-ctmonitor",
    version="0.1.2",
    author="Viktoryia Valiuk",
    author_email="viktoriapogorzhelska@gmail.com",
    description="A tool for monitoring the certificate transparency logs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nbdknws/phisher",
    packages=setuptools.find_packages(),
    install_requires=[
        "construct==2.10.70",
        "cryptography==45.0.4",
        "python-telegram-bot==22.2",
        "Requests==2.32.4",
        "rich==14.0.0",
        "rich_argparse==1.7.1",
        "rich_gradient==0.3.2",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
        # phisher will invoke the main() in your __main__.py (or wherever you point it)
        "phisher = phisher.__main__:main",
        ],
    },
)
