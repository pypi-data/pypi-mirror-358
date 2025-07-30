
from .base import *
from .cached_property import cached_property

class SemTraceLoggersHandler(BaseListUpdateHandler):
	'''SEM Trace Loggers

	Methods
	-------
		createEntry()
			Creates a new SemTraceLogger entry object.
		update(data)

	Inherited Methods
	-----------------
		list (BaseListHandler)
	'''


	def createEntry(self):
		'''Creates a new SemTraceLogger entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SemTraceLogger(self)

	def update(self, id_or_data : Union[int, BaseEntry, dict], data : Union[None, BaseEntry, dict] = None, options=None) -> Optional[BaseEntry]:
		"""wrapper around BaseUpdateHandler._update(), returns Entry object or None.
			update can be calles eigther:
				handler.update(data)
			if data contains 'Id'
			or:
				handler.update(id, data)
		"""
		if data != None:
			d = data
			assert id_or_data is None, "Id and data was given, but SemTraceLogger does not support Id"
		else:
			d = id_or_data
			if not isinstance(d, BaseEntry) or isinstance(d, dict):
				raise TypeError("update() is missing one required argument: 'data'")
		return self._update(self._url + "/", {"Loggers": [d]}, options)
		# give list(d) to _update, since SemTraceLoggers only accepts arrays


class SemTraceLogger(ModifiableListEntry):
	'''Parameters of a SEM trace logger entry

	Attributes [writable]
	---------------------
		Process : string
			Process
		Logger : string
			Logger
		LogLevel : integer
			Log Level
			Enum Values: 1=error, 2=warning, 3=info, 4=debug, 5=trace, 6=default
	'''

	def __init__(self, getHandler):
		ModifiableListEntry.__init__(self, getHandler)		#Default values
		self._defaultValues = {
			"Process" : "",
			"Logger" : "",
			"LogLevel" : 0,
		}

	def update(self, data=None):
		if data == None:
			_data = self.__dict__["_changes"]
		else:
			_data = data
		_data["Logger"] = self.__dict__["Logger"]
		_data["Process"] = self.__dict__["Process"]
		return self._getHandler.update(None, _data)

	@cached_property
	def Process(self):
		return self.__getattr__("Process")

	@cached_property
	def Logger(self):
		return self.__getattr__("Logger")

	@cached_property
	def LogLevel(self):
		return self.__getattr__("LogLevel")

