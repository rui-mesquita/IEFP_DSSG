import pandas as pd

class Utente:

    class Conjuge:
        def __init__ (self, estadoCivil, motivoIndisponibilidade):
            self.estadoCivil
            self.motivoIndisponibilidade



    def __init__(self, pandas_row):
        self.id = pandas_row['UteId']
        self.dataNascimento = pandas_row['Ute-Data Nascimento']
        self.sexo = pandas_row['Sexo']
        self.nacionalidade = pandas_row['DNacionalidade']
        self.estadoCivil = pandas_row['Ute-Estado Civil']
        self.deficiencia = nivelDeficiencia()
        self.conjuge = Conjuge(pandas_row['Conjuge Estado Civil'], pandas_row['Conjuge Motivo Indisponibilidade
'])
    


    def nivelDeficiencia(descricaoDeficiencia):
        """ Recebe campo descricao da deficiência e atribui um nível de deficiencia """
        return {
            'NÃO DEFICIENTE': 0,
            'OUTRAS DEFICIÊNCIAS ESTÉTICAS': 1,
            'DEFICIÊNCIAS DA AUDIÇÃO': 1 
        }.get(x, 2)