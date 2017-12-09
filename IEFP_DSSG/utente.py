import pandas as pd
from collections.abc import Mapping
from datetime import datetime
import pickle
import os.path
import getpass

TEMP_DIR = './temp/'
PICKLE_FILENAME = 'ListaUtentes.pickle'
PICKLE_FILEPATH = TEMP_DIR+PICKLE_FILENAME
PASSWORD_FILENAME = './password.txt'
SQL_LIMIT = 999999999999

def date2str(date):
    try:
        return str(date.strftime("%Y/%m/%d"))
    except:
        return "N/A"

class Utente:

    # Utente nested classes

    class Conjuge:
        def __init__ (self, estadoCivil, motivoIndisponibilidade):
            self.estadoCivil = estadoCivil
            self.motivoIndisponibilidade = motivoIndisponibilidade

        def __str__(self):
            return "Cônjuge: Estado Civil: {:>8}  | Motivo Indisponibilidade: {}". format(self.estadoCivil, self.motivoIndisponibilidade)

    class Pedido:
        PRIORITY = 1
        def __init__ (self, pd_row):
            self.descricao = "Pedido de Emprego"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Candidatura-Data']

        def __str__(self):
            # Pedido Emprego: 19/01/2016 (201610)  
            return "{:^20} | {:6} | {:9}".format(self.descricao, self.anoMes, date2str(self.data))

        def typeDescription(self):
            return "{}".format(self.descricao )
        

    class Anulacao:
        PRIORITY = 2
        def __init__ (self, pd_row):
            self.descricao = "Anulacao"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Anulacao Data']
            self.indD = pd_row['DMotivo Anulação']

        def __str__(self):
            # Pedido Emprego: 19/01/2016 (201610)  
            return "{:^20} | {:6} | {:9} | {}".format(self.descricao, self.anoMes, date2str(self.data), self.indD)

        def typeDescription(self):
            return "{} | {}".format(self.descricao, str(self.indD))


    class Intervencao:
        PRIORITY = 5
        def __init__ (self, pd_row):
            self.descricao = "Intervenção"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Intervenção Data']
            self.codigoD = pd_row['Intervenção Codigo D']
            self.indD = pd_row['Intervencao Ind D']
            self.resultado = pd_row['DResultado Intervencao']

        def __str__(self):
            return "{:^20} | {:6} | {:9} | {:20.20} | {:30.30} | {:12.12}".format(self.descricao, self.anoMes, date2str(self.data), str(self.indD), str(self.codigoD), str(self.resultado))
        
        def typeDescription(self):
            return "{} | {} | {} | {}".format(self.descricao, str(self.indD), str(self.codigoD), str(self.resultado) )

    class Encaminhamento:
        PRIORITY = 4
        def __init__ (self, pd_row):
            self.descricao = "Encaminhamento"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Intervenção Data']
            self.codigoD = pd_row['Intervenção Codigo D']
            self.resultado = pd_row['DResultado Intervencao']

        def __str__(self):
            return "{:^20} | {:6} | {:9} | {:30.30} | {:20}".format(self.descricao, self.anoMes, date2str(self.data), str(self.codigoD), str(self.resultado))

        def typeDescription(self):
            return "{} | {} | {}".format(self.descricao, str(self.codigoD), str(self.resultado) )

    class Apresentacao:
        PRIORITY = 6
        def __init__ (self, pd_row):
            self.descricao = "Apresentação"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Apresentacao Data']
            self.ofertaNr = int(pd_row['Oferta Nr'])
            self.ofertaServico = pd_row['Oferta Servico']
            self.resultado = pd_row['DResultado Apresentação']

        def __str__(self):
            return "{:^20} | {:6} | {:9} | {:5} | {:3} | {:60.60}".format(self.descricao, self.anoMes, date2str(self.data), str(self.ofertaNr), str(self.ofertaServico), str(self.resultado))

        def typeDescription(self):
            return "{} | {}".format(self.descricao, str(self.resultado) )

    class Convocatoria:
        PRIORITY = 3
        def __init__ (self, pd_row):
            self.descricao = "Convocatória"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Convocatoria Em'] # Data em que foi efetuada a convocatória
            self.tipo = pd_row['DTipo Convocatória']
            self.resultado = pd_row['DResultado Convocatória']

        def __str__(self):
            return "{:^20} | {:6} | {:9} | {:19} | {:15.15}".format(self.descricao, self.anoMes, date2str(self.data), str(self.tipo), str(self.resultado))

        def typeDescription(self):
            return "{} | {} | {}".format(self.descricao, str(self.tipo), str(self.resultado) )

    class MudancaCategoria:
        PRIORITY = 7
        def __init__ (self, pd_row):
            self.descricao = "Mudança de Categoria"
            self.anoMes = pd_row['AnoMes']
            self.data = pd_row['Mo-Data Movimento'] # Data em que é gerado o movimento de mudança de categoria
            self.categoria = pd_row['DCategoria']
            self.categoriaAnterior = pd_row['Dcategoria anterior']  # Descritivo da categoria anterior ao movimento (dados disponíveis a partir de janeiro de 2012)

        def __str__(self):
            return "{:^20} | {:6} | {:9} | {:^35.35} | {:^35.35}".format(self.descricao, self.anoMes, date2str(self.data), str(self.categoria), str(self.categoriaAnterior))

        def typeDescription(self):
            return "{} | {} | {}".format(self.descricao, str(self.categoria), str(self.categoriaAnterior) )


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

    ## Utente Methods

    def stringListOfEventsTypeDescription(self):
        lines = []
        for event in self.eventsList():
            lines.append(event.typeDescription()) # Chama method typeDescription do respectivo evento
        return lines

    def stringListOfEventsFullDescription(self):
        lines = []
        for event in self.eventsList():
            lines.append(str(event)) # Chama method _str_ do respectivo evento
        return lines

    def eventsList(self):
        # Retorna todos os eventos num list ordenado cronologicamente
        unorderedHistorico = {**self.pedidosEmprego, **self.anulacoes, **self.intervencoes, **self.encaminhamentos, **self.apresentacoes, **self.convocatorias, **self.mudancasCategoria}
        orderedEventsList = []
        for k, v in sorted(unorderedHistorico.items()):
            orderedEventsList.append(v)

        return orderedEventsList

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
        try:
            ts = int(pd_row['Candidatura-Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp
        
        ts = Utente.returnUniqueTSFromDict(self.pedidosEmprego, ts) # incrementa 1 se timestamp já existe
        ts = ts *10 + self.Pedido.PRIORITY # Inclui prioridade para melhor reordenacao

        self.pedidosEmprego[ts] = self.Pedido(pd_row) # adiciona nova entrada
    
    def addNewAnulacao(self, pd_row):
        try:
            ts = int(pd_row['Anulacao Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.anulacoes, ts)
        ts = ts *10 + self.Anulacao.PRIORITY # Inclui prioridade para melhor reordenacao

        self.anulacoes[ts] = self.Anulacao(pd_row) # adiciona nova entrada
    
    def addNewIntervencao(self, pd_row):
        try:
            ts = int(pd_row['Intervenção Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.intervencoes, ts)
        ts = ts *10 + self.Intervencao.PRIORITY # Inclui prioridade para melhor reordenacao

        self.intervencoes[ts] = self.Intervencao(pd_row) # adiciona nova entrada

    def addNewEncaminhamento(self, pd_row):
        try:
            ts = int(pd_row['Intervenção Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.encaminhamentos, ts)
        ts = ts *10 + self.Encaminhamento.PRIORITY # Inclui prioridade para melhor reordenacao

        self.encaminhamentos[ts] = self.Encaminhamento(pd_row) # adiciona nova entrada    

    def addNewApresentacao(self, pd_row):
        try:
            ts = int(pd_row['Apresentacao Data'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.apresentacoes, ts)
        ts = ts *10 + self.Apresentacao.PRIORITY # Inclui prioridade para melhor reordenacao
        
        self.apresentacoes[ts] = self.Apresentacao(pd_row) # adiciona nova entrada    

    def addNewConvocatoria(self, pd_row):
        try:
            ts = int(pd_row['Convocatoria Em'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.convocatorias, ts)
        ts = ts *10 + self.Convocatoria.PRIORITY # Inclui prioridade para melhor reordenacao

        self.convocatorias[ts] = self.Convocatoria(pd_row) # adiciona nova entrada                   

    def addNewMudancaCategoria(self, pd_row):
        try:
            ts = int(pd_row['Mo-Data Movimento'].timestamp()) # !!! Corresponde à data efectiva do evento
        except: # Fallback caso o campo Anulacao Data não tenha registo
            ts = Utente.anoMesToTimeStamp(pd_row['AnoMes']) # converte AnoMes para timestamp

        ts = Utente.returnUniqueTSFromDict(self.mudancasCategoria, ts)
        ts = ts *10 + self.MudancaCategoria.PRIORITY # Inclui prioridade para melhor reordenacao


        self.mudancasCategoria[ts] = self.MudancaCategoria(pd_row) # adiciona nova entrada 

class ListaUtentes(Mapping):
    def __init__(self, forceFetch = False):
        self.__dict__ = dict()
        if forceFetch:
            self.fetch()
        else:
            self.load()
        
    
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
    def fetch(self):
        from sqlalchemy import create_engine
        import pymysql
        import pandas as pd

        if os.path.isfile(PASSWORD_FILENAME):
            with open(PASSWORD_FILENAME) as f: mysqlpass = f.read()
        else:
            print("Ficheiro {} não encontrado. Inserir password acesso à MySQL DB: ". format(PASSWORD_FILENAME))
            mysqlpass = getpass.getpass()
            with open(PASSWORD_FILENAME, 'w') as f: f.write(mysqlpass)

        mysqlpass = mysqlpass.strip()

        engine = create_engine('mysql+pymysql://grupo_1:{}@151.236.42.86:3306/iefp'.format(mysqlpass))
        connection = engine.raw_connection()

        print('A executar queries SQL...')
        pil = pd.read_sql('SELECT * FROM pedidos_inscritos_longos LIMIT {}'.format(SQL_LIMIT), connection)
        sie_31 = pd.read_sql('SELECT * FROM sie_31 LIMIT {}'.format(SQL_LIMIT), connection)
        sie_35 = pd.read_sql('SELECT * FROM sie_35 LIMIT {}'.format(SQL_LIMIT), connection)
        sie_36 = pd.read_sql('SELECT * FROM sie_36 LIMIT {}'.format(SQL_LIMIT), connection)
        sie_37 = pd.read_sql('SELECT * FROM sie_37 LIMIT {}'.format(SQL_LIMIT), connection)
        sie_38 = pd.read_sql('SELECT * FROM sie_38 LIMIT {}'.format(SQL_LIMIT), connection)
        sie_43 = pd.read_sql('SELECT * FROM sie_43 LIMIT {}'.format(SQL_LIMIT), connection)

        self.__parseUserHistoryFromDatasets(pil, sie_31, sie_35, sie_36, sie_37, sie_38, sie_43)

        #self.save()

    def __parseUserHistoryFromDatasets(self, pedidos_inscritos_longos, sie_31, sie_35, sie_36, sie_37, sie_38, sie_43):
        print("Parsing da tabela pedidos_inscritos_longos... (1/7)")
        self.parsePedidos(pedidos_inscritos_longos)
        print("Parsing das Anulacoes... (2/7)")
        self.parseAnulacoes(sie_31)
        print("Parse das Intervenções... (3/7)")
        self.parseIntervencoes(sie_35)
        print("Parse dos Encaminhamentos... (4/7)")
        self.parseEncaminhamentos(sie_36)
        print("Parse dos Apresentações... (5/7)")
        self.parseApresentacoes(sie_37)
        print("Parse das Convocatórias... (6/7)")
        self.parseConvocatorias(sie_38)
        print("Parse das Mudanças de Categoria... (7/7)")
        self.parseMudancasCategoria(sie_43)
        
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

    def printHistoricosTodosUtentes(self):
        lines = self.generateHistoricosTodosUtentes()
        for l in lines:
            print(l)

    def output2FileHistoricosTodosUtentes(self):
        lines = self.generateHistoricosTodosUtentes()
        with open(TEMP_DIR+"HistoricosUtentes.txt", 'w', encoding="utf-8") as f:
            for l in lines:
                f.write(l+"\n")
            f.close()

    def generateHistoricosTodosUtentes(self):
        lines = []
        for id, utente in self.items():
            lines.append("\n {:^100}".format("Utente ID: "+str(id)))
            lines.extend(utente.stringListOfEventsFullDescription())
        return lines

    def save(self):
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        print('Saving to {}'.format(PICKLE_FILEPATH))
        with open(PICKLE_FILEPATH, 'wb') as f:
            pickle.dump(self.__dict__, f, protocol=pickle.HIGHEST_PROTOCOL)
            
    def load(self):
        print('Loading from {}'.format(PICKLE_FILEPATH))
        with  open(PICKLE_FILEPATH, 'rb') as f:
            self.__dict__ = pickle.load(f)            
        print('Finished')
