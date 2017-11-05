import pandas as pd
from collections.abc import Mapping
from datetime import datetime
import pickle

class Utente:

    # Utente nested classes

    class Conjuge:
        def __init__ (self, estadoCivil, motivoIndisponibilidade):
            self.estadoCivil = estadoCivil
            self.motivoIndisponibilidade = motivoIndisponibilidade 

    class Pedido:
        def __init__ (self, pd_row):
            self.descricao = "Pedido de Emprego"

    class Anulacao:
        def __init__ (self, pd_row):
            self.descricao = "Anulacao"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Anulacao Data']
            self.indD = pd_row['DMotivo Anulação']

    class Intervencao:
        def __init__ (self, pd_row):
            self.descricao = "Intervenção"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Intervenção Data']
            self.codigoD = pd_row['Intervenção Codigo D']
            self.indD = pd_row['Intervencao Ind D']
            self.resultado = pd_row['DResultado Intervencao']

    class Encaminhamento:
        def __init__ (self, pd_row):
            self.descricao = "Encaminhamento"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Intervenção Data']
            self.codigoD = pd_row['Intervenção Codigo D']
            self.resultado = pd_row['DResultado Intervencao']
    
    class Apresentacao:
        def __init__ (self, pd_row):
            self.descricao = "Apresentação"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Apresentacao Data']
            self.ofertaNr = pd_row['Oferta Nr']
            self.ofertaNr = pd_row['Oferta Servico']
            self.resultado = pd_row['DResultado Apresentação']

    class Convocatoria:
        def __init__ (self, pd_row):
            self.descricao = "Apresentação"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Convocatoria Em'] # Data em que foi efetuada a convocatória
            self.tipo = pd_row['DTipo Convocatória']
            self.resultado = pd_row['DResultado Convocatória']

    class MudancaCategoria:
        def __init__ (self, pd_row):
            self.descricao = "Mudança de Categoria"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Mo-Data Movimento'] # Data em que é gerado o movimento de mudança de categoria
            self.categoria = pd_row['DCategoria']
            self.categoriaAnterior = pd_row['Dcategoria anterior']  # Descritivo da categoria anterior ao movimento (dados disponíveis a partir de janeiro de 2012)



    # Utente initialization method

    def __init__(self, pd_row):
        self.id = pd_row['UteId']
        self.dataNascimento = pd_row['Ute-Data Nascimento']
        self.sexo = pd_row['Sexo']
        self.nacionalidade = pd_row['DNacionalidade']
        self.estadoCivil = pd_row['Ute-Estado Civil']
        self.deficiencia = Utente.nivelDeficiencia(pd_row['DDeficiencia'])
        self.conjuge = self.Conjuge(pd_row['Conjuge Estado Civil'], pd_row['Conjuge Motivo Indisponibilidade'])
        
        # Inicializa todos dicionarios
        self.pedidosEmprego = {}
        self.anulacoes = {}
        self.intervencoes = {}
        self.encaminhamentos = {}
        self.apresentacoes = {}
        self.convocatorias = {}
        self.mudancasCategoria = {}

        # Adiciona primeiro pedido de emprego deste utente à lista
        self.addNewPedido(pd_row)


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

    @staticmethod
    def anoMesToTimeStamp(anoMes):
        """ Recebe campo AnoMes (ex: 200709) e converte para timestamp """
        return int(datetime.strptime(anoMes , '%Y%m').timestamp())
    
    @staticmethod
    def returnUniqueTSFromDict(dictionary, ts):
        """ Retorna timestamp incrementado em 1s caso ts que se pretende inserir já exista """
        newTs = ts # Parte de ts inicial
        while True: # Vai incrementando até não haver key idêntica
            if newTs not in dictionary:
                break
            else:
                newTs += 1
        return newTs
    

    # Utente Methods
    # TODO: method unico para todos os add*

    def addNewPedido(self, pd_row):
        # TODO: Temos casos de pedidos de emprego no mesmo mes...faz sentido? Não se deveria ignorar?
        ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp
        ts = Utente.returnUniqueTSFromDict(self.pedidosEmprego, ts) # incrementa 1 se timestamp já existe
        self.pedidosEmprego[ts] = self.Pedido(pd_row) # adiciona nova entrada
    
    def addNewAnulacao(self, pd_row):
        try:
            ts = int(pd_row['Anulacao Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.anulacoes, ts)
        self.anulacoes[ts] = self.Anulacao(pd_row) # adiciona nova entrada
    
    def addNewIntervencao(self, pd_row):
        try:
            ts = int(pd_row['Intervenção Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.intervencoes, ts)
        self.intervencoes[ts] = self.Intervencao(pd_row) # adiciona nova entrada

    def addNewEncaminhamento(self, pd_row):
        try:
            ts = int(pd_row['Intervenção Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.encaminhamentos, ts)
        self.encaminhamentos[ts] = self.Encaminhamento(pd_row) # adiciona nova entrada    

    def addNewApresentacao(self, pd_row):
        try:
            ts = int(pd_row['Apresentacao Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.apresentacoes, ts)
        self.apresentacoes[ts] = self.Apresentacao(pd_row) # adiciona nova entrada    

    def addNewConvocatoria(self, pd_row):
        try:
            ts = int(pd_row['Convocatoria Em'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.convocatorias, ts)
        self.convocatorias[ts] = self.Convocatoria(pd_row) # adiciona nova entrada                   

    def addNewMudancaCategoria(self, pd_row):
        try:
            ts = int(pd_row['Mo-Data Movimento'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.mudancasCategoria, ts)
        self.mudancasCategoria[ts] = self.MudancaCategoria(pd_row) # adiciona nova entrada 

class ListaUtentes(Mapping):
    PICKLE_FILENAME = './temp/ListaUtentes.pickle'
    SQL_LIMIT = 30000000

    def __init__(self):
        self.__dict__ = dict()
        
    
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

    # ListaUtentes Methods
    def fetch(self, passwordFile):
        from sqlalchemy import create_engine
        import pymysql
        import pandas as pd

        with open(passwordFile) as f: mysqlpass = f.read()

        mysqlpass = mysqlpass.strip()

        engine = create_engine('mysql+pymysql://grupo_1:{}@151.236.42.86:3306/iefp'.format(mysqlpass))
        connection = engine.raw_connection()

        pil = pd.read_sql('SELECT * FROM pedidos_inscritos_longos LIMIT {}'.format(self.SQL_LIMIT), connection)
        sie_31 = pd.read_sql('SELECT * FROM sie_31 LIMIT {}'.format(self.SQL_LIMIT), connection)
        sie_35 = pd.read_sql('SELECT * FROM sie_35 LIMIT {}'.format(self.SQL_LIMIT), connection)
        sie_36 = pd.read_sql('SELECT * FROM sie_36 LIMIT {}'.format(self.SQL_LIMIT), connection)
        sie_37 = pd.read_sql('SELECT * FROM sie_37 LIMIT {}'.format(self.SQL_LIMIT), connection)
        sie_38 = pd.read_sql('SELECT * FROM sie_38 LIMIT {}'.format(self.SQL_LIMIT), connection)
        sie_43 = pd.read_sql('SELECT * FROM sie_43 LIMIT {}'.format(self.SQL_LIMIT), connection)

        self.__parseUserHistoryFromDatasets(pil, sie_31, sie_35, sie_36, sie_37, sie_38, sie_43)

        self.save()

    def __parseUserHistoryFromDatasets(self, pedidos_inscritos_longos, sie_31, sie_35, sie_36, sie_37, sie_38, sie_43):
        print("Starting parsing...")
        self.parsePedidos(pedidos_inscritos_longos)
        print("Parse dos pedidos terminado (1/7)")
        self.parseAnulacoes(sie_31)
        print("Parse das Anulações terminado (2/7)")
        self.parseIntervencoes(sie_35)
        print("Parse das Intervenções terminado (3/7)")
        self.parseEncaminhamentos(sie_36)
        print("Parse dos Encaminhamentos terminado (4/7)")
        self.parseApresentacoes(sie_37)
        print("Parse das Apresentações terminado (5/7)")
        self.parseConvocatorias(sie_38)
        print("Parse das Convocatórias terminado (6/7)")
        self.parseMudancasCategoria(sie_43)
        print("Parse das Mudanças de Categoria terminado (7/7)")
        
    def __addNewPedidoEmpregoTo(self, utente, pd_row):
        utente.addNewPedido(pd_row)

    def parsePedidos(self, pedidos_inscritos_longos):
        for index, row in pedidos_inscritos_longos.iterrows():
            idUtente = row['UteId']

            if idUtente in self: # Id utente já existe
                self.__addNewPedidoEmpregoTo(self[idUtente], row) # Adiciona novo pedido de emprego à lista
                # TODO comparar os campos para perceber se existe informação adicional
            else:                 # Id utente inexistente
                self[idUtente] = Utente(row) # Cria nova entrada

    # TODO: method unico para todos parse*. 

    def parseAnulacoes(self, pd_sie_31):
        countUtentesIgnorados = 0
        countTotal = 0
        for index, row in pd_sie_31.iterrows():
            countTotal += 1
            idUtente = int(row['ID'])
            if idUtente in self: # Id utente já existe
                self[idUtente].addNewAnulacao(row)
            else:
                countUtentesIgnorados+=1 # Não faz nada porque não tem info desse utente
        print("Total de {} ({}%) utentes existentes em sie_31 mas sem equivalencia na pedidos_inscritos_longos:".format(countUtentesIgnorados, int(countUtentesIgnorados/countTotal*100)))
    
    def parseIntervencoes(self, pd_sie_35):
        countUtentesIgnorados = 0
        countTotal = 0
        for index, row in pd_sie_35.iterrows():
            countTotal += 1
            idUtente = int(row['UteId'])
            if idUtente in self: # Id utente já existe
                self[idUtente].addNewIntervencao(row)
            else:
                countUtentesIgnorados+=1 # Não faz nada porque não tem info desse utente
        print("Total de {} ({}%) utentes existentes em sie_35 mas sem equivalencia na pedidos_inscritos_longos:".format(countUtentesIgnorados, int(countUtentesIgnorados/countTotal*100)))
        
    def parseEncaminhamentos(self, pd_sie_36):
        countUtentesIgnorados = 0
        countTotal = 0
        for index, row in pd_sie_36.iterrows():
            countTotal += 1
            idUtente = int(row['UteId'])
            if idUtente in self: # Id utente já existe
                self[idUtente].addNewEncaminhamento(row)
            else:
                countUtentesIgnorados+=1 # Não faz nada porque não tem info desse utente
        print("Total de {} ({}%) utentes existentes em sie_36 mas sem equivalencia na pedidos_inscritos_longos:".format(countUtentesIgnorados, int(countUtentesIgnorados/countTotal*100)))

    def parseApresentacoes(self, pd_sie_37):
        countUtentesIgnorados = 0
        countTotal = 0
        for index, row in pd_sie_37.iterrows():
            countTotal += 1
            idUtente = int(row['UteId'])
            if idUtente in self: # Id utente já existe
                self[idUtente].addNewApresentacao(row)
            else:
                countUtentesIgnorados+=1 # Não faz nada porque não tem info desse utente
        print("Total de {} ({}%) utentes existentes em pd_sie_37 mas sem equivalencia na pedidos_inscritos_longos:".format(countUtentesIgnorados, int(countUtentesIgnorados/countTotal*100)))

    def parseConvocatorias(self, pd_sie_38):
        countUtentesIgnorados = 0
        countTotal = 0
        for index, row in pd_sie_38.iterrows():
            countTotal += 1
            idUtente = int(row['UteId'])
            if idUtente in self: # Id utente já existe
                self[idUtente].addNewConvocatoria(row)
            else:
                countUtentesIgnorados+=1 # Não faz nada porque não tem info desse utente
        print("Total de {} ({}%) utentes existentes em pd_sie_38 mas sem equivalencia na pedidos_inscritos_longos:".format(countUtentesIgnorados, int(countUtentesIgnorados/countTotal*100)))

    def parseMudancasCategoria(self, pd_sie_43):
        countUtentesIgnorados = 0
        countTotal = 0
        for index, row in pd_sie_43.iterrows():
            countTotal += 1
            idUtente = int(row['UteId'])
            if idUtente in self: # Id utente já existe
                self[idUtente].addNewMudancaCategoria(row)
            else:
                countUtentesIgnorados+=1 # Não faz nada porque não tem info desse utente
        print("Total de {} ({}%) utentes existentes em pd_sie_43 mas sem equivalencia na pedidos_inscritos_longos:".format(countUtentesIgnorados, int(countUtentesIgnorados/countTotal*100)))

    def save(self):
        print('Saving to {}'.format(self.PICKLE_FILENAME))
        with open(self.PICKLE_FILENAME, 'wb') as f:
            pickle.dump(self, f)

    def load(self):
        print('Loading from {}'.format(self.PICKLE_FILENAME))
        f = open(self.PICKLE_FILENAME, 'rb') 
        self = pickle.load(f) 