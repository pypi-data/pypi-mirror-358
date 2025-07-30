from .base import BaseEntry, BaseListHandler
from .sem import NcpSemApi
from .apiauth import AuthAccessToken
from .group import SemGroup
import os
from collections.abc import Iterable
import socket
import json
import struct
import re
from enum import Enum

class Wizard(NcpSemApi):
	def __init__(self, auth=None, **kwargs):
		env = os.environ
		host = env.get("NCP_SEMAPI_HOST")
		if not host:
			raise RuntimeError("Scripts that use the NcpSemApi.Wizard class can only be run from the SEM-WebUI.")
		token = env.get("NCP_SEMAPI_ACCESS_TOKEN")
		self.upd_port = int(env.get("NCP_SEM_WEBUI_UDP_PORT"))
		if "port" not in kwargs:
			kwargs["port"] = int(env.get("NCP_SEMAPI_PORT"))
		if "ssl_verify" not in kwargs:
			# we connect to localhost, so verification it is not needed.
			# however there often is a self-signed certificate in use;
			# ssl_verify does not like those.
			kwargs["ssl_verify"] = False
		if auth:
			_auth = auth
		else:
			if not token:
				raise RuntimeError("Missing access token. Scripts that use the NcpSemApi.Wizard class can only be run from the SEM-WebUI.")
			_auth = AuthAccessToken(token)
		super().__init__(host, _auth, **kwargs)
		self._stored_default_values = {}	# used when a Page element is present
		self.dialog_results = {}	# contains all answers from all calls, so the user does not have to update the returned results on their own.

	def dialog(self, *args):
		"""Displays a dialog in the WebUI.
			The args must be UI-Elements, defined by the classes in NcpSemApi.ui
		"""
		request_list = []
		key_elements = dict()
		once_classes_used = set()
		for arg in args:
			# Caption and Page can only occure once
			if isinstance(arg, OncePerDialog):
				cls = type(arg)
				if cls in once_classes_used:
					raise ValueError(f"{cls} can only be used once per dialog")
				once_classes_used.add(cls)

		# when Page is present, try to load previously stored answers as default values, if no default value is given by the user
		if Page in once_classes_used:
			for arg in args:
				if isinstance(arg, InputElement) and arg.default is None:
					arg.default = self._stored_default_values.get(arg.key)

		for arg in args:
			# set sem, since some selectors may call get()
			arg.sem = self
			# convert to json
			jarg = arg.to_json()
			# each key must only occure once
			if "key" in jarg:
				if jarg["key"] in key_elements:
					raise ValueError("duplicate key '{0}' found".format(jarg["key"]))
				else:
					key_elements[jarg["key"]] = arg
			# add to requested ui elements
			request_list.append(jarg)

		# make the call
		answers = self.udpComm(request_list)
		result = dict()
		for key, value in answers.items():
			if key in key_elements:
				element = key_elements[key]
				retval = element.return_value(value)
				result[key] = retval
				self.dialog_results[key] = retval
				if Page in once_classes_used:
					# when Page element is present, store the answers and apply them, whenever the key is used again. If the Page element is not present, don't store the answer internally, to not confuse unexperienced script users who use the same keys in multiple dialogues.
					if isinstance(element, Select):
						# Select may return the element, instead of the index
						self._stored_default_values[key] = element.return_value(value, return_index=True)
					else:
						self._stored_default_values[key] = retval
		return result

	def udpComm(self, data):
		# send
		message = bytes(json.dumps(data),encoding="utf-8")
		size = len(message)
		assert size < 2**32, "Dialog message size exceeds maximum of 2**32 bytes"
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		while size > 0:
			# send in 4k chunks
			msg_size = min(size, 4096-4)
			buffer = struct.pack(f"!I{msg_size}s", size, message)
			if self._verbose:
				print("udpComm: send "+str(len(buffer))+" bytes to "+str(self.upd_port), flush=True)
			sock.sendto(buffer, ("localhost", self.upd_port))
			if size > msg_size:
				message = message[msg_size:]
			size -= msg_size

		# receive
		message = bytes()
		while True:
			buffer, addr = sock.recvfrom(4096)
			if self._verbose:
				print("udpComm: got "+str(len(buffer))+" bytes", flush=True)
			size = struct.unpack_from("!I", buffer)[0]
			if self._verbose:
				print("udpComm: size: "+str(size), flush=True)
			msg_size = min(size, 4096-4)
			message += struct.unpack_from(f"{msg_size}s", buffer, offset=4)[0]
			if size == msg_size:
				break

		# parse
		message = str(message, encoding="utf-8")
		try:
			message = json.loads(message)
		except Exception as e:	# TODO better type
			raise Exception("data: "+repr(message)) from e
		return message 

### Base classes:

class OncePerDialog:
	"""Classes derived from this class can be used only once per dialog"""
	pass

class InputElement:
	"Classes derived from this class have a key, a label and a default value"
	def __init__(self, key, label=None, default=None):
		self.key = str(key)
		self.label = str(label or key)	# uses key if label is empty 
		self.default = default
		self.sem = None	# is set by calling dialog

### Output Elements:

class Caption(OncePerDialog):
	def __init__(self, value):
		"""Displays a caption for the dialog."""
		self.value = str(value)
	
	def to_json(self):
		return {"type": "caption", "value": self.value}

class Label:
	def __init__(self, first, second=None):
		"""Displays a label.
			Call with ui.Label("line spanning string") for a single string.
			Call with ui.Label("key", "value") for a key-value/pair of stings.
		"""
		if second is None:
			self.value = str(first)
			self.key = None
		else:
			self.key = str(first)
			self.value = str(second)
	
	def to_json(self):
		if self.key:
			return {"type": "label", "key": self.key, "value": self.value}
		else:
			return {"type": "label", "value": self.value}
			
### Input elements:

class TextInput(InputElement):
	class AddressType(Enum):
		IPADDR = "ipaddr"
		IPV4 = "ipv4"
		IPV6 = "ipv6"
		MACADDR = "macaddr"

	def __init__(self, key, label=None, default=None, is_password=False, address_type=None, regex=None):
		"""Asks the user to provide an input string."""
		InputElement.__init__(self, key, label=label, default=default)
		if not isinstance(is_password, bool):
			raise TypeError("is_password must be of type bool")
		self.is_password = is_password
		_address_type = address_type
		if address_type is not None:
			if isinstance(_address_type, str):
				_address_type = TextInput.AddressType(address_type)
			elif not isinstance(_address_type, TextInput.AddressType):
				raise TypeError("address_type must be of type TextInput.AddressType")
		self.address_type = _address_type
		if regex:
			self.regex = re.compile(regex)
		else:
			self.regex = None
	
	def to_json(self):
		if self.default is None:
			default = ""
		else:
			default = str(self.default)
		result = {
			"type": "str",
			"key": self.key,
			"label": self.label,
			"default": default,
			"is_password": self.is_password
		}
		if self.address_type is not None:
			result["address_type"] = self.address_type.value
		if self.regex is not None:
			result["regex"] = self.regex.pattern
		return result 
	
	def return_value(self, value):
		ret = str(value)
		if self.regex is not None:
			if self.regex.fullmatch(ret) is None:
				raise ValueError(f"returned value '{ret}' does not match regular expression '{self.regex.pattern}'")
		return ret

class NumberInput(InputElement):
	"""Asks the user to provide a number as input."""
	
	def to_json(self):
		if self.default is None:
			default = 0
		else:
			default = int(self.default)
		result = {
			"type": "int",
			"key": self.key,
			"label": self.label,
			"default": default
		}
		return result 
	
	def return_value(self, value):
		return int(value)

class Check(InputElement):
	"""Displays a checkbox"""
	
	def to_json(self):
		if self.default is None:
			default = False
		else:
			default = int(self.default)
		result = {
			"type": "bool",
			"key": self.key,
			"label": self.label,
			"default": default
		}
		return result 
	
	def return_value(self, value):
		return bool(value)

class Group(InputElement):
	"""Displays a group select box. Returns a sem group."""
	
	def to_json(self):
		default = 0
		if isinstance(default, SemGroup):
			default = default.Id
		elif isinstance(self.default, int):
			default = self.default
		elif isinstance(self.default, str):
			default = self.sem.getGroupByName(self.default)
			if not default:
				raise ValueError(f"Group: invalid default group '{self.default}'.")
			default = default.Id
		elif self.default is not None:
			raise TypeError(f"Parameter 'default' of 'Group' is of type {type(self.default)}. Expected one of SemGroup or int or str.")
		result = {
			"type": "group",
			"key": self.key,
			"label": self.label,
			"default": default
		}
		return result 
	
	def return_value(self, value):
		# with id
		id = int(value)
		if self.sem._semGroupsHandler is None:
			self.sem._getSessionInfo()
		entry = SemGroup(self.sem._semGroupsHandler)
		entry.Id = id
		return entry


class Select(InputElement):
	def __init__(self, key, values, label=None, default=None, attr_as_name="Name", return_index=False):
		"""Asks the user to select a value from a list."""
		InputElement.__init__(self, key, label=label, default=default)
		if isinstance(values, BaseListHandler):
			# forbid Handlers - call list manually
			raise TypeError(f"parameter 2 (values) of {type(self)} is of type {type(values)}. Expected list. Try: 'values.list()'")
		self.values = list(values)
		if len(self.values) < 1:
			raise ValueError("values must not be empty")
		self.return_index = return_index
		self.attr_as_name = attr_as_name
	
	def to_json(self):
		if self.default is None:
			default = 0
		else:
			default = int(self.default)
		if not (0 <= default < len(self.values)):
			raise ValueError(f"default must be a valid index for values (0 <= default < {len(self.values)}). Got {self.default}")

		# convert values to str
		str_values = []
		for value in self.values:
			if isinstance(value, BaseEntry) and hasattr(value, self.attr_as_name):
				str_values.append(str(value.__dict__[self.attr_as_name]))
			elif isinstance(value, str):
				str_values.append(value)
			elif hasattr(value, "value") and hasattr(value, "text"):
				# we don't have a data structure like that now
				str_values.append(str(value.text))
			else:
				str_values.append(str(value))	# raises exception when the given value can not be converted to string.
		result = {
			"type": "select",
			"key": self.key,
			"values": str_values,
			"default": default,
			"label": self.label
		}
		return result 

	def return_value(self, index, return_index=None):
		index = int(index)
		if not (0 <= index < len(self.values)):
			raise RuntimeError(f"Return index {index} out of bounds")
		if return_index is not None:
			# explicite argument is stronger than stored argument
			if return_index:
				return index
			return self.values[index]
		elif self.return_index:
			return index
		return self.values[index]

class Radio(Select):
	def to_json(self):
		result = Select.to_json(self)
		result["type"] = "radio"
		return result 

### Special elements:

class Page(OncePerDialog):
	def __init__(self, next="", back=""):
		"""Displays page navigation elements for multi-page dialogs.
			The key of the return value is always 'page'
		"""
		if next == "" and back == "":
			raise RuntimeError("Page: eighter next or back must be non-empty")
		self.next = str(next)
		self.back = str(back)
	
	def to_json(self):
		return {
			"type": "page",
			"key": "page",
			"next": self.next,
			"back": self.back,
			}

	def return_value(self, value):
		return str(value)


