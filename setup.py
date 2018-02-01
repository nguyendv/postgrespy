from setuptools import setup, find_packages
import os
import postgrespy

setup(
    name='postgrespy',
    packages=find_packages(),
    version=os.environ['POSTGRESPY_VERSION'],
    description='A simple postgres ORM',
    author='Dave Nguyen',
    author_email='dv@dvnguyen.com',
    url='https://github.com/nguyendv/postgrespy',
    download_url='https://github.com/nguyendv/postgrespy/archive/' + os.environ['POSTGRESPY_VERSION'] +'.tar.gz',
    install_requires=[
        'psycopg2>=2.7',
        'Jinja2>=2.9',
        'click~=6.7'
    ],
    entry_points={
        'console_scripts': [
            'postgrespy = postgrespy.__main__:main',
        ]
    },
    python_requires='~=3.6',
    keywords=[],
    classifiers=[]
)
