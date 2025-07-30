from setuptools import setup,find_packages

setup(
    name='HyTechMaster-STT',
    version='0.1',
    author='Arman Rathore',
    authore_email='example@gmail.com',
    description='this is speech to text packages created by arman rahtore'
)
packages = find_packages(),
install_requirement = [
    'selenium',
    'webdriver_manager'
]
