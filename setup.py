from setuptools import setup
import os

setup(
    name="postgrespy",
    packages=["postgrespy"],
    version=os.environ["POSTGRESPY_VERSION"],
    description="A simple postgres ORM",
    author="Dave Nguyen",
    author_email="dv@dvnguyen.com",
    url="https://github.com/nguyendv/postgrespy",
    download_url="https://github.com/nguyendv/postgrespy/archive/{}.tar.gz".format(
        os.environ["POSTGRESPY_VERSION"]
    ),
    install_requires=["psycopg2>=2.7", "Jinja2>=2.9"],
    python_requires="~=3.6",
    keywords=[],
    classifiers=[],
)
