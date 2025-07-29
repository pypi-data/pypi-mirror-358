import json
from decimal import Decimal

from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)

def decimal_default_proc(obj):
    """"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def to_json(value: dict) -> str:
    """"""
    return json.dumps(value, ensure_ascii=False, default=decimal_default_proc)

def load_json(value: str) -> object:
    """"""
    if value and isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception as e:
            logger.warning(e)

    return value

def bin2signed(bin_data: str) -> int:  # {{{
    if bin_data[0:1] == '1':
        return -int(bin_data[1:], 2)
    else:
        return int(bin_data, 2)  # }}}

def gather_registers_value(registers: list, base=16) -> int:
    '''
    >>> gather_registers_value([0], base=2)
        0
    >>> gather_registers_value([1], base=2)
        1
    >>> gather_registers_value([1, 0], base=2)
        4
    >>> gather_registers_value([0b01, 0b0], base=2)
        4
    >>> gather_registers_value([0b01, 0b00], base=2)
        4
    >>> gather_registers_value([1, 0], base=4)
        16
    >>> gather_registers_value([1, 1], base=4)
        17
    >>> gather_registers_value([0b0001, 0b0000], base=4)
        16
    >>> gather_registers_value([1, 1, 1], base=4)
        273
    >>> gather_registers_value([0, 0, 1], base=8)
        1
    >>> gather_registers_value([0, 1, 1], base=8)
        257
    >>> gather_registers_value([1, 0, 0], base=8)
        65536
    >>> gather_registers_value([0, 0, 1], base=16)
        1
    >>> gather_registers_value([0, 1, 1], base=16)
        65537
    >>> gather_registers_value([1, 0, 0], base=16)
        4294967296
    '''
    return sum(
        bits << (idx * base)
            for idx, bits in enumerate(reversed(registers))
        )

def scatter_value_to_registers(value, base=16) ->list:
    '''
    # opposite of gather_registers_value()
    >>> scatter_value_to_registers(1)
        [1]
    >>> scatter_value_to_registers(65537)
        [1, 1]
    >>> scatter_value_to_registers(4294967296)
        [1, 0, 0]
    '''
    result = []
    while value > 0:
        result.append(value & (2 ** base - 1))
        value >>= base
    if len(result) == 0:
        result = [0]
    return list(reversed(result))

def twos_comp(val: int, bits: int) -> int:
    """compute the 2's complement of int value val"""
    """
    >>> twos_comp(0, 8)
    0
    >>> twos_comp(1, 8)
    1
    >>> twos_comp(127, 8)
    127
    >>> twos_comp(128, 8)
    -128
    >>> twos_comp(129, 8)
    -127
    >>> twos_comp(255, 8)
    -1
    """
    if val & (0b1 << (bits - 1)):    # leftmost bit is set
        return val - (1 << bits)
    else:
        return val

def is_nth_bit_set(num: int, n: int):
    return (num >> n) & 1 == 1
