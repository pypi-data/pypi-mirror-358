
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  
def accdist(ctx: Ctx) -> List[float]:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """

    return _lib.Incr_fn_accdist_305c42(ctx).collect()

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
        self.inner = _lib.Incr_fn_accdist_305c42(ctx)
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def cum(ctx: Ctx, src: List[float]) -> List[float]:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """

    return _lib.Incr_fn_cum_e247fb(ctx).collect(_797_src=src)

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
        self.inner = _lib.Incr_fn_cum_e247fb(ctx)
        self.locals = CumLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_797_src=src)
    

def change(ctx: Ctx, src: List[float]) -> List[float]:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """

    return _lib.Incr_fn_change_e208c4(ctx).collect(_799_src=src)

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
        self.inner = _lib.Incr_fn_change_e208c4(ctx)
        self.locals = ChangeLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_799_src=src)
    

def barssince(ctx: Ctx, condition: List[bool]) -> List[int]:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """

    return _lib.Incr_fn_barssince_e94dcc(ctx).collect(_801_condition=condition)

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
        self.inner = _lib.Incr_fn_barssince_e94dcc(ctx)
        self.locals = BarssinceLocals(self.inner)

    def next(self, condition: bool) -> Optional[int]:
        return self.inner.next(_801_condition=condition)
    

def roc(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> series<float>`
    """

    return _lib.Incr_fn_roc_aa8f1d(ctx).collect(_803_src=src, _804_length=length)

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
        self.inner = _lib.Incr_fn_roc_aa8f1d(ctx)
        self.locals = RocLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_803_src=src, _804_length=length)
    

def crossover(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_crossover_89899d(ctx).collect(_806_source1=source1, _807_source2=source2)

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
        self.inner = _lib.Incr_fn_crossover_89899d(ctx)
        self.locals = CrossoverLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_806_source1=source1, _807_source2=source2)
    

def crossunder(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_crossunder_09f56c(ctx).collect(_809_source1=source1, _810_source2=source2)

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
        self.inner = _lib.Incr_fn_crossunder_09f56c(ctx)
        self.locals = CrossunderLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_809_source1=source1, _810_source2=source2)
    

def cross(ctx: Ctx, source1: List[float], source2: List[float]) -> List[bool]:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """

    return _lib.Incr_fn_cross_1392d4(ctx).collect(_812_source1=source1, _813_source2=source2)

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
        self.inner = _lib.Incr_fn_cross_1392d4(ctx)
        self.locals = CrossLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_812_source1=source1, _813_source2=source2)
    

def highestbars(ctx: Ctx, src: List[float], length: Optional[int]) -> List[int]:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """

    return _lib.Incr_fn_highestbars_790de0(ctx).collect(_815_src=src, _816_length=length)

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
        self.inner = _lib.Incr_fn_highestbars_790de0(ctx)
        self.locals = HighestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[int]:
        return self.inner.next(_815_src=src, _816_length=length)
    

def lowestbars(ctx: Ctx, src: List[float], length: Optional[int]) -> List[int]:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """

    return _lib.Incr_fn_lowestbars_a667b6(ctx).collect(_818_src=src, _819_length=length)

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
        self.inner = _lib.Incr_fn_lowestbars_a667b6(ctx)
        self.locals = LowestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[int]:
        return self.inner.next(_818_src=src, _819_length=length)
    

def highest(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_highest_ef6663(ctx).collect(_821_src=src, _822_length=length)

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
        self.inner = _lib.Incr_fn_highest_ef6663(ctx)
        self.locals = HighestLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_821_src=src, _822_length=length)
    

def lowest(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_lowest_7dba0d(ctx).collect(_824_src=src, _825_length=length)

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
        self.inner = _lib.Incr_fn_lowest_7dba0d(ctx)
        self.locals = LowestLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_824_src=src, _825_length=length)
    

def swma(ctx: Ctx, src: List[float]) -> List[float]:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """

    return _lib.Incr_fn_swma_19e026(ctx).collect(_827_src=src)

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
        self.inner = _lib.Incr_fn_swma_19e026(ctx)
        self.locals = SwmaLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_827_src=src)
    

def sma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_sma_f5304f(ctx).collect(_829_src=src, _830_length=length)

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
        self.inner = _lib.Incr_fn_sma_f5304f(ctx)
        self.locals = SmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_829_src=src, _830_length=length)
    

def ema(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_ema_897d85(ctx).collect(_832_src=src, _833_length=length)

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
        self.inner = _lib.Incr_fn_ema_897d85(ctx)
        self.locals = EmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_832_src=src, _833_length=length)
    

def rma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_rma_27493c(ctx).collect(_835_src=src, _836_length=length)

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
        self.inner = _lib.Incr_fn_rma_27493c(ctx)
        self.locals = RmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_835_src=src, _836_length=length)
    

def wma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_wma_942878(ctx).collect(_838_src=src, _839_length=length)

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
        self.inner = _lib.Incr_fn_wma_942878(ctx)
        self.locals = WmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_838_src=src, _839_length=length)
    

def lwma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_lwma_01256b(ctx).collect(_841_src=src, _842_length=length)

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
        self.inner = _lib.Incr_fn_lwma_01256b(ctx)
        self.locals = LwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_841_src=src, _842_length=length)
    

def hma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_hma_b8a8ac(ctx).collect(_844_src=src, _845_length=length)

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
        self.inner = _lib.Incr_fn_hma_b8a8ac(ctx)
        self.locals = HmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_844_src=src, _845_length=length)
    

def vwma(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_vwma_92afed(ctx).collect(_847_src=src, _848_length=length)

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
        self.inner = _lib.Incr_fn_vwma_92afed(ctx)
        self.locals = VwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_847_src=src, _848_length=length)
    

def dev(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_dev_2b18be(ctx).collect(_850_src=src, _851_length=length)

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
        self.inner = _lib.Incr_fn_dev_2b18be(ctx)
        self.locals = DevLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_850_src=src, _851_length=length)
    

def tr(ctx: Ctx, handle_na: Optional[bool]) -> List[float]:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """

    return _lib.Incr_fn_tr_32161c(ctx).collect(_853_handle_na=handle_na)

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
        self.inner = _lib.Incr_fn_tr_32161c(ctx)
        self.locals = TrLocals(self.inner)

    def next(self, handle_na: Optional[bool]) -> Optional[float]:
        return self.inner.next(_853_handle_na=handle_na)
    

def atr(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """

    return _lib.Incr_fn_atr_a63fd3(ctx).collect(_855_length=length)

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
        self.inner = _lib.Incr_fn_atr_a63fd3(ctx)
        self.locals = AtrLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_855_length=length)
    

def rsi(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_rsi_66bbba(ctx).collect(_857_src=src, _858_length=length)

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
        self.inner = _lib.Incr_fn_rsi_66bbba(ctx)
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_857_src=src, _858_length=length)
    

def cci(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_cci_d8a893(ctx).collect(_860_src=src, _861_length=length)

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
        self.inner = _lib.Incr_fn_cci_d8a893(ctx)
        self.locals = CciLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_860_src=src, _861_length=length)
    

def stdev(ctx: Ctx, src: List[float], length: int, biased: Optional[bool]) -> List[float]:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """

    return _lib.Incr_fn_stdev_446993(ctx).collect(_863_src=src, _864_length=length, _865_biased=biased)

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
        self.inner = _lib.Incr_fn_stdev_446993(ctx)
        self.locals = StdevLocals(self.inner)

    def next(self, src: float, length: int, biased: Optional[bool]) -> Optional[float]:
        return self.inner.next(_863_src=src, _864_length=length, _865_biased=biased)
    

def aroon(ctx: Ctx, length: Optional[int]) -> Tuple[float, float]:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """

    return _lib.Incr_fn_aroon_dc77b6(ctx).collect(_867_length=length)

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
        self.inner = _lib.Incr_fn_aroon_dc77b6(ctx)
        self.locals = AroonLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_867_length=length)
    

def supertrend(ctx: Ctx, src: List[float], factor: float, atr_period: int) -> Tuple[float, int]:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """

    return _lib.Incr_fn_supertrend_a55981(ctx).collect(_869_src=src, _870_factor=factor, _871_atr_period=atr_period)

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
        self.inner = _lib.Incr_fn_supertrend_a55981(ctx)
        self.locals = SupertrendLocals(self.inner)

    def next(self, src: float, factor: float, atr_period: int) -> Optional[Tuple[float, int]]:
        return self.inner.next(_869_src=src, _870_factor=factor, _871_atr_period=atr_period)
    

def awesome_oscillator(ctx: Ctx, src: List[float], slow_length: Optional[int], fast_length: Optional[int]) -> List[float]:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """

    return _lib.Incr_fn_awesome_oscillator_cb6e5e(ctx).collect(_873_src=src, _874_slow_length=slow_length, _875_fast_length=fast_length)

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
        self.inner = _lib.Incr_fn_awesome_oscillator_cb6e5e(ctx)
        self.locals = AwesomeOscillatorLocals(self.inner)

    def next(self, src: float, slow_length: Optional[int], fast_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_873_src=src, _874_slow_length=slow_length, _875_fast_length=fast_length)
    

def balance_of_power(ctx: Ctx) -> List[float]:
    """
Balance of power between buyers and sellers

`balance_of_power() -> series<float>`
    """

    return _lib.Incr_fn_balance_of_power_33c4f1(ctx).collect()

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
        self.inner = _lib.Incr_fn_balance_of_power_33c4f1(ctx)
        self.locals = BalanceOfPowerLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def bollinger_bands_pct_b(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> List[float]:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> series<float>`
    """

    return _lib.Incr_fn_bollinger_bands_pct_b_5fe173(ctx).collect(_880_src=src, _881_length=length, _882_mult=mult)

class BollingerBandsPctBLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def bbr(self) -> float:
        return self.__inner._887_bbr()
  
      

class BollingerBandsPctB:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_pct_b_5fe173(ctx)
        self.locals = BollingerBandsPctBLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[float]:
        return self.inner.next(_880_src=src, _881_length=length, _882_mult=mult)
    

def bollinger_bands_width(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> List[float]:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """

    return _lib.Incr_fn_bollinger_bands_width_9a6f45(ctx).collect(_889_src=src, _890_length=length, _891_mult=mult)

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
        self.inner = _lib.Incr_fn_bollinger_bands_width_9a6f45(ctx)
        self.locals = BollingerBandsWidthLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[float]:
        return self.inner.next(_889_src=src, _890_length=length, _891_mult=mult)
    

def bollinger_bands(ctx: Ctx, src: List[float], length: Optional[int], mult: Optional[float]) -> Tuple[float, float]:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """

    return _lib.Incr_fn_bollinger_bands_4fd0bc(ctx).collect(_898_src=src, _899_length=length, _900_mult=mult)

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
        self.inner = _lib.Incr_fn_bollinger_bands_4fd0bc(ctx)
        self.locals = BollingerBandsLocals(self.inner)

    def next(self, src: float, length: Optional[int], mult: Optional[float]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_898_src=src, _899_length=length, _900_mult=mult)
    

def chaikin_money_flow(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """

    return _lib.Incr_fn_chaikin_money_flow_e0b6ad(ctx).collect(_906_length=length)

class ChaikinMoneyFlowLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def cumVol(self) -> float:
        return self.__inner._907_cumVol()
  

    @property
    def ad(self) -> float:
        return self.__inner._908_ad()
  
      

class ChaikinMoneyFlow:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chaikin_money_flow_e0b6ad(ctx)
        self.locals = ChaikinMoneyFlowLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_906_length=length)
    

def chande_kroll_stop(ctx: Ctx, atr_length: Optional[int], atr_coeff: Optional[float], stop_length: Optional[int]) -> Tuple[float, float]:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """

    return _lib.Incr_fn_chande_kroll_stop_673012(ctx).collect(_911_atr_length=atr_length, _912_atr_coeff=atr_coeff, _913_stop_length=stop_length)

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
        self.inner = _lib.Incr_fn_chande_kroll_stop_673012(ctx)
        self.locals = ChandeKrollStopLocals(self.inner)

    def next(self, atr_length: Optional[int], atr_coeff: Optional[float], stop_length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_911_atr_length=atr_length, _912_atr_coeff=atr_coeff, _913_stop_length=stop_length)
    

def choppiness_index(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """

    return _lib.Incr_fn_choppiness_index_f50dd2(ctx).collect(_922_length=length)

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
        self.inner = _lib.Incr_fn_choppiness_index_f50dd2(ctx)
        self.locals = ChoppinessIndexLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_922_length=length)
    

def coppock_curve(ctx: Ctx, src: List[float], wma_length: Optional[int], long_roc_length: Optional[int], short_roc_length: Optional[int]) -> List[float]:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """

    return _lib.Incr_fn_coppock_curve_8df175(ctx).collect(_924_src=src, _925_wma_length=wma_length, _926_long_roc_length=long_roc_length, _927_short_roc_length=short_roc_length)

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
        self.inner = _lib.Incr_fn_coppock_curve_8df175(ctx)
        self.locals = CoppockCurveLocals(self.inner)

    def next(self, src: float, wma_length: Optional[int], long_roc_length: Optional[int], short_roc_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_924_src=src, _925_wma_length=wma_length, _926_long_roc_length=long_roc_length, _927_short_roc_length=short_roc_length)
    

def donchian_channel(ctx: Ctx, src: List[float], length: Optional[int]) -> Tuple[float, float, float]:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """

    return _lib.Incr_fn_donchian_channel_c4cac1(ctx).collect(_929_src=src, _930_length=length)

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
        self.inner = _lib.Incr_fn_donchian_channel_c4cac1(ctx)
        self.locals = DonchianChannelLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[Tuple[float, float, float]]:
        return self.inner.next(_929_src=src, _930_length=length)
    

def macd(ctx: Ctx, src: List[float], short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """

    return _lib.Incr_fn_macd_5e1437(ctx).collect(_935_src=src, _936_short_length=short_length, _937_long_length=long_length)

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
        self.inner = _lib.Incr_fn_macd_5e1437(ctx)
        self.locals = MacdLocals(self.inner)

    def next(self, src: float, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_935_src=src, _936_short_length=short_length, _937_long_length=long_length)
    

def price_oscillator(ctx: Ctx, src: List[float], short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """

    return _lib.Incr_fn_price_oscillator_9742a7(ctx).collect(_940_src=src, _941_short_length=short_length, _942_long_length=long_length)

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
        self.inner = _lib.Incr_fn_price_oscillator_9742a7(ctx)
        self.locals = PriceOscillatorLocals(self.inner)

    def next(self, src: float, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_940_src=src, _941_short_length=short_length, _942_long_length=long_length)
    

def relative_vigor_index(ctx: Ctx, length: Optional[int]) -> List[float]:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """

    return _lib.Incr_fn_relative_vigor_index_bf6dd3(ctx).collect(_947_length=length)

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
        self.inner = _lib.Incr_fn_relative_vigor_index_bf6dd3(ctx)
        self.locals = RelativeVigorIndexLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_947_length=length)
    

def relative_volatility_index(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """

    return _lib.Incr_fn_relative_volatility_index_3f3b32(ctx).collect(_949_src=src, _950_length=length)

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
        self.inner = _lib.Incr_fn_relative_volatility_index_3f3b32(ctx)
        self.locals = RelativeVolatilityIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_949_src=src, _950_length=length)
    

def ultimate_oscillator(ctx: Ctx, fast_length: Optional[int], medium_length: Optional[int], slow_length: Optional[int]) -> List[float]:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """

    return _lib.Incr_fn_ultimate_oscillator_d5933e(ctx).collect(_960_fast_length=fast_length, _961_medium_length=medium_length, _962_slow_length=slow_length)

class UltimateOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def bp(self) -> float:
        return self.__inner._965_bp()
  
      

class UltimateOscillator:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ultimate_oscillator_d5933e(ctx)
        self.locals = UltimateOscillatorLocals(self.inner)

    def next(self, fast_length: Optional[int], medium_length: Optional[int], slow_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_960_fast_length=fast_length, _961_medium_length=medium_length, _962_slow_length=slow_length)
    

def volume_oscillator(ctx: Ctx, short_length: Optional[int], long_length: Optional[int]) -> List[float]:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """

    return _lib.Incr_fn_volume_oscillator_fa7242(ctx).collect(_972_short_length=short_length, _973_long_length=long_length)

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
        self.inner = _lib.Incr_fn_volume_oscillator_fa7242(ctx)
        self.locals = VolumeOscillatorLocals(self.inner)

    def next(self, short_length: Optional[int], long_length: Optional[int]) -> Optional[float]:
        return self.inner.next(_972_short_length=short_length, _973_long_length=long_length)
    

def vortex_indicator(ctx: Ctx, length: Optional[int]) -> Tuple[float, float]:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """

    return _lib.Incr_fn_vortex_indicator_0bf46d(ctx).collect(_978_length=length)

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
        self.inner = _lib.Incr_fn_vortex_indicator_0bf46d(ctx)
        self.locals = VortexIndicatorLocals(self.inner)

    def next(self, length: Optional[int]) -> Optional[Tuple[float, float]]:
        return self.inner.next(_978_length=length)
    

def williams_pct_r(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> series<float>`
    """

    return _lib.Incr_fn_williams_pct_r_3489ff(ctx).collect(_985_src=src, _986_length=length)

class WilliamsPctRLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def wpctr(self) -> float:
        return self.__inner._989_wpctr()
  
      

class WilliamsPctR:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_williams_pct_r_3489ff(ctx)
        self.locals = WilliamsPctRLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_985_src=src, _986_length=length)
    
          