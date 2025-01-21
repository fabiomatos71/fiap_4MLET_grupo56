import re
from enum import Enum
from typing import List

class Categoria_proc:
    """
    Processamento - Representa a categoria de um cultivar ('TINTAS', 'BRANCAS E ROSADAS').
    
    Atributos:
        nome (str): Nome da categoria.
        cultivares (list[Cultivar_proc]): Lista de cultivares que pertencem a esta categoria.
    """
    def __init__(self, nome: str):
        self.nome = nome
        self.cultivares = []

    def adicionar_cultivar(self, cultivar: 'Cultivar_proc'):
        """
        Associa um cultivar a esta categoria.
        """
        if cultivar not in self.cultivares:
            self.cultivares.append(cultivar)
            
class EnumTipoUva_proc(Enum):
    VINIFERAS = "Viniferas"
    AMERICANASEHIBRIDAS = "Americanas e Hibridas"
    UVASDEMESA = "Uvas de Mesa"
    SEMCLASSIFICACAO = "Sem Classificacao"

class Cultivar_proc:
    """
    Processamento - Representa um cultivar ou espécie de uva  (p.ex., 'Carmenere', 'Malbec').
    
    Atributos:
        nome (str): Nome do cultivar.
        categoria (Categoria): Referência à categoria à qual o cultivar pertence.
        processamentos (list[ProcessamentoAnual]): Registros de processaemnto anual deste cultivar.
    """
    def __init__(self, nome: str, categoria: Categoria_proc = None, tipo_uva: EnumTipoUva_proc = None):
        self.nome = nome
        self.categoria = None
        self.TipoUva = tipo_uva
        self.processamentos = []

        if categoria:
            self.set_categoria(categoria)

        if tipo_uva == None:
            self.TipoUva = EnumTipoUva_proc.SEMCLASSIFICACAO

    def set_categoria(self, categoria: Categoria_proc):
        """
        Atribui uma categoria ao cultivar e registra o cultivar na lista da categoria.
        """
        self.categoria = categoria
        categoria.adicionar_cultivar(self)

    def adicionar_processamento(self, processamento_anual: 'ProcessamentoAnual'):
        """
        Associa um objeto ProcessamentoAnual a este cultivar.
        """
        if processamento_anual not in self.processamentos:
            self.processamentos.append(processamento_anual)

class ProcessamentoAnual:
    """
    Processamento - Representa o registro de processamento de um cultivar em um determinado ano.
    
    Atributos:
        ano (int): Ano de referência.
        quantidade (int): Quantidade processada.
        cultivar (Cultivar_proc): Referência ao cultivar associado.
    """
    def __init__(self, ano: int, quantidade: int, cultivar: Cultivar_proc = None):
        self.ano = ano
        self.quantidade = self.filtra_valor_int(quantidade)
        self.cultivar = None
        if cultivar:
            self.set_cultivar(cultivar)

    def set_cultivar(self, cultivar: Cultivar_proc):
        """
        Associa este processamento anual a um cultivar específico.
        """
        self.cultivar = cultivar
        cultivar.adicionar_processamento(self)

    def filtra_valor_int(self, valor: int) -> int:
        apenasNumericos = re.sub(r'\D', '', valor) # retira caracteres não numéricos
        if apenasNumericos == "":
            return  0
        return int(apenasNumericos)



class RepositorioCultivar_proc:
    """
    Processamento - Armazena e gerencia a lista de cultivares criados no sistema.
    
    Atributos:
        cultivares (list[Cultivar_proc]): Lista de todos os cultivares cadastrados.
    """
    def __init__(self):
        self.cultivares = []

    def adicionar_cultivar(self, cultivar: Cultivar_proc):
        """
        Adiciona um cultivar ao repositório, caso ainda não exista.
        """
        if cultivar not in self.cultivares:
            self.cultivares.append(cultivar)

    def remover_cultivar(self, cultivar: Cultivar_proc):
        """
        Remove um cultivar do repositório, caso exista.
        """
        if cultivar in self.cultivares:
            self.cultivares.remove(cultivar)

    def buscar_cultivar_por_nome_categoria_tipo(self, nome: str, categoria: Categoria_proc, tipo_uva: EnumTipoUva_proc) -> Cultivar_proc:
        """
        Retorna o primeiro cultivar que corresponda aos parâmetros informados, ou None se não encontrado.
        """
        for p in self.cultivares:
            if (p.nome == nome) and (p.categoria == categoria) and (p.TipoUva == tipo_uva):
                return p
        return None

    def listar_cultivares(self) -> List[Cultivar_proc]:
        """
        Retorna a lista completa de cultivares cadastrados.
        """
        return self.cultivares

class RepositorioCategorias_proc:
    """
    Processamento - Armazena e gerencia a lista de categorias de processamento cadastradas no sistema.
    
    Atributos:
        categorias (list[Categoria_proc]): Lista de todas as categorias cadastradas.
    """
    def __init__(self):
        self.categorias = []

    def adicionar_categoria(self, categoria: Categoria_proc):
        """
        Adiciona uma categoria ao repositório, caso ainda não exista.
        """
        if categoria not in self.categorias:
            self.categorias.append(categoria)

    def remover_categoria(self, categoria: Categoria_proc):
        """
        Remove uma categoria do repositório, caso exista.
        """
        if categoria in self.categorias:
            self.categorias.remove(categoria)

    def buscar_categoria_por_nome(self, nome: str) -> Categoria_proc:
        """
        Retorna a primeira categoria que corresponda ao nome informado, ou None se não encontrado.
        """
        for c in self.categorias:
            if c.nome == nome:
                return c
        return None

    def listar_categorias(self) -> List[Categoria_proc]:
        """
        Retorna a lista completa de categorias cadastradas.
        """
        return self.categorias

class RepositorioProcessamentosAnuais:
    """
    Processamento - Armazena e gerencia a lista de registros de processamento anual cadastrados no sistema.
    
    Atributos:
        processamentos (list[ProcessamentoAnual]): Lista de todos os registros de processamento.
    """
    def __init__(self):
        self.processamentos = []

    def adicionar_processamento(self, processamento: ProcessamentoAnual):
        """
        Adiciona um registro de produtividade ao repositório, caso ainda não exista.
        """
        if processamento not in self.processamentos:
            self.processamentos.append(processamento)

    def remover_processamento(self, processamento: ProcessamentoAnual):
        """
        Remove um registro de produtividade do repositório, caso exista.
        """
        if processamento in self.processamentos:
            self.processamentos.remove(processamento)

    def buscar_processamento(self, cultivar: Cultivar_proc, ano: int) -> ProcessamentoAnual:
        """
        Retorna o processamento para determinado cultivar e ano, ou None se não encontrado.
        """
        for p in self.processamentos:
            if p.cultivar == cultivar and p.ano == ano:
                return p
        return None

    def buscar_processamentosPorAno(self, ano: int) -> List[ProcessamentoAnual]:
        """
        Retorna os processamentos de todos os cultivares para determinado ano, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for p in self.processamentos:
            if p.ano == ano:
                retorno.append(p)
        return retorno

    def buscar_processamentosPorAno_TipoUva(self, ano: int, tipo_uva: EnumTipoUva_proc) -> List[ProcessamentoAnual]:
        """
        Retorna os processamentos de todos os cultivares para determinado ano e TipoUva, ou uma lista vazia, se não encontrado.
        """
        retorno = []
        for p in self.processamentos:
            if (p.ano == ano) and (p.cultivar.TipoUva == tipo_uva):
                retorno.append(p)
        return retorno



    def buscarProcessamentoTotalDeCategoriaPorAno_TipoUva(self, categoria: Categoria_proc, ano: int, tipo_uva: EnumTipoUva_proc) -> int:
        """
        Retorna a quantidade total de processamento de todos os cultivares para determinado ano, categoria e tipo uva, ou uma lista vazia, se não encontrado.
        """
        retorno: int = 0
        processamentosDoAno = self.buscar_processamentosPorAno_TipoUva(ano, tipo_uva)
        for p in processamentosDoAno:
            if p.cultivar.categoria == categoria:
                retorno = retorno + p.quantidade
        return retorno


    def listar_processamentos(self) -> List[ProcessamentoAnual]:
        """
        Retorna a lista completa de produtividades cadastradas.
        """
        return self.processamentos

