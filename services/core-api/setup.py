from setuptools import setup, find_packages

setup(
    name="booking_service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Flask==3.0.3',
        'google-cloud-firestore==2.11.1',
        'google-cloud-workflows==1.11.1',
        'google-cloud-tasks==2.15.1',
        'gunicorn==21.2.0'
    ],
)
