from datetime import timedelta
import requests
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flasgger import Swagger
import json
from site_embrapa import SiteEmbrapa
from modelo_dados.processamento import EnumTipoUva_proc
from modelo_dados.importacaoExportacao import EnumCategoria_im_ex

app = Flask(__name__)
# configuração para conversão correta de caracteres acentuados
app.config['JSON_AS_ASCII'] = False
# chave para geração dos tokens jwt
app.config['JWT_SECRET_KEY'] = '9577610b1442bedb155e45770852db7b825d0fa27cf367d8d082909fecfc85021c133d74503ee35aa086cad320471fbad4d8515d26df3e13380aa0ae6b25a607d33daa7917006ea0f551357a2970ba2302221cfc103a6e7432a14b5f2ae023885824ef220a4fbcc7cd78f48cd3c5ea9e8a752785d18755600fe95bc91dc88ad9'
# validade do token gerado no login
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1) # timedelta(minutes=15)

# jwt para autenticação
jwt = JWTManager(app)

# respostas personalizadas para o jwt - INICIO
# Token não fornecido
@jwt.unauthorized_loader
def response_sem_token(err_msg):
    return json_response_msg_erro({
        "error": "Token não fornecido.",
        "message": "Você precisa fornecer um token válido no cabeçalho Authorization."
    }, 401)

# Token inválido ou expirado
@jwt.invalid_token_loader
def response_token_Invalido(err_msg):
    return json_response_msg_erro({
        "error": "Token inválido.",
        "message": "O token fornecido é inválido ou expirou. Faça login novamente para obter um novo token."
    }, 422)

#token expirado
@jwt.expired_token_loader
def response_token_expirado(jwt_header, jwt_payload):
    return json_response_msg_erro({
        "error": "Token expirado.",
        "message": "O token fornecido expirou. Faça login novamente para obter um novo token."
    }, 401)
# respostas personalizadas para o jwt - FIM

# swagger - INICIO


# Inicialização do Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,  # Documentar todas as rotas
            "model_filter": lambda tag: True,  # Documentar todos os modelos
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
}
swagger_template = {
    "info": {
        "title": "Grupo 56 - 4MLET - API Tech Challenge",
        "description": "Documentação da API do Tech Challenge para obtenção de dados a partir do site http://vitibrasil.cnpuv.embrapa.br/",
        "version": "1.0.0",
        "contact": {
            "responsibleOrganization": "Grupo56 4MLET",
            "responsibleDeveloper": "Fabio Vargas Matos",
            "email": "fabiomatos@baneses.com.br",
        },
    },
}
Swagger(app, config=swagger_config, template=swagger_template)
# swagger - FIM


# Instacia da classe que realiza toda a busca e controle das informações
# classe definida no pacote fiap_lib-grupo56
siteEmbrapa = SiteEmbrapa()

def json_response_msg_erro(data, status=200):
    """
    Para criar respostas JSON com conversão correta dos caracteres acentuados. ensure_ascii=False
    """
    return app.response_class(
        response=json.dumps(data, ensure_ascii=False),
        status=status,
        mimetype='application/json'
    )

@app.route('/login', methods=['POST'])
def login():
    """
    Obter token para acesso à API
    ---
    tags:
      - Autenticação
    parameters:
      - name: username
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "4MLET"
            password:
              type: string
              example: "4MLET"
        description: Utilizar '4MLET' como username e password, para testes do Tech Challenge.
    responses:
      200:
        description: Retorna token jwt para ser utilizado nas demais chamadas da API
        examples:
          application/json: |
            [
              {
                "token": "asdasdafasdfasd..."
              }
            ]
      400:
        description: Usuário ou senha não informados.
      401:
        description: Usuário ou senha incorretos.  Acesso não autorizado.
    """
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return json_response_msg_erro({"msg": "Usuário ou senha não informados"}, 400)
    
    if username == "4MLET" and password == "4MLET":
        # Gerar token 
        token = create_access_token(identity=username)
        return jsonify({"token": token}), 200
    else:
        return json_response_msg_erro({"msg": "Usuário ou senha incorretos.  Acesso não autorizado."}, 401)

@app.route('/vitibrasil/carrega_csv', methods=['GET'])
@jwt_required()
def carrega_csv():
    """
    Carrega todos os dados dos arquivos .CSV fornecidos no site e armazenados offline na aplicação.  Coloca todos os dados em cache.
    ---
    tags:
      - Configuração
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
    responses:
      200:
        description: Carrega todos os dados dos arquivos .CSV fornecidos no site e armazenados offline na aplicação.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        siteEmbrapa.carregaRepositoriosFromArquivosCSV()
        return jsonify({"result": "ok"}), 200
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/limpa_cache', methods=['GET'])
@jwt_required()
def limpa_cache():
    """
    Esvazia o cache de dados.  Tanto dados de consultas anteriores, que ficam em cache, como os dados possivelmente carregados dos arquivos .CSV serão limpos do cache.
    ---
    tags:
      - Configuração
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
    responses:
      200:
        description: Esvazia o cache de dados.  Tanto dados de consultas anteriores, que ficam em cache, como os dados possivelmente carregados dos arquivos .CSV serão limpos do cache.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        siteEmbrapa.inicializa_repositorios()
        return jsonify({"result": "ok"}), 200
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/producao', methods=['GET'])
@jwt_required()
def producao():
    """
    Obter toda lista de produtos com suas categorias, produzidos em um ano
    ---
    tags:
      - Produção
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de produções para o ano informado.
        examples:
          application/json: |
            [
                {
                    "ano": 2021,
                    "quantidade": 40450,
                    "produto": "Suco de uva adoçado",
                    "categoria": "SUCO"
                },
                {
                    "ano": 2021,
                    "quantidade": 146075996,
                    "produto": "Tinto",
                    "categoria": "VINHO DE MESA"
                },
                {
                    "ano": 2021,
                    "quantidade": 26432799,
                    "produto": "Branco",
                    "categoria": "VINHO DE MESA"
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
        examples:
          application/json: |
            {
              "error": "O parâmetro 'ano' é obrigatório."
            }
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        # Busca produtividades para o ano informado
        produtividades = siteEmbrapa.obterProducoesPorAno(ano)

        # Monta a lista de respostas
        retorno = []
        for produtividade in produtividades:
            retorno.append({
                "ano": produtividade.ano,
                "quantidade": produtividade.quantidade,
                "produto": produtividade.produto.nome,
                "categoria": produtividade.produto.categoria.nome
            })

        # Retorna usando json.dumps com ensure_ascii=False
        return app.response_class(
            response=json.dumps(retorno, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/producao_por_categoria', methods=['GET'])
@jwt_required()
def producao_por_categoria():
    """
    Obter quantidade total da produção anual de apenas uma categoria
    ---
    tags:
      - Produção
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
      - name: categoria
        in: query
        type: string
        required: true
        description: A categoria da produção a ser consultada.
    responses:
      200:
        description: Retorna o total de produção para a categoria e ano informados.
        examples:
          application/json: |
            {
              "ano": 2021,
              "categoria": "SUCO",
              "total": 50000
            }
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        # Obtém o parâmetro 'categoria'
        nome_categoria = request.args.get('categoria', type=str)
        if nome_categoria is None:
            return json_response_msg_erro({"error": "O parâmetro 'categoria' é obrigatório."}, 400)

        # Busca produtividades para o ano informado
        produtividade_total_categoria = siteEmbrapa.obterProducaoTotalDeCategoriaPorAno(nome_categoria, ano)

        # Monta a lista de respostas
        retorno = []
        retorno.append({
            "ano": ano,
            "categoria": nome_categoria,
            "total": produtividade_total_categoria})

        # Retorna usando json.dumps com ensure_ascii=False
        return app.response_class(
            response=json.dumps(retorno, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)


@app.route('/vitibrasil/processamento/viniferas', methods=['GET'])
@jwt_required()
def processamento_viniferas():
    """
    Obter toda lista de cultivares de uvas viníferas processados em um ano
    ---
    tags:
      - Processamento
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de processamentos de cultivares de uvas viníferas para o ano informado.
        examples:
          application/json: |
            [
                {
                    "tipo": "Viniferas",
                    "ano": 2021,
                    "quantidade": 811140,
                    "cultivar": "Alicante Bouschet",
                    "categoria": "TINTAS"
                },
                {
                    "tipo": "Viniferas",
                    "ano": 2021,
                    "quantidade": 6513974,
                    "cultivar": "Ancelota",
                    "categoria": "TINTAS"
                },
                {
                    "tipo": "Viniferas",
                    "ano": 2021,
                    "quantidade": 0,
                    "cultivar": "Aramon",
                    "categoria": "TINTAS"
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return processamento(ano, EnumTipoUva_proc.VINIFERAS)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/processamento/americanas_e_hibridas', methods=['GET'])
@jwt_required()
def processamento_americanas_hibridas():
    """
    Obter toda lista de cultivares de uvas americanas e hibridas processados em um ano
    ---
    tags:
      - Processamento
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de processamentos de cultivares de uvas americanas e hibridas para o ano informado.
        examples:
          application/json: |
            [
                {
                    "tipo": "Americanas e Hibridas",
                    "ano": 2021,
                    "quantidade": 0,
                    "cultivar": "Bacarina",
                    "categoria": "TINTAS"
                },
                {
                    "tipo": "Americanas e Hibridas",
                    "ano": 2021,
                    "quantidade": 4092669,
                    "cultivar": "Bailey",
                    "categoria": "TINTAS"
                },
                {
                    "tipo": "Americanas e Hibridas",
                    "ano": 2021,
                    "quantidade": 117655879,
                    "cultivar": "Bordo",
                    "categoria": "TINTAS"
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return processamento(ano, EnumTipoUva_proc.AMERICANASEHIBRIDAS)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/processamento/uvas_de_mesa', methods=['GET'])
@jwt_required()
def processamento_uvas_mesa():
    """
    Obter toda lista de cultivares de uvas de mesa processados em um ano
    ---
    tags:
      - Processamento
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de processamentos de cultivares de uvas de mesa para o ano informado.
        examples:
          application/json: |
            [
                {
                    "tipo": "Uvas de Mesa",
                    "ano": 2022,
                    "quantidade": 0,
                    "cultivar": "Alphonse Lavallee",
                    "categoria": "TINTAS"
                },
                {
                    "tipo": "Uvas de Mesa",
                    "ano": 2022,
                    "quantidade": 0,
                    "cultivar": "Moscato de Hamburgo",
                    "categoria": "TINTAS"
                },
                {
                    "tipo": "Uvas de Mesa",
                    "ano": 2022,
                    "quantidade": 0,
                    "cultivar": "Cardinal",
                    "categoria": "BRANCAS"
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return processamento(ano, EnumTipoUva_proc.UVASDEMESA)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/processamento/sem_classificacao', methods=['GET'])
@jwt_required()
def processamento_sem_classificacao():
    """
    Obter toda lista de cultivares de uvas sem classificação processados em um ano
    ---
    tags:
      - Processamento
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de processamentos de cultivares de uvas sem classificação para o ano informado.
        examples:
          application/json: |
            [
                {
                    "tipo": "Sem Classificacao",
                    "ano": 2017,
                    "quantidade": 0,
                    "cultivar": "Sem classificação",
                    "categoria": "Sem classificação"
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return processamento(ano, EnumTipoUva_proc.SEMCLASSIFICACAO)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

def processamento(ano: int, tipo_uva: EnumTipoUva_proc):
    """
    Obtem lista de ProcessamentoAnual para um ano e o tipo_uva informado.
    """
    try:

        # Busca processamentos para o ano e tipo_uva (sub_opcao) informados
        processamentos = siteEmbrapa.obterProcessamentoPorAnoTipoUva(ano, tipo_uva)

        # Monta a lista de respostas
        retorno = []
        for processamento in processamentos:
            retorno.append({
                "tipo": processamento.cultivar.TipoUva.value,
                "ano": processamento.ano,
                "quantidade": processamento.quantidade,
                "cultivar": processamento.cultivar.nome,
                "categoria": processamento.cultivar.categoria.nome
            })

        # Retorna usando json.dumps com ensure_ascii=False
        return app.response_class(
            response=json.dumps(retorno, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/comercializacao', methods=['GET'])
@jwt_required()
def comercializacao():
    """
    Obter toda lista de produtos com suas categorias, comercializados em um ano
    ---
    tags:
      - Comercialização
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de comercializações do ano informado.
        examples:
          application/json: |
            [
                {
                    "ano": 2021,
                    "quantidade": 185653678,
                    "produto": "Tinto",
                    "categoria": "VINHO DE MESA"
                },
                {
                    "ano": 2021,
                    "quantidade": 1931606,
                    "produto": "Rosado",
                    "categoria": "VINHO DE MESA"
                },
                {
                    "ano": 2021,
                    "quantidade": 22426954,
                    "produto": "Branco",
                    "categoria": "VINHO DE MESA"
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        # Busca comercializações para o ano informado
        comercializacoes = siteEmbrapa.obterComercializacoesPorAno(ano)

        # Monta a lista de respostas
        retorno = []
        for comercializacao in comercializacoes:
            retorno.append({
                "ano": comercializacao.ano,
                "quantidade": comercializacao.quantidade,
                "produto": comercializacao.produto.nome,
                "categoria": comercializacao.produto.categoria.nome
            })

        # Retorna usando json.dumps com ensure_ascii=False
        return app.response_class(
            response=json.dumps(retorno, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/importacao/vinhos_de_mesa', methods=['GET'])
@jwt_required()
def importacao_vinhos_mesa():
    """
    Obter toda lista paises com as importações de vinho de mesa realizadas em um ano
    ---
    tags:
      - Importação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as importações de vinho de mesa realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Vinhos de Mesa",
                    "ano": 2021,
                    "pais": "Africa do Sul",
                    "quantidade": 859169,
                    "valor": 2508140
                },
                {
                    "categoria": "Vinhos de Mesa",
                    "ano": 2021,
                    "pais": "Alemanha",
                    "quantidade": 106541,
                    "valor": 546967
                },
                {
                    "categoria": "Vinhos de Mesa",
                    "ano": 2021,
                    "pais": "Argélia",
                    "quantidade": 0,
                    "valor": 0
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return importacao(ano, EnumCategoria_im_ex.VINHOSDEMESA)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/importacao/espumantes', methods=['GET'])
@jwt_required()
def importacao_espumantes():
    """
    Obter toda lista paises com as importações de espumantes realizadas em um ano
    ---
    tags:
      - Importação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as importações de espumantes realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Espumantes",
                    "ano": 2007,
                    "pais": "Africa do Sul",
                    "quantidade": 90,
                    "valor": 1073
                },
                {
                    "categoria": "Espumantes",
                    "ano": 2007,
                    "pais": "Alemanha",
                    "quantidade": 1980,
                    "valor": 11786
                },
                {
                    "categoria": "Espumantes",
                    "ano": 2007,
                    "pais": "Argentina",
                    "quantidade": 556320,
                    "valor": 1441196
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return importacao(ano, EnumCategoria_im_ex.ESPUMANTES)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/importacao/uvas_frescas', methods=['GET'])
@jwt_required()
def importacao_uvas_frescas():
    """
    Obter toda lista paises com as importações de uvas frescas realizadas em um ano
    ---
    tags:
      - Importação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as importações de uvas frescas realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Uvas Frescas",
                    "ano": 1985,
                    "pais": "Argélia",
                    "quantidade": 0,
                    "valor": 0
                },
                {
                    "categoria": "Uvas Frescas",
                    "ano": 1985,
                    "pais": "Argentina",
                    "quantidade": 208150,
                    "valor": 125910
                },
                {
                    "categoria": "Uvas Frescas",
                    "ano": 1985,
                    "pais": "Brasil",
                    "quantidade": 0,
                    "valor": 0
                }
            ]   
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return importacao(ano, EnumCategoria_im_ex.UVASFRESCAS)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/importacao/uvas_passas', methods=['GET'])
@jwt_required()
def importacao_uvas_passas():
    """
    Obter toda lista paises com as importações de uvas passas realizadas em um ano
    ---
    tags:
      - Importação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as importações de uvas passas realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Uvas Passas",
                    "ano": 1986,
                    "pais": "Arábia Saudita",
                    "quantidade": 0,
                    "valor": 0
                },
                {
                    "categoria": "Uvas Passas",
                    "ano": 1986,
                    "pais": "Argentina",
                    "quantidade": 2116776,
                    "valor": 2515764
                },
                {
                    "categoria": "Uvas Passas",
                    "ano": 1986,
                    "pais": "Austrália",
                    "quantidade": 0,
                    "valor": 0
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return importacao(ano, EnumCategoria_im_ex.UVASPASSAS)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/importacao/suco_uva', methods=['GET'])
@jwt_required()
def importacao_suco_uva():
    """
    Obter toda lista paises com as importações de suco de uva realizadas em um ano
    ---
    tags:
      - Importação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as importações de suco de uva realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Suco de Uva",
                    "ano": 1989,
                    "pais": "Africa do Sul",
                    "quantidade": 0,
                    "valor": 0
                },
                {
                    "categoria": "Suco de Uva",
                    "ano": 1989,
                    "pais": "Alemanha",
                    "quantidade": 0,
                    "valor": 0
                },
                {
                    "categoria": "Suco de Uva",
                    "ano": 1989,
                    "pais": "Argentina",
                    "quantidade": 1901597,
                    "valor": 1339369
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return importacao(ano, EnumCategoria_im_ex.SUCODEUVA)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)


def importacao(ano: int, categoria: EnumCategoria_im_ex):
    """
    Obtem lista de importacoes para um ano e categoria informados.
    """
    try:

        # Busca importacoes para o ano e categoria (sub_opcao) informados
        importacoes = siteEmbrapa.obterImportacaoPorAnoCategoria(ano, categoria)

        # Monta a lista de respostas
        retorno = []
        for importacao in importacoes:
            retorno.append({
                "categoria": importacao.categoria.value,
                "ano": importacao.ano,
                "pais": importacao.pais.nome,
                "quantidade": importacao.quantidade,
                "valor": importacao.valor
            })

        # Retorna usando json.dumps com ensure_ascii=False
        return app.response_class(
            response=json.dumps(retorno, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/exportacao/vinhos_de_mesa', methods=['GET'])
@jwt_required()
def exportacao_vinhos_mesa():
    """
    Obter toda lista paises com as exportações de vinho de mesa realizadas em um ano
    ---
    tags:
      - Exportação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as exportações de vinho de mesa realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Vinhos de Mesa",
                    "ano": 2021,
                    "pais": "Africa do Sul",
                    "quantidade": 859169,
                    "valor": 2508140
                },
                {
                    "categoria": "Vinhos de Mesa",
                    "ano": 2021,
                    "pais": "Alemanha",
                    "quantidade": 106541,
                    "valor": 546967
                },
                {
                    "categoria": "Vinhos de Mesa",
                    "ano": 2021,
                    "pais": "Argélia",
                    "quantidade": 0,
                    "valor": 0
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return exportacao(ano, EnumCategoria_im_ex.VINHOSDEMESA)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/exportacao/espumantes', methods=['GET'])
@jwt_required()
def exportacao_espumantes():
    """
    Obter toda lista paises com as exportações de espumantes realizadas em um ano
    ---
    tags:
      - Exportação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as exportações de espumantes realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Espumantes",
                    "ano": 2007,
                    "pais": "Alemanha",
                    "quantidade": 3547,
                    "valor": 10192
                },
                {
                    "categoria": "Espumantes",
                    "ano": 2007,
                    "pais": "Angola",
                    "quantidade": 6293,
                    "valor": 26252
                },
                {
                    "categoria": "Espumantes",
                    "ano": 2007,
                    "pais": "Antigua e Barbuda",
                    "quantidade": 0,
                    "valor": 0
                }            
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return exportacao(ano, EnumCategoria_im_ex.ESPUMANTES)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/exportacao/uvas_frescas', methods=['GET'])
@jwt_required()
def exportacao_uvas_frescas():
    """
    Obter toda lista paises com as exportações de uvas frescas realizadas em um ano
    ---
    tags:
      - Exportação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as exportações de uvas frescas realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Uvas Frescas",
                    "ano": 1985,
                    "pais": "Argélia",
                    "quantidade": 0,
                    "valor": 0
                },
                {
                    "categoria": "Uvas Frescas",
                    "ano": 1985,
                    "pais": "Argentina",
                    "quantidade": 208150,
                    "valor": 125910
                },
                {
                    "categoria": "Uvas Frescas",
                    "ano": 1985,
                    "pais": "Brasil",
                    "quantidade": 0,
                    "valor": 0
                }
            ]   
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return exportacao(ano, EnumCategoria_im_ex.UVASFRESCAS)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

@app.route('/vitibrasil/exportacao/suco_uva', methods=['GET'])
@jwt_required()
def exportacao_suco_uva():
    """
    Obter toda lista paises com as exportações de suco de uva realizadas em um ano
    ---
    tags:
      - Exportação
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Token JWT para autenticação no formato "Bearer <token>"
      - name: ano
        in: query
        type: integer
        required: true
        description: O ano a ser consultado.
    responses:
      200:
        description: Retorna a lista de paises com as exportações de suco de uva realizadas no ano informado.
        examples:
          application/json: |
            [
                {
                    "categoria": "Suco de Uva",
                    "ano": 1989,
                    "pais": "Africa do Sul",
                    "quantidade": 0,
                    "valor": 0
                },
                {
                    "categoria": "Suco de Uva",
                    "ano": 1989,
                    "pais": "Alemanha",
                    "quantidade": 0,
                    "valor": 0
                },
                {
                    "categoria": "Suco de Uva",
                    "ano": 1989,
                    "pais": "Argentina",
                    "quantidade": 1901597,
                    "valor": 1339369
                }
            ]
      400:
        description: Falha na requisição devido à falta de parâmetros obrigatórios.
      401:
        description: Falha de autenticação devido à falta ou invalidez do token JWT.
    """
    try:
        # Obtém o parâmetro 'ano'
        ano = request.args.get('ano', type=int)
        if ano is None:
            return json_response_msg_erro({"error": "O parâmetro 'ano' é obrigatório."}, 400)

        return exportacao(ano, EnumCategoria_im_ex.SUCODEUVA)
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

def exportacao(ano: int, categoria: EnumCategoria_im_ex):
    """
    Obtem lista de exportacoes para um ano e categoria informados.
    """
    try:

        # Busca exportacoes para o ano e categoria (sub_opcao) informados
        exportacoes = siteEmbrapa.obterExportacaoPorAnoCategoria(ano, categoria)

        # Monta a lista de respostas
        retorno = []
        for exportacao in exportacoes:
            retorno.append({
                "categoria": exportacao.categoria.value,
                "ano": exportacao.ano,
                "pais": exportacao.pais.nome,
                "quantidade": exportacao.quantidade,
                "valor": exportacao.valor
            })

        # Retorna usando json.dumps com ensure_ascii=False
        return app.response_class(
            response=json.dumps(retorno, ensure_ascii=False),
            status=200,
            mimetype='application/json')
    except Exception as e:
        return json_response_msg_erro({"error": str(e)}, 500)

if __name__ == '__main__':
    app.run(debug=True)
