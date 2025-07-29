from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='mansufa_api-package',
    version='1.0.0',
    packages=find_packages(),
    description='Descricao da sua lib cursofiap',
    author='Fellipe Pinho',
    author_email='fellipemrpinho@gmail.com',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
