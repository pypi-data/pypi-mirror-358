import urllib
import urllib.request
import urllib.error
from urllib.parse import quote
import ssl
import json
from pprint import pprint, pformat #for debugging
import copy
import functools
from typing import Union, Optional, List

"""
Entry Classes:
BaseEntry
	|-ListEntry
 	|	|-ModifiableListEntry
	|-LazyEntry
		|-LazyListEntry (ListEntry)
			|-LazyModifiableListEntry (ModifiableListEntry)

Handler Classes:
BaseHandler
	|-BaseGetHandler
	|-BaseUpdateHandler
	|-BaseListHandler
		|-BaseListGetHandler (BaseGetHandler)
		|	|-BaseListFindHandler
		|-BaseListUpdateHandler
		|-BaseListInsertHandler
		|-BaseListDeleteHandler

Exception Classes:
ApiException
	|-ApiNotFoundException
	|-ApiExistsException
	|-ApiBadValueException
	|-ApiAuthenticationException

Other Classes:
Options
SearchFilter
BaseApi
"""

#Note about Method Resolution Order with multiple inheritance:
#depth-first, then left to right
#Example:
#class A
#class B(A)
#class C(A)
#class D(B,C)
#Resolution Order: D, B, A, C
#
#So when inheriting from the Base*Handler classes the following order is mandatory:

class ApiException(Exception):
	"""Raised whenever a request fails.
		
		Attributes
		----------
			message : str
				Contains the reason, why this exception was raised.
				Same as HTTP response string.
			data : dict
				Contains all key-value pairs of the HTTP response.
				May be an empty dict.
				Most likely contains the keys "URL" and "HttpStatusCode"

		Methods
		-------
			HttpStatusCode()
				returns the HTTP status code of the HTTP response.
				returns 0, when no status code is available.

	"""
	def __init__ (self, msg, data={}):
		self.message = msg
		self.data = data
		code = self.semErrorCode()
		if code:
			self.data["SemErrorCode"] = code

	def __str__ (self):
		ret = self.message
		for k,v in self.data.items():
			ret += "\n  " + str(k) + ": " + str(v)
		return ret

	def httpStatusCode(self):
		if 'HttpStatusCode' in self.data:
			return self.data['HttpStatusCode']
		return 0

	def semErrorCode(self):
		if 'Response' in self.data and "Error" in self.data["Response"] and "ErrorCode" in self.data["Response"]["Error"]:
			return self.data["Response"]["Error"]["ErrorCode"]
		return 0

	def reason(self):
		if 'Reason' in self.data:
			return self.data['Reason']
		return ""

	def response(self):
		if 'Response' in self.data:
			return self.data['Response']
		return ""

class ApiNotFoundException(ApiException):
	pass
	
class ApiExistsException(ApiException):
	pass
	
class ApiBadValueException(ApiException):
	pass
	
class ApiAuthenticationException(ApiException):
	pass

	
APIEXCEPTIONS = {
	"NotFound": 		ApiNotFoundException,
	"AlreadyExists":	ApiExistsException,
	"BadValue": 		ApiBadValueException,
	"Authentication": 	ApiAuthenticationException,
}

		
def getApiException(msg, data={}):
	"""Called when a error is recieved from the SEM.
		used to define several different Excetions.
	"""
	if 'Response' in data and "Error" in data["Response"] and "ErrorGroup" in data["Response"]["Error"]:
		exc = data["Response"]["Error"]["ErrorGroup"]
		if exc in APIEXCEPTIONS:
			return APIEXCEPTIONS[exc](msg, data)
	return ApiException(msg, data)


class Options:
	def __init__ (self, **kwargs):
		self.timeFormat = "string"
		self.passwordFormat = "encrypred" 
		self.enumFormat = "string"
		self.keyFormat = "name"
		for key, value in kwargs.items():
			self[key] = value

	def toQuery(self):
		ret = {}
		if self.timeFormat in ["unixtime", "unix", "time", "1", 1]:
			ret["timeFormat"] = "1"
		if self.passwordFormat in ["asterisk", "1", 1]:
			ret["passwordFormat"] = "1"
		if self.enumFormat in ["uint", "int", int, "0", 0]:
			ret["enumFormat"] = "0"
		if self.keyFormat in ["id", "int", "uint", int, "0", 0]:
			ret["keyFormat"] = "0"
		for key, value in self.__dict__.items():
			if key not in ["timeFormat", "passwordFormat", "enumFormat", "keyFormat"]:
				ret[key] = value
		return ret

	def update(self, optionsDict):
		if not isinstance(optionsDict, dict):
			raise TypeError("Options.update expects dict, but "+str(type(optionsDict)), " was given.")
		self.__dict__.update(optionsDict)
		return self

	def __getitem__(self, key):
		return getattr(self, key)

	def __setitem__(self, key, value):
		setattr(self, key, value)

	def __str__(self):
		return str(self.__dict__)


class SearchFilter:
	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			self[key] = value

	def __setattr__(self, key, value):
		self.__dict__[key] = value

	def __setitem__(self, key, value):
		setattr(self, key, value)

	def clear(self):
		self.__dict__ = {}

	def getQuery(self):
		ret = ""
		for key, value in self.__dict__.items():
			ret += "&" + quote(str(key)) + "=" + quote(str(value))
		return ret

	def __str__(self):
		return str(self.__dict__)



class BaseEntry():
	"""
		Base class for entries
		Encapsulates the answers of handlers as objects.
	"""
	def __init__(self, getHandler=None):
		self._changes = {}
		self._defaultValues = {}
		self.__dict__["_getHandler"] = getHandler
		# self._getHandler = None would cause problems in setattr

	def __getattr__(self, key):
		if key not in self.__dict__:
			raise AttributeError(self.__class__.__name__ +" has no attribute named "+repr(key))
		return self.__dict__[key]

	def __getitem__(self, key):
		return self.__getattr__(key)

	def __setattr__(self, key, value):
		if isinstance(value, BaseEntry):
			value = value.Id
		self.__dict__[key] = value
		if key.startswith("_") and value is not None:
			return
		self._changes[key] = value

	def __setitem__(self, key, value):
		if isinstance(value, BaseEntry):
			value = value["Id"]
		self.__dict__[key] = value
		if key.startswith("_") and value is not None:
			return
		self._changes[key] = value

	def __contains__(self, key):
		return self.__dict__.__contains__(key)

	def __iter__(self):
		for key in self.__dict__:
			if not key.startswith("_"):
				yield key

	def items(self):
		for key,value in self.__dict__.items():
			if not key.startswith("_"):
				yield key, value

	def __str__(self):
		ret = {}
		for key, value in self.__dict__.items():
			if not key.startswith("_"):
				ret[key] = value
		return pformat(ret)

	def _update (self, data):
		if isinstance(data, BaseEntry):
			self.__dict__.update(data.__dict__)
		else:
			self.__dict__.update(data)
		# handling of inherited templates:
		# a inherited template can have another GroupId than the _groupid of the getHandler.
		# calling get() would cause a 'Invalid group id' error.
		# when GroupId and _groupid differ, a new getHandler is created
		if "GroupId" in self.__dict__ and "_groupid" in self.__dict__ and self._getHandler is not None:
			newGroupId = self.__dict__["GroupId"]
			if newGroupId != self.__dict__["_groupid"]:
				self.__dict__["_groupid"] = newGroupId
				self.__dict__["_getHandler"] = self.__dict__["_getHandler"].__class__(self.__dict__["_api"], newGroupId)

	def clearChanges(self):
		self._changes={}


class ListEntry(BaseEntry):
	"""Implements methods with Id"""

	def _callMethod(self, url, options=None, **kwargs):
		return self._getHandler._callEntryFunction(self.__dict__["Id"], url, options=options, **kwargs)

	def _callMethodGet(self, url, options=None, **kwargs):
		return self._getHandler._callEntryFunction(self.__dict__["Id"], url, method="GET", options=options, **kwargs)

class ModifiableListEntry(ListEntry):
	"""
		Implements update method with Id
	"""

	def update(self, data=None):
		if data == None:
			return self._getHandler.update(self.__dict__["Id"], self.__dict__["_changes"])
		return self._getHandler.update(self.__dict__["Id"], data)


class LazyEntry(BaseEntry):
	"""
		Unterstützt lazy-get: Wenn der entry durch die list() Funktion eines
		List-Handlers angelegt wurde sind oftmals nur nur die Attribute id und
		name vorhanden. Erst wenn auf ein anderes Attribut zugegriffen wird
		(oder die get-Methode von Hand aufgerufen wird) wird vom Handler ein
		richtiges get() durchgeführt. Falls die get() Methode des Handlers
		Parameter erwartet, muss in einer von BaseEntry abgeleiteten Klasse die
		get()-Methode entsprechend überladen werden.
	"""

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		self._getComplete = False

	def __getattr__(self, key):
		if not key.startswith("_") and not self._getComplete:
			self._get()
		#raises key error, if get is not successfull
		#but since this is an instance of a class, an AttributeError is expected
		try:
			return self.__dict__[key]
		except KeyError as e:
			raise AttributeError(self.__class__.__name__ +" has no attribute "+str(e))
	
	def __str__(self):
		if not self._getComplete:
			self._get()
		return BaseEntry.__str__(self)

	def _get(self):
		if not self._getComplete:
			new = self.get()
			for key, value in new.__dict__.items():
				if not key.startswith("_"):
					self.__dict__[key] = value
			self._getComplete = True
		return self

	def get(self):
		if "RestURI" in self.__dict__:
			new = self._getHandler.get(url=self.__dict__["RestURI"])
		else:
			new = self._getHandler.get()
		# set default values, since they are not transmittet when calling get()
		# must be done here, so get() must be called at least once
		self.__dict__.update(self._defaultValues)
		# update values from the answer of get()
		for key, value in new.__dict__.items():
			if not key.startswith("_"):
				self.__dict__[key] = value
		self._getComplete = True
		return self


class LazyListEntry(LazyEntry, ListEntry):
	"""
		Implements get method with Id
	"""

	def get(self):
		if "RestURI" in self.__dict__:
			new = self._getHandler.get(self.__dict__["Id"], url=self.__dict__["RestURI"])
		else:
			new = self._getHandler.get(self.__dict__["Id"])
		# set default values, since they are not transmittet when calling get()
		# must be done here, so get() must be called at least once
		self.__dict__.update(self._defaultValues)
		# update values from the answer of get()
		for key, value in new.__dict__.items():
			if not key.startswith("_"):
				self.__dict__[key] = value
		self._getComplete = True
		return self


class LazyModifiableListEntry(LazyListEntry, ModifiableListEntry):
	pass


class BaseHandler:
	"""
		Base class for handlers.
		Derived classes may implement get, list, update, insert, delete.
	"""
	def __init__ (self, api, url):
		self._api = api
		self._url = url
		self._cache = {} 

	def getOptionsStr (self, options):
		if options is None:
			return ""
		elif isinstance(options, dict):
			options = Options().update(options)	# convert to Options object
		if isinstance(options, Options):
			options = options.toQuery()	# convert to dict containing int values

		pairs = []
		for key, value in options.items():
			pairs.append(quote(key, safe="") + "=" + quote(value, safe=""))
		return "?" + str.join("&", pairs)	# convert to query string

	def createEntryClass(self, data={}) -> BaseEntry:
		obj = self.createEntry()
		obj._update(data)
		obj.clearChanges()
		return obj

	def _hasmethod(self, name):
		"""returns weather a method with the given name exists"""
		if name in dir(self) :
			return callable(getattr(self,name))
		return False

	def createEntry(self) -> BaseEntry:
		"""create entry is intended to be owerridden by endpoint classes."""
		# Note: this default behaviour is implemented in the base class,
		#	since it is easy to make mistakes when using multiple inheritance.
		if self._hasmethod("list"):
			if self._hasmethod("update"):
				# If get(id) exists, update() may return incomplete results.
				if self._hasmethod("get"):
					return LazyModifiableListEntry(self)
				else:
					return ModifiableListEntry()
			elif self._hasmethod("get"):
				# If get(id) and list() exist, list() may return incomplete results
				return LazyListEntry(self)
			else:
				return ListEntry(self)
		elif self._hasmethod("get") and self._hasmethod("update"):
			# If get() exists, update() may return incomplete results.
			return LazyEntry(self)
		else:
			return BaseEntry()

	def _callFunction(self, url, method="POST", options=None, **kwargs):
		url = self._url + url + self.getOptionsStr(options)
		#remove None entries from data
		data = {}
		for k,v in kwargs.items():
			if v is not None:
				if isinstance(v, BaseEntry):
					data[k] = v["Id"]
				else:
					data[k] = v
		resp = self._api.makeRequest (method, url, data=data)
		if 'Result' not in resp:
			raise ApiException ("Missing 'Result' parameter in JSON response")
		return resp["Result"]


class BaseGetHandler(BaseHandler):
	"""
		This handler provides read access to simple result objects (not lists).
		It implements get() without id (getentry).
		Example:
			data = handler.get()
	"""
	def get(self, options=None, url=None) -> BaseEntry:
		if url:
			url = url.removeprefix("/api/")
			return self._get (url, options)
		"""wrapper around _get()
			makes GET request
			returns result as Entry object
		"""
		return self._get (self._url, options)

	def _get(self, url, options) -> BaseEntry:
		"""makes GET request, returns result as Entry object"""
		url += self.getOptionsStr(options)
		resp = self._api.makeRequest ("GET", url)
		if 'Result' not in resp:
			raise ApiException ("Missing 'Result' parameter in JSON response")
		e = self.createEntryClass(resp['Result']) 
		e._getComplete = True
		self._cache["latest"] = e
		return e

	def __getattr__(self, key):
		"""Convenience method for a more easy user experience.
			Allows accessing the attributes of the get-response directly.
			Example:
				x = handler.x
		"""
		if key.startswith("_") or key in self.__dict__:
			return key
		if not self._cache.get("latest"):
			self.get()
		return self._cache["latest"].__getattr__(key)

	def __str__(self):
		return str(self.get())


class BaseUpdateHandler(BaseHandler):
	"""
		This handler provides write access to simple result objects (not lists).
		It implements update() without id.
		Example:
			data = handler.get()
			data.x = y
			handler.update(data)
	"""
	# There may be special cases where update() is possible without get()
	# So BaseUpdateHandler is not derived from BaseListGetHandler
	# If get() exists, update() may return incomplete results.

	def update(self, data : Union[BaseEntry, dict], options=None) -> Optional[BaseEntry]:
		"""wrapper around _update()
			makes PUT request
			returns result as Entry object or None.
		"""
		return self._update(self._url, data, options)

	def _update(self, url, data : Union[BaseEntry, dict], options) -> Optional[BaseEntry]:
		"""makes PUT request, returns result as Entry object or None."""
		if not isinstance(data, BaseEntry) and not isinstance(data, dict):
			raise ApiException("update(data): data must be a subclass of BaseEntry or dict. But got "+type(data).__name__)
		url += self.getOptionsStr(options)
		resp = self._api.makeRequest ("PUT", url, data) 

		if isinstance(data, BaseEntry):
			#invalidate old entry, so a new get() is called when accessing changed attributes
			if self._hasmethod("get"):
				data._getComplete = False
				for key in data._changes:
					if key != "Id":
						del data.__dict__[key]	#__getattr__ is only called when attr does not exist
			data.clearChanges()

		self._cache = {}
		if 'Result' not in resp:
			return None
		else:
			e = self.createEntryClass(resp['Result']) 
			e._getComplete = False
			return e

	def __setattr__(self, key, value):
		"""Convenience method for a more easy user experience.
			Example:
				handler.x = y
			Allows modifying the attributes directly.
			Warning: Every access causes a PUT operation.
			To update within a single PUT, use explicit get() and update() methods.
		"""
		if isinstance(value, BaseEntry):
			value = value["Id"]
		if key.startswith("_") or key in self.__dict__:
			self.__dict__[key] = value
			return
		self.update({key:value})


class BaseModifyHandler(BaseUpdateHandler, BaseGetHandler):
	pass


class BaseListHandler(BaseHandler):
	"""
		This handler provides read access to lists of objects.
		It implements list() (getlist).
		Example:
			entries = handler.list()
	"""
	# There are endpoints that implement list() but not get() (e.g. Logs or Notifications)

	def list(self, offset=0, limit=None, sortKey=None, sortDir=None, searchFilter=None) -> List[BaseEntry]:
		"""wrapper around _list()
			makes GET request
			returns a list of Entry objects
		"""
		if limit == None:
			complete_list = []
			list_offset = offset
			max_limit = 10000 	# 10000 is the max limit allowed - defined in rsuwebadmmgmapi.cpp
			while len(complete_list) % max_limit == 0:
				received_list = self._list(self._url, list_offset, max_limit, sortKey, sortDir, searchFilter)
				if len(received_list) == 0:
					break
				complete_list += received_list
				list_offset += max_limit
			return complete_list
		else:
			return self._list (self._url, offset, limit, sortKey, sortDir, searchFilter)

	def _list(self, url, offset, limit, sortKey, sortDir, searchFilter) -> List[BaseEntry]:
		"""makes GET request, returns a list of Entry objects"""
		url += "?offset=" + str(offset)
		if limit != None:
			url += "&limit=" + str(limit)
		if sortKey != None:
			url +="&sort=" + str(sortKey)
		if sortDir != None:
			url +="&sortDir=" + str(sortDir)
		if searchFilter != None:
			url += searchFilter.getQuery()
		resp = self._api.makeRequest ("GET", url)
		if 'Result' not in resp:
			raise ApiException ("Missing 'Result' parameter in JSON response")
		return self.createEntryList (resp['Result'])

	def _callEntryFunction(self, id, url, method="POST", options=None, **kwargs):
		url = "/" + str(id) + url
		return self._callFunction(url, method, options=options, **kwargs)

	def __iter__(self):
		"""Convenience method for a more easy user experience.
			Called with 'for data in handler: ...'
		"""
		return iter(self.list())

	def createEntryList(self, arr) -> List[BaseEntry]:
		ret = []
		for data in arr:
			obj = self.createEntryClass(data)
			ret.append(obj)
		return ret


class BaseListGetHandler(BaseListHandler, BaseGetHandler):
	"""
		This handler provides read access to lists of objects.
		It implements get(id), inherits list()
		Example:
			data = handler.get(id)
	"""
	# Assumtion: When there is get(id) from list, there must be list()
	# If get(id) and list() exist, list() may return incomplete results

	def get(self, id : int, options=None, url = None) -> BaseEntry:
		"""wrapper around BaseGetHandler._get()
			makes GET request
			returns result as Entry object
		"""
		if url:
			url = url.removeprefix("/api/")
			ret = self._get (url, options)
		else:
			ret = self._get (self._url + "/" + str(id), options)
		if not "Id" in ret.__dict__:
			ret.Id = id
		return ret

	def __getattr__(self, key):
		if key in self.__dict__:
			return key
		else:
			raise AttributeError(self.__class__.__name__ +" object has no attribute "+repr(key))

	def __getitem__(self, index):
		"""Convenience method for a more easy user experience.
			Example:
				data = handler[id]
		"""
		if isinstance(index, int):
			return self.get(index)
		else:
			raise TypeError(self.__class__.__name__ +" index must be of type int, got " + index.__class__.__name__)

	def __str__(self):
		return str(self.list())

class BaseListFindHandler(BaseListGetHandler):
	"""
		This handler provides read access to lists of objects.
		It implements find() and inherits list() and get(id).
		Example:
			data = handler.find(name)
	"""
	# Assumtion: When there is find(), there must be list() and get(id)

	def find(self, searchValue, searchKey="Name", throw=False, options={}) -> Optional[BaseEntry]:
		"""wrapper around _find(), returns Entry object
			if throw is true, an exception is raised when no entry is found.
			otherwise None is returned
		"""
		modifiedOptions = copy.deepcopy(options)
		if "returnValues" not in options:
			modifiedOptions["returnValues"] = "true"
		modifiedOptions[searchKey] = searchValue
		return self._find(self._url + "/find", throw=throw, **modifiedOptions)

	def _find(self, url, throw=False, **options) -> Optional[BaseEntry]:
		"""makes GET request, returns result as Entry object"""
		url += self.getOptionsStr(options)
		resp = self._api.makeRequest ("GET", url)
		if 'Result' not in resp:
			raise ApiException ("Missing 'Result' parameter in JSON response", resp['Error'])
		result = resp['Result']
		if 'Id' not in result:
			raise ApiException ("Missing 'Result.Id' parameter in JSON response", resp['Error'])
		id = result['Id']
		if id == 0:
			if throw:
				raise APIEXCEPTIONS["NotFound"] ("Entry not found", resp['Error'])
			else:
				return None
		e = self.createEntryClass(resp['Result'])
		return e

	def __getitem__(self, index):
		"""Convenience method for a more easy user experience.
			Example 1:
				data = handler[name]
			Example 2:
				data = handler[id]
		"""
		if isinstance(index, int) and self._hasmethod("get"):
			return self.get(index)
		elif isinstance(index, str):
			return self.find(index, throw=True)
		elif self._hasmethod("get"):
			raise TypeError(self.__class__.__name__ +" index must be of type int or string, got " + index.__class__.__name__)
		else:
			raise TypeError(self.__class__.__name__ +" index must be of type string, got " + index.__class__.__name__)


class BaseListUpdateHandler(BaseListHandler):
	"""
		This handler provides write access to lists of objects.
		It implements update() and inherits list().
		Example 1:
			data = handler.get(id)
			data.x = y
			handler.update(data)
		Example 2:
			data = {x: y}
			handler.update(id, data)
	"""
	# If get(id) exists, update() may return incomplete results.

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
			id = id_or_data
		else:
			d = id_or_data
			if isinstance(d, BaseEntry):
				id = d.__dict__["Id"]
			elif isinstance(d, dict) and "Id" in d:
				id = d["Id"]
			else:
				raise TypeError("update() is missing one required argument: 'data'")
		return self._update(self._url + "/" + str(id), d, options)

	def _update(self, url, data : Union[BaseEntry, dict], options) -> Optional[BaseEntry]:
		"""makes PUT request, returns result as Entry object or None."""
		if not isinstance(data, BaseEntry) and not isinstance(data, dict):
			raise ApiException("update(data): data must be a subclass of BaseEntry or dict. But got "+type(data).__name__)
		url += self.getOptionsStr(options)
		resp = self._api.makeRequest ("PUT", url, data) 

		if isinstance(data, BaseEntry):
			#invalidate old entry, so a new get() is called when accessing changed attributes
			if self._hasmethod("get"):
				data._getComplete = False
				for key in data._changes:
					if key != "Id":
						del data.__dict__[key]	#__getattr__ is only called when attr does not exist
			data.clearChanges()

		self._cache = {}
		if 'Result' not in resp:
			return None
		else:
			e = self.createEntryClass(resp['Result']) 
			e._getComplete = False
			return e

	def __setitem__(self, index, data):
		"""Convenience method for a more easy user experience.
			Example 1:
				handler[name] = data
			Example 2:
				handler[id] = data
		"""
		if isinstance(index, int):
			return self.update(index, data)
		elif isinstance(index, str) and self._hasmethod("find"):
			index = self.find(index, throw=True).Id
			self.update(index, data)
		elif self._hasmethod("find"):
			raise TypeError(self.__class__.__name__ +" index must be of type int or string, got " + index.__class__.__name__)
		else:
			raise TypeError(self.__class__.__name__ +" index must be of type int, got " + index.__class__.__name__)


class BaseListInsertHandler(BaseListHandler):
	"""
		This handler provides write access to lists of objects.
		It implements insert() and inherits list().
		Example:
			data = handler.newEntry()
			data.x = y
			handler.insert(data)
	"""

	def newEntry(self) -> BaseEntry:
		"""creates a new local empty entry that can be filled before insert()"""
		return self.createEntryClass()

	def insert(self, data : Union[BaseEntry, dict], options=None) -> BaseEntry:
		"""wrapper around _insert()
			makes POST request
			returns result as Entry object.
		"""
		return self._insert(self._url, data, options)

	def _insert(self, url, data : Union[BaseEntry, dict], options) -> BaseEntry:
		"""makes POST request, returns result as Entry object."""
		url += self.getOptionsStr(options)
		resp = self._api.makeRequest ("POST", url, data)
		if 'Result' not in resp:
			raise ApiException ("Missing 'Result' parameter in JSON response")
		e = self.createEntryClass()
		e._update(data)
		e._update(resp['Result'])
		e.clearChanges()
		return e


class BaseListDeleteHandler(BaseListHandler):
	"""
		This handler provides write access to lists of objects.
		It implements delete() and inherits list().
		Example:
			handler.delete(id)
	"""
	def delete(self, id : Union[int, BaseEntry]):
		"""wrapper around _delete()
			makes DELETE request
			returns True.
		"""
		if isinstance(id, BaseEntry):
			id = id["Id"]
		return self._delete(self._url + "/" + str(id))

	def _delete(self, url : str):
		"""makes DELETE request, returns True."""
		resp = self._api.makeRequest ("DELETE", url)
		return True

	def __delitem__(self, index : Union[int, str]):
		"""Convenience method for a more easy user experience.
			Example 1:
				del handler[name]
			Example 2:
				del handler[id]
		"""
		if isinstance(index, int):
			return self.delete(index)
		elif isinstance(index, str) and self._hasmethod("find"):
			index = self.find(index, throw=True).Id
			return self.delete(index)
		elif self._hasmethod("find"):
			raise TypeError(self.__class__.__name__ +" index must be of type int or string, got " + index.__class__.__name__)
		else:
			raise TypeError(self.__class__.__name__ +" index must be of type int, got " + index.__class__.__name__)


class BaseListModifyHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	pass


class BaseApi():
	"""Root node of the API. Designed to be used by any REST-API."""
	def __init__ (self, host, auth, port=None, tls=True, ssl_verify=True, ssl_cafile=None, ssl_capath=None, ssl_cadata=None, verbose=False, show_requests=False):
		""" Creates an object to access the API.
			host (str): hostname or ip-address.
			auth (AuthBase): authentication credential object
			port (optional, int): tcp port of SEM REST interface. Defaults to 12512.
			tls (optional, bool): use tls for secure connection. Defaults to True.
				When tls is set to False, all ssl options are ignored.
			ssl_verify (optional, bool): verify ssl certificates. Defaults to True. 
			ssl_cafile, ssl_capath, ssl_cadata represent optional CA certificates to trust for
				certificate verification, as in SSLContext.load_verify_locations(). If all three
				are None, ssl functions can choose to trust the system's default CA certificates.
				If tls or ssl_verify is set to False, those options are ignored.
			verbose (optional, bool): print requests and response to stdout. Defaults to False.
			show_requests (optional. bool): print requests stdout. Defaults to False.
		"""
		self._tls = tls
		if tls:
			self._ssl_verify = ssl_verify
		else:
			self._ssl_verify = False
		if self._ssl_verify:
			self._ssl_ca_options = {
				"cafile": ssl_cafile,
				"capath": ssl_capath,
				"cadata": ssl_cadata,
			}
		else:
			self._ssl_ca_options = {}

		if not hasattr(self, "_host"):
			# derived classes may set self._host before
			self._host = BaseApi.composeURL(host, port, tls)
		self._auth = auth 
		self._sessId = ""
		self._verbose = verbose
		self._show_requests = show_requests
		if hasattr(self, "_authCallback"):
			# derived classes may define a _authCallback function that is called by auth. Since this is not required and should not be exposed to the user, it is stored as attribute rather than as parameter for init
			cb = self._authCallback
		else:
			cb = None
		self._auth.init(self._host, tls, self._ssl_verify, self._ssl_ca_options, callback=cb)

	def composeURL(host:str, port:int, tls:bool):
		""" Create URL in form of 'http(s):{host}:{port}'
			port is optional and can be None
			tls must be set
			host may or may not contain the port and 'http(s):// at the beginning'
		"""
		if tls:
			if host.startswith("https://"):
				url = host
			elif host.startswith("http://"):
				raise ValueError("host starts with 'http://' but should be 'https://' since tls=True")
			else:
				url = "https://" + host
		else:
			if host.startswith("http://"):
				url = host
			elif host.startswith("https://"):
				raise ValueError("host starts with 'https://' but should be 'http://' since tls=False")
			else:
				url = "http://" + host
		if port:	# may be None
			parts = url.split(":")	# first : is after http(s)
			if len(parts) > 2:
				if parts[-1] != str(port):
					raise ValueError(f"host contains port '{parts[-1]}' but explicit port '{port}' was given.")
			else:
				# no port given inside host, just append it
				url += ":"+ str(port)
		return url

	def _sendRequest(self, url, data, headers, method):
		resp = ""	# json http response as dict
		err = {}	# http error object, if error occured
		msg = ""	# http exception message, if error occured
		try:
			if self._tls:
				context = ssl.create_default_context(**self._ssl_ca_options)
				if not self._ssl_verify:
					context.check_hostname = False
					context.verify_mode = ssl.CERT_NONE
			else:
				context = None
			conn = urllib.request.Request(url, data=data, headers=headers, method=method)
			res = urllib.request.urlopen(conn, context=context)	# here an Exception may be thrown
			self._httpStatusCode = res.getcode()
			self._httpReason = res.msg
			content = res.read().decode("utf-8")
			resp = json.loads(content)
		except urllib.error.HTTPError as e:
			err["URL"] = url
			err["HttpStatusCode"] = e.code
			err["Reason"] = e.reason
			try:
				# e.read() is the same as res.read()
				content = e.read().decode("utf-8")
				resp = json.loads(content)
				err["Response"] = resp
				if "Error" in resp and "Message" in resp["Error"]:
					msg = resp["Error"]["Message"]
			except:
				# some strage exception
				msg = str(e)
		except urllib.error.URLError as e:
			err["URL"] = url
			err["Reason"] = e.reason
			msg = str(e)
		return resp, err, msg

	def makeRequest (self, method, url, data : Union[None, BaseEntry, dict] = None):
		"""Sends REST-Request to url. Returns Response object as dict."""
		if self._verbose:
			print ("URL------------")
		if self._verbose or self._show_requests:
			print (method + " " + "/api/" + url)
		headers = {
			'Accept'		: 'application/json,UTF-8',
			'Content-Type'	: 'application/json',
		}

		headers.update(self._auth.getHeader())	#accessToken, called login if required

		url = self._host + url
		currPostData = self.getPostData (data)
		resp, err, msg = self._sendRequest(url, currPostData, headers, method)
		if err.get("HttpStatusCode") == 401:
			if hasattr(self._auth, "_login"):
				#try again with login
				self._auth._login()	# if login failes, this raises ApiAuthenticationException 
				headers.update(self._auth.getHeader())	#accessToken
				resp, err, msg = self._sendRequest(url, currPostData, headers, method)
		if err:
			raise getApiException(msg, err)

		# from here, err is an API error
		err = resp['Error']
		if 'Message' not in err:
			raise ApiException ("Missing 'Message' parameter in 'Error' object")
		if err['Message'] != "":
			err['URL'] = url
			if err["Message"]:
				msg = err["Message"]
				del err["Message"]	#entfernt element aus dict
		if self._verbose:
			print ("DICT-----------")
			pprint(resp)	#print the python dict
			print ("---------------")

		return resp


	def getPostData (self, data : Union[None, BaseEntry, dict]):
		d = {}
		if data != None:
			if isinstance (data, BaseEntry):
				for k in data._changes:
					if k == "_changes":
						continue
					d[k] = data._changes[k]
			else:
				d = data

		ret = bytes(json.dumps (d), encoding="utf-8")
		return ret

