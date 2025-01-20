import re
from typing import List

class Categoria:
    """
    Representa a categoria de um produto (e.g. 'Vinho de mesa', 'Suco', 'Espumante').
    
    Atributos:
        nome (str): Nome da categoria.
        produtos (list[Produto]): Lista de produtos que pertencem a esta categoria.
    """
    def __init__(self, nome: str):
        self.nome = nome
        self.produtos = []

    def adicionar_produto(self, produto: 'Produto'):
        """
        Associa um produto a esta categoria.
        """
        if produto not in self.produtos:
            self.produtos.append(produto)


class Produto:
    """
    Representa um produto derivado da uva (p.ex., 'Vinho Tinto', 'Suco Integral').
    
    Atributos:
        nome (str): Nome do produto.
        categoria (Categoria): Referência à categoria à qual o produto pertence.
        produtividades (list[ProdutividadeAnual]): Registros de produtividade anual deste produto.
    """
    def __init__(self, nome: str, categoria: Categoria = None):
        self.nome = nome
        self.categoria = None
        self.produtividades = []

        if categoria:
            self.set_categoria(categoria)

    def set_categoria(self, categoria: Categoria):
        """
        Atribui uma categoria ao produto e registra o produto na lista da categoria.
        """
        self.categoria = categoria
        categoria.adicionar_produto(self)

    def adicionar_produtividade(self, produtividade_anual: 'ProdutividadeAnual'):
        """
        Associa um objeto ProdutividadeAnual a este produto.
        """
        if produtividade_anual not in self.produtividades:
            self.produtividades.append(produtividade_anual)


class ProdutividadeAnual:
    """
    Representa a produtividade de um produto em um determinado ano.
    
    Atributos:
        ano (int): Ano de referência.
        quantidade (int): Quantidade produzida.
        produto (Produto): Referência ao produto associado.
    """
    def __init__(self, ano: int, quantidade: int, produto: Produto = None):
        self.ano = ano
        apenasNumericos = re.sub(r'\D', '', quantidade) # retira caracteres não numéricos
        if apenasNumericos == "":
            self.quantidade = 0
        else:
            self.quantidade = int(apenasNumericos)
        self.produto = None
        if produto:
            self.set_produto(produto)

    def set_produto(self, produto: Produto):
        """
        Associa esta produtividade anual a um produto específico.
        """
        self.produto = produto
        produto.adicionar_produtividade(self)


class RepositorioProdutos:
    """
    Armazena e gerencia a lista de produtos criados no sistema.
    
    Atributos:
        produtos (list[Produto]): Lista de todos os produtos cadastrados.
    """
    def __init__(self):
        self.produtos = []

    def adicionar_produto(self, produto: Produto):
        """
        Adiciona um produto ao repositório, caso ainda não exista.
        """
        if produto not in self.produtos:
            self.produtos.append(produto)

    def remover_produto(self, produto: Produto):
        """
        Remove um produto do repositório, caso exista.
        """
        if produto in self.produtos:
            self.produtos.remove(produto)

    def buscar_produto_por_nome_categoria(self, nome: str, categoria: Categoria) -> Produto:
        """
        Retorna o primeiro produto que corresponda ao nome informado, ou None se não encontrado.
        """
        for p in self.produtos:
            if (p.nome == nome) and (p.categoria == categoria):
                return p
        return None

    def listar_produtos(self) -> list:
        """
        Retorna a lista completa de produtos cadastrados.
        """
        return self.produtos


class RepositorioCategorias:
    """
    Armazena e gerencia a lista de categorias cadastradas no sistema.
    
    Atributos:
        categorias (list[Categoria]): Lista de todas as categorias cadastradas.
    """
    def __init__(self):
        self.categorias = []

    def adicionar_categoria(self, categoria: Categoria):
        """
        Adiciona uma categoria ao repositório, caso ainda não exista.
        """
        if categoria not in self.categorias:
            self.categorias.append(categoria)

    def remover_categoria(self, categoria: Categoria):
        """
        Remove uma categoria do repositório, caso exista.
        """
        if categoria in self.categorias:
            self.categorias.remove(categoria)

    def buscar_categoria_por_nome(self, nome: str) -> Categoria:
        """
        Retorna a primeira categoria que corresponda ao nome informado, ou None se não encontrado.
        """
        for c in self.categorias:
            if c.nome == nome:
                return c
        return None

    def listar_categorias(self) -> list:
        """
        Retorna a lista completa de categorias cadastradas.
        """
        return self.categorias


class RepositorioProdutividadesAnuais:
    """
    Armazena e gerencia a lista de registros de produtividade anual cadastrados no sistema.
    
    Atributos:
        produtividades (list[ProdutividadeAnual]): Lista de todos os registros de produtividade.
    """
    def __init__(self):
        self.produtividades = []

    def adicionar_produtividade(self, produtividade: ProdutividadeAnual):
        """
        Adiciona um registro de produtividade ao repositório, caso ainda não exista.
        """
        if produtividade not in self.produtividades:
            self.produtividades.append(produtividade)

    def remover_produtividade(self, produtividade: ProdutividadeAnual):
        """
        Remove um registro de produtividade do repositório, caso exista.
        """
        if produtividade in self.produtividades:
            self.produtividades.remove(produtividade)

    def buscar_produtividade(self, produto: Produto, ano: int) -> ProdutividadeAnual:
        """
        Retorna a produtividade para determinado produto e ano, ou None se não encontrado.
        """
        for p in self.produtividades:
            if p.produto == produto and p.ano == ano:
                return p
        return None

    def buscar_produtividadesPorAno(self, ano: int) -> List[ProdutividadeAnual]:
        """
        Retorna as produtividades de todos os produtos para determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for p in self.produtividades:
            if p.ano == ano:
                retorno.append(p)
        return retorno

    def buscarProdutividadeTotalDeCategoriaPorAno(self, categoria: Categoria, ano: int) -> int:
        """
        Retorna as produtividades de todos os produtos para determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno: int = 0
        produtividadesDoAno = self.buscar_produtividadesPorAno(ano)
        for p in produtividadesDoAno:
            if p.produto.categoria == categoria:
                retorno = retorno + p.quantidade
        return retorno


    def listar_produtividades(self) -> List[ProdutividadeAnual]:
        """
        Retorna a lista completa de produtividades cadastradas.
        """
        return self.produtividades



