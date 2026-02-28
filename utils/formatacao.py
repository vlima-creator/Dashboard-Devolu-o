"""
Módulo de formatação padronizada para valores monetários e percentuais.
Padrão: BRL R$ 132.715,54 e Percentual 21.1%
"""

def formatar_brl(valor):
    """
    Formata valor para padrão BRL: R$ 132.715,54
    
    Args:
        valor: float ou int
        
    Returns:
        str: Valor formatado no padrão brasileiro
    """
    if valor is None or (isinstance(valor, float) and valor != valor):  # NaN check
        return "R$ 0,00"
    
    try:
        valor = float(valor)
        # Formatar com separador de milhares (.) e decimal (,)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"


def formatar_percentual(valor, casas_decimais=1):
    """
    Formata percentual para padrão: 21.1%
    
    Args:
        valor: float (0-100 ou 0-1)
        casas_decimais: int (padrão 1)
        
    Returns:
        str: Percentual formatado
    """
    if valor is None or (isinstance(valor, float) and valor != valor):  # NaN check
        return "0.0%"
    
    try:
        valor = float(valor)
        
        # Se valor está entre 0 e 1, converter para percentual
        if 0 <= valor <= 1:
            valor = valor * 100
        
        # Formatar com ponto decimal
        formato = f"{{:.{casas_decimais}f}}"
        return formato.format(valor) + "%"
    except (ValueError, TypeError):
        return "0.0%"


def formatar_numero(valor, casas_decimais=0):
    """
    Formata número inteiro com separador de milhares.
    
    Args:
        valor: int ou float
        casas_decimais: int (padrão 0)
        
    Returns:
        str: Número formatado
    """
    if valor is None or (isinstance(valor, float) and valor != valor):  # NaN check
        return "0"
    
    try:
        valor = float(valor)
        if casas_decimais == 0:
            return f"{int(valor):,}".replace(",", ".")
        else:
            formato = f"{{:,.{casas_decimais}f}}"
            return formato.format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0"


def validar_valor_monetario(valor):
    """
    Valida se um valor é monetário válido.
    
    Args:
        valor: float ou int
        
    Returns:
        bool: True se válido, False caso contrário
    """
    try:
        float(valor)
        return True
    except (ValueError, TypeError):
        return False


def validar_percentual(valor):
    """
    Valida se um valor é percentual válido (0-100 ou 0-1).
    
    Args:
        valor: float
        
    Returns:
        bool: True se válido, False caso contrário
    """
    try:
        v = float(valor)
        return (0 <= v <= 100) or (0 <= v <= 1)
    except (ValueError, TypeError):
        return False


# Testes
if __name__ == "__main__":
    print("TESTES DE FORMATAÇÃO")
    print("=" * 60)
    
    # Testes BRL
    print("\nTestes BRL:")
    print(f"  1234.56 -> {formatar_brl(1234.56)}")
    print(f"  132715.54 -> {formatar_brl(132715.54)}")
    print(f"  -238500.00 -> {formatar_brl(-238500.00)}")
    print(f"  0 -> {formatar_brl(0)}")
    
    # Testes Percentual
    print("\nTestes Percentual:")
    print(f"  0.815 -> {formatar_percentual(0.815)}")
    print(f"  21.1 -> {formatar_percentual(21.1)}")
    print(f"  0.0815 -> {formatar_percentual(0.0815)}")
    print(f"  100 -> {formatar_percentual(100)}")
    
    # Testes Número
    print("\nTestes Número:")
    print(f"  7861 -> {formatar_numero(7861)}")
    print(f"  132715.54 -> {formatar_numero(132715.54, 2)}")
    
    # Testes Validação
    print("\nTestes Validação:")
    print(f"  Valor 1234.56 válido? {validar_valor_monetario(1234.56)}")
    print(f"  Percentual 0.815 válido? {validar_percentual(0.815)}")
    print(f"  Percentual 150 válido? {validar_percentual(150)}")
