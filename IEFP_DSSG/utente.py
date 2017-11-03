import pandas as pd
from collections.abc import Mapping

class Utente:

    STR_PEMPREGO = "PedidoEmprego"

    # Utente nested classes

    class Conjuge:
        def __init__ (self, estadoCivil, motivoIndisponibilidade):
            self.estadoCivil = estadoCivil
            self.motivoIndisponibilidade = motivoIndisponibilidade 


    # Utente initialization method

    def __init__(self, pd_row):
        self.id = pd_row['UteId']
        self.dataNascimento = pd_row['Ute-Data Nascimento']
        self.sexo = pd_row['Sexo']
        self.nacionalidade = pd_row['DNacionalidade']
        self.estadoCivil = pd_row['Ute-Estado Civil']
        self.deficiencia = Utente.nivelDeficiencia(pd_row['DDeficiencia'])
        self.conjuge = self.Conjuge(pd_row['Conjuge Estado Civil'], pd_row['Conjuge Motivo Indisponibilidade'])
        self.pedidosEmprego = { int(pd_row['AnoMes'])*100 : self.STR_PEMPREGO } 
        # ex: 200704 -> 200704[00] para caso ocorra novo registo no mesmo mês vai somando 1 -> 20070401 
        self.anulacoes = {}
        self.intervencoes = {}
        self.encaminhamentos = {}
        self.apresentacoes = {}
        self.convocatorias = {}
        self.mudancasCategoria = {}

    # Utente Properties

    @property
    def nrPedidosEmprego(self):
        return len(self.pedidosEmprego)

    ## Utente Static Methods

    @staticmethod
    def nivelDeficiencia(descricaoDeficiencia):
        """ Recebe campo descricao da deficiência e atribui um nível de deficiencia """
        return {
            'NÃO DEFICIENTE': 0,
            'OUTRAS DEFICIÊNCIAS ESTÉTICAS': 1,
            'DEFICIÊNCIAS DA AUDIÇÃO': 1 
        }.get(descricaoDeficiencia, 2)

    # Utente Methods

    def addNovoPedidoEmprego(self, pd_row):
        # TODO: Temos casos de pedidos de emprego no mesmo mes...faz sentido? Não se deveria ignorar?
        anoMes=int(pd_row['AnoMes'])
        anoMes *= 100
        while True:
            if anoMes not in self.pedidosEmprego:
                self.pedidosEmprego[anoMes] = self.STR_PEMPREGO
                break
            else:
                anoMes += 1
    
    
        

class ListaUtentes(Mapping):
    def __init__(self, pd_pedidosInscritos):
        self.__dict__ = dict()
        for index, row in pd_pedidosInscritos.iterrows():
            idUtente = row['UteId']

            if idUtente in self: # Id utente já existe
                self.__addNewPedidoEmpregoTo(self[idUtente], row) # Adiciona novo pedido de emprego à lista
                # TODO comparar os campos para perceber se existe informação adicional
            else:                 # Id utente inexistente
                self[idUtente] = Utente(row)
    
    # The next five methods are requirements of the ABC.
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def __getitem__(self, key):
        return self.__dict__[key]
    def __delitem__(self, key):
        del self.__dict__[key]
    def __iter__(self):
        return iter(self.__dict__)
    def __len__(self):
        return len(self.__dict__)

    # Utente Methods

    def __addNewPedidoEmpregoTo(self, utente, pd_row):
        utente.addNovoPedidoEmprego(pd_row)

    def parseCancellations(self, pd_sie_31):
        for index, row in pd_sie_31:
            idUtente = int(row['ID'])
            self.__addNewCancellationTo(utente, pd_row)
    
    def __addNewCancellationTo(self, utente, pd_row):
        utente.addNewCancellation(pd_row)