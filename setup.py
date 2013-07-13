from setuptools import setup, find_packages
setup(
    name="torngas",
    version="0.09",
    description="torngas based on tornado",
    author="qingyun meng",
    url="http://github.com/mqingyn/torngas",
    license="LGPL",
    packages= find_packages(),
    package_data={'torngas': ['resources/*.*']},
    author_email = "maingyn@gmail.com",
    requires=['Tornado'],
    )
