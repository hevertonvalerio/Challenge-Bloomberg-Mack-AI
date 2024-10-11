import pandas as pd 
from .obtencao_dados import FonteDados
from .controle import PortfolioChallenge
from .predicao import Modelo

class ChallengeTrader:
    """ Classe para informar operações a serem realizadas e controlar risco """

    def __init__(self, portfolio: PortfolioChallenge, modelo: Modelo):
        self.portfolio = portfolio 
        self.dados = FonteDados()
        self.modelo = modelo


    def executar(self):
        
        previsao = self.modelo.predict() 


    def _checar_ordem_compra(self, previsao):
        """ Método para checar se há ordem de compra """
        
