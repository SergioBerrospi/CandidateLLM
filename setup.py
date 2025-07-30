from setuptools import find_packages, setup
from typing import List

HYPEN_E_DOT = '-e .'

def get_requirements(file_path)->List[str]:
    '''
    this function will return a list of requirements
    '''
    requirements=[]
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements=[req.replace("\n","") for req in requirements]
        requirements = [r for r in requirements if r != "-e ."]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
    
    return requirements

setup(
    name='aipe_project',
    version='0.0.1',
    author='selbver',
    author_email='selbver@gmail.com',
    python_requires='>=3.9',
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["aipe_*"]),
    install_requires=get_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            "aipe-ingest = aipe_ingest.cli:app",
        ]
    }
)