from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='fiap-package-fernandarufato',
    version='1.0.0',
    packages=find_packages(),
    description='Descricao da sua lib Fiap',
    author='Fernanda Oliveira Rufato',
    author_email='nandaoliveira1985@terra.com.br',
    url='https://github.com/ferRufato/Fiap',  
    license='MIT',  
    long_description=long_description,
    long_description_content_type='text/markdown'
)
