from setuptools import setup, find_packages

setup(
    name="torngas",
    version="1.6.3",
    description="torngas based on tornado",
    long_description="torngas is based on tornado,django like web framework.",
    keywords='python torngas django tornado',
    author="mqingyn",
    url="https://github.com/mqingyn/torngas",
    license="BSD",
    packages=find_packages(),
    package_data={'torngas': ['resource/exception.html']},
    author_email="mqingyn@gmail.com",
    requires=['Tornado', 'futures'],
    scripts=[],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'futures',
    ],
)
