# coding:UTF-8
from lib.data_processor.interface.i_data_processor import IDataProcessor

"""
    WT53R485数据处理器 Data Processor
"""


class WT53R485DataProcessor(IDataProcessor):
    onVarChanged = []
    def onOpen(self, deviceModel):
        pass

    def onClose(self):
        pass

    @staticmethod
    def onUpdate(*args):
        for fun in WT53R485DataProcessor.onVarChanged:
            fun(*args)