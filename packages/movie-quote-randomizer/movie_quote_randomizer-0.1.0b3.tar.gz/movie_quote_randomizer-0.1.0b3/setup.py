from setuptools import find_packages, setup

about = {}
with open("mq_randomizer/__about__.py") as fp:
    exec(fp.read(), about)

with open("README.md") as fp:
    long_description = fp.read()

packages = find_packages(
    where=".", include=["mq_randomizer", "mq_randomizer.*"]
)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__summary__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zachary Cutlip",
    author_email="uid000@gmail.com",
    url="https://github.com/zcutlip/movie-quote-randomizer",
    license="MIT",
    packages=find_packages(),
    package_data={'mq_randomizer': ['py.typed'],
                  'mq_randomizer.data': ['**/*.json']},
    python_requires='>=3.10',
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities"
    ],
)
