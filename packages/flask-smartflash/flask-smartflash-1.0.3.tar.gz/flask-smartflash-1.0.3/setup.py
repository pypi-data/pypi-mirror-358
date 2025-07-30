from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flask_smartflash",
    version="1.0.3",
    author="Eze CHimenma Goodness",
    author_email="chimenmagoodness@gmail.com",
    description="A Flask extension for smart flash messages with toast and popup support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chimenmagoodness/flask-smartflash.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Flask",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Flask>=1.0",
    ],
    keywords="flask, flash messages, toast, popup, custom popup, custom toast, custom notifications, flask notifications with animation, notifications, smartflash, flask-smartflash, modern flask notifications, web development, flask extension",
)
# pip install flask_smartflash-1.0.0-py3-none-any.whl
# pip install setuptools wheel twine