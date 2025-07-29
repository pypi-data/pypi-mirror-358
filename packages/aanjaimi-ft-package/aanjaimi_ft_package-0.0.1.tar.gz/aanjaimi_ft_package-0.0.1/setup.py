from setuptools import setup

setup(
    name='aanjaimi_ft_package',
    version='0.0.1',
    description='A sample test package',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='aanjaimi',
    author_email='aanjaimi@student.1337.ma',
    url='https://github.com/aanjaimi/ft_package',
    license='MIT',
    packages=['ft_package'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
