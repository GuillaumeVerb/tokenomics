from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, DivisionByZero
from functools import lru_cache

# Constantes décimales pré-calculées
ZERO = Decimal('0')
ONE = Decimal('1')
TWO = Decimal('2')
FIVE = Decimal('5')
TEN = Decimal('10')
TWELVE = Decimal('12')
HUNDRED = Decimal('100')
THOUSAND = Decimal('1000')

# Pourcentages courants
FIVE_PERCENT = Decimal('0.05')
TEN_PERCENT = Decimal('0.10')
TWENTY_PERCENT = Decimal('0.20')
FIFTY_PERCENT = Decimal('0.50')
NINETY_FIVE_PERCENT = Decimal('0.95')
NINETY_NINE_PERCENT = Decimal('0.99')

@lru_cache(maxsize=128)
def to_decimal(value: str) -> Decimal:
    """Convertit une chaîne en Decimal avec cache."""
    return Decimal(value)

@lru_cache(maxsize=128)
def calculate_monthly_rate(annual_rate: Decimal) -> Decimal:
    """Calcule le taux mensuel à partir d'un taux annuel."""
    return annual_rate / TWELVE

@lru_cache(maxsize=128)
def calculate_percentage(value: Decimal, percentage: Decimal) -> Decimal:
    """Calcule un pourcentage d'une valeur."""
    return (value * percentage / HUNDRED).quantize(Decimal('0.01'))

def safe_divide(numerator: Decimal, denominator: Decimal, default: Decimal = ZERO) -> Decimal:
    """Division sécurisée avec gestion des divisions par zéro."""
    try:
        return (numerator / denominator).quantize(Decimal('0.01'))
    except (DivisionByZero, InvalidOperation):
        return default

def quantize_decimal(value: Decimal, places: int = 2) -> Decimal:
    """Arrondit un Decimal au nombre de décimales spécifié."""
    return value.quantize(Decimal(f'0.{"0" * places}'))

def clamp_decimal(value: Decimal, min_value: Decimal, max_value: Decimal) -> Decimal:
    """Limite une valeur décimale entre min et max."""
    return max(min_value, min(value, max_value))

def calculate_compound_interest(principal: Decimal, rate: Decimal, time: int) -> Decimal:
    """Calculate compound interest with monthly compounding."""
    monthly_rate = calculate_monthly_rate(rate)
    months = time * 12
    return principal * (ONE + monthly_rate) ** Decimal(str(months)) 