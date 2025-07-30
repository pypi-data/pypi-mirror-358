from setuptools import setup

setup(
    name="pysick",
    version="15.0.0",
    license="MIT",
    packages= ['pysick'],
    package_data={'pysick':['assets/*.ico','assets/*.png']},
    install_requires=[],
    author="CowZik",
    author_email="cowzik@email.com",
    description='A lightweight 2D game framework using Tkinter, A super duper Video Player using ',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/COWZIIK/pysick",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
