import pandas as pd 
import yfinance as yf 
from dateutil.relativedelta import relativedelta
from datetime import datetime as dt 
from sklearn.linear_model import LinearRegression
import numpy as np 
import ta 

class FonteDados:
    """ Essa é a classe para busca de dados atualizados sobre os ativos em investimento """
    
    def __init__(self, diff_time = relativedelta(days=120)):
        self.end_date = dt.today()
        self.start_date = self.end_date - diff_time 
        self.dados = {}

        ativos = pd.read_csv(r'..\data\sistema_challenge\portfolio.csv', index_col = [0], parse_dates = [0], nrows=1)
        for ativo in ativos.columns:
            self.dados[ativo] = yf.download(ativo, start=self.start_date, end=self.end_date, progress=False)[['Open', 'Close', 'High', 'Low', 'Volume']]

        self.adicionar_macd_volume()
        self.adicionar_estocastico()
        self.adicionar_true_range()

    def __getattr__(self, name):
        return self.dados[name]
    

    def _adicionar_indicador_volume(self, volume):
        
        # Utilizando média exponencial para 7 dias (captar rápido mudanças)
        media_7 = volume.ewm(span=7, adjust=False).mean()

        # Utilizando média aritmética para 30 dias (não captar ruídos de médio prazo)
        media_30 = volume.rolling(30).mean()

        # Obtendo diferença entre a média de 7 e média de 30 
        macd_volume = media_7 - media_30 

        # Normalizando para ser mais fácil compreender o MACD
        macd_volume = (macd_volume - macd_volume.mean()) / macd_volume.std()
        return macd_volume

    
    def adicionar_macd_volume(self):
        """ Propriedade para adicionar betas de volume em 3 dias """

        for _, df in self.dados.items():
            macd_volume = self._adicionar_indicador_volume(df['Volume'])
            df['MACDVolume'] = macd_volume
    


    def adicionar_estocastico(self):
        """ Método para adicionar estocástico"""
        for _, df in self.dados.items():
            stochastic = ta.momentum.StochasticOscillator(close = df.Close, high=df.High, low = df.Low)
            df['%K'] = stochastic.stoch()
            df['%D'] = stochastic.stoch_signal()

    def adicionar_true_range(self):
        """ Método para adicionar ATR de 3 períodos """
        for _, df in self.dados.items():
            df['ATR'] = ta.volatility.AverageTrueRange(
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            window=3
                        ).average_true_range()
            
            

    