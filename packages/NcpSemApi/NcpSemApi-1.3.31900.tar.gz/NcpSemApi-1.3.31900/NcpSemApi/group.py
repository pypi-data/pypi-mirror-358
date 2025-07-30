from .base import *
from .client import *
from .firewall import *
from .radius import *
from .pki import *
from .license import *
from .semmgm import *

from .cached_property import cached_property

import importlib.util
import sys
import tempfile

class SemGroup(LazyListEntry):
	'''Configuration of a sem group

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by

	Attributes [writable]
	---------------------
		Name : string
			Name

		Description : string
			Description

		FullGroupName : string
			Full group name

		Suffix : string
			Suffix

		LdapDN : string
			LDAP DN

		InitUser : string
			Init Username

		UseLicKeysInSubGroups : boolean
			Use license keys in subgroups

		DebugLevel : integer
			Debug Level

		MaxManagedUnits : integer
			Max. managed units

		AuthCodeResetClientCfg : integer
			Reset Authentication Code: Client Configuration
			Enum Values: 0=default, 1=disableReset, 2=defaultWithSubgroups, 3=disableResetWithSubgroups

		AuthCodeResetCert : integer
			Reset Authentication Code: Certificate
			Enum Values: 0=default, 1=disableReset, 2=defaultWithSubgroups, 3=disableResetWithSubgroups

	Sub-Handlers
	------------
		subGroups
			Access SemGroupsHandler

		softwareUpdateLists
			Access SoftwareUpdateListsHandler

		admins
			Access AdminsHandler

		adminGroups
			Access AdminGroupsHandler

		notifications
			Access NotificationsHandler

		semLogs
			Access SemLogsHandler

		tasks
			Tasks TasksHandler

		clientTemplates
			Access ClientTemplatesHandler
			Configuration of Client Templates

		clientConfigurations
			Access ClientConfigurationsHandler
			Configuration of Clients

		firewallTemplates
			Access FirewallTemplatesHandler
			Configuration of Firewall Templates

		radiusTemplates
			Access RadiusTemplatesHandler
			Configuration of RADIUS Templates

		radiusUserConfigurations
			Access RadiusUserConfigurationsHandler
			Configuration of RADIUS Users

		radiusGroupSettings
			Access RadiusGroupSettingsHandler
			Configuration of RADIUS Groups Settings

		radiusUsers
			Access RadiusUsersHandler
			State of RADIUS Users

		radiusSessions
			Access RadiusSessionsHandler
			State of RADIUS Sessions

		radiusAccountingDetails
			Access RadiusAccountingDetailsHandler
			RADIUS Accounting Details

		licenseDetails
			Access LicensesHandler
			Management of licenses

		licenseOverview
			Access LicenseOverviewHandler
			Overview of licenses

		subscriptions
			Access SubscriptionsHandler
			Management of subscriptions

		certificateRequests
			Access CertificateRequestsHandler
			Mamagement of Certificarte Requests

		issuedCertificates
			Access IssuedCertificatesHandler
			Mamagement of issued Requests

		certificateTemplates
			Access CertificateTemplatesHandler
			Configuration of PKI Certificate Templates

		pkiProfiles
			Access PkiProfilesHandler
			Configuration of PKI Profiles
	'''

	#--------------------------------------------------------
	# SEM Base Management
	#--------------------------------------------------------
	@cached_property
	def subGroups(self):
		return SemGroupsHandler(self._getHandler._api, self.Id)

	@cached_property
	def softwareUpdateLists(self):
		return SoftwareUpdateListsHandler(self._getHandler._api, self.Id)

	@cached_property
	def admins(self):
		return AdminsHandler(self._getHandler._api, self.Id)

	@cached_property
	def adminGroups(self):
		return AdminGroupsHandler(self._getHandler._api,self.Id)

	@cached_property
	def notifications(self):
		return NotificationsHandler(self._getHandler._api, self.Id)

	@cached_property
	def semLogs(self):
		return SemLogsHandler(self._getHandler._api, self.Id)

	@cached_property
	def semScripts(self):
		return SemScriptsHandler(self._getHandler._api, self.Id)

	@cached_property
	def tasks(self):
		return TasksHandler(self._getHandler._api, self.Id)

	def import_script(self, sem_script):
		"""Import a python script from the SEM and return the loaded module.
			examples:
				my_script = grp.import_script("my_script")
			or
				script = grp.semScripts.find("my_script")
				my_script = grp.import_script(script)
			both examples produce a similar outcome as 'import my_script' would, if my_script was a file.

			When import_script() is called, the script is downloaded from the SEM into a temporary file.
			The file is imported as module, and gets deleted when the function returns.
		"""
		if isinstance(sem_script, str):
			sem_script = self.semScripts.find(sem_script, throw=True)	# raises Exception if not found
		if not isinstance(sem_script, SemScript):
			raise TypeError(f"First argument of import_script() must be of type SemScript or str, but is of type {type(sem_script)}")

		delete_args = {
			"delete": True
		}
		if sys.version_info.minor >= 12:
			# since python 3.12 delete_on_close is needed on windows, but it is not defined on earlier python versions
			delete_args["delete_on_close"] = False

		with tempfile.NamedTemporaryFile(mode="w", suffix=".py", encoding="utf-8", **delete_args) as file:
			script = sem_script.Script
			# the encoding of script from sem is latin-1, but it is stored in a string, so python assumes it is utf-8 encoded.
			# this line converts it to the correct utf-8 string:
			script = bytes(script, "latin-1").decode("latin-1")
			file.write(script)
			file.seek(0)
			path = file.name
			# for documentation see: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
			spec = importlib.util.spec_from_file_location(sem_script.Name, path)
			module = importlib.util.module_from_spec(spec)
			sys.modules[sem_script.Name] = module
			spec.loader.exec_module(module)
			return module


	#--------------------------------------------------------
	# Client plug-in
	#--------------------------------------------------------
	# Configuration of Client Templates
	@cached_property
	def clientTemplates(self):
		return ClientTemplatesHandler (self._getHandler._api, self.Id)

	# Configuration of Clients
	@cached_property
	def clientConfigurations(self):
		return ClientConfigurationsHandler (self._getHandler._api, self.Id)


	#--------------------------------------------------------
	# Firewall plug-in
	#--------------------------------------------------------
	# Configuration of Firewall Templates
	@cached_property
	def firewallTemplates(self):
		return FirewallTemplatesHandler(self._getHandler._api, self.Id)

	#--------------------------------------------------------
	# RADIUS plug-in
	#--------------------------------------------------------
	# Configuration of RADIUS Templates
	@cached_property
	def radiusTemplates(self):
		return RadiusTemplatesHandler (self._getHandler._api, self.Id)

	# Configuration of RADIUS Users
	@cached_property
	def radiusUserConfigurations(self):
		return RadiusUserConfigurationsHandler (self._getHandler._api, self.Id)

	# Configuration of RADIUS Groups Settings
	@cached_property
	def radiusGroupSettings(self):
		return RadiusGroupSettingsHandler(self._getHandler._api, self.Id)

	# State of RADIUS Users
	@cached_property
	def radiusUsers(self):
		return RadiusUsersHandler(self._getHandler._api, self.Id)

	# State of RADIUS Sessions
	@cached_property
	def radiusSessions(self):
		return RadiusSessionsHandler(self._getHandler._api, self.Id)

	# RADIUS Accounting Details
	@cached_property
	def radiusAccountingDetails(self):
		return RadiusAccountingDetailsHandler(self._getHandler._api, self.Id)

	#--------------------------------------------------------
	# License Plug-in
	#--------------------------------------------------------
	# Management of licenses
	@cached_property
	def licenseDetails(self):
		return LicenseDetailsHandler(self._getHandler._api, self.Id)

	# Overview of licenses
	@cached_property
	def licenseOverview(self):
		return LicenseOverviewHandler(self._getHandler._api, self.Id)

	# Management of subscriptions
	@cached_property
	def subscriptions(self):
		return SubscriptionsHandler(self._getHandler._api, self.Id)

	#--------------------------------------------------------
	# PKI plug-in
	#--------------------------------------------------------
	# Mamagement of Certificarte Requests
	@cached_property
	def certificateRequests(self):
		return CertificateRequestsHandler(self._getHandler._api, self.Id)

	# Mamagement of issued Requests
	@cached_property
	def issuedCertificates(self):
		return IssuedCertificatesHandler(self._getHandler._api, self.Id)

	# Mamagement of CA certificates
	@cached_property
	def cACertificates(self):
		return CACertificatesHandler(self._getHandler._api, self.Id)

	# Configuration of PKI Certificate Templates
	@cached_property
	def certificateTemplates(self):
		return CertificateTemplatesHandler(self._getHandler._api, self.Id)

	# Configuration of PKI Profiles
	@cached_property
	def pkiProfiles(self):
		return PkiProfilesHandler(self._getHandler._api, self.Id)


	#--------------------------------------------------------
	# Attributes
	#--------------------------------------------------------

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def Description(self):
		return self.__getattr__("Description")

	@cached_property
	def FullGroupName(self):
		return self.__getattr__("FullGroupName")

	@cached_property
	def Suffix(self):
		return self.__getattr__("Suffix")

	@cached_property
	def LdapDN(self):
		return self.__getattr__("LdapDN")

	@cached_property
	def InitUser(self):
		return self.__getattr__("InitUser")

	@cached_property
	def UseLicKeysInSubGroups(self):
		return self.__getattr__("UseLicKeysInSubGroups")

	@cached_property
	def DebugLevel(self):
		return self.__getattr__("DebugLevel")

	@cached_property
	def MaxManagedUnits(self):
		return self.__getattr__("MaxManagedUnits")

	@cached_property
	def AuthCodeResetClientCfg(self):
		return self.__getattr__("AuthCodeResetClientCfg")

	@cached_property
	def AuthCodeResetCert(self):
		return self.__getattr__("AuthCodeResetCert")


class SemGroupsHandler(BaseListModifyHandler):
	def __init__ (self, api, parentGrpId):
		BaseHandler.__init__ (self, api, "sem-mgm/groups")
		self._parentGrpId = parentGrpId

	def list (self, offset=0, limit=10000, sortKey=None, sortDir=None, searchFilter=None):
		# offset has to be set manually if sem has over 10000 groups
		url = self._url + "/" + str(self._parentGrpId) + "/subgroups"
		return self._list (url, offset, limit, sortKey, sortDir, searchFilter)

	def find (self, groupName, options={}):
		# find uses the absolute FullGroupName - so it is not relavtive to the group it it called on!
		url = self._url + "/" + str(self._parentGrpId) + "/find"
		modifiedOptions = copy.deepcopy(options)
		if "returnValues" not in options:
			modifiedOptions["returnValues"] = "false"
		return self._find (url, FullGroupName=groupName, **modifiedOptions)

	def insert (self, data, options=None):
		url = self._url + "/" + str(self._parentGrpId) + "/subgroups"
		return self._insert(url, data, options)

	def createEntry(self) :
		return SemGroup (self)

