"""
created matt_dumont 
on: 21/09/23
"""
from komanawa.kendall_stats.version import __version__
from komanawa.kendall_stats.multi_part_kendall import MultiPartKendall, SeasonalMultiPartKendall
from komanawa.kendall_stats.mann_kendall import MannKendall, SeasonalKendall
import komanawa.kendall_stats.example_data
from komanawa.kendall_stats.utils import estimate_runtime
