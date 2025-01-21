from setuptools import setup, find_packages

setup(
   name='fiap_lib_grupo56',
   version='0.3.5',
   package_dir={"" : "src"},
   packages=find_packages(),
#    packages=['modelo_dados', 'site_embrapa'],
   description='Biblioteca para o trabalho Tech Challenge do grupo 56 da 4MLET',
   author='Fabio Vargas Matos',
   author_email='fabiomatos@baneses.com.br',
   url='https://github.com/fabiomatos71/fiap_4MLET_grupo56',
   install_requires=[],
   include_package_data=True,  # Inclui arquivos listados no MANIFEST.in
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.12.0',
)