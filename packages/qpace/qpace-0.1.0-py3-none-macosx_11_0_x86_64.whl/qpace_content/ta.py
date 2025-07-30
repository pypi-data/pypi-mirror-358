
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  
def accdist(ctx: Ctx) -> List[float]:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """

    return _lib.Incr_fn_accdist_2099a0(ctx).collect()

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
        self.inner = _lib.Incr_fn_accdist_2099a0(ctx)
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def cum(ctx: Ctx, src: List[float]) -> List[float]:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """

    return _lib.Incr_fn_cum_896f4f(ctx).collect(_44176_src=src)

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
        self.inner = _lib.Incr_fn_cum_896f4f(ctx)
        self.locals = CumLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_44176_src=src)
    

def change(ctx: Ctx, src: List[float]) -> List[float]:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """

    return _lib.Incr_fn_change_a45bf8(ctx).collect(_44178_src=src)

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
        self.inner = _lib.Incr_fn_change_a45bf8(ctx)
        self.locals = ChangeLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_44178_src=src)
    

def barssince(ctx: Ctx, condition: List[bool]) -> List[int]:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """

    return _lib.Incr_fn_barssince_f2eac5(ctx).collect(_44180_condition=condition)

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
        self.inner = _lib.Incr_fn_barssince_f2eac5(ctx)
        self.locals = BarssinceLocals(self.inner)

    def next(self, condition: bool) -> Optional[int]:
        return self.inner.next(_44180_condition=condition)
    

def roc(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> series<float>`
    """

    return _lib.Incr_fn_roc_e80340(ctx).collect(_44182_src=src, _44183_length=length)

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
        self.inner = _lib.Incr_fn_roc_e80340(ctx)
        self.locals = RocLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44182_src=src, _44183_length=length)
    

def crossover(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_crossover_b556c1(ctx).collect(_44185_source1=source1, _44186_source2=source2)

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
        self.inner = _lib.Incr_fn_crossover_b556c1(ctx)
        self.locals = CrossoverLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_44185_source1=source1, _44186_source2=source2)
    

def crossunder(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_crossunder_4d8467(ctx).collect(_44188_source1=source1, _44189_source2=source2)

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
        self.inner = _lib.Incr_fn_crossunder_4d8467(ctx)
        self.locals = CrossunderLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_44188_source1=source1, _44189_source2=source2)
    

def cross(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_cross_fded64(ctx).collect(_44191_source1=source1, _44192_source2=source2)

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
        self.inner = _lib.Incr_fn_cross_fded64(ctx)
        self.locals = CrossLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_44191_source1=source1, _44192_source2=source2)
    

def highestbars(ctx: Ctx, src: List[float], length: Optional[int]) -> List[int]:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """

    return _lib.Incr_fn_highestbars_d4c833(ctx).collect(_44194_src=src, _44195_length=length)

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
        self.inner = _lib.Incr_fn_highestbars_d4c833(ctx)
        self.locals = HighestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[int]:
        return self.inner.next(_44194_src=src, _44195_length=length)
    

def lowestbars(ctx: Ctx, src: List[float], length: Optional[int]) -> List[int]:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """

    return _lib.Incr_fn_lowestbars_287852(ctx).collect(_44197_src=src, _44198_length=length)

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
        self.inner = _lib.Incr_fn_lowestbars_287852(ctx)
        self.locals = LowestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[int]:
        return self.inner.next(_44197_src=src, _44198_length=length)
    

def highest(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_highest_a0297e(ctx).collect(_44200_src=src, _44201_length=length)

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
        self.inner = _lib.Incr_fn_highest_a0297e(ctx)
        self.locals = HighestLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44200_src=src, _44201_length=length)
    

def lowest(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_lowest_b8a15b(ctx).collect(_44203_src=src, _44204_length=length)

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
        self.inner = _lib.Incr_fn_lowest_b8a15b(ctx)
        self.locals = LowestLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44203_src=src, _44204_length=length)
    

def swma(ctx: Ctx, src: List[float]) -> List[float]:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """

    return _lib.Incr_fn_swma_7e3bd0(ctx).collect(_44206_src=src)

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
        self.inner = _lib.Incr_fn_swma_7e3bd0(ctx)
        self.locals = SwmaLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_44206_src=src)
    

def sma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_sma_4aef8b(ctx).collect(_44208_src=src, _44209_length=length)

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
        self.inner = _lib.Incr_fn_sma_4aef8b(ctx)
        self.locals = SmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44208_src=src, _44209_length=length)
    

def ema(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_ema_6d5e6f(ctx).collect(_44211_src=src, _44212_length=length)

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
        self.inner = _lib.Incr_fn_ema_6d5e6f(ctx)
        self.locals = EmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44211_src=src, _44212_length=length)
    

def rma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_rma_4cc0d2(ctx).collect(_44214_src=src, _44215_length=length)

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
        self.inner = _lib.Incr_fn_rma_4cc0d2(ctx)
        self.locals = RmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44214_src=src, _44215_length=length)
    

def wma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_wma_5c25e5(ctx).collect(_44217_src=src, _44218_length=length)

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
        self.inner = _lib.Incr_fn_wma_5c25e5(ctx)
        self.locals = WmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44217_src=src, _44218_length=length)
    

def lwma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_lwma_ce7e21(ctx).collect(_44220_src=src, _44221_length=length)

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
        self.inner = _lib.Incr_fn_lwma_ce7e21(ctx)
        self.locals = LwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44220_src=src, _44221_length=length)
    

def hma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_hma_13e2e6(ctx).collect(_44223_src=src, _44224_length=length)

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
        self.inner = _lib.Incr_fn_hma_13e2e6(ctx)
        self.locals = HmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44223_src=src, _44224_length=length)
    

def vwma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_vwma_f17ee5(ctx).collect(_44226_src=src, _44227_length=length)

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
        self.inner = _lib.Incr_fn_vwma_f17ee5(ctx)
        self.locals = VwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44226_src=src, _44227_length=length)
    

def dev(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_dev_f1ab03(ctx).collect(_44229_src=src, _44230_length=length)

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
        self.inner = _lib.Incr_fn_dev_f1ab03(ctx)
        self.locals = DevLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44229_src=src, _44230_length=length)
    

def tr(ctx: Ctx, handle_na: Optional[bool]) -> List[float]:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """

    return _lib.Incr_fn_tr_1e0418(ctx).collect(_44232_handle_na=handle_na)

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
        self.inner = _lib.Incr_fn_tr_1e0418(ctx)
        self.locals = TrLocals(self.inner)

    def next(self, handle_na: Optional[bool]) -> Optional[float]:
        return self.inner.next(_44232_handle_na=handle_na)
    

def atr(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """

    return _lib.Incr_fn_atr_b44469(ctx).collect(_44234_length=length)

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
        self.inner = _lib.Incr_fn_atr_b44469(ctx)
        self.locals = AtrLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44234_length=length)
    

def rsi(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_rsi_9aff67(ctx).collect(_44236_src=src, _44237_length=length)

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
        self.inner = _lib.Incr_fn_rsi_9aff67(ctx)
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44236_src=src, _44237_length=length)
    

def cci(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_cci_2a41e1(ctx).collect(_44239_src=src, _44240_length=length)

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
        self.inner = _lib.Incr_fn_cci_2a41e1(ctx)
        self.locals = CciLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44239_src=src, _44240_length=length)
    

def stdev(ctx: Ctx, src: List[float], length: int, biased: Optional[bool]) -> List[float]:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """

    return _lib.Incr_fn_stdev_bc8ef1(ctx).collect(_44242_src=src, _44243_length=length, _44244_biased=biased)

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
        self.inner = _lib.Incr_fn_stdev_bc8ef1(ctx)
        self.locals = StdevLocals(self.inner)

    def next(self, src: float, length: int, biased: Optional[bool]) -> Optional[float]:
        return self.inner.next(_44242_src=src, _44243_length=length, _44244_biased=biased)
    

def aroon(ctx: Ctx, length: Optional[int]) -> Tuple[float, float]:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """

    return _lib.Incr_fn_aroon_7bd46d(ctx).collect(_44246_length=length)

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
        self.inner = _lib.Incr_fn_aroon_7bd46d(ctx)
        self.locals = AroonLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_44246_length=length)
    

def supertrend(ctx: Ctx, src: List[float], factor: float, atr_period: int) -> Tuple[float, int]:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """

    return _lib.Incr_fn_supertrend_8e16d2(ctx).collect(_44248_src=src, _44249_factor=factor, _44250_atr_period=atr_period)

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
        self.inner = _lib.Incr_fn_supertrend_8e16d2(ctx)
        self.locals = SupertrendLocals(self.inner)

    def next(self, src: float, factor: float, atr_period: int) -> Optional[Tuple[float, int]]:
        return self.inner.next(_44248_src=src, _44249_factor=factor, _44250_atr_period=atr_period)
    

def awesome_oscillator(ctx: Ctx, src: List[float], slow_length: Optional[int], fast_length: Optional[int]) -> List[float]:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """

    return _lib.Incr_fn_awesome_oscillator_3d4871(ctx).collect(_44252_src=src, _44253_slow_length=slow_length, _44254_fast_length=fast_length)

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
        self.inner = _lib.Incr_fn_awesome_oscillator_3d4871(ctx)
        self.locals = AwesomeOscillatorLocals(self.inner)

    def next(self, src: float, slow_length: Optional[int], fast_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44252_src=src, _44253_slow_length=slow_length, _44254_fast_length=fast_length)
    

def balance_of_power(ctx: Ctx) -> List[float]:
    """
Balance of power between buyers and sellers

`balance_of_power() -> series<float>`
    """

    return _lib.Incr_fn_balance_of_power_a3f0bc(ctx).collect()

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
        self.inner = _lib.Incr_fn_balance_of_power_a3f0bc(ctx)
        self.locals = BalanceOfPowerLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def bollinger_bands_pct_b(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> List[float]:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> series<float>`
    """

    return _lib.Incr_fn_bollinger_bands_pct_b_746fee(ctx).collect(_44259_src=src, _44260_length=length, _44261_mult=mult)

class BollingerBandsPctBLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def bbr(self) -> float:
        return self.__inner._44266_bbr()
  
      

class BollingerBandsPctB:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_pct_b_746fee(ctx)
        self.locals = BollingerBandsPctBLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[float]:
        return self.inner.next(_44259_src=src, _44260_length=length, _44261_mult=mult)
    

def bollinger_bands_width(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> List[float]:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """

    return _lib.Incr_fn_bollinger_bands_width_fccb94(ctx).collect(_44268_src=src, _44269_length=length, _44270_mult=mult)

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
        self.inner = _lib.Incr_fn_bollinger_bands_width_fccb94(ctx)
        self.locals = BollingerBandsWidthLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[float]:
        return self.inner.next(_44268_src=src, _44269_length=length, _44270_mult=mult)
    

def bollinger_bands(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> Tuple[float, float]:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """

    return _lib.Incr_fn_bollinger_bands_f91d52(ctx).collect(_44277_src=src, _44278_length=length, _44279_mult=mult)

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
        self.inner = _lib.Incr_fn_bollinger_bands_f91d52(ctx)
        self.locals = BollingerBandsLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_44277_src=src, _44278_length=length, _44279_mult=mult)
    

def chaikin_money_flow(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """

    return _lib.Incr_fn_chaikin_money_flow_02eafa(ctx).collect(_44285_length=length)

class ChaikinMoneyFlowLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def cumVol(self) -> float:
        return self.__inner._44286_cumVol()
  

    @property
    def ad(self) -> float:
        return self.__inner._44287_ad()
  
      

class ChaikinMoneyFlow:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chaikin_money_flow_02eafa(ctx)
        self.locals = ChaikinMoneyFlowLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44285_length=length)
    

def chande_kroll_stop(ctx: Ctx, atr_length: Optional[int], atr_coeff: Optional[float], stop_length: Optional[int]) -> Tuple[float, float]:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """

    return _lib.Incr_fn_chande_kroll_stop_488b8c(ctx).collect(_44290_atr_length=atr_length, _44291_atr_coeff=atr_coeff, _44292_stop_length=stop_length)

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
        self.inner = _lib.Incr_fn_chande_kroll_stop_488b8c(ctx)
        self.locals = ChandeKrollStopLocals(self.inner)

    def next(self, atr_length: Optional[int], atr_coeff: Optional[float], stop_length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_44290_atr_length=atr_length, _44291_atr_coeff=atr_coeff, _44292_stop_length=stop_length)
    

def choppiness_index(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """

    return _lib.Incr_fn_choppiness_index_3b62e9(ctx).collect(_44301_length=length)

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
        self.inner = _lib.Incr_fn_choppiness_index_3b62e9(ctx)
        self.locals = ChoppinessIndexLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44301_length=length)
    

def coppock_curve(ctx: Ctx, src: List[float], wma_length: Optional[int], long_roc_length: Optional[int], short_roc_length: Optional[int]) -> List[float]:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """

    return _lib.Incr_fn_coppock_curve_2ee552(ctx).collect(_44303_src=src, _44304_wma_length=wma_length, _44305_long_roc_length=long_roc_length, _44306_short_roc_length=short_roc_length)

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
        self.inner = _lib.Incr_fn_coppock_curve_2ee552(ctx)
        self.locals = CoppockCurveLocals(self.inner)

    def next(self, src: float, wma_length: Optional[int], long_roc_length: Optional[int], short_roc_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44303_src=src, _44304_wma_length=wma_length, _44305_long_roc_length=long_roc_length, _44306_short_roc_length=short_roc_length)
    

def donchian_channel(ctx: Ctx, src: List[float], length: Optional[int]) -> Tuple[float, float, float]:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """

    return _lib.Incr_fn_donchian_channel_1dd5d0(ctx).collect(_44308_src=src, _44309_length=length)

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
        self.inner = _lib.Incr_fn_donchian_channel_1dd5d0(ctx)
        self.locals = DonchianChannelLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[Tuple[float, float, float]]:
        return self.inner.next(_44308_src=src, _44309_length=length)
    

def macd(ctx: Ctx, src: List[float], short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """

    return _lib.Incr_fn_macd_047fc7(ctx).collect(_44314_src=src, _44315_short_length=short_length, _44316_long_length=long_length)

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
        self.inner = _lib.Incr_fn_macd_047fc7(ctx)
        self.locals = MacdLocals(self.inner)

    def next(self, src: float, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44314_src=src, _44315_short_length=short_length, _44316_long_length=long_length)
    

def price_oscillator(ctx: Ctx, src: List[float], short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """

    return _lib.Incr_fn_price_oscillator_2a944c(ctx).collect(_44319_src=src, _44320_short_length=short_length, _44321_long_length=long_length)

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
        self.inner = _lib.Incr_fn_price_oscillator_2a944c(ctx)
        self.locals = PriceOscillatorLocals(self.inner)

    def next(self, src: float, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44319_src=src, _44320_short_length=short_length, _44321_long_length=long_length)
    

def relative_vigor_index(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """

    return _lib.Incr_fn_relative_vigor_index_b136a1(ctx).collect(_44326_length=length)

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
        self.inner = _lib.Incr_fn_relative_vigor_index_b136a1(ctx)
        self.locals = RelativeVigorIndexLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44326_length=length)
    

def relative_volatility_index(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_relative_volatility_index_558935(ctx).collect(_44328_src=src, _44329_length=length)

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
        self.inner = _lib.Incr_fn_relative_volatility_index_558935(ctx)
        self.locals = RelativeVolatilityIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44328_src=src, _44329_length=length)
    

def ultimate_oscillator(ctx: Ctx, fast_length: Optional[int], medium_length: Optional[int], slow_length: Optional[int]) -> List[float]:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """

    return _lib.Incr_fn_ultimate_oscillator_f67830(ctx).collect(_44339_fast_length=fast_length, _44340_medium_length=medium_length, _44341_slow_length=slow_length)

class UltimateOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def bp(self) -> float:
        return self.__inner._44344_bp()
  
      

class UltimateOscillator:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ultimate_oscillator_f67830(ctx)
        self.locals = UltimateOscillatorLocals(self.inner)

    def next(self, fast_length: Optional[int], medium_length: Optional[int], slow_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44339_fast_length=fast_length, _44340_medium_length=medium_length, _44341_slow_length=slow_length)
    

def volume_oscillator(ctx: Ctx, short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """

    return _lib.Incr_fn_volume_oscillator_e1c88a(ctx).collect(_44351_short_length=short_length, _44352_long_length=long_length)

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
        self.inner = _lib.Incr_fn_volume_oscillator_e1c88a(ctx)
        self.locals = VolumeOscillatorLocals(self.inner)

    def next(self, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44351_short_length=short_length, _44352_long_length=long_length)
    

def vortex_indicator(ctx: Ctx, length: Optional[int]) -> Tuple[float, float]:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """

    return _lib.Incr_fn_vortex_indicator_f90c06(ctx).collect(_44357_length=length)

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
        self.inner = _lib.Incr_fn_vortex_indicator_f90c06(ctx)
        self.locals = VortexIndicatorLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_44357_length=length)
    

def williams_pct_r(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> series<float>`
    """

    return _lib.Incr_fn_williams_pct_r_abbbdc(ctx).collect(_44364_src=src, _44365_length=length)

class WilliamsPctRLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def wpctr(self) -> float:
        return self.__inner._44368_wpctr()
  
      

class WilliamsPctR:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_williams_pct_r_abbbdc(ctx)
        self.locals = WilliamsPctRLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_44364_src=src, _44365_length=length)
    
          