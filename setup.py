from setuptools import setup, find_packages
import torngas

setup(
    name="torngas",
    version=torngas.__version__,
    description="torngas based on tornado",
    long_description="torngas is based on tornado,django like web framework.",
    keywords='python torngas django tornado',
    author="mqingyn",
    url="https://github.com/mqingyn/torngas",
    license="BSD",
    packages=find_packages(),
    package_data={'torngas': ['resource/exception.html']},
    author_email="mqingyn@gmail.com",
    requires=['tornado', 'futures'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    scripts=[],
    install_requires=[
        'futures',
    ],
)
