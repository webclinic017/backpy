from strategies.Btc_triple_conf import Btc_triple_conf
from strategies.Passive import Passive
from strategies.Btc_mac import Btc_mac
from strategies.Btc_multi_mac import Btc_multi_mac
from strategies.C10_multi_mac import C10_multi_mac
from strategies.RandomForest import RandomForest
from strategies.RandomForestLongShort import RandomForestLongShort
from strategies.Momentum import Momentum
from strategies.Optimizer import Optimizer
from strategies.TAMomentum import TAMomentum
from strategies.RandomForests import RandomForests
from strategies.OneLongShort import OneLongShort
from strategies.bitso.MarketLeaders import MarketLeaders
from strategies.TopN import TopN
from strategies.LongBTC import LongBTC



strategies = {
    "Btc_triple_conf": Btc_triple_conf,
    "Passive": Passive,
    "Btc_mac": Btc_mac,
    "Btc_multi_mac": Btc_multi_mac,
    "C10_multi_mac": C10_multi_mac,
    "RandomForest": RandomForest,
    "RandomForestLongShort": RandomForestLongShort,
    "Momentum": Momentum,
    "Optimizer": Optimizer,
    "TAMomentum": TAMomentum,
    "RandomForests": RandomForests,
    "OneLongShort": OneLongShort,
    "MarketLeaders": MarketLeaders,
    "TopN": TopN,
    "LongBTC": LongBTC
}