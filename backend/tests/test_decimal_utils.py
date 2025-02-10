import pytest
from decimal import Decimal, DivisionByZero, InvalidOperation
from app.core.decimal_utils import (
    ZERO, ONE, HUNDRED,
    calculate_monthly_rate,
    calculate_percentage,
    safe_divide,
    quantize_decimal,
    clamp_decimal,
    calculate_compound_interest
)

def test_constants():
    """Test that decimal constants are correctly defined."""
    assert ZERO == Decimal('0')
    assert ONE == Decimal('1')
    assert HUNDRED == Decimal('100')

def test_calculate_monthly_rate():
    """Test monthly rate calculation."""
    assert calculate_monthly_rate(Decimal('12')) == Decimal('1')
    assert calculate_monthly_rate(Decimal('6')) == Decimal('0.5')
    
    # Test cache hit
    result1 = calculate_monthly_rate(Decimal('12'))
    result2 = calculate_monthly_rate(Decimal('12'))
    assert result1 is result2  # Should return cached value

def test_calculate_percentage():
    """Test percentage calculation."""
    assert calculate_percentage(Decimal('100'), Decimal('10')) == Decimal('10.00')
    assert calculate_percentage(Decimal('50'), Decimal('20')) == Decimal('10.00')
    assert calculate_percentage(Decimal('1000'), Decimal('5')) == Decimal('50.00')

def test_safe_divide():
    """Test safe division with error handling."""
    assert safe_divide(Decimal('10'), Decimal('2')) == Decimal('5.00')
    assert safe_divide(Decimal('0'), Decimal('5')) == Decimal('0.00')
    
    # Test division by zero
    assert safe_divide(Decimal('10'), ZERO) == ZERO
    assert safe_divide(Decimal('10'), ZERO, default=Decimal('999')) == Decimal('999')

def test_quantize_decimal():
    """Test decimal quantization."""
    assert quantize_decimal(Decimal('10.1234')) == Decimal('10.12')
    assert quantize_decimal(Decimal('10.1234'), places=3) == Decimal('10.123')
    assert quantize_decimal(Decimal('10.1'), places=4) == Decimal('10.1000')

def test_clamp_decimal():
    """Test decimal value clamping."""
    assert clamp_decimal(Decimal('5'), Decimal('0'), Decimal('10')) == Decimal('5')
    assert clamp_decimal(Decimal('-5'), Decimal('0'), Decimal('10')) == Decimal('0')
    assert clamp_decimal(Decimal('15'), Decimal('0'), Decimal('10')) == Decimal('10')

def test_calculate_compound_interest():
    principal = Decimal('1000.00')
    rate = Decimal('10.00')  # 10% annual rate
    time = 1  # 1 year
    
    result = calculate_compound_interest(principal, rate, time)
    
    # With monthly compounding over 1 year at 10% APR
    # Final amount should be more than 1100 (simple interest)
    assert result.quantize(Decimal('0.01')) > Decimal('1100.00')
    
    # Test with zero rate
    assert calculate_compound_interest(principal, ZERO, time) == principal
    
    # Test with zero principal
    assert calculate_compound_interest(ZERO, rate, time) == ZERO

def test_edge_cases():
    """Test edge cases and error conditions."""
    # Zero values
    assert calculate_percentage(ZERO, Decimal('50')) == ZERO
    assert calculate_percentage(Decimal('100'), ZERO) == ZERO
    
    # Very small values
    small_value = Decimal('0.0001')
    assert quantize_decimal(small_value) == Decimal('0.00')
    
    # Very large values
    large_value = Decimal('1000000000')
    assert calculate_percentage(large_value, Decimal('1')).quantize(Decimal('0.01')) == Decimal('10000000.00')

def test_precision_handling():
    """Test handling of decimal precision."""
    value = Decimal('100.12345')
    
    # Default precision (2 places)
    assert len(str(quantize_decimal(value)).split('.')[1]) == 2
    
    # Custom precision
    assert len(str(quantize_decimal(value, places=4)).split('.')[1]) == 4
    
    # Percentage calculation should maintain 2 decimal places
    result = calculate_percentage(value, Decimal('10'))
    assert len(str(result).split('.')[1]) == 2 