
from setuptools import setup

project = "datanews"

setup(
    name=project,
    version='0.01',
    url='https://github.com/joehand/data_news',
    description='DataNews is a flask application for posting and discussing data news!',
    author='Joe Hand',
    author_email='joeahand@gmail.com',
    packages=["datanews"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Security',
        'Flask-Script',
        'Flask-Classy',
        'Flask-Compress',
        'Flask-Restless',
        'Flask-Heroku-Cacheify',
        'Flask-Admin',
        'Flask-Assets',
        'Flask-DebugToolbar',
        'bleach',
        'beautifulsoup4',
        'markdown',
        'markdownify',
        'mechanize',
        'twython',
        'cssmin',
        'alembic',
        'py-bcrypt',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)