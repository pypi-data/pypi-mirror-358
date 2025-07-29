from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
setup(
   name='meu_investimento_vinimedeiros',
   version='0.2',
   packages=find_packages(),
   install_requires=[],
   author='Vinicius Medeiros',
   author_email='vinicius.medeiros-2025@hotmail.com',
   description='Uma biblioteca para cálculos de investimentos.',
   url='https://github.com/viniciusmedeiros/meu_investimento',
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.6',
)