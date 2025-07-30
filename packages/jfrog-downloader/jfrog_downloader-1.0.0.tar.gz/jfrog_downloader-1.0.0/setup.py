from setuptools import setup, find_packages

setup(
    name='Jfrog-Downloader', 
    version='1.0.0',    
    description='Download files from JFrog Artifactory',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='abi-sheak',
    author_email='abisheakkumarasamy@gmail.com',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.6",
)
