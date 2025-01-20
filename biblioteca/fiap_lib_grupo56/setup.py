from setuptools import setup, find_packages

setup(
   name='fiap_lib_grupo56',
   version='0.1.13',
   packages=find_packages(),
   description='Biblioteca para o trabalho Tech Challenge do grupo 56 da 4MLET',
   author='Fabio Vargas Matos',
   author_email='fabiomatos@baneses.com.br',
   url='https://github.com/fabiomatos71/Pos',
   install_requires=[],
   include_package_data=True,  # Inclui arquivos listados no MANIFEST.in
   package_data={
       # Especifica arquivos dentro de `fiap_lib_grupo56/arquivos_csv/`
       "fiap_lib_grupo56": ["site_embrapa/arquivos_csv/*.csv"],
    },
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.12.7',
)