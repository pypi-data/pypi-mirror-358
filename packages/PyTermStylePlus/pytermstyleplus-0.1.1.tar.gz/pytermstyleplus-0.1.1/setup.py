import setuptools

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyTermStylePlus",
    version="0.1.1",
    author="Mohammedcha",
    author_email="contact@mohammedcha.com", 
    description="An elegant Python library for terminal text styling with themes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mohammedcha/PyTermStylePlus",
    py_modules=["PyTermStylePlus"], 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Development Status :: 3 - Alpha", 
    ],
    python_requires='>=3.6',
)
