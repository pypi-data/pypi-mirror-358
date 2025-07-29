from setuptools import setup, find_packages

setup(
    name='microauth-fastapi',
    version='0.1.10',
    description='FastAPI JWT verification integration for MicroAuth IdP',
    author='MicroAuth',
    author_email='support@microauth.com',
    url='https://github.com/microauth-org/microauth-fastapi',
    packages=find_packages(exclude=['tests', 'docs']),
    install_requires=[
        'fastapi',
        'httpx',
        'python-jose[cryptography]',
        'pydantic',
        'structlog'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.13',
        'Framework :: FastAPI',
        'License :: OSI Approved :: MIT License',
    ],
)
