def calcular_retorno_investimento(valor_inicial, valor_final):
    return ((valor_final - valor_inicial) / valor_inicial) * 100

def calcular_juros_compostos(valor_inicial, taxa_juros_anual, anos):
    return valor_inicial * ((1 + (taxa_juros_anual / 100)) ** anos)

def converter_taxa_anual_para_mensal(taxa_anual):
    return (1 + taxa_anual / 100) ** (1 / 12) - 1

def calcular_cagr(valor_inicial, valor_final, anos):
    return ((valor_final / valor_inicial) ** (1 / anos) - 1) * 100
