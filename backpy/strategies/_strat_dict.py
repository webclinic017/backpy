from .Btc_triple_conf import Btc_triple_conf
from .Passive import Passive
from .Btc_mac import Btc_mac
from .Btc_multi_mac import Btc_multi_mac
from .C10_multi_mac import C10_multi_mac
from .RandomForest import RandomForest
from .RandomForestLongShort import RandomForestLongShort
from .Momentum import Momentum
from .Optimizer import Optimizer
from .TAMomentum import TAMomentum
from .RandomForests import RandomForests
from .OneLongShort import OneLongShort
from .TopN import TopN
from .LongBTC import LongBTC



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
    "TopN": TopN,
    "LongBTC": LongBTC
}