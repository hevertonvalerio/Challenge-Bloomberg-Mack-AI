import pandas as pd 
from datetime import datetime as dt 
import logging

class PortfolioChallenge:

    """ Classe que armazena os dados do portfólio usado no Challenge """

    def __init__(self, disponibilidade = 1000000):

        try:
            self._portfolio = pd.read_csv(r'..\data\sistema_challenge\portfolio.csv', index_col = [0], parse_dates = [0])
            self._historico_compras = pd.read_csv(r'..\data\sistema_challenge\historico_compras.csv', index_col = [0], parse_dates = [0])
            self._historico_venda = pd.read_csv(r'..\data\sistema_challenge\historico_vendas.csv', index_col = [0], parse_dates = [0])
            self._desempenho = pd.read_csv(r'..\data\sistema_challenge\rendimento_portfolio.csv', index_col = [0], parse_dates = [0])
        
        except FileNotFoundError:
            ativos = pd.read_csv(r'..\data\ativos_selecionados\setores_selecionados_us.csv')
            ativos_a_investir = ativos[['YFTicker']].set_index('YFTicker').T
            ativos_a_investir.loc[dt.today().strftime('%d/%m/%Y')] = 0
            
            ativos_a_investir.to_csv(r'..\data\sistema_challenge\portfolio.csv', index=True)
            self._portfolio = ativos_a_investir.copy()

            ativos_a_investir.to_csv(r'..\data\sistema_challenge\historico_compras.csv', index=True)
            ativos_a_investir.to_csv(r'..\data\sistema_challenge\historico_venda.csv', index=True)
            self._historico_compras = ativos_a_investir.copy()
            self._historico_venda = ativos_a_investir.copy()

            self._desempenho = pd.DataFrame({'disponibilidade': []})
            self._desempenho.loc[dt.today().strftime('%d/%m/%Y'), 'disponibilidade'] = disponibilidade

    @property
    def status(self):
        raise NotImplementedError('Não está pronto ainda!')
        portfolio_atualizado = self._portfolio.copy()
        historico_compras = self._historico_compras.copy().reset_index()
        historico_vendas = self._historico_venda.copy().reset_index()
        
    def _salvar_registros(self):
        self._historico_compras.to_csv(r'..\data\sistema_challenge\historico_compras.csv', index=True)
        self._historico_venda.to_csv(r'..\data\sistema_challenge\historico_vendas.csv', index=True)
        self._desempenho.to_csv(r'..\data\sistema_challenge\rendimento_portfolio.csv', index=True)
        self._portfolio.to_csv(r'..\data\sistema_challenge\portfolio.csv', index=True)



    def registrar_compra(self, ativo: str, quantidade: float, preco: float, data: dt = dt.today()) -> None:
        """ 
        Método para registrar uma compra.
        ---------------------------------
        ativo: str
            Nome do symbol (pelo yfinance) do ativo investido

        quantidade: float
            Quantidade de valores adicionados 
        
        preco: float
            Preço unitário da aquisição feita

        data: datetime.datetime (optional)
            Data de aquisição
        """
        assert self._desempenho['disponilidade'].values[-1] > quantidade * preco, "Não há valor em caixa para adquirir o ativo! Operação impossível!"
        self._historico_compras.loc[data.strftime('%d/%m/%Y'), ativo] = preco 
        self._portfolio.loc[data.strftime('%d/%m/%Y'), ativo] = quantidade 

        self._portfolio.ffill(inplace=True) # Garantindo que o resto seja mantido no valor anterior caso seja omisso 

        self._desempenho.loc[data.strftime('%d/%m/%Y'), 'disponilidade'] = self._desempenho['disponilidade'].values[-1] -  quantidade * preco
        self._salvar_registros()
  

    def registrar_venda(self, ativo: str, quantidade: float, preco: float, data: dt = dt.today()) -> None:
        """ 
        Método para registrar uma compra.
        ---------------------------------
        ativo: str
            Nome do symbol (pelo yfinance) do ativo investido

        quantidade: float
            Quantidade de valores adicionados 
        
        preco: float
            Preço unitário da aquisição feita

        data: datetime.datetime (optional)
            Data de aquisição
        """
        assert self._portfolio[ativo].values[-1] > quantidade, "Não há ativo suficiente para a venda! Operação impossível!"

        self._historico_venda.loc[data.strftime('%d/%m/%Y'), ativo] = preco 
        self._portfolio.loc[data.strftime('%d/%m/%Y'), ativo] = quantidade 
        self._desempenho.loc[data.strftime('%d/%m/%Y'), 'disponilidade'] = self._desempenho['disponilidade'].values[-1] +  quantidade * preco
        self._salvar_registros()

    