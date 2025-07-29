from setuptools import setup,find_packages

setup(
    name='HyTechMaster',
    version='0.1.1', # bumped verison 
    authore='Arman Rathore',
    author_email='armanrathore236@gmail.com',
    description='This is speech to text package created by arman rathore'
)
packages = find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]
