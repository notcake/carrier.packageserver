from knotcake.oop import abstract

from ibasestream import IBaseStream

class IInStream(IBaseStream):
	@abstract
	def read(self, size): pass
	
	def toStreamReader(self):
		from bufferedstreamreader import BufferedStreamReader
		return BufferedStreamReader(self)
