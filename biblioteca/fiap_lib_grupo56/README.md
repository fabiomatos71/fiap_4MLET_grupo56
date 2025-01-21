
# API Tech Challenge - Grupo 56 (4MLET)

Este repositório contém a implementação de uma API desenvolvida em Python utilizando o framework Flask. A API foi criada como parte de um trabalho acadêmico do curso de pós-graduação em Machine Learning Engineering, da FIAP.

A API é capaz de acessar, processar e fornecer dados relacionados à produção, processamento, comercialização, importação e exportação de produtos vitivinícolas no Brasil. Esses dados são obtidos a partir do site da **Embrapa** via **web scraping**, com suporte a arquivos **CSV** como fallback.

Site utilizado: http://vitibrasil.cnpuv.embrapa.br/

## Biblioteca fiap_lib_grupo56

### link do módulo criado e publicado no pypi.org

https://pypi.org/project/fiap-lib-grupo56/

```bash
   pip install fiap_lib_grupo56
```

### Componentes
A lógica do servidor está organizada em:
- **Classe SiteEmbrapa**: Centraliza a lógica de negócios e orquestra o acesso a dados.
- **Repositórios**: Mantêm os dados carregados em memória, obtidos a partir de:
     - **Web Scraping**: Obtém informações diretamente do site da Embrapa.
     - **CSV**: Carrega dados de backup em caso de indisponibilidade do site.
- **Classes de dados**: Com os dados obtidos do site, mantidos estruturados em memória.
     - **Produtos**, **Categorias**, **Produções**, **Processamento**, **Importação** 

![](./ClassesSiteEmbrapa.png)

## Funcionalidades da API

### Funcionamento padrão
Todas as chamadas recebidas pela API serão repassadas para a classe SiteEmbrapa.

A camada da API, fora da biblioteca, trata das questões de segurança, exigência de parâmetros nas chamadas, swagger etc...

A camada da biblioteca trada da obtenção, tratamento e fornecimento dos dados.

As informações relacionadas à Produção, Processamento, Comercialização, Importação e Exportação são obtidos ou através do web scrapping ou através do fallback nos arquivos .CSV, previamente baixados e empacotados dentro da biblioteca.

A classe SiteEmbrapa se utiliza de outras classes de apoio internas à biblioteca para gerir a obtenção dos dados de forma otimizada e disponibilizá-los de forma organizada e estruturada.

## Requisitos

- Python 3.12

### Dependências
As principais dependências incluem:
- bs4 (BeautifulSoup)
- setuptools
- wheel
- twine

### Preparação de uma versão da biblioteca

1. Atualizar a versão no setup.py, pois o PyPi.org não aceita repetições de numero de versão (version='0.3.3',):
   ```bash
   from setuptools import setup, find_packages

   setup(
      name='fiap_lib_grupo56',
      version='0.3.2',
      packages=find_packages(),
      description='Biblioteca para o trabalho Tech Challenge do grupo 56 da 4MLET',
      author='Fabio Vargas Matos',
      author_email='fabiomatos@baneses.com.br',
      url='https://github.com/fabiomatos71/fiap_4MLET_grupo56',
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
      python_requires='>=3.12.0',
   )   
   ```

2. gerar o dist da aplicação "biblioteca":
   ```bash
   python setup.py sdist bdist_wheel
   ```

3. Para subir para o Pypi:
   ```bash
   twine upload dist/*
   ```

## Estrutura de Arquivos

```
(fiap_4MLET_grupo56)                    # pasta raiz do repositório no github
├── api_grupo56/                        # PASTA RAIZ DO PROJETO DA API. (abrir esta pasta no VS)
│   ├── .venv                           # python
│   ├── ...                             
│   └── requirements.txt                # Dependências do projeto
├── biblioteca/                    
│   ├── fiap_lib_grupo56/               # PASTA RAIZ DO PROJETO DA BIBLIOTECA (https://pypi.org/project/fiap-lib-grupo56/). (abrir esta pasta no VS)
│   │   ├── .venv                       # python da biblioteca
│   │   ├── modelo_dados/               # Classes para tratamento de dados
│   │   │   ├── __init__.py             # Arquivo de inicialização do pacote
│   │   │   ├── comercializacao.py      # classes de dados e repositório
│   │   │   ├── importacaoExportacao.py # classes de dados e repositório
│   │   │   ├── processamento.py        # classes de dados e repositório
│   │   │   └── produção.py             # classes de dados e repositório
│   │   ├── site_embrapa/           
│   │   │   ├── __init__.py             # Arquivo de inicialização do pacote
│   │   │   ├── site_embrapa.py         # Classe central da lógica do servidor
│   │   │   └── arquivos_csv/           # Arquivos CSV com dados de backup
│   │   │       └── ...(*.CSV)          # Arquivos CSV para fallback
│   │   ├── anotacoes.txt               # Orientações de como publicar fiap_lib_grupo56 no pypi.org
│   │   ├── MANIFEST.in                 # Manifesto para inclusão dos arquivos .CSV no pacote
│   │   ├── LICENSE                     
│   │   ├── setup.py                    # Configuração do fiap_lib_grupo56 para o pypi.org
│   │   └── requirements.txt            # Dependências do projeto
│   └── ...
├── Diagrama_TechChallenge_grupo56.png  # Diagrama de estrutura e macro funcionamento da API
└── README.md                           # Descrição do projeto no github.  Este arquivo.
```

## Autor
- **Nome**: Fábio Vargas Matos - Grupo 56 - 4MLET
- **Contato**: [fabiomatos@baneses.com.br](mailto:fabiomatos@baneses.com.br)

## Licença
Este projeto é distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.
