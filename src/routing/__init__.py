"""Routing algorithms module."""
from .base import RoutingAlgorithm

# Baseline algorithms
from .baselines.leach import LEACH
from .baselines.pegasis import PEGASIS
from .baselines.ospf import OSPF

# Advanced algorithms (2023-2026)
from .nn_ileach import NN_ILEACH
from .dos_rl import DOS_RL
from .msso_fcm import MSSO_FCM
from .pgaecr import PGAECR
from .woad3qn_rp import WOAD3QN_RP
from .gn_dqn import GN_DQN

# Optional DRL routing (requires torch)
try:
    from .drl_sdn import DRLSDNRouting
    HAS_DRL_SDN = True
except ImportError:
    DRLSDNRouting = None
    HAS_DRL_SDN = False

__all__ = [
    'RoutingAlgorithm',
    # Baselines
    'LEACH',
    'PEGASIS',
    'OSPF',
    # Advanced
    'NN_ILEACH',
    'DOS_RL',
    'MSSO_FCM',
    'PGAECR',
    'WOAD3QN_RP',
    'GN_DQN',
]

if HAS_DRL_SDN:
    __all__.append('DRLSDNRouting')
