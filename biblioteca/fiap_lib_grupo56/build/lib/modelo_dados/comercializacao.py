import re
from typing import List

class Categoria_com:
    """
    Comercialização - Representa a categoria de um produto ('VINHO DE MESA', 'VINHO FINO DE MESA').
    
    Atributos:
        nome (str): Nome da categoria.
        produtos (list[Produto]): Lista de produtos que pertencem a esta categoria.
    """
    def __init__(self, nome: str):
        self.nome = nome
        self.produtos = []

    def adicionar_produto(self, produto: 'Produto_com'):
        """
        Associa um produto a esta categoria.
        """
        if produto not in self.produtos:
            self.produtos.append(produto)


class Produto_com:
    """
    Comercialização - Representa um produto derivado da uva (p.ex., 'Vinho Tinto', 'Suco Natural Integral').
    
    Atributos:
        nome (str): Nome do produto.
        categoria (Categoria): Referência à categoria à qual o produto pertence.
        comercializacoes (list[ComercializacaoAnual]): Registros de comercializações anuais deste produto.
    """
    def __init__(self, nome: str, categoria: Categoria_com = None):
        self.nome = nome
        self.categoria = None
        self.comercializacoes = []

        if categoria:
            self.set_categoria(categoria)

    def set_categoria(self, categoria: Categoria_com):
        """
        Atribui uma categoria ao produto e registra o produto na lista da categoria.
        """
        self.categoria = categoria
        categoria.adicionar_produto(self)

    def adicionar_comercializacao(self, comercializacao_anual: 'ComercializacaoAnual'):
        """
        Associa um objeto ProdutividadeAnual a este produto.
        """
        if comercializacao_anual not in self.comercializacoes:
            self.comercializacoes.append(comercializacao_anual)


class ComercializacaoAnual:
    """
    Comercialização - Representa a comercialização de um produto em um determinado ano.
    
    Atributos:
        ano (int): Ano de referência.
        quantidade (int): Quantidade produzida.
        produto (Produto): Referência ao produto associado.
    """
    def __init__(self, ano: int, quantidade: int, produto: Produto_com = None):
        self.ano = ano
        apenasNumericos = re.sub(r'\D', '', quantidade) # retira caracteres não numéricos
        if apenasNumericos == "":
            self.quantidade = 0
        else:
            self.quantidade = int(apenasNumericos)
        self.produto = None
        if produto:
            self.set_produto(produto)

    def set_produto(self, produto: Produto_com):
        """
        Associa esta comercializacao anual a um produto específico.
        """
        self.produto = produto
        produto.adicionar_comercializacao(self)


class RepositorioProdutos_com:
    """
    Comercialização - Armazena e gerencia a lista de produtos criados no sistema.
    
    Atributos:
        produtos (list[Produto]): Lista de todos os produtos cadastrados.
    """
    def __init__(self):
        self.produtos = []

    def adicionar_produto(self, produto: Produto_com):
        """
        Adiciona um produto ao repositório, caso ainda não exista.
        """
        if produto not in self.produtos:
            self.produtos.append(produto)

    def remover_produto(self, produto: Produto_com):
        """
        Remove um produto do repositório, caso exista.
        """
        if produto in self.produtos:
            self.produtos.remove(produto)

    def buscar_produto_por_nome_categoria(self, nome: str, categoria: Categoria_com) -> Produto_com:
        """
        Retorna o primeiro produto que corresponda aos parametros informados, ou None se não encontrado.
        """
        for p in self.produtos:
            if (p.nome == nome) and (p.categoria == categoria):
                return p
        return None

    def listar_produtos(self) -> List[Produto_com]:
        """
        Retorna a lista completa de produtos cadastrados.
        """
        return self.produtos


class RepositorioCategorias_com:
    """
    Comercialização - Armazena e gerencia a lista de categorias de produtos comercializados cadastradas no sistema.
    
    Atributos:
        categorias (list[Categoria_prod]): Lista de todas as categorias cadastradas.
    """
    def __init__(self):
        self.categorias = []

    def adicionar_categoria(self, categoria: Categoria_com):
        """
        Adiciona uma categoria ao repositório, caso ainda não exista.
        """
        if categoria not in self.categorias:
            self.categorias.append(categoria)

    def remover_categoria(self, categoria: Categoria_com):
        """
        Remove uma categoria do repositório, caso exista.
        """
        if categoria in self.categorias:
            self.categorias.remove(categoria)

    def buscar_categoria_por_nome(self, nome: str) -> Categoria_com:
        """
        Retorna a primeira categoria que corresponda ao nome informado, ou None se não encontrado.
        """
        for c in self.categorias:
            if c.nome == nome:
                return c
        return None

    def listar_categorias(self) -> List[Categoria_com]:
        """
        Retorna a lista completa de categorias cadastradas.
        """
        return self.categorias


class RepositorioComercializacoesAnuais:
    """
    Comercialização - Armazena e gerencia a lista de registros de comercializacao anual cadastrados no sistema.
    
    Atributos:
        comercializacoes (list[ComercializacaoAnual]): Lista de todos os registros de comercializacao.
    """
    def __init__(self):
        self.comercializacoes = []

    def adicionar_comercializacao(self, comercializacao: ComercializacaoAnual):
        """
        Adiciona um registro de comercialização ao repositório, caso ainda não exista.
        """
        if comercializacao not in self.comercializacoes:
            self.comercializacoes.append(comercializacao)

    def remover_comercializacao(self, comercializacao: ComercializacaoAnual):
        """
        Remove um registro de produtividade do repositório, caso exista.
        """
        if comercializacao in self.comercializacoes:
            self.comercializacoes.remove(comercializacao)

    def buscar_comercializacao(self, produto: Produto_com, ano: int) -> ComercializacaoAnual:
        """
        Retorna a comercializacao para determinado produto e ano, ou None se não encontrado.
        """
        for p in self.comercializacoes:
            if p.produto == produto and p.ano == ano:
                return p
        return None

    def buscar_comercializacoesPorAno(self, ano: int) -> List[ComercializacaoAnual]:
        """
        Retorna as comercializações de todos os produtos para determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for p in self.comercializacoes:
            if p.ano == ano:
                retorno.append(p)
        return retorno

    def buscarComercializacaoTotalDeCategoriaPorAno(self, categoria: Categoria_com, ano: int) -> int:
        """
        Retorna as comercializacoes de todos os produtos da categoria, para determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno: int = 0
        comercializacoesDoAno = self.buscar_comercializacoesPorAno(ano)
        for p in comercializacoesDoAno:
            if p.produto.categoria == categoria:
                retorno = retorno + p.quantidade
        return retorno


    def listar_comercializacoes(self) -> List[ComercializacaoAnual]:
        """
        Retorna a lista completa de produtividades cadastradas.
        """
        return self.comercializacoes



