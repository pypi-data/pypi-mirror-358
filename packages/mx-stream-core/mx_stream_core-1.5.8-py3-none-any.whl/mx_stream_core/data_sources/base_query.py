class BaseQuery:
    def foreach(self, func, processing_time=None):
        raise NotImplementedError('Not implemented')

    def awaitTermination(self):
        raise NotImplemented('Not implemented')
