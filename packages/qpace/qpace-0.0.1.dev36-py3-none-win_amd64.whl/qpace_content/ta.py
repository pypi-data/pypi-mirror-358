
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  
def accdist(ctx: Ctx) -> List[float]:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """

    return _lib.Incr_fn_accdist_ae3590(ctx).collect()

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
        self.inner = _lib.Incr_fn_accdist_ae3590(ctx)
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def cum(ctx: Ctx, src: List[float]) -> List[float]:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """

    return _lib.Incr_fn_cum_c15799(ctx).collect(_4962_src=src)

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
        self.inner = _lib.Incr_fn_cum_c15799(ctx)
        self.locals = CumLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_4962_src=src)
    

def change(ctx: Ctx, src: List[float]) -> List[float]:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """

    return _lib.Incr_fn_change_0e0bb9(ctx).collect(_4964_src=src)

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
        self.inner = _lib.Incr_fn_change_0e0bb9(ctx)
        self.locals = ChangeLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_4964_src=src)
    

def barssince(ctx: Ctx, condition: List[bool]) -> List[int]:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """

    return _lib.Incr_fn_barssince_9ddc0d(ctx).collect(_4966_condition=condition)

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
        self.inner = _lib.Incr_fn_barssince_9ddc0d(ctx)
        self.locals = BarssinceLocals(self.inner)

    def next(self, condition: bool) -> Optional[int]:
        return self.inner.next(_4966_condition=condition)
    

def roc(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> series<float>`
    """

    return _lib.Incr_fn_roc_76cd15(ctx).collect(_4968_src=src, _4969_length=length)

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
        self.inner = _lib.Incr_fn_roc_76cd15(ctx)
        self.locals = RocLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_4968_src=src, _4969_length=length)
    

def crossover(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_crossover_6b13f4(ctx).collect(_4971_source1=source1, _4972_source2=source2)

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
        self.inner = _lib.Incr_fn_crossover_6b13f4(ctx)
        self.locals = CrossoverLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_4971_source1=source1, _4972_source2=source2)
    

def crossunder(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_crossunder_2512e6(ctx).collect(_4974_source1=source1, _4975_source2=source2)

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
        self.inner = _lib.Incr_fn_crossunder_2512e6(ctx)
        self.locals = CrossunderLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_4974_source1=source1, _4975_source2=source2)
    

def cross(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_cross_6cac35(ctx).collect(_4977_source1=source1, _4978_source2=source2)

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
        self.inner = _lib.Incr_fn_cross_6cac35(ctx)
        self.locals = CrossLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_4977_source1=source1, _4978_source2=source2)
    

def highestbars(ctx: Ctx, src: List[float], length: Optional[int]) -> List[int]:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """

    return _lib.Incr_fn_highestbars_e727ec(ctx).collect(_4980_src=src, _4981_length=length)

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
        self.inner = _lib.Incr_fn_highestbars_e727ec(ctx)
        self.locals = HighestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[int]:
        return self.inner.next(_4980_src=src, _4981_length=length)
    

def lowestbars(ctx: Ctx, src: List[float], length: Optional[int]) -> List[int]:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """

    return _lib.Incr_fn_lowestbars_1bbdae(ctx).collect(_4983_src=src, _4984_length=length)

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
        self.inner = _lib.Incr_fn_lowestbars_1bbdae(ctx)
        self.locals = LowestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[int]:
        return self.inner.next(_4983_src=src, _4984_length=length)
    

def highest(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_highest_598164(ctx).collect(_4986_src=src, _4987_length=length)

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
        self.inner = _lib.Incr_fn_highest_598164(ctx)
        self.locals = HighestLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_4986_src=src, _4987_length=length)
    

def lowest(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_lowest_0d3a0e(ctx).collect(_4989_src=src, _4990_length=length)

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
        self.inner = _lib.Incr_fn_lowest_0d3a0e(ctx)
        self.locals = LowestLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_4989_src=src, _4990_length=length)
    

def swma(ctx: Ctx, src: List[float]) -> List[float]:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """

    return _lib.Incr_fn_swma_2189bd(ctx).collect(_4992_src=src)

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
        self.inner = _lib.Incr_fn_swma_2189bd(ctx)
        self.locals = SwmaLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_4992_src=src)
    

def sma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_sma_a116cc(ctx).collect(_4994_src=src, _4995_length=length)

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
        self.inner = _lib.Incr_fn_sma_a116cc(ctx)
        self.locals = SmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_4994_src=src, _4995_length=length)
    

def ema(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_ema_67936f(ctx).collect(_4997_src=src, _4998_length=length)

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
        self.inner = _lib.Incr_fn_ema_67936f(ctx)
        self.locals = EmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_4997_src=src, _4998_length=length)
    

def rma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_rma_c2c131(ctx).collect(_5000_src=src, _5001_length=length)

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
        self.inner = _lib.Incr_fn_rma_c2c131(ctx)
        self.locals = RmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5000_src=src, _5001_length=length)
    

def wma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_wma_1f72e3(ctx).collect(_5003_src=src, _5004_length=length)

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
        self.inner = _lib.Incr_fn_wma_1f72e3(ctx)
        self.locals = WmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5003_src=src, _5004_length=length)
    

def lwma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_lwma_ce8f3d(ctx).collect(_5006_src=src, _5007_length=length)

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
        self.inner = _lib.Incr_fn_lwma_ce8f3d(ctx)
        self.locals = LwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5006_src=src, _5007_length=length)
    

def hma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_hma_64a46f(ctx).collect(_5009_src=src, _5010_length=length)

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
        self.inner = _lib.Incr_fn_hma_64a46f(ctx)
        self.locals = HmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5009_src=src, _5010_length=length)
    

def vwma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_vwma_52a80c(ctx).collect(_5012_src=src, _5013_length=length)

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
        self.inner = _lib.Incr_fn_vwma_52a80c(ctx)
        self.locals = VwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5012_src=src, _5013_length=length)
    

def dev(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_dev_6814e9(ctx).collect(_5015_src=src, _5016_length=length)

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
        self.inner = _lib.Incr_fn_dev_6814e9(ctx)
        self.locals = DevLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5015_src=src, _5016_length=length)
    

def tr(ctx: Ctx, handle_na: Optional[bool]) -> List[float]:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """

    return _lib.Incr_fn_tr_73a268(ctx).collect(_5018_handle_na=handle_na)

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
        self.inner = _lib.Incr_fn_tr_73a268(ctx)
        self.locals = TrLocals(self.inner)

    def next(self, handle_na: Optional[bool]) -> Optional[float]:
        return self.inner.next(_5018_handle_na=handle_na)
    

def atr(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """

    return _lib.Incr_fn_atr_1bb532(ctx).collect(_5020_length=length)

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
        self.inner = _lib.Incr_fn_atr_1bb532(ctx)
        self.locals = AtrLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5020_length=length)
    

def rsi(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_rsi_04f4cd(ctx).collect(_5022_src=src, _5023_length=length)

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
        self.inner = _lib.Incr_fn_rsi_04f4cd(ctx)
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5022_src=src, _5023_length=length)
    

def cci(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_cci_1931a7(ctx).collect(_5025_src=src, _5026_length=length)

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
        self.inner = _lib.Incr_fn_cci_1931a7(ctx)
        self.locals = CciLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5025_src=src, _5026_length=length)
    

def stdev(ctx: Ctx, src: List[float], length: int, biased: Optional[bool]) -> List[float]:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """

    return _lib.Incr_fn_stdev_453d70(ctx).collect(_5028_src=src, _5029_length=length, _5030_biased=biased)

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
        self.inner = _lib.Incr_fn_stdev_453d70(ctx)
        self.locals = StdevLocals(self.inner)

    def next(self, src: float, length: int, biased: Optional[bool]) -> Optional[float]:
        return self.inner.next(_5028_src=src, _5029_length=length, _5030_biased=biased)
    

def aroon(ctx: Ctx, length: Optional[int]) -> Tuple[float, float]:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """

    return _lib.Incr_fn_aroon_12c203(ctx).collect(_5032_length=length)

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
        self.inner = _lib.Incr_fn_aroon_12c203(ctx)
        self.locals = AroonLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_5032_length=length)
    

def supertrend(ctx: Ctx, src: List[float], factor: float, atr_period: int) -> Tuple[float, int]:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """

    return _lib.Incr_fn_supertrend_544717(ctx).collect(_5034_src=src, _5035_factor=factor, _5036_atr_period=atr_period)

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
        self.inner = _lib.Incr_fn_supertrend_544717(ctx)
        self.locals = SupertrendLocals(self.inner)

    def next(self, src: float, factor: float, atr_period: int) -> Optional[Tuple[float, int]]:
        return self.inner.next(_5034_src=src, _5035_factor=factor, _5036_atr_period=atr_period)
    

def awesome_oscillator(ctx: Ctx, src: List[float], slow_length: Optional[int], fast_length: Optional[int]) -> List[float]:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """

    return _lib.Incr_fn_awesome_oscillator_94ccf6(ctx).collect(_5038_src=src, _5039_slow_length=slow_length, _5040_fast_length=fast_length)

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
        self.inner = _lib.Incr_fn_awesome_oscillator_94ccf6(ctx)
        self.locals = AwesomeOscillatorLocals(self.inner)

    def next(self, src: float, slow_length: Optional[int], fast_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5038_src=src, _5039_slow_length=slow_length, _5040_fast_length=fast_length)
    

def balance_of_power(ctx: Ctx) -> List[float]:
    """
Balance of power between buyers and sellers

`balance_of_power() -> series<float>`
    """

    return _lib.Incr_fn_balance_of_power_872fa9(ctx).collect()

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
        self.inner = _lib.Incr_fn_balance_of_power_872fa9(ctx)
        self.locals = BalanceOfPowerLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def bollinger_bands_pct_b(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> List[float]:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> series<float>`
    """

    return _lib.Incr_fn_bollinger_bands_pct_b_122e55(ctx).collect(_5045_src=src, _5046_length=length, _5047_mult=mult)

class BollingerBandsPctBLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def bbr(self) -> float:
        return self.__inner._5052_bbr()
  
      

class BollingerBandsPctB:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_pct_b_122e55(ctx)
        self.locals = BollingerBandsPctBLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[float]:
        return self.inner.next(_5045_src=src, _5046_length=length, _5047_mult=mult)
    

def bollinger_bands_width(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> List[float]:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """

    return _lib.Incr_fn_bollinger_bands_width_077f67(ctx).collect(_5054_src=src, _5055_length=length, _5056_mult=mult)

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
        self.inner = _lib.Incr_fn_bollinger_bands_width_077f67(ctx)
        self.locals = BollingerBandsWidthLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[float]:
        return self.inner.next(_5054_src=src, _5055_length=length, _5056_mult=mult)
    

def bollinger_bands(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> Tuple[float, float]:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """

    return _lib.Incr_fn_bollinger_bands_30e557(ctx).collect(_5063_src=src, _5064_length=length, _5065_mult=mult)

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
        self.inner = _lib.Incr_fn_bollinger_bands_30e557(ctx)
        self.locals = BollingerBandsLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_5063_src=src, _5064_length=length, _5065_mult=mult)
    

def chaikin_money_flow(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """

    return _lib.Incr_fn_chaikin_money_flow_130da8(ctx).collect(_5071_length=length)

class ChaikinMoneyFlowLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def cumVol(self) -> float:
        return self.__inner._5072_cumVol()
  

    @property
    def ad(self) -> float:
        return self.__inner._5073_ad()
  
      

class ChaikinMoneyFlow:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chaikin_money_flow_130da8(ctx)
        self.locals = ChaikinMoneyFlowLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5071_length=length)
    

def chande_kroll_stop(ctx: Ctx, atr_length: Optional[int], atr_coeff: Optional[float], stop_length: Optional[int]) -> Tuple[float, float]:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """

    return _lib.Incr_fn_chande_kroll_stop_0ff120(ctx).collect(_5076_atr_length=atr_length, _5077_atr_coeff=atr_coeff, _5078_stop_length=stop_length)

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
        self.inner = _lib.Incr_fn_chande_kroll_stop_0ff120(ctx)
        self.locals = ChandeKrollStopLocals(self.inner)

    def next(self, atr_length: Optional[int], atr_coeff: Optional[float], stop_length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_5076_atr_length=atr_length, _5077_atr_coeff=atr_coeff, _5078_stop_length=stop_length)
    

def choppiness_index(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """

    return _lib.Incr_fn_choppiness_index_cd04d9(ctx).collect(_5087_length=length)

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
        self.inner = _lib.Incr_fn_choppiness_index_cd04d9(ctx)
        self.locals = ChoppinessIndexLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5087_length=length)
    

def coppock_curve(ctx: Ctx, src: List[float], wma_length: Optional[int], long_roc_length: Optional[int], short_roc_length: Optional[int]) -> List[float]:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """

    return _lib.Incr_fn_coppock_curve_4ac932(ctx).collect(_5089_src=src, _5090_wma_length=wma_length, _5091_long_roc_length=long_roc_length, _5092_short_roc_length=short_roc_length)

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
        self.inner = _lib.Incr_fn_coppock_curve_4ac932(ctx)
        self.locals = CoppockCurveLocals(self.inner)

    def next(self, src: float, wma_length: Optional[int], long_roc_length: Optional[int], short_roc_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5089_src=src, _5090_wma_length=wma_length, _5091_long_roc_length=long_roc_length, _5092_short_roc_length=short_roc_length)
    

def donchian_channel(ctx: Ctx, src: List[float], length: Optional[int]) -> Tuple[float, float, float]:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """

    return _lib.Incr_fn_donchian_channel_f0f4de(ctx).collect(_5094_src=src, _5095_length=length)

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
        self.inner = _lib.Incr_fn_donchian_channel_f0f4de(ctx)
        self.locals = DonchianChannelLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[Tuple[float, float, float]]:
        return self.inner.next(_5094_src=src, _5095_length=length)
    

def macd(ctx: Ctx, src: List[float], short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """

    return _lib.Incr_fn_macd_544e58(ctx).collect(_5100_src=src, _5101_short_length=short_length, _5102_long_length=long_length)

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
        self.inner = _lib.Incr_fn_macd_544e58(ctx)
        self.locals = MacdLocals(self.inner)

    def next(self, src: float, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5100_src=src, _5101_short_length=short_length, _5102_long_length=long_length)
    

def price_oscillator(ctx: Ctx, src: List[float], short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """

    return _lib.Incr_fn_price_oscillator_24cd8b(ctx).collect(_5105_src=src, _5106_short_length=short_length, _5107_long_length=long_length)

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
        self.inner = _lib.Incr_fn_price_oscillator_24cd8b(ctx)
        self.locals = PriceOscillatorLocals(self.inner)

    def next(self, src: float, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5105_src=src, _5106_short_length=short_length, _5107_long_length=long_length)
    

def relative_vigor_index(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """

    return _lib.Incr_fn_relative_vigor_index_c30368(ctx).collect(_5112_length=length)

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
        self.inner = _lib.Incr_fn_relative_vigor_index_c30368(ctx)
        self.locals = RelativeVigorIndexLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5112_length=length)
    

def relative_volatility_index(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_relative_volatility_index_5833ee(ctx).collect(_5114_src=src, _5115_length=length)

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
        self.inner = _lib.Incr_fn_relative_volatility_index_5833ee(ctx)
        self.locals = RelativeVolatilityIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5114_src=src, _5115_length=length)
    

def ultimate_oscillator(ctx: Ctx, fast_length: Optional[int], medium_length: Optional[int], slow_length: Optional[int]) -> List[float]:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """

    return _lib.Incr_fn_ultimate_oscillator_b53ab4(ctx).collect(_5125_fast_length=fast_length, _5126_medium_length=medium_length, _5127_slow_length=slow_length)

class UltimateOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def bp(self) -> float:
        return self.__inner._5130_bp()
  
      

class UltimateOscillator:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ultimate_oscillator_b53ab4(ctx)
        self.locals = UltimateOscillatorLocals(self.inner)

    def next(self, fast_length: Optional[int], medium_length: Optional[int], slow_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5125_fast_length=fast_length, _5126_medium_length=medium_length, _5127_slow_length=slow_length)
    

def volume_oscillator(ctx: Ctx, short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """

    return _lib.Incr_fn_volume_oscillator_96ddad(ctx).collect(_5137_short_length=short_length, _5138_long_length=long_length)

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
        self.inner = _lib.Incr_fn_volume_oscillator_96ddad(ctx)
        self.locals = VolumeOscillatorLocals(self.inner)

    def next(self, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5137_short_length=short_length, _5138_long_length=long_length)
    

def vortex_indicator(ctx: Ctx, length: Optional[int]) -> Tuple[float, float]:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """

    return _lib.Incr_fn_vortex_indicator_5c6ac1(ctx).collect(_5143_length=length)

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
        self.inner = _lib.Incr_fn_vortex_indicator_5c6ac1(ctx)
        self.locals = VortexIndicatorLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_5143_length=length)
    

def williams_pct_r(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> series<float>`
    """

    return _lib.Incr_fn_williams_pct_r_39694b(ctx).collect(_5150_src=src, _5151_length=length)

class WilliamsPctRLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def wpctr(self) -> float:
        return self.__inner._5154_wpctr()
  
      

class WilliamsPctR:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_williams_pct_r_39694b(ctx)
        self.locals = WilliamsPctRLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_5150_src=src, _5151_length=length)
    
          