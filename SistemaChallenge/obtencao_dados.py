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

        ativos = pd.read_csv(r'..\data\sistema_challenge\portfolio.csv', index_col = [0], parse_data = [0], nrows=1)
        for ativo in ativos.columns:
            self.dados[ativo] = yf.download(ativo, start=self.start_date, end=self.end_date, progress=False)[['Open', 'Close', 'High', 'Low', 'Volume']]

        self.adicionar_beta_volume()
        self.adicionar_estocastico()


    def __getattr__(self, name):
        return self.dados[name]
    

    def _adicionar_beta(self, volume):
        if len(volume) < 7:
                return np.nan  # Skip if not enough data
        # Day indices (0 to 6)
        X = np.arange(len(volume)).reshape(-1, 1)
        y = volume.values
        # Weights: more weight to recent days
        weights = np.linspace(1, 7, num=7)
        # Perform weighted linear regression
        model = LinearRegression()
        model.fit(X, y, sample_weight=weights)
        # Extract beta (slope)
        beta = model.coef_[0]
        return beta 
    
    def adicionar_beta_volume(self):
        """ Propriedade para adicionar betas de volume em 3 dias """

        for _, df in self.dados.items():
            beta = df['Volume'].rolling(3).apply(lambda x: self._adicionar_beta(x), raw=False)
            beta_normalizado = (beta - beta.mean()) / beta.std()
            df['BetaNormalizado3D'] = beta_normalizado
    
    def adicionar_estocastico(self):
        """ Método para adicionar estocástico"""
        for _, df in self.dados.items():
            stochastic = ta.momentum.StochasticOscillator(close = df.Close, high=df.High, low = df.Low)
            df['%K'] = stochastic.stoch()
            df['%D'] = stochastic.stoch_signal()
            

    