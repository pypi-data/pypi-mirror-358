from .base import * 
from .group import *
from .semmgm import *
from .radius import *
from .traceloggers import *
from .cached_property import cached_property

class NcpSemApi(BaseApi):

	def __init__(self, host, *args, tls=True, port=None, **kwargs):
		__doc__ = BaseApi.__init__.__doc__
		self._rootGrpId = 0 
		self._semGroupsHandler = None
		self._host = NcpSemApi._composeURL(host, port, tls)
		self._authCallback = self._getSessionInfo
		BaseApi.__init__(self, host, *args, tls=tls, **kwargs)
		self._host = self._host + "/api/"	# in BaseApi.__init__ auth needs the host without "/api/". But for all future calls we need "/api/" in the URL.

	def _composeURL(host:str, port:int, tls:bool):
		""" When no port is given per host-string or port option,
			append the sem default ports
		"""
		url = BaseApi.composeURL(host, port, tls)
		if len(url.split(":")) == 2 and port is None:
			if tls:
				url += ":12512"
			else:
				url += ":12511"
		return url

	def _getSessionInfo(self):
		ret = self.makeRequest ("GET", "session-info")
		self._rootGrpId	= ret['Result']['RootGroupId']
		self._semGroupsHandler = SemGroupsHandler(self, self._rootGrpId)

	def getRootGroupId(self):
		"""returns id of the root group"""
		if self._rootGrpId == 0:
			self._getSessionInfo()
		return self._rootGrpId

	def getRootGroup(self):
		"""returns the handler of the root group."""
		if self._rootGrpId == 0:
			self._getSessionInfo()
			if self._rootGrpId == 0:
				raise ApiException("Login required")
		entry = SemGroup(self._semGroupsHandler)
		entry.Id = self._rootGrpId
		return entry
		
	def getGroupByName(self, name):
		"""returns the subgroup with the given name, if it exists."""
		if self._rootGrpId == 0:
			self._getSessionInfo()
			if self._rootGrpId == 0:
				raise ApiException("Login required")
		entry = self._semGroupsHandler.find(name)
		return entry

	def getAllGroups(self, rootGroup=None):
		"""recursive iterate over all groups.
			if rootGroup is given, yield only that group and all it's subgroups.
			if rootGroup is None (default), yield all available groups
		"""
		if rootGroup:
			grp = rootGroup
		else:
			grp = self.getRootGroup()
		yield grp
		for subGroup in grp.subGroups:
			yield from self.getAllGroups(subGroup)

	# SEM MGM
	@cached_property
	def semInfo(self):
		"""returns the semInfo handler."""
		return BaseGetHandler(self, "sem-mgm/info")

	@cached_property
	def semSettings(self):
		"""returns the semSettings handler."""
		return BaseListModifyHandler(self, "sem-mgm/settings")
		
	@cached_property
	def semLicense(self):
		"""returns the semLicense handler."""
		return BaseModifyHandler(self, "sem-mgm/license")

	@cached_property
	def stateDBReplication(self):
		"""returns the stateDBReplication handler."""
		return BaseGetHandler(self, "sem-mgm/state-db-repl")

	@cached_property
	def backupServers(self):
		"""returns the backupServers handler."""
		return BaseListHandler(self, "sem-mgm/backup-servers")

	@cached_property
	def semTraceLogs(self):
		"""returns the semTraceLogs handler."""
		return BaseListHandler(self, "sem-mgm/sem-trace-logs")

	@cached_property
	def semTraceLoggers(self):
		"""returns the semTraceLoggers handler."""
		return SemTraceLoggersHandler(self, "sem-mgm/trace-loggers")

	@cached_property
	def radiusClients(self):
		"""returns the radiusClients handler."""
		return RadiusClientsHandler(self, "radius-mgm/clients")
	
	@cached_property
	def radiusConfigurations(self):
		"""returns the radiusConfigurations handler."""
		return RadiusConfigurationsHandler(self, "radius-mgm/configurations")

	@cached_property
	def radiusDictionaries(self):
		"""returns the radiusDictionaries handler."""
		return RadiusDictionariesHandler(self, "radius-mgm/dictionaries")


	def import_script(self, sem_script, group=None):
		"""Import a python script from the SEM and return the loaded module.
			example:
				my_script = NcpSemApi.import_script("my_script")
			produces a similar outcome as 'import my_script' would, if my_script was a file.

			iIf a NcpSemApi.group is given, the script if seached in that group instead of the root group.
			You may also call grp.import_script(...) or give a NcpSemApi.SemScript directly as first parameter.

			When NcpSemApi.import_script() is called, the script is downloaded from the sem into a temporary file.
			The file is imported as module, and gets deleted when the function returns.
		"""
		if group is not None:
			return group.import_script(sem_script)
		else:
			return self.getRootGroup().import_script(sem_script)

