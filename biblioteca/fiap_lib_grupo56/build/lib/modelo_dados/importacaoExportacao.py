import re
from typing import List
from enum import Enum

class EnumCategoria_im_ex(Enum):
    VINHOSDEMESA = "Vinhos de Mesa"
    ESPUMANTES = "Espumantes"
    UVASFRESCAS = "Uvas Frescas"
    UVASPASSAS = "Uvas Passas"
    SUCODEUVA = "Suco de Uva"

class Pais:
    """
    Importação e Exportação - Representa o País com o qual se realizou algum negócio (importação ou exportação)
    
    Atributos:
        nome (str): Nome da categoria.
        importacoes (list[ImportacaoAnual]): Lista de importações anuais realizadas deste Pais
    """
    def __init__(self, nome: str):
        self.nome = nome
        self.importacoes = []
        self.exportacoes = []

    def adicionar_importacao(self, importacao: 'ImportacaoAnual'):
        """
        Associa/registra um importação a este Pais.
        """
        if importacao not in self.importacoes:
            self.importacoes.append(importacao)

    def adicionar_exportacao(self, exportacao: 'ExportacaoAnual'):
        """
        Associa/registra um exportação a este país
        """
        if exportacao not in self.exportacoes:
            self.exportacoes.append(exportacao)


class ImportacaoAnual:
    """
    Importação e Exportação - Representa um registro de importação anual de uma categoria de produtos
    
    Atributos:
        Ano (int): Ano da importação
        valor (int): Valor em US$
        quantidade (int): Quantidade em Kg
        categoria (EnumCategoria_im_ex): Referência à categoria à qual a importação se refere
        pais (Pais): Referência ao Pais de qual foi realizada a importação
        
    """
    def __init__(self, ano: int, valor: int, quantidade: int, categoria: EnumCategoria_im_ex, pais: Pais = None):
        self.ano = ano
        self.valor = self.filtra_valor_int(valor)
        self.quantidade = self.filtra_valor_int(quantidade)
        self.categoria = categoria
        self.Pais = None

        if pais:
            self.set_pais(pais)

    def filtra_valor_int(self, valor: int) -> int:
        apenasNumericos = re.sub(r'\D', '', valor) # retira caracteres não numéricos
        if apenasNumericos == "":
            return  0
        return int(apenasNumericos)

    def set_pais(self, pais: Pais):
        """
        Atribui um pais ao registro de importação anual e registra a importação na lista de importações do pais.
        """
        self.pais = pais
        pais.adicionar_importacao(self)

class ExportacaoAnual:
    """
    Importação e Exportação - Representa um registro de exportação anual de uma categoria de produtos
    
    Atributos:
        Ano (int): Ano da exportação
        valor (int): Valor em US$
        quantidade (int): Quantidade em Kg
        categoria (EnumCategoria_im_ex): Referência à categoria à qual a exportação se refere
        pais (Pais): Referência ao Pais de qual foi realizada a exportação
        
    """
    def __init__(self, ano: int, valor: int, quantidade: int, categoria: EnumCategoria_im_ex = None, pais: Pais = None):
        self.ano = ano
        self.valor = self.filtra_valor_int(valor)
        self.quantidade = self.filtra_valor_int(quantidade)
        self.categoria = categoria
        self.Pais = None

        if pais:
            self.set_pais(pais)

    def filtra_valor_int(self, valor: int) -> int:
        apenasNumericos = re.sub(r'\D', '', valor) # retira caracteres não numéricos
        if apenasNumericos == "":
            return  0
        return int(apenasNumericos)

    def set_pais(self, pais: Pais):
        """
        Atribui um pais ao registro de exportação anual e registra a exportação na lista de exportações do pais.
        """
        self.pais = pais
        pais.adicionar_exportacao(self)

class RepositorioPaises:
    """
    Importação e Exportação - Armazena e gerencia a lista de paises criados no sistema.
    
    Atributos:
        paises (list[Pais]): Lista de todos os paises cadastrados.
    """
    def __init__(self):
        self.paises = []

    def adicionar_pais(self, pais: Pais):
        """
        Adiciona um pais ao repositório, caso ainda não exista.
        """
        if pais not in self.paises:
            self.paises.append(pais)

    def remover_pais(self, pais: Pais):
        """
        Remove um pais do repositório, caso exista.
        """
        if pais in self.paises:
            self.paises.remove(pais)

    def buscar_pais_por_nome(self, nome: str) -> Pais:
        """
        Retorna o primeiro Pais com o Nome informado, ou NONE se não encontrado.
        """
        for p in self.paises:
            if p.nome == nome:
                return p
        return None

    def listar_paises(self) -> List[Pais]:
        """
        Retorna a lista completa de paises cadastrados.
        """
        return self.paises

class RepositorioImportacoesAnuais:
    """
    Importação e Exportação - Armazena e gerencia a lista de registros de importação anual cadastrados no sistema.
    
    Atributos:
        importacoes (list[ImportacaoAnual]): Lista de todos os registros de importacao.
    """
    def __init__(self):
        self.importacoes = []

    def adicionar_importacao(self, importacao: ImportacaoAnual):
        """
        Adiciona um registro de importacao ao repositório, caso ainda não exista.
        """
        if importacao not in self.importacoes:
            self.importacoes.append(importacao)

    def remover_importacao(self, importacao: ImportacaoAnual):
        """
        Remove um registro de importacao do repositório, caso exista.
        """
        if importacao in self.importacoes:
            self.importacoes.remove(importacao)

    def buscar_importacao(self, categoria: EnumCategoria_im_ex, ano: int, pais: Pais) -> ImportacaoAnual:
        """
        Retorna a importação referente a determinada categoria ano e pais, ou None se não encontrado.
        """
        for i in self.importacoes:
            if i.categoria == categoria and i.ano == ano and i.pais == pais:
                return i
        return None

    def buscar_importacoesPorAno(self, ano: int) -> List[ImportacaoAnual]:
        """
        Retorna as importacoes de todos as categorias para determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for i in self.importacoes:
            if i.ano == ano:
                retorno.append(i)
        return retorno

    def buscar_importacoesPorCategoria(self, categoria: EnumCategoria_im_ex) -> List[ImportacaoAnual]:
        """
        Retorna as importacoes de uma determinada categoria, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for i in self.importacoes:
            if i.categoria == categoria:
                retorno.append(i)
        return retorno

    def buscar_importacoesPorAnoCategoria(self, ano: int, categoria: EnumCategoria_im_ex) -> List[ImportacaoAnual]:
        """
        Retorna as importacoes de uma determinada categoria em um determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for i in self.importacoes:
            if i.categoria == categoria and i.ano == ano:
                retorno.append(i)
        return retorno

    def listar_importacoes(self) -> List[ImportacaoAnual]:
        """
        Retorna a lista completa de importações cadastradas.
        """
        return self.importacoes

class RepositorioExportacoesAnuais:
    """
    Importação e Exportação - Armazena e gerencia a lista de registros de exportação anual cadastrados no sistema.
    
    Atributos:
        exportacoes (list[ExportacaoAnual]): Lista de todos os registros de exportacao.
    """
    def __init__(self):
        self.exportacoes = []

    def adicionar_exportacao(self, exportacao: ExportacaoAnual):
        """
        Adiciona um registro de exportação ao repositório, caso ainda não exista.
        """
        if exportacao not in self.exportacoes:
            self.exportacoes.append(exportacao)

    def remover_exportacao(self, exportacao: ExportacaoAnual):
        """
        Remove um registro de exportação do repositório, caso exista.
        """
        if exportacao in self.exportacoes:
            self.exportacoes.remove(exportacao)

    def buscar_exportacao(self, categoria: EnumCategoria_im_ex, ano: int, pais: Pais) -> ExportacaoAnual:
        """
        Retorna a exportação referente a determinada categoria, ano e pais, ou None se não encontrado.
        """
        for i in self.exportacoes:
            if i.categoria == categoria and i.ano == ano and i.pais == pais:
                return i
        return None

    def buscar_exportacoesPorAno(self, ano: int) -> List[ExportacaoAnual]:
        """
        Retorna as exportacoes de todos as categorias para determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for i in self.exportacoes:
            if i.ano == ano:
                retorno.append(i)
        return retorno

    def buscar_exportacoesPorCategoria(self, categoria: EnumCategoria_im_ex) -> List[ExportacaoAnual]:
        """
        Retorna as exportacoes de todos as categorias de uma determinada categoria, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for i in self.exportacoes:
            if i.categoria == categoria:
                retorno.append(i)
        return retorno

    def buscar_exportacoesPorAnoCategoria(self, ano: int, categoria: EnumCategoria_im_ex) -> List[ExportacaoAnual]:
        """
        Retorna as exportacoes de uma determinada categoria em um determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for i in self.exportacoes:
            if i.categoria == categoria and i.ano == ano:
                retorno.append(i)
        return retorno

    def listar_exportacoes(self) -> List[ExportacaoAnual]:
        """
        Retorna a lista completa de exportações cadastradas.
        """
        return self.exportacoes





