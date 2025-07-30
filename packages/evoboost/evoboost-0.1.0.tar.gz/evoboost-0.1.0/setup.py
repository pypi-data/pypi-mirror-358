from setuptools import setup, find_packages

setup(
    name='evoboost',
    version='0.1.0',
    description='EvoBoost: A novel gradient boosting classifier and regressor by Sudip Barua',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Sudip Barua',
    author_email='your@email.com',
    url='https://osf.io/xxxxx',  # Replace with your actual OSF link
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'scikit-learn',
        'scipy',
    ],
)
