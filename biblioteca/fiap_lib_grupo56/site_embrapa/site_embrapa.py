import csv
import locale
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from typing import List
from importlib.resources import files
from modelo_dados.producao import Categoria_prod, Produto_prod, ProdutividadeAnual
from modelo_dados.producao import RepositorioCategorias_prod, RepositorioProdutos_prod, RepositorioProdutividadesAnuais
from modelo_dados.processamento import EnumTipoUva_proc, Categoria_proc, Cultivar_proc, ProcessamentoAnual
from modelo_dados.processamento import RepositorioCategorias_proc, RepositorioCultivar_proc, RepositorioProcessamentosAnuais
from modelo_dados.comercializacao import Categoria_com, Produto_com, ComercializacaoAnual
from modelo_dados.comercializacao import RepositorioCategorias_com, RepositorioProdutos_com, RepositorioComercializacoesAnuais
from modelo_dados.importacaoExportacao import EnumCategoria_im_ex, Pais, ImportacaoAnual, ExportacaoAnual
from modelo_dados.importacaoExportacao import RepositorioPaises, RepositorioImportacoesAnuais, RepositorioExportacoesAnuais

class SiteEmbrapa:
    """
    Possui os métodos necessários para se fazer o webscrapping dos dados do site.
    Também gerencia um tipo de cache dos dados para quando o site estiver fora do ar.
    
    """
    def __init__(self):
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.webscrapping = WebscrappingSiteEmbrapa("http://vitibrasil.cnpuv.embrapa.br/index.php")
        self.inicializa_repositorios()

    def inicializa_repositorios(self):
        self.repositorio_categorias_prod = RepositorioCategorias_prod()
        self.repositorio_produtos_prod = RepositorioProdutos_prod()
        self.repositorio_produtividades = RepositorioProdutividadesAnuais()

        self.repositorio_categorias_proc = RepositorioCategorias_proc()
        self.repositorio_cultivares_proc = RepositorioCultivar_proc()
        self.repositorio_processamentos = RepositorioProcessamentosAnuais()

        self.repositorio_categorias_com = RepositorioCategorias_com()
        self.repositorio_produtos_com = RepositorioProdutos_com()
        self.repositorio_comercializacoes = RepositorioComercializacoesAnuais()

        self.repositorio_paises = RepositorioPaises()
        self.repositorio_importacoes = RepositorioImportacoesAnuais()
        self.repositorio_exportacoes = RepositorioExportacoesAnuais()
        
    def carregaRepositoriosFromArquivosCSV(self):
        self.carregaRepoProdutividadeFromArquivoCSV()
        self.carregaRepoComercializacaoFromArquivoCSV()
        self.carregaRepoTodosProcessamentosFromArquivoCSV()
        self.carregaRepoTodasImportacoesFromArquivoCSV()
        self.carregaRepoTodasExportacoesFromArquivoCSV()

    def carregaRepoTodosProcessamentosFromArquivoCSV(self):
        self.repositorio_categorias_proc = RepositorioCategorias_proc()
        self.repositorio_cultivares_proc = RepositorioCultivar_proc()
        self.repositorio_processamentos = RepositorioProcessamentosAnuais()
        self.carregaRepoProcessamentoFromArquivoCSV("ProcessaViniferas.csv", EnumTipoUva_proc.VINIFERAS, ";")
        self.carregaRepoProcessamentoFromArquivoCSV("ProcessaAmericanas.csv", EnumTipoUva_proc.AMERICANASEHIBRIDAS, "\t")
        self.carregaRepoProcessamentoFromArquivoCSV("ProcessaMesa.csv", EnumTipoUva_proc.UVASDEMESA, "\t")
        self.carregaRepoProcessamentoFromArquivoCSV("ProcessaSemclass.csv", EnumTipoUva_proc.SEMCLASSIFICACAO, "\t")

    def carregaRepoTodasImportacoesFromArquivoCSV(self):
        self.repositorio_importacoes = RepositorioImportacoesAnuais()
        self.carregaRepoImportacaoFromArquivoCSV("ImpVinhos.csv", EnumCategoria_im_ex.VINHOSDEMESA, ";")
        self.carregaRepoImportacaoFromArquivoCSV("ImpEspumantes.csv", EnumCategoria_im_ex.ESPUMANTES, ";")
        self.carregaRepoImportacaoFromArquivoCSV("ImpFrescas.csv", EnumCategoria_im_ex.UVASFRESCAS, ";")
        self.carregaRepoImportacaoFromArquivoCSV("ImpPassas.csv", EnumCategoria_im_ex.UVASPASSAS, ";")
        self.carregaRepoImportacaoFromArquivoCSV("ImpSuco.csv", EnumCategoria_im_ex.SUCODEUVA, ";")

    def carregaRepoTodasExportacoesFromArquivoCSV(self):
        self.repositorio_exportacoes = RepositorioExportacoesAnuais()
        self.carregaRepoExportacaoFromArquivoCSV("ExpVinho.csv", EnumCategoria_im_ex.VINHOSDEMESA, ";")
        self.carregaRepoExportacaoFromArquivoCSV("ExpEspumantes.csv", EnumCategoria_im_ex.ESPUMANTES, ";")
        self.carregaRepoExportacaoFromArquivoCSV("ExpUva.csv", EnumCategoria_im_ex.UVASFRESCAS, ";")
        self.carregaRepoExportacaoFromArquivoCSV("ExpSuco.csv", EnumCategoria_im_ex.SUCODEUVA, ";")


    def carregaRepoExportacaoFromArquivoCSV(self, arquivo_csv: str, categoria: EnumCategoria_im_ex, delimitador_arquivo: str):
        caminho_csv = files("site_embrapa.arquivos_csv").joinpath(arquivo_csv)
        with open(caminho_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter = delimitador_arquivo)
            
            # Itera sobre cada linha do arquivo CSV
            for linha in reader:
                nome_pais = linha.get("País")

                if not nome_pais:
                    continue  # Pula linhas com dados incompletos

                pais = self.repositorio_paises.buscar_pais_por_nome(nome_pais)
                if not pais:
                    pais = Pais(nome_pais)
                    self.repositorio_paises.adicionar_pais(pais)
                col_quantidade = 0
                col_valor = 0
                for coluna, valor in linha.items():
                    if coluna[:4].isdigit():  
                        ano = int(coluna[:4])
                        if coluna[4] == 'a':
                            col_quantidade = valor
                        elif coluna[4] == 'b':
                            col_valor = valor
                            exportacao = ExportacaoAnual(ano, col_valor, col_quantidade, categoria, pais)
                            self.repositorio_exportacoes.adicionar_exportacao(exportacao)

    def carregaRepoImportacaoFromArquivoCSV(self, arquivo_csv: str, categoria: EnumCategoria_im_ex, delimitador_arquivo: str):
        caminho_csv = files("site_embrapa.arquivos_csv").joinpath(arquivo_csv)
        with open(caminho_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter = delimitador_arquivo)
            
            # Itera sobre cada linha do arquivo CSV
            for linha in reader:
                nome_pais = linha.get("País")

                if not nome_pais:
                    continue  # Pula linhas com dados incompletos

                pais = self.repositorio_paises.buscar_pais_por_nome(nome_pais)
                if not pais:
                    pais = Pais(nome_pais)
                    self.repositorio_paises.adicionar_pais(pais)
                col_quantidade = 0
                col_valor = 0
                for coluna, valor in linha.items():
                    if coluna[:4].isdigit():  
                        ano = int(coluna[:4])
                        if coluna[4] == 'a':
                            col_quantidade = valor
                        elif coluna[4] == 'b':
                            col_valor = valor
                            importacao = ImportacaoAnual(ano, col_valor, col_quantidade, categoria, pais)
                            self.repositorio_importacoes.adicionar_importacao(importacao)


    def carregaRepoProcessamentoFromArquivoCSV(self, arquivo_csv: str, tipo_uva: EnumTipoUva_proc, delimitador_arquivo: str):
        caminho_csv = files("site_embrapa.arquivos_csv").joinpath(arquivo_csv)
        categoria_atual = None
        with open(caminho_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter = delimitador_arquivo)
            
            # Itera sobre cada linha do arquivo CSV
            for linha in reader:
                nome_categoria = linha.get("control")
                nome_cultivar = linha.get("cultivar")

                if not nome_categoria or not nome_cultivar:
                    continue  # Pula linhas com dados incompletos
                
                if nome_categoria == nome_cultivar:
                    # Verifica se a categoria já existe no repositório
                    categoria_atual = self.repositorio_categorias_proc.buscar_categoria_por_nome(nome_categoria)
                    if not categoria_atual:
                        categoria_atual = Categoria_proc(nome_categoria)
                        self.repositorio_categorias_proc.adicionar_categoria(categoria_atual)
                else:
                    if nome_cultivar == "Sem classificação":
                        categoria_atual = self.repositorio_categorias_proc.buscar_categoria_por_nome(nome_cultivar)
                        if not categoria_atual:
                            categoria_atual = Categoria_proc(nome_cultivar)
                            self.repositorio_categorias_proc.adicionar_categoria(categoria_atual)
                    # Verifica se o cultivar já existe no repositório
                    cultivar = self.repositorio_cultivares_proc.buscar_cultivar_por_nome_categoria_tipo(nome_cultivar, categoria_atual, tipo_uva)
                    if not cultivar:
                        cultivar = Cultivar_proc(nome_cultivar, categoria_atual, tipo_uva)
                        self.repositorio_cultivares_proc.adicionar_cultivar(cultivar)
                    
                    # Cria instâncias de ProdutividadeAnual para os anos disponíveis
                    for coluna, valor in linha.items():
                        if coluna.isdigit():  
                            ano = int(coluna)
                            processamento = ProcessamentoAnual(ano, valor, cultivar)
                            self.repositorio_processamentos.adicionar_processamento(processamento)        


    def carregaRepoProdutividadeFromArquivoCSV(self):
        # caminho_csv = "./arquivos_csv/producao.csv"
        caminho_csv = files("site_embrapa.arquivos_csv").joinpath("producao.csv")
        self.repositorio_categorias_prod = RepositorioCategorias_prod()
        self.repositorio_produtos_prod = RepositorioProdutos_prod()
        self.repositorio_produtividades = RepositorioProdutividadesAnuais()
        categoria_atual = None
        with open(caminho_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Itera sobre cada linha do arquivo CSV
            for linha in reader:
                nome_categoria = linha.get("control")
                nome_produto = linha.get("produto")

                if not nome_categoria or not nome_produto:
                    continue  # Pula linhas com dados incompletos
                
                if nome_categoria == nome_produto:
                    # Verifica se a categoria já existe no repositório
                    categoria_atual = self.repositorio_categorias_prod.buscar_categoria_por_nome(nome_categoria)
                    if not categoria_atual:
                        categoria_atual = Categoria_prod(nome_categoria)
                        self.repositorio_categorias_prod.adicionar_categoria(categoria_atual)
                else:
                    # Verifica se o produto já existe no repositório
                    produto = self.repositorio_produtos_prod.buscar_produto_por_nome_categoria(nome_produto, categoria_atual)
                    if not produto:
                        produto = Produto_prod(nome_produto, categoria_atual)
                        self.repositorio_produtos_prod.adicionar_produto(produto)
                    
                    # Cria instâncias de ProdutividadeAnual para os anos disponíveis
                    for coluna, valor in linha.items():
                        if coluna.isdigit():  
                            ano = int(coluna)
                            produtividade = ProdutividadeAnual(ano, valor, produto)
                            self.repositorio_produtividades.adicionar_produtividade(produtividade)

    def carregaRepoComercializacaoFromArquivoCSV(self):
        # caminho_csv = "./arquivos_csv/comercio.csv"
        caminho_csv = files("site_embrapa.arquivos_csv").joinpath("comercio.csv")
        self.repositorio_categorias_com = RepositorioCategorias_com()
        self.repositorio_produtos_com = RepositorioProdutos_com()
        self.repositorio_comercializacoes = RepositorioComercializacoesAnuais()

        categoria_atual = None
        ultima_linha_foi_categoria = False
        with open(caminho_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Itera sobre cada linha do arquivo CSV
            for linha in reader:
                nome_categoria = linha.get("control").lstrip().rstrip()
                nome_produto = linha.get("Produto").lstrip().rstrip()

                if not nome_categoria or not nome_produto:
                    continue  # Pula linhas com dados incompletos
                
                if nome_categoria == nome_produto:
                    if ultima_linha_foi_categoria:
                        produto = self.repositorio_produtos_com.buscar_produto_por_nome_categoria(categoria_atual.nome, categoria_atual)
                        if not produto:
                            produto = Produto_com(categoria_atual.nome, categoria_atual)
                            self.repositorio_produtos_com.adicionar_produto(produto)
                        # Cria instâncias de ProdutividadeAnual para os anos disponíveis
                        for coluna, valor in linha_anterior.items():
                            if coluna.isdigit():  
                                ano = int(coluna)
                                comercializacao = ComercializacaoAnual(ano, valor, produto)
                                self.repositorio_comercializacoes.adicionar_comercializacao(comercializacao)
                    # Verifica se a categoria já existe no repositório
                    categoria_atual = self.repositorio_categorias_com.buscar_categoria_por_nome(nome_categoria)
                    if not categoria_atual:
                        categoria_atual = Categoria_com(nome_categoria)
                        self.repositorio_categorias_com.adicionar_categoria(categoria_atual)
                    ultima_linha_foi_categoria = True
                    linha_anterior = linha
                else:
                    # Verifica se o produto já existe no repositório
                    ultima_linha_foi_categoria = False
                    produto = self.repositorio_produtos_com.buscar_produto_por_nome_categoria(nome_produto, categoria_atual)
                    if not produto:
                        produto = Produto_com(nome_produto, categoria_atual)
                        self.repositorio_produtos_com.adicionar_produto(produto)
                    
                    # Cria instâncias de ProdutividadeAnual para os anos disponíveis
                    for coluna, valor in linha.items():
                        if coluna.isdigit():  
                            ano = int(coluna)
                            comercializacao = ComercializacaoAnual(ano, valor, produto)
                            self.repositorio_comercializacoes.adicionar_comercializacao(comercializacao)

    def obterProducoesPorAno(self, ano: int) -> List[ProdutividadeAnual]:
        """
        Recupera do site da embrapa, toda a produção de um ano.  Se o site estiver offline, retornará a produção de cache obtido previamente.
        
        """
        produtividadesEmCache = self.repositorio_produtividades.buscar_produtividadesPorAno(ano)
        if len(produtividadesEmCache) == 0:
            produtividadesEmCache = self.carregaRepoProdutividadePorAnoFromWebscrapping(ano)
        return produtividadesEmCache

    def obterProducaoTotalDeCategoriaPorAno(self, nomeCategoria: str, ano: int) -> int:
        """
        Recupera do site da embrapa, toda da produção de uma categoria em um ano.  Se o site estiver offline, retornará a produção de cache obtido previamente.
        
        """
        produtividadesEmCache = self.repositorio_produtividades.buscar_produtividadesPorAno(ano)
        if len(produtividadesEmCache) == 0:
            produtividadesEmCache = self.carregaRepoProdutividadePorAnoFromWebscrapping(ano)

        categoria = self.repositorio_categorias_prod.buscar_categoria_por_nome(nomeCategoria)
        if categoria == None:
            return 0
        
        producao_total_categoria = self.repositorio_produtividades.buscarProdutividadeTotalDeCategoriaPorAno(categoria, ano)
        return producao_total_categoria

    def obterProcessamentoPorAnoTipoUva(self, ano: int, tipo_uva: EnumTipoUva_proc) -> List[ProcessamentoAnual]:
        """
        Recupera do site da embrapa, toda o processamento de um ano e tipo uva.  Se o site estiver offline, retornará o processamento de cache obtido previamente.
        
        """
        processamentoEmCache = self.repositorio_processamentos.buscar_processamentosPorAno_TipoUva(ano, tipo_uva)
        if len(processamentoEmCache) == 0:
            processamentoEmCache = self.carregaRepoProcessamentoPorAnoTipoUvaFromWebscrapping(ano, tipo_uva)
        return processamentoEmCache

    def obterProcessamentoTotalDeCategoriaPorAnoTipoUva(self, nomeCategoria: str, ano: int, tipo_uva: EnumTipoUva_proc) -> int:
        """
        Recupera do site da embrapa, toda da processamento de uma categoria em um ano, por TipoUva.  Se o site estiver offline, retornará o processamento de cache obtido previamente.
        
        """
        processamentoEmCache = self.repositorio_processamentos.buscar_processamentosPorAno_TipoUva(ano, tipo_uva)
        if len(processamentoEmCache) == 0:
            processamentoEmCache = self.carregaRepoProcessamentoPorAnoTipoUvaFromWebscrapping(ano, tipo_uva)

        categoria = self.repositorio_categorias_proc.buscar_categoria_por_nome(nomeCategoria)
        if categoria == None:
            return 0
        
        processamento_total_categoria = self.repositorio_processamentos.buscarProcessamentoTotalDeCategoriaPorAno_TipoUva(categoria, ano, tipo_uva)
        return processamento_total_categoria

    def obterComercializacoesPorAno(self, ano: int) -> List[ComercializacaoAnual]:
        """
        Recupera do site da embrapa, toda a comercialização de um ano.  Se o site estiver offline, retornará a produção de cache obtido previamente.
        
        """
        comercializacoesEmCache = self.repositorio_comercializacoes.buscar_comercializacoesPorAno(ano)
        if len(comercializacoesEmCache) == 0:
            comercializacoesEmCache = self.carregaRepoComercializacaoPorAnoFromWebscrapping(ano)
        return comercializacoesEmCache

    def obterComercializacaoTotalDeCategoriaPorAno(self, nomeCategoria: str, ano: int) -> int:
        """
        Recupera do site da embrapa, toda da comercialização de uma categoria em um ano.  Se o site estiver offline, retornará a produção de cache obtido previamente.
        
        """
        comercializacoesEmCache = self.repositorio_comercializacoes.buscar_comercializacoesPorAno(ano)
        if len(comercializacoesEmCache) == 0:
            comercializacoesEmCache = self.carregaRepoComercializacaoPorAnoFromWebscrapping(ano)

        categoria = self.repositorio_categorias_com.buscar_categoria_por_nome(nomeCategoria)
        if categoria == None:
            return 0
        
        comercializacao_total_categoria = self.repositorio_comercializacoes.buscarComercializacaoTotalDeCategoriaPorAno(categoria, ano)
        return comercializacao_total_categoria

    def obterImportacaoPorAnoCategoria(self, ano: int, categoria: EnumCategoria_im_ex) -> List[ImportacaoAnual]:
        """
        Recupera do site da embrapa, toda importacao de um ano e de uma categoria específica.  Se o site estiver offline, retornará o processamento de cache obtido previamente.
        
        """
        importacaoEmCache = self.repositorio_importacoes.buscar_importacoesPorAnoCategoria(ano, categoria)
        if len(importacaoEmCache) == 0:
            importacaoEmCache = self.carregaRepoImportacaoPorAnoCategoriaFromWebscrapping(ano, categoria)
        return importacaoEmCache

    def obterExportacaoPorAnoCategoria(self, ano: int, categoria: EnumCategoria_im_ex) -> List[ExportacaoAnual]:
        """
        Recupera do site da embrapa, toda exportacao de um ano e de uma categoria específica.  Se o site estiver offline, retornará o processamento de cache obtido previamente.
        
        """
        if categoria == EnumCategoria_im_ex.UVASPASSAS:
            raise Exception(f"Categoria [{categoria} não existente para Exportações.]")
        exportacaoEmCache = self.repositorio_exportacoes.buscar_exportacoesPorAnoCategoria(ano, categoria)
        if len(exportacaoEmCache) == 0:
            exportacaoEmCache = self.carregaRepoExportacaoPorAnoCategoriaFromWebscrapping(ano, categoria)
        return exportacaoEmCache

    def carregaRepoProdutividadePorAnoFromWebscrapping(self, ano: int) -> List[ProdutividadeAnual]:
        tags_tr_do_tbody = self.webscrapping.obterProducaoPorAno(ano)

        categoriaAtual: Categoria_prod = None
        produtoAtual: Produto_prod = None
        produtividadeAnualAtual: ProdutividadeAnual = None

        """
            Carrega self.repositorio_produtos_prod, self.repositorio_categorias_prod e self.repositorio_produtividades com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 2):
                if(tags_td[0].get_attribute("class") == "tb_item"):
                    nomeCategoria = tags_td[0].text
                    categoriaAtual = self.repositorio_categorias_prod.buscar_categoria_por_nome(nomeCategoria)
                    if categoriaAtual == None:
                        categoriaAtual = Categoria_prod(nomeCategoria)
                        self.repositorio_categorias_prod.adicionar_categoria(categoriaAtual)
                elif(tags_td[0].get_attribute("class") == "tb_subitem"):
                    nomeProduto = tags_td[0].text
                    produtoAtual = self.repositorio_produtos_prod.buscar_produto_por_nome_categoria(nomeProduto, categoriaAtual)
                    if produtoAtual == None:
                        produtoAtual = Produto_prod(nomeProduto, categoriaAtual)
                        self.repositorio_produtos_prod.adicionar_produto(produtoAtual)
                    produtividadeAnualAtual = ProdutividadeAnual(ano, tags_td[1].text, produtoAtual)
                    self.repositorio_produtividades.adicionar_produtividade(produtividadeAnualAtual)
        return self.repositorio_produtividades.buscar_produtividadesPorAno(ano)

    def carregaRepoProcessamentoPorAnoTipoUvaFromWebscrapping(self, ano: int, tipo_uva: EnumTipoUva_proc) -> List[ProcessamentoAnual]:
        tags_tr_do_tbody = self.webscrapping.obterProcessamentoPorAno_TipoUva(ano, tipo_uva)

        categoriaAtual: Categoria_proc = None
        cultivarAtual: Cultivar_proc = None
        processamentoAnualAtual: ProcessamentoAnual = None

        """
            Carrega self.repositorio_produtos_proc, self.repositorio_categorias_proc e self.repositorio_processamentos com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 2):
                if(tags_td[0].get_attribute("class") == "tb_item"):
                    nomeCategoria = tags_td[0].text
                    categoriaAtual = self.repositorio_categorias_proc.buscar_categoria_por_nome(nomeCategoria)
                    if categoriaAtual == None:
                        categoriaAtual = Categoria_proc(nomeCategoria)
                        self.repositorio_categorias_proc.adicionar_categoria(categoriaAtual)
                    # no caso de SEMCLASSIFICACAO, o site não possui tb_subitem, apresentado o total de produção na própria categoria
                    # neste caso, estamos criando um processamento com o total processado para refletir nas consultas de totalização
                    if tipo_uva == EnumTipoUva_proc.SEMCLASSIFICACAO:
                        nomeCultivar = nomeCategoria
                        cultivarAtual = self.repositorio_cultivares_proc.buscar_cultivar_por_nome_categoria_tipo(nomeCultivar, categoriaAtual, tipo_uva)
                        if cultivarAtual == None:
                            cultivarAtual = Cultivar_proc(nomeCultivar, categoriaAtual, tipo_uva)
                            self.repositorio_cultivares_proc.adicionar_cultivar(cultivarAtual)
                        processamentoAnualAtual = ProcessamentoAnual(ano, tags_td[1].text, cultivarAtual)
                        self.repositorio_processamentos.adicionar_processamento(processamentoAnualAtual)
                elif(tags_td[0].get_attribute("class") == "tb_subitem"):
                    nomeCultivar = tags_td[0].text
                    cultivarAtual = self.repositorio_cultivares_proc.buscar_cultivar_por_nome_categoria_tipo(nomeCultivar, categoriaAtual, tipo_uva)
                    if cultivarAtual == None:
                        cultivarAtual = Cultivar_proc(nomeCultivar, categoriaAtual, tipo_uva)
                        self.repositorio_cultivares_proc.adicionar_cultivar(cultivarAtual)
                    processamentoAnualAtual = ProcessamentoAnual(ano, tags_td[1].text, cultivarAtual)
                    self.repositorio_processamentos.adicionar_processamento(processamentoAnualAtual)
        return self.repositorio_processamentos.buscar_processamentosPorAno_TipoUva(ano, tipo_uva)

    def carregaRepoComercializacaoPorAnoFromWebscrapping(self, ano: int) -> List[ProdutividadeAnual]:
        tags_tr_do_tbody = self.webscrapping.obterComercializacaoPorAno(ano)

        categoriaAtual: Categoria_prod = None
        produtoAtual: Produto_prod = None
        comercializacaoAnualAtual: ComercializacaoAnual = None
        ultima_tag_foi_categoria: bool = False

        """
            Carrega self.repositorio_produtos_com, self.repositorio_categorias_com e self.repositorio_comercializacoes com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 2):
                if tags_td[0].get_attribute("class") == "tb_item":
                    if ultima_tag_foi_categoria == True:
                        # variáveis nomeCategoria e categoriaAtual estão com valores da linha anterior(linha de categoria que não tem produtos listados abaixo)
                        nomeProduto = nomeCategoria 
                        produtoAtual = self.repositorio_produtos_com.buscar_produto_por_nome_categoria(nomeProduto, categoriaAtual)
                        if produtoAtual == None:
                            produtoAtual = Produto_com(nomeProduto, categoriaAtual)
                            self.repositorio_produtos_com.adicionar_produto(produtoAtual)
                        comercializacaoAnualAtual = ComercializacaoAnual(ano, quantidadeCategoria, produtoAtual) # quantidadeCategoria foi setado na linha de categoria anterior.  No loop anterior do for.
                        self.repositorio_comercializacoes.adicionar_comercializacao(comercializacaoAnualAtual)
                    # processa os dados da linha atual (tag_tr) do tbody do site.  Linha da categoria atual
                    nomeCategoria = tags_td[0].text
                    quantidadeCategoria = tags_td[1].text
                    categoriaAtual = self.repositorio_categorias_com.buscar_categoria_por_nome(nomeCategoria)
                    if categoriaAtual == None:
                        categoriaAtual = Categoria_com(nomeCategoria)
                        self.repositorio_categorias_com.adicionar_categoria(categoriaAtual)
                    ultima_tag_foi_categoria = True
                elif(tags_td[0].get_attribute("class") == "tb_subitem"):
                    nomeProduto = tags_td[0].text
                    produtoAtual = self.repositorio_produtos_com.buscar_produto_por_nome_categoria(nomeProduto, categoriaAtual)
                    if produtoAtual == None:
                        produtoAtual = Produto_com(nomeProduto, categoriaAtual)
                        self.repositorio_produtos_com.adicionar_produto(produtoAtual)
                    comercializacaoAnualAtual = ComercializacaoAnual(ano, tags_td[1].text, produtoAtual)
                    self.repositorio_comercializacoes.adicionar_comercializacao(comercializacaoAnualAtual)
                    ultima_tag_foi_categoria = False
        return self.repositorio_comercializacoes.buscar_comercializacoesPorAno(ano)

    def carregaRepoImportacaoPorAnoCategoriaFromWebscrapping(self, ano: int, categoria: EnumCategoria_im_ex) -> List[ImportacaoAnual]:
        tags_tr_do_tbody = self.webscrapping.obterImportacaoPorAno_categoria(ano, categoria)

        paisAtual: Pais = None
        importacaoAnualAtual: ImportacaoAnual = None

        """
            Carrega self.repositorio_importacoes, self.repositorio_categorias_im_ex e self.repositorio_paises com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 3):
                nomePais = tags_td[0].text
                quantidadeAtual = tags_td[1].text
                valorAtual = tags_td[2].text
                paisAtual = self.repositorio_paises.buscar_pais_por_nome(nomePais)
                if paisAtual == None:
                    paisAtual = Pais(nomePais)
                    self.repositorio_paises.adicionar_pais(paisAtual)
                importacaoAnualAtual = ImportacaoAnual(ano, valorAtual, quantidadeAtual, categoria, paisAtual)
                self.repositorio_importacoes.adicionar_importacao(importacaoAnualAtual)
        return self.repositorio_importacoes.buscar_importacoesPorAnoCategoria(ano, categoria)

    def carregaRepoExportacaoPorAnoCategoriaFromWebscrapping(self, ano: int, categoria: EnumCategoria_im_ex) -> List[ExportacaoAnual]:
        tags_tr_do_tbody = self.webscrapping.obterExportacaoPorAno_categoria(ano, categoria)

        paisAtual: Pais = None
        exportacaoAnualAtual: ExportacaoAnual = None

        """
            Carrega self.repositorio_importacoes, self.repositorio_categorias_im_ex e self.repositorio_paises com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 3):
                nomePais = tags_td[0].text
                quantidadeAtual = tags_td[1].text
                valorAtual = tags_td[2].text
                paisAtual = self.repositorio_paises.buscar_pais_por_nome(nomePais)
                if paisAtual == None:
                    paisAtual = Pais(nomePais)
                    self.repositorio_paises.adicionar_pais(paisAtual)
                exportacaoAnualAtual = ExportacaoAnual(ano, valorAtual, quantidadeAtual, categoria, paisAtual)
                self.repositorio_exportacoes.adicionar_exportacao(exportacaoAnualAtual)
        return self.repositorio_exportacoes.buscar_exportacoesPorAnoCategoria(ano, categoria)

class WebscrappingSiteEmbrapa:
    """
    Realiza o webscrapping na página especifica do site, de acordo com o método utilizado. (Producao, Processamento etc...)

    """
    def __init__(self, urlBase: str):
        self.UrlBase = urlBase
                # Defina as opções do navegador
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        # Adiciona o modo headless
        # chrome_options.add_argument("--headless")
        # (Opcional) Evita possíveis erros de hardware/gpu
        # chrome_options.add_argument("--disable-gpu")

        # O webdriver_manager cuida de baixar a versão correta do ChromeDriver
        self.driverChrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def obterProducaoPorAno(self, ano: int) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        url = f"{self.UrlBase}?ano={ano}&opcao=opt_02" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno

    def obterProcessamentoPorAno_TipoUva(self, ano: int, tipo_uva: EnumTipoUva_proc) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        if tipo_uva == EnumTipoUva_proc.VINIFERAS:
            subopcao_tipouva = "subopt_01"
        elif tipo_uva == EnumTipoUva_proc.AMERICANASEHIBRIDAS:
            subopcao_tipouva = "subopt_02"
        elif tipo_uva == EnumTipoUva_proc.UVASDEMESA:
            subopcao_tipouva = "subopt_03"
        elif tipo_uva == EnumTipoUva_proc.SEMCLASSIFICACAO:
            subopcao_tipouva = "subopt_04"
        else:
            subopcao_tipouva = "subopt_04"

        url = f"{self.UrlBase}?ano={ano}&opcao=opt_03&subopcao={subopcao_tipouva}" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno

    def obterComercializacaoPorAno(self, ano: int) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        url = f"{self.UrlBase}?ano={ano}&opcao=opt_04" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno

    def obterImportacaoPorAno_categoria(self, ano: int, categoria: EnumCategoria_im_ex) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        if categoria == EnumCategoria_im_ex.VINHOSDEMESA:
            subopcao_categoria = "subopt_01"
        elif categoria == EnumCategoria_im_ex.ESPUMANTES:
            subopcao_categoria = "subopt_02"
        elif categoria == EnumCategoria_im_ex.UVASFRESCAS:
            subopcao_categoria = "subopt_03"
        elif categoria == EnumCategoria_im_ex.UVASPASSAS:
            subopcao_categoria = "subopt_04"
        elif categoria == EnumCategoria_im_ex.SUCODEUVA:
            subopcao_categoria = "subopt_05"
        else:
            subopcao_categoria = "subopt_99"

        url = f"{self.UrlBase}?ano={ano}&opcao=opt_05&subopcao={subopcao_categoria}" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno

    def obterExportacaoPorAno_categoria(self, ano: int, categoria: EnumCategoria_im_ex) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        if categoria == EnumCategoria_im_ex.VINHOSDEMESA:
            subopcao_categoria = "subopt_01"
        elif categoria == EnumCategoria_im_ex.ESPUMANTES:
            subopcao_categoria = "subopt_02"
        elif categoria == EnumCategoria_im_ex.UVASFRESCAS:
            subopcao_categoria = "subopt_03"
        elif categoria == EnumCategoria_im_ex.SUCODEUVA:
            subopcao_categoria = "subopt_04"
        else:
            subopcao_categoria = "subopt_99"

        url = f"{self.UrlBase}?ano={ano}&opcao=opt_06&subopcao={subopcao_categoria}" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno

    def obterElementosTR(self, url: str, xpath_tbody: str) -> list:
        """
        Abre a página da url e obtem lista de WebElement

        """
        # Abre a página no navegador
        self.driverChrome.get(url)

        # Encontra todos os elementos <a> que têm links
        # link_elements = driver.find_elements('tag name', 'a')

        tags_tr_do_tbody = self.driverChrome.find_elements(By.XPATH, xpath_tbody)

        return tags_tr_do_tbody
