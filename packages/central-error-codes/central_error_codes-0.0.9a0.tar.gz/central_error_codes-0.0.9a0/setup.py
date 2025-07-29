from setuptools import setup, find_packages

setup(
    name='central_error_codes',  
    version='0.0.9a',            
    packages=find_packages(),    
    include_package_data=True,   
    install_requires=[           
    ],
    author='Snigdha Dutta',
    author_email='', 
    description='A Python package to manage error codes for multiple microservices',  
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown', 
    url='',  
    classifiers=[  # C
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
