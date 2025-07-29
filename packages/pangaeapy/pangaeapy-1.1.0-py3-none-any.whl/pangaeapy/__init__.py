"""
pangaeapy is a package allowing to download and analyse metadata
as well as data from tabular PANGAEA (https://www.pangaea.de) datasets.
"""

__all__ = ["exporter", "PanDataSet", "PanQuery"]

from pangaeapy import exporter
from pangaeapy.pandataset import PanDataSet
from pangaeapy.panquery import PanQuery
