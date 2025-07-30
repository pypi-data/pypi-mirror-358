
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  
def accdist(ctx: Ctx) -> List[float]:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """

    return _lib.Incr_fn_accdist_a4764c(ctx).collect()

class AccdistLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Accdist:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_accdist_a4764c(ctx)
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def cum(ctx: Ctx, src: List[float]) -> List[float]:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """

    return _lib.Incr_fn_cum_3f3f23(ctx).collect(_1567_src=src)

class CumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cum:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cum_3f3f23(ctx)
        self.locals = CumLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_1567_src=src)
    

def change(ctx: Ctx, src: List[float]) -> List[float]:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """

    return _lib.Incr_fn_change_454afa(ctx).collect(_1569_src=src)

class ChangeLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Change:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_change_454afa(ctx)
        self.locals = ChangeLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_1569_src=src)
    

def barssince(ctx: Ctx, condition: List[bool]) -> List[int]:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """

    return _lib.Incr_fn_barssince_287b95(ctx).collect(_1571_condition=condition)

class BarssinceLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Barssince:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_barssince_287b95(ctx)
        self.locals = BarssinceLocals(self.inner)

    def next(self, condition: bool) -> Optional[int]:
        return self.inner.next(_1571_condition=condition)
    

def roc(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> series<float>`
    """

    return _lib.Incr_fn_roc_d2600f(ctx).collect(_1573_src=src, _1574_length=length)

class RocLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Roc:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_roc_d2600f(ctx)
        self.locals = RocLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1573_src=src, _1574_length=length)
    

def crossover(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_crossover_419cc7(ctx).collect(_1576_source1=source1, _1577_source2=source2)

class CrossoverLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossover:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossover_419cc7(ctx)
        self.locals = CrossoverLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_1576_source1=source1, _1577_source2=source2)
    

def crossunder(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_crossunder_d2dc48(ctx).collect(_1579_source1=source1, _1580_source2=source2)

class CrossunderLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossunder:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossunder_d2dc48(ctx)
        self.locals = CrossunderLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_1579_source1=source1, _1580_source2=source2)
    

def cross(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_cross_8519f5(ctx).collect(_1582_source1=source1, _1583_source2=source2)

class CrossLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Cross:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cross_8519f5(ctx)
        self.locals = CrossLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_1582_source1=source1, _1583_source2=source2)
    

def highestbars(ctx: Ctx, src: List[float], length: Optional[int]) -> List[int]:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """

    return _lib.Incr_fn_highestbars_655803(ctx).collect(_1585_src=src, _1586_length=length)

class HighestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highestbars:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highestbars_655803(ctx)
        self.locals = HighestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[int]:
        return self.inner.next(_1585_src=src, _1586_length=length)
    

def lowestbars(ctx: Ctx, src: List[float], length: Optional[int]) -> List[int]:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """

    return _lib.Incr_fn_lowestbars_676487(ctx).collect(_1588_src=src, _1589_length=length)

class LowestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowestbars:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowestbars_676487(ctx)
        self.locals = LowestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[int]:
        return self.inner.next(_1588_src=src, _1589_length=length)
    

def highest(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_highest_f8dff6(ctx).collect(_1591_src=src, _1592_length=length)

class HighestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highest:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highest_f8dff6(ctx)
        self.locals = HighestLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1591_src=src, _1592_length=length)
    

def lowest(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_lowest_c17bb7(ctx).collect(_1594_src=src, _1595_length=length)

class LowestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowest:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowest_c17bb7(ctx)
        self.locals = LowestLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1594_src=src, _1595_length=length)
    

def swma(ctx: Ctx, src: List[float]) -> List[float]:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """

    return _lib.Incr_fn_swma_410adb(ctx).collect(_1597_src=src)

class SwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Swma:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_swma_410adb(ctx)
        self.locals = SwmaLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_1597_src=src)
    

def sma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_sma_d1e095(ctx).collect(_1599_src=src, _1600_length=length)

class SmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Sma:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_sma_d1e095(ctx)
        self.locals = SmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1599_src=src, _1600_length=length)
    

def ema(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_ema_a30eb5(ctx).collect(_1602_src=src, _1603_length=length)

class EmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Ema:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ema_a30eb5(ctx)
        self.locals = EmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1602_src=src, _1603_length=length)
    

def rma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_rma_680f76(ctx).collect(_1605_src=src, _1606_length=length)

class RmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rma:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rma_680f76(ctx)
        self.locals = RmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1605_src=src, _1606_length=length)
    

def wma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_wma_d6862c(ctx).collect(_1608_src=src, _1609_length=length)

class WmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Wma:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_wma_d6862c(ctx)
        self.locals = WmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1608_src=src, _1609_length=length)
    

def lwma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_lwma_f0eb76(ctx).collect(_1611_src=src, _1612_length=length)

class LwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Lwma:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lwma_f0eb76(ctx)
        self.locals = LwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1611_src=src, _1612_length=length)
    

def hma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_hma_36b6f5(ctx).collect(_1614_src=src, _1615_length=length)

class HmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Hma:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_hma_36b6f5(ctx)
        self.locals = HmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1614_src=src, _1615_length=length)
    

def vwma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_vwma_33a74b(ctx).collect(_1617_src=src, _1618_length=length)

class VwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Vwma:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vwma_33a74b(ctx)
        self.locals = VwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1617_src=src, _1618_length=length)
    

def dev(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_dev_617b6a(ctx).collect(_1620_src=src, _1621_length=length)

class DevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dev:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dev_617b6a(ctx)
        self.locals = DevLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1620_src=src, _1621_length=length)
    

def tr(ctx: Ctx, handle_na: Optional[bool]) -> List[float]:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """

    return _lib.Incr_fn_tr_ead3db(ctx).collect(_1623_handle_na=handle_na)

class TrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Tr:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tr_ead3db(ctx)
        self.locals = TrLocals(self.inner)

    def next(self, handle_na: Optional[bool]) -> Optional[float]:
        return self.inner.next(_1623_handle_na=handle_na)
    

def atr(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """

    return _lib.Incr_fn_atr_566c37(ctx).collect(_1625_length=length)

class AtrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Atr:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_atr_566c37(ctx)
        self.locals = AtrLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1625_length=length)
    

def rsi(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_rsi_bf09ad(ctx).collect(_1627_src=src, _1628_length=length)

class RsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rsi:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rsi_bf09ad(ctx)
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1627_src=src, _1628_length=length)
    

def cci(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_cci_bf1a8a(ctx).collect(_1630_src=src, _1631_length=length)

class CciLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cci:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cci_bf1a8a(ctx)
        self.locals = CciLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1630_src=src, _1631_length=length)
    

def stdev(ctx: Ctx, src: List[float], length: int, biased: Optional[bool]) -> List[float]:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """

    return _lib.Incr_fn_stdev_5ec273(ctx).collect(_1633_src=src, _1634_length=length, _1635_biased=biased)

class StdevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Stdev:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stdev_5ec273(ctx)
        self.locals = StdevLocals(self.inner)

    def next(self, src: float, length: int, biased: Optional[bool]) -> Optional[float]:
        return self.inner.next(_1633_src=src, _1634_length=length, _1635_biased=biased)
    

def aroon(ctx: Ctx, length: Optional[int]) -> Tuple[float, float]:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """

    return _lib.Incr_fn_aroon_e31363(ctx).collect(_1637_length=length)

class AroonLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Aroon:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_aroon_e31363(ctx)
        self.locals = AroonLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_1637_length=length)
    

def supertrend(ctx: Ctx, src: List[float], factor: float, atr_period: int) -> Tuple[float, int]:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """

    return _lib.Incr_fn_supertrend_63e53f(ctx).collect(_1639_src=src, _1640_factor=factor, _1641_atr_period=atr_period)

class SupertrendLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Supertrend:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_supertrend_63e53f(ctx)
        self.locals = SupertrendLocals(self.inner)

    def next(self, src: float, factor: float, atr_period: int) -> Optional[Tuple[float, int]]:
        return self.inner.next(_1639_src=src, _1640_factor=factor, _1641_atr_period=atr_period)
    

def awesome_oscillator(ctx: Ctx, src: List[float], slow_length: Optional[int], fast_length: Optional[int]) -> List[float]:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """

    return _lib.Incr_fn_awesome_oscillator_e77118(ctx).collect(_1643_src=src, _1644_slow_length=slow_length, _1645_fast_length=fast_length)

class AwesomeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AwesomeOscillator:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_awesome_oscillator_e77118(ctx)
        self.locals = AwesomeOscillatorLocals(self.inner)

    def next(self, src: float, slow_length: Optional[int], fast_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1643_src=src, _1644_slow_length=slow_length, _1645_fast_length=fast_length)
    

def balance_of_power(ctx: Ctx) -> List[float]:
    """
Balance of power between buyers and sellers

`balance_of_power() -> series<float>`
    """

    return _lib.Incr_fn_balance_of_power_2ac0aa(ctx).collect()

class BalanceOfPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class BalanceOfPower:
    """
Balance of power between buyers and sellers

`balance_of_power() -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_balance_of_power_2ac0aa(ctx)
        self.locals = BalanceOfPowerLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def bollinger_bands_pct_b(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> List[float]:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> series<float>`
    """

    return _lib.Incr_fn_bollinger_bands_pct_b_dc0f82(ctx).collect(_1650_src=src, _1651_length=length, _1652_mult=mult)

class BollingerBandsPctBLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def bbr(self) -> float:
        return self.__inner._1657_bbr()
  
      

class BollingerBandsPctB:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_pct_b_dc0f82(ctx)
        self.locals = BollingerBandsPctBLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[float]:
        return self.inner.next(_1650_src=src, _1651_length=length, _1652_mult=mult)
    

def bollinger_bands_width(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> List[float]:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """

    return _lib.Incr_fn_bollinger_bands_width_d24b3e(ctx).collect(_1659_src=src, _1660_length=length, _1661_mult=mult)

class BollingerBandsWidthLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsWidth:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_width_d24b3e(ctx)
        self.locals = BollingerBandsWidthLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[float]:
        return self.inner.next(_1659_src=src, _1660_length=length, _1661_mult=mult)
    

def bollinger_bands(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> Tuple[float, float]:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """

    return _lib.Incr_fn_bollinger_bands_a6f5b7(ctx).collect(_1668_src=src, _1669_length=length, _1670_mult=mult)

class BollingerBandsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBands:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_a6f5b7(ctx)
        self.locals = BollingerBandsLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_1668_src=src, _1669_length=length, _1670_mult=mult)
    

def chaikin_money_flow(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """

    return _lib.Incr_fn_chaikin_money_flow_eec01c(ctx).collect(_1676_length=length)

class ChaikinMoneyFlowLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def cumVol(self) -> float:
        return self.__inner._1677_cumVol()
  

    @property
    def ad(self) -> float:
        return self.__inner._1678_ad()
  
      

class ChaikinMoneyFlow:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chaikin_money_flow_eec01c(ctx)
        self.locals = ChaikinMoneyFlowLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1676_length=length)
    

def chande_kroll_stop(ctx: Ctx, atr_length: Optional[int], atr_coeff: Optional[float], stop_length: Optional[int]) -> Tuple[float, float]:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """

    return _lib.Incr_fn_chande_kroll_stop_a9bb8b(ctx).collect(_1681_atr_length=atr_length, _1682_atr_coeff=atr_coeff, _1683_stop_length=stop_length)

class ChandeKrollStopLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChandeKrollStop:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chande_kroll_stop_a9bb8b(ctx)
        self.locals = ChandeKrollStopLocals(self.inner)

    def next(self, atr_length: Optional[int], atr_coeff: Optional[float], stop_length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_1681_atr_length=atr_length, _1682_atr_coeff=atr_coeff, _1683_stop_length=stop_length)
    

def choppiness_index(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """

    return _lib.Incr_fn_choppiness_index_9b49e3(ctx).collect(_1692_length=length)

class ChoppinessIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChoppinessIndex:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_choppiness_index_9b49e3(ctx)
        self.locals = ChoppinessIndexLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1692_length=length)
    

def coppock_curve(ctx: Ctx, src: List[float], wma_length: Optional[int], long_roc_length: Optional[int], short_roc_length: Optional[int]) -> List[float]:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """

    return _lib.Incr_fn_coppock_curve_bb7ce8(ctx).collect(_1694_src=src, _1695_wma_length=wma_length, _1696_long_roc_length=long_roc_length, _1697_short_roc_length=short_roc_length)

class CoppockCurveLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class CoppockCurve:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_coppock_curve_bb7ce8(ctx)
        self.locals = CoppockCurveLocals(self.inner)

    def next(self, src: float, wma_length: Optional[int], long_roc_length: Optional[int], short_roc_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1694_src=src, _1695_wma_length=wma_length, _1696_long_roc_length=long_roc_length, _1697_short_roc_length=short_roc_length)
    

def donchian_channel(ctx: Ctx, src: List[float], length: Optional[int]) -> Tuple[float, float, float]:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """

    return _lib.Incr_fn_donchian_channel_ca439c(ctx).collect(_1699_src=src, _1700_length=length)

class DonchianChannelLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DonchianChannel:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_donchian_channel_ca439c(ctx)
        self.locals = DonchianChannelLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[Tuple[float, float, float]]:
        return self.inner.next(_1699_src=src, _1700_length=length)
    

def macd(ctx: Ctx, src: List[float], short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """

    return _lib.Incr_fn_macd_3591e2(ctx).collect(_1705_src=src, _1706_short_length=short_length, _1707_long_length=long_length)

class MacdLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Macd:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_macd_3591e2(ctx)
        self.locals = MacdLocals(self.inner)

    def next(self, src: float, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1705_src=src, _1706_short_length=short_length, _1707_long_length=long_length)
    

def price_oscillator(ctx: Ctx, src: List[float], short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """

    return _lib.Incr_fn_price_oscillator_572b32(ctx).collect(_1710_src=src, _1711_short_length=short_length, _1712_long_length=long_length)

class PriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class PriceOscillator:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_price_oscillator_572b32(ctx)
        self.locals = PriceOscillatorLocals(self.inner)

    def next(self, src: float, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1710_src=src, _1711_short_length=short_length, _1712_long_length=long_length)
    

def relative_vigor_index(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """

    return _lib.Incr_fn_relative_vigor_index_a3b5d2(ctx).collect(_1717_length=length)

class RelativeVigorIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVigorIndex:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_vigor_index_a3b5d2(ctx)
        self.locals = RelativeVigorIndexLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1717_length=length)
    

def relative_volatility_index(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_relative_volatility_index_4f9aed(ctx).collect(_1719_src=src, _1720_length=length)

class RelativeVolatilityIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVolatilityIndex:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_volatility_index_4f9aed(ctx)
        self.locals = RelativeVolatilityIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1719_src=src, _1720_length=length)
    

def ultimate_oscillator(ctx: Ctx, fast_length: Optional[int], medium_length: Optional[int], slow_length: Optional[int]) -> List[float]:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """

    return _lib.Incr_fn_ultimate_oscillator_260197(ctx).collect(_1730_fast_length=fast_length, _1731_medium_length=medium_length, _1732_slow_length=slow_length)

class UltimateOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def bp(self) -> float:
        return self.__inner._1735_bp()
  
      

class UltimateOscillator:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ultimate_oscillator_260197(ctx)
        self.locals = UltimateOscillatorLocals(self.inner)

    def next(self, fast_length: Optional[int], medium_length: Optional[int], slow_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1730_fast_length=fast_length, _1731_medium_length=medium_length, _1732_slow_length=slow_length)
    

def volume_oscillator(ctx: Ctx, short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """

    return _lib.Incr_fn_volume_oscillator_390e22(ctx).collect(_1742_short_length=short_length, _1743_long_length=long_length)

class VolumeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VolumeOscillator:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_volume_oscillator_390e22(ctx)
        self.locals = VolumeOscillatorLocals(self.inner)

    def next(self, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1742_short_length=short_length, _1743_long_length=long_length)
    

def vortex_indicator(ctx: Ctx, length: Optional[int]) -> Tuple[float, float]:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """

    return _lib.Incr_fn_vortex_indicator_b36981(ctx).collect(_1748_length=length)

class VortexIndicatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VortexIndicator:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vortex_indicator_b36981(ctx)
        self.locals = VortexIndicatorLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_1748_length=length)
    

def williams_pct_r(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> series<float>`
    """

    return _lib.Incr_fn_williams_pct_r_9e3c11(ctx).collect(_1755_src=src, _1756_length=length)

class WilliamsPctRLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def wpctr(self) -> float:
        return self.__inner._1759_wpctr()
  
      

class WilliamsPctR:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_williams_pct_r_9e3c11(ctx)
        self.locals = WilliamsPctRLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_1755_src=src, _1756_length=length)
    
          