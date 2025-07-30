from setuptools import setup 
with open('/home/ali/Downloads/ML Libraries/README','r',encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='RegressionLibrary',
    version='0.3',
    description='Educational regression models built from scratch in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ali Khalid Ali Khalid',
    author_email='ali88883737@gmail.com',
    url = 'https://github.com/Alouakhalid/RegressionLibrary',
    py_modules=['Regression'],
    install_requires=[
        'numpy',
        'tqdm'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)