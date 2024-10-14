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
        
        previsao = self.modelo.predict(tipo='preco') 
        compras_possiveis = self._checar_ordem_compra(previsao)
        vendas_possiveis = self._checar_ordem_venda(previsao)



    def _checar_ordem_compra(self, previsao):
        """ 
        Método para checar se há ordem de compra (Não chega a verificar o risco)
        ----------------------------------------
        a. Adquirir um ativo caso as seguintes condições sejam satisfeitas:  
         
            i. Modelo prevê aumento de preço para pelo menos 5 dias seguintes; 

            ii. Os indicadores de reversão e o comportamento do volume não estejam 
            conclusivos quanto à condição de sobrecomprado. Para isso, será considerado 
            condição de sobrevendido caso o volume esteja em redução (beta negativo em 
            regressão linear) e o indicador de reversão (“estocástico”) indique sobrecompra 
            (valores acima de 70). A presença de uma linha de resistência reforça a 
            conclusão. 

            iii. O risco geral da carteira não esteja acima de 30% do valor total da carteira; e 

            iv. O risco do ativo não seja superior a 6% do valor total da carteira
        
        """
        ativos_p_compras = []
        for ticker in self.portfolio.columns:
            # Obter indicador de reversão e comportamento do volume dos últimos dias para os dados OHLCV
            dados = self.dados.dados[ticker][['Close', 'MACDVolume', '%K', '%D', 'ATR']]

            # Obter previsão 
            previsao_ticker = previsao[ticker]

            # Primeiro filtro: indicadores não concluam sobre situação de comprendido
            perda_confianca = (dados.loc[dados.index[-1], 'MACDVolume'] < dados.loc[dados.index[-2], 'MACDVolume']) and (dados.loc[dados.index[-2], 'MACDVolume'] < dados.loc[dados.index[-3], 'MACDVolume'])
            aumento_preco = (dados.loc[dados.index[-1], 'Close'] > dados.loc[dados.index[-2], 'Close']) and (dados.loc[dados.index[-2], 'Close'] > dados.loc[dados.index[-3], 'Close'])
            estocastico_sobrecomprado = (dados.loc[dados.index[-1], '%K'] > 90) and (dados.loc[dados.index[-1], '%D'] > 90) 

            if perda_confianca & aumento_preco & estocastico_sobrecomprado:
                continue # Retira a possibilidade de verificar se há previsão de subida 

            # Segundo filtro: modelo prevê aumento de preço para pelo menos 5 dias seguintes
            tendencia_subida = True 

            for i in range(1, 5):
                tendencia_subida = tendencia_subida & (previsao_ticker[-i] > tendencia_subida[-i-1])

            if not tendencia_subida:
                continue # Retira ativos que não estejam com previsão de subida 
            
            # Adicionando ativo na ordem de compra 
            ativos_p_compras.append(ticker)

        return ativos_p_compras


