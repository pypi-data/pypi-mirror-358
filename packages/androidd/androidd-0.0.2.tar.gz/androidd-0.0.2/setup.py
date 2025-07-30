from setuptools import setup, find_packages

setup(
    name='androidd',
    version='0.0.2',
    packages=find_packages(),
    include_package_data=True,
    description='A package containing the androidd folder.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/androidd', # Replace with your project's URL
    author='Your Name', # Replace with your name
    author_email='your.email@example.com', # Replace with your email
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='androidd package',
)
