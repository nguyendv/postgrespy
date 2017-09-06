from setuptools import setup

setup(
    name='postgrespy',
    packages=['postgrespy'],
    version='0.2.2',
    description='A simple postgres orm',
    author='Dung (Dave) Nguyen',
    author_email='dvnguyen.vn@gmail.com',
    url='https://github.com/nguyendv/postgrespy',
    download_url='https://github.com/nguyendv/postgrespy/archive/0.2.2.tar.gz',
    install_requires=[
        'psycopg2>=2.7',
        'Jinja2>=2.9'
    ],
    python_requires='~=3.6',
    keywords=[],
    classifiers=[]
)
