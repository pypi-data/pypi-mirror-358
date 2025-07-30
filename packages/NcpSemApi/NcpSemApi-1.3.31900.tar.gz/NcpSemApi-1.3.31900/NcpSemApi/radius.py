
#---------------------------------------------------------------
# This file is generated! Dont make any changes in this file.
#---------------------------------------------------------------
from .base import *
from .cached_property import cached_property



class RadiusTemplatesHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Management of RADIUS Templates

	Methods
	-------
		createEntry()
			Creates a new RadiusTemplate entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "radius-mgm/{groupid}/templates".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new RadiusTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusTemplate(self, self._groupid)
	

class RadiusTemplate(LazyModifiableListEntry):
	'''Parameters of RADIUS template

	Attributes [read-only]
	----------------------
		ConfiguredIn : string
			Configured in
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by

	Attributes [writable]
	---------------------
		Name : string
			Name
		GenerateTotpSecrets : boolean
			Generate T-OTP Secrets
		TOTPlabel : string
			T-OTP Label
		ForceNCPAppAuth : boolean
			Force NCP App Authentication
		Attributes : object(Model)
			Attributes
		InheritedToSubgroups : boolean
			Entry inherited to subgroups
	'''

	def __init__(self, getHandler, groupid):
		LazyModifiableListEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Name" : "",
			"GenerateTotpSecrets" : False,
			"TOTPlabel" : "",
			"ForceNCPAppAuth" : False,
			"Attributes" : [],
			"InheritedToSubgroups" : False,
			"ConfiguredIn" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def GenerateTotpSecrets(self):
		return self.__getattr__("GenerateTotpSecrets")
	
	@cached_property
	def TOTPlabel(self):
		return self.__getattr__("TOTPlabel")
	
	@cached_property
	def ForceNCPAppAuth(self):
		return self.__getattr__("ForceNCPAppAuth")
	
	@cached_property
	def Attributes(self):
		return self.__getattr__("Attributes")
	
	@cached_property
	def InheritedToSubgroups(self):
		return self.__getattr__("InheritedToSubgroups")
	
	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class RadiusUserConfigurationsHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Management of RADIUS Users

	Methods
	-------
		createEntry()
			Creates a new RadiusUserConfig entry object.
		generate_all_configs()
			Generates all RADIUS user configurations in this SEM group
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "radius-mgm/{groupid}/user-configs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		
	def generate_all_configs(self):
		'''Generates all RADIUS user configurations in this SEM group'''
		return self._callFunction('/generate-all-configs')

	def createEntry(self):
		'''Creates a new RadiusUserConfig entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusUserConfig(self, self._groupid)
	

class RadiusUserConfig(LazyModifiableListEntry):
	'''Parameters of RADIUS user configuration

	Attributes [read-only]
	----------------------
		TotpSecret : string
			Time based OTP secret
		TotpURI : string
			Time based OTP URI
		LastChangeTime : time
			Last change time
		LastCreationTime : time
			Last creation time
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by

	Attributes [writable]
	---------------------
		Name : string
			Name
		Template : string or integer from {Controller}
			Template
		UserName : string
			User Name
		Password : string
			Password
		Attributes : object(Model)
			Attributes
		NotBefore : time
			Not before
		NotAfter : time
			Not after

	Methods
	-------
		generate_config()
			Generates a RADIUS user configuration
	'''

	def __init__(self, getHandler, groupid):
		LazyModifiableListEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Name" : "",
			"Template" : "",
			"UserName" : "",
			"Password" : "",
			"TotpSecret" : "",
			"TotpURI" : "",
			"Attributes" : [],
			"NotBefore" : "",
			"NotAfter" : "",
			"LastChangeTime" : "",
			"LastCreationTime" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Template(self):
		return self.__getattr__("Template")
	
	@cached_property
	def UserName(self):
		return self.__getattr__("UserName")
	
	@cached_property
	def Password(self):
		return self.__getattr__("Password")
	
	@cached_property
	def TotpSecret(self):
		return self.__getattr__("TotpSecret")
	
	@cached_property
	def TotpURI(self):
		return self.__getattr__("TotpURI")
	
	@cached_property
	def Attributes(self):
		return self.__getattr__("Attributes")
	
	@cached_property
	def NotBefore(self):
		return self.__getattr__("NotBefore")
	
	@cached_property
	def NotAfter(self):
		return self.__getattr__("NotAfter")
	
	@cached_property
	def LastChangeTime(self):
		return self.__getattr__("LastChangeTime")
	
	@cached_property
	def LastCreationTime(self):
		return self.__getattr__("LastCreationTime")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
			
	def generate_config(self):
		'''Generates a RADIUS user configuration'''
		return self._callMethod('/generate-config')
	

class RadiusGroupSettingsHandler(BaseUpdateHandler, BaseGetHandler):
	'''Management of RADIUS group settings

	Methods
	-------
		createEntry()
			Creates a new RadiusGroupSettings entry object.
	
	Inherited Methods
	-----------------
		get (BaseGetHandler)
		update (BaseUpdateHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "radius-mgm/{groupid}/group-settings".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new RadiusGroupSettings entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusGroupSettings(self, self._groupid)
	

class RadiusGroupSettings(LazyEntry):
	'''Parameters of RADIUS group settings

	Attributes [read-only]
	----------------------
		ConfiguredIn : string
			Configured in
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by

	Attributes [writable]
	---------------------
		AllowProtPAP : boolean
			Allow protocol PAP
		AllowProtCHAP : boolean
			Allow protocol CHAP
		AllowProtMsChapV1 : boolean
			Allow protocol MSCHAPv1
		AllowProtMsChapV2 : boolean
			Allow protocol MSCHAPv2
		AllowProtEapMd5 : boolean
			Allow protocol EAP-MD5
		AllowProtEapTls : boolean
			Allow protocol EAP-TLS
		AllowProtEapNcpOtp : boolean
			Allow protocol EAP-NCP-OTP
		AllowProtEapMsChapV2 : boolean
			Allow protocol EAP-MSCHAPv2
		MaxErrorCount : integer
			Max. wrong RADIUS logins
		ResetTime : integer
			Reset RADIUIS lock after
		EapTlsCheckMode : integer
			EAP-TLS certificate check
			Enum Values: 0=disabled, 1=userNameEqCN, 2=UserNameEqEMail, 101=CNeqAttributeValue, 102=EMaileqAttributeValue
		TlsCheckAttributeName : string
			Certificate check attribute
		ExAuthNAS : boolean
			Ext. Authenitcation for NAS users
		ExAuthVPN : boolean
			Ext. Authenitcation for VPN users
		ExAuthManual : boolean
			Ext. Authenitcation for manual generated users
		ModifyUsername : integer
			Modify Username
			Enum Values: 0=keepUsername, 1=removeSuffix, 2=removePrefix
		ModifyUsernameString : string
			Modify Username String
		ExtAuthProtocol : integer
			Ext. authentication protocol
			Enum Values: 0=disabled, 1=otp, 2=ldap, 3=radius, 4=kerberos
		ExtAuthHostPrimary : string
			Ext. authentication primary host
		ExtAuthHostBackup : string
			Ext. authentication backup host
		ExtAuthPort : integer
			Ext. authentication port
		ExAuthLdapBindDN : string
			Ext. authentication LDAP bind DN
		ExAuthLdapMemberOf : string
			Ext. authentication LDAP member of
		ExAuthUseTLS : boolean
			Ext. authentication with TLS
		ExAuthDomainName : string
			Ext. authentication domain name
		ExAuthOtpSecret : string
			Ext. authentication OTP secret
		AdvAuthUseNAS : boolean
			NCP Adv. authenitcation for NAS users
		AdvAuthUseVPN : boolean
			NCP Adv. authenitcation for VPN users
		AdvAuthUseManual : boolean
			NCP Adv. authenitcation for manual generated users
		AdvAuthProvider : string
			NCP Adv. authenitcation provider
		AdvAuthUrlPrimary : string
			NCP Adv. authenitcation primary URL
		AdvAuthUrlBackup : string
			NCP Adv. authenitcation backup URL
		AdvAuthProxyHost : string
			NCP Adv. authenitcation proxy host
		AdvAuthProxyPort : integer
			NCP Adv. authenitcation proxy port
		AdvAuthProxyUsername : string
			NCP Adv. authenitcation username
		AdvAuthProxyPassword : string
			NCP Adv. authenitcation password
		AdvAuthPasscodeKind : integer
			NCP Adv. passcode kind
			Enum Values: 0=onlyNum, 1=alpha, 2=numAndAlpha, 3=all
		AdvAuthPasscodeLen : integer
			NCP Adv. passcode length
		TotpUseNAS : boolean
			Time-Based OTP for NAS users
		TotpUseVPN : boolean
			Time-Based OTP for VPN users
		TotpUseManual : boolean
			Time-Based OTP for manual generated users
		InheritedToSubgroups : boolean
			Entry inherited to subgroups
	'''

	def __init__(self, getHandler, groupid):
		LazyEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"AllowProtPAP" : True,
			"AllowProtCHAP" : True,
			"AllowProtMsChapV1" : True,
			"AllowProtMsChapV2" : True,
			"AllowProtEapMd5" : True,
			"AllowProtEapTls" : True,
			"AllowProtEapNcpOtp" : True,
			"AllowProtEapMsChapV2" : True,
			"MaxErrorCount" : 5,
			"ResetTime" : 0,
			"EapTlsCheckMode" : 0,
			"TlsCheckAttributeName" : "",
			"ExAuthNAS" : False,
			"ExAuthVPN" : False,
			"ExAuthManual" : False,
			"ModifyUsername" : 0,
			"ModifyUsernameString" : "",
			"ExtAuthProtocol" : 0,
			"ExtAuthHostPrimary" : "",
			"ExtAuthHostBackup" : "",
			"ExtAuthPort" : 0,
			"ExAuthLdapBindDN" : "",
			"ExAuthLdapMemberOf" : "",
			"ExAuthUseTLS" : False,
			"ExAuthDomainName" : "",
			"ExAuthOtpSecret" : "",
			"AdvAuthUseNAS" : False,
			"AdvAuthUseVPN" : False,
			"AdvAuthUseManual" : False,
			"AdvAuthProvider" : "",
			"AdvAuthUrlPrimary" : "",
			"AdvAuthUrlBackup" : "",
			"AdvAuthProxyHost" : "",
			"AdvAuthProxyPort" : 0,
			"AdvAuthProxyUsername" : "",
			"AdvAuthProxyPassword" : "",
			"AdvAuthPasscodeKind" : 0,
			"AdvAuthPasscodeLen" : 0,
			"TotpUseNAS" : False,
			"TotpUseVPN" : False,
			"TotpUseManual" : False,
			"InheritedToSubgroups" : False,
			"ConfiguredIn" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}
	
	@cached_property
	def AllowProtPAP(self):
		return self.__getattr__("AllowProtPAP")
	
	@cached_property
	def AllowProtCHAP(self):
		return self.__getattr__("AllowProtCHAP")
	
	@cached_property
	def AllowProtMsChapV1(self):
		return self.__getattr__("AllowProtMsChapV1")
	
	@cached_property
	def AllowProtMsChapV2(self):
		return self.__getattr__("AllowProtMsChapV2")
	
	@cached_property
	def AllowProtEapMd5(self):
		return self.__getattr__("AllowProtEapMd5")
	
	@cached_property
	def AllowProtEapTls(self):
		return self.__getattr__("AllowProtEapTls")
	
	@cached_property
	def AllowProtEapNcpOtp(self):
		return self.__getattr__("AllowProtEapNcpOtp")
	
	@cached_property
	def AllowProtEapMsChapV2(self):
		return self.__getattr__("AllowProtEapMsChapV2")
	
	@cached_property
	def MaxErrorCount(self):
		return self.__getattr__("MaxErrorCount")
	
	@cached_property
	def ResetTime(self):
		return self.__getattr__("ResetTime")
	
	@cached_property
	def EapTlsCheckMode(self):
		return self.__getattr__("EapTlsCheckMode")
	
	@cached_property
	def TlsCheckAttributeName(self):
		return self.__getattr__("TlsCheckAttributeName")
	
	@cached_property
	def ExAuthNAS(self):
		return self.__getattr__("ExAuthNAS")
	
	@cached_property
	def ExAuthVPN(self):
		return self.__getattr__("ExAuthVPN")
	
	@cached_property
	def ExAuthManual(self):
		return self.__getattr__("ExAuthManual")
	
	@cached_property
	def ModifyUsername(self):
		return self.__getattr__("ModifyUsername")
	
	@cached_property
	def ModifyUsernameString(self):
		return self.__getattr__("ModifyUsernameString")
	
	@cached_property
	def ExtAuthProtocol(self):
		return self.__getattr__("ExtAuthProtocol")
	
	@cached_property
	def ExtAuthHostPrimary(self):
		return self.__getattr__("ExtAuthHostPrimary")
	
	@cached_property
	def ExtAuthHostBackup(self):
		return self.__getattr__("ExtAuthHostBackup")
	
	@cached_property
	def ExtAuthPort(self):
		return self.__getattr__("ExtAuthPort")
	
	@cached_property
	def ExAuthLdapBindDN(self):
		return self.__getattr__("ExAuthLdapBindDN")
	
	@cached_property
	def ExAuthLdapMemberOf(self):
		return self.__getattr__("ExAuthLdapMemberOf")
	
	@cached_property
	def ExAuthUseTLS(self):
		return self.__getattr__("ExAuthUseTLS")
	
	@cached_property
	def ExAuthDomainName(self):
		return self.__getattr__("ExAuthDomainName")
	
	@cached_property
	def ExAuthOtpSecret(self):
		return self.__getattr__("ExAuthOtpSecret")
	
	@cached_property
	def AdvAuthUseNAS(self):
		return self.__getattr__("AdvAuthUseNAS")
	
	@cached_property
	def AdvAuthUseVPN(self):
		return self.__getattr__("AdvAuthUseVPN")
	
	@cached_property
	def AdvAuthUseManual(self):
		return self.__getattr__("AdvAuthUseManual")
	
	@cached_property
	def AdvAuthProvider(self):
		return self.__getattr__("AdvAuthProvider")
	
	@cached_property
	def AdvAuthUrlPrimary(self):
		return self.__getattr__("AdvAuthUrlPrimary")
	
	@cached_property
	def AdvAuthUrlBackup(self):
		return self.__getattr__("AdvAuthUrlBackup")
	
	@cached_property
	def AdvAuthProxyHost(self):
		return self.__getattr__("AdvAuthProxyHost")
	
	@cached_property
	def AdvAuthProxyPort(self):
		return self.__getattr__("AdvAuthProxyPort")
	
	@cached_property
	def AdvAuthProxyUsername(self):
		return self.__getattr__("AdvAuthProxyUsername")
	
	@cached_property
	def AdvAuthProxyPassword(self):
		return self.__getattr__("AdvAuthProxyPassword")
	
	@cached_property
	def AdvAuthPasscodeKind(self):
		return self.__getattr__("AdvAuthPasscodeKind")
	
	@cached_property
	def AdvAuthPasscodeLen(self):
		return self.__getattr__("AdvAuthPasscodeLen")
	
	@cached_property
	def TotpUseNAS(self):
		return self.__getattr__("TotpUseNAS")
	
	@cached_property
	def TotpUseVPN(self):
		return self.__getattr__("TotpUseVPN")
	
	@cached_property
	def TotpUseManual(self):
		return self.__getattr__("TotpUseManual")
	
	@cached_property
	def InheritedToSubgroups(self):
		return self.__getattr__("InheritedToSubgroups")
	
	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class RadiusConfigurationsHandler(BaseListFindHandler):
	'''Management of RADIUS configurations

	Methods
	-------
		createEntry()
			Creates a new RadiusConfiguration entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	

	def createEntry(self):
		'''Creates a new RadiusConfiguration entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusConfiguration(self)
	

class RadiusConfiguration(LazyListEntry):
	'''Parameters of RADIUS configurations

	Attributes [writable]
	---------------------
		Name : string
			Name
		Attributes : array from model {Model}
			Attributes
	'''

	def __init__(self, getHandler):
		LazyListEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Name" : "",
			"Attributes" : [],
		}
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Attributes(self):
		return self.__getattr__("Attributes")
	

class RadiusDictionariesHandler(BaseListFindHandler):
	'''Management of RADIUS dictionaries

	Methods
	-------
		createEntry()
			Creates a new RadiusDictionary entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	

	def createEntry(self):
		'''Creates a new RadiusDictionary entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusDictionary(self)
	

class RadiusDictionary(LazyListEntry):
	'''Parameters of RADIUS dictionaries

	Attributes [writable]
	---------------------
		Name : string
			Name
		Attributes : array from model {Model}
			Attributes
	'''

	def __init__(self, getHandler):
		LazyListEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Name" : "",
			"Attributes" : [],
		}
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Attributes(self):
		return self.__getattr__("Attributes")
	

class RadiusClientsHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Management of RADIUS clients

	Methods
	-------
		createEntry()
			Creates a new RadiusClient entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	

	def createEntry(self):
		'''Creates a new RadiusClient entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusClient(self)
	

class RadiusClient(LazyModifiableListEntry):
	'''Parameters of RADIUS Client

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
		Enabled : boolean
			Enabled
		IpAddress : string
			IP address
		SharetSecret : string
			Sharet secret
		RadiusDictionary : string or integer from {Controller}
			RADIUS Dictionary
		RadiusConfiguration : string or integer from {Controller}
			RADIUS Configuration
		AllowProtPAP : boolean
			Allow protocol PAP
		AllowProtCHAP : boolean
			Allow protocol CHAP
		AllowProtMsChapV1 : boolean
			Allow protocol MSCHAPv1
		AllowProtMsChapV2 : boolean
			Allow protocol MSCHAPv2
		AllowProtEapMd5 : boolean
			Allow protocol EAP-MD5
		AllowProtEapTls : boolean
			Allow protocol EAP-TLS
		AllowProtEapNcpOtp : boolean
			Allow protocol EAP-NCP-OTP
		AllowProtEapMsChapV2 : boolean
			Allow protocol EAP-MSCHAPv2
	'''

	def __init__(self, getHandler):
		LazyModifiableListEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Name" : "",
			"Enabled" : False,
			"IpAddress" : "",
			"SharetSecret" : "",
			"RadiusDictionary" : "0",
			"RadiusConfiguration" : "0",
			"AllowProtPAP" : True,
			"AllowProtCHAP" : True,
			"AllowProtMsChapV1" : True,
			"AllowProtMsChapV2" : True,
			"AllowProtEapMd5" : True,
			"AllowProtEapTls" : True,
			"AllowProtEapNcpOtp" : True,
			"AllowProtEapMsChapV2" : True,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Enabled(self):
		return self.__getattr__("Enabled")
	
	@cached_property
	def IpAddress(self):
		return self.__getattr__("IpAddress")
	
	@cached_property
	def SharetSecret(self):
		return self.__getattr__("SharetSecret")
	
	@cached_property
	def RadiusDictionary(self):
		return self.__getattr__("RadiusDictionary")
	
	@cached_property
	def RadiusConfiguration(self):
		return self.__getattr__("RadiusConfiguration")
	
	@cached_property
	def AllowProtPAP(self):
		return self.__getattr__("AllowProtPAP")
	
	@cached_property
	def AllowProtCHAP(self):
		return self.__getattr__("AllowProtCHAP")
	
	@cached_property
	def AllowProtMsChapV1(self):
		return self.__getattr__("AllowProtMsChapV1")
	
	@cached_property
	def AllowProtMsChapV2(self):
		return self.__getattr__("AllowProtMsChapV2")
	
	@cached_property
	def AllowProtEapMd5(self):
		return self.__getattr__("AllowProtEapMd5")
	
	@cached_property
	def AllowProtEapTls(self):
		return self.__getattr__("AllowProtEapTls")
	
	@cached_property
	def AllowProtEapNcpOtp(self):
		return self.__getattr__("AllowProtEapNcpOtp")
	
	@cached_property
	def AllowProtEapMsChapV2(self):
		return self.__getattr__("AllowProtEapMsChapV2")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class RadiusUsersHandler(BaseListFindHandler):
	'''Status of RADIUS users

	Methods
	-------
		createEntry()
			Creates a new RadiusUser entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "radius-mgm/{groupid}/users".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new RadiusUser entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusUser(self, self._groupid)
	

class RadiusUser(LazyListEntry):
	'''Parameters of RADIUS user status

	Attributes [read-only]
	----------------------
		Id : integer
			Id
		Username : string
			Username
		GroupName : string
			Group Name
		State : integer
			State
			Enum Values: 0=disabled, 1=enabled, 2=locked
		ErrorCount : integer
			Error Count
		CreationTime : time
			Creation time
		LastLoginTime : time
			Last login time
		LastFailedLoginTime : time
			Last failed login time
		FallBack2FAAuthTime : integer
			Fall Back 2FA end date/time

	Methods
	-------
		disable()
			Disable a RADIUS user
		enable()
			Enable a RADIUS user
		call_2fa_fallback(Duration, Passcode=None)
			Enable 2FA fall back for a RADIUS user
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Username" : "",
			"GroupName" : "",
			"State" : 0,
			"ErrorCount" : 0,
			"CreationTime" : "",
			"LastLoginTime" : "",
			"LastFailedLoginTime" : "",
			"FallBack2FAAuthTime" : 0,
		}
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def Username(self):
		return self.__getattr__("Username")
	
	@cached_property
	def GroupName(self):
		return self.__getattr__("GroupName")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def ErrorCount(self):
		return self.__getattr__("ErrorCount")
	
	@cached_property
	def CreationTime(self):
		return self.__getattr__("CreationTime")
	
	@cached_property
	def LastLoginTime(self):
		return self.__getattr__("LastLoginTime")
	
	@cached_property
	def LastFailedLoginTime(self):
		return self.__getattr__("LastFailedLoginTime")
	
	@cached_property
	def FallBack2FAAuthTime(self):
		return self.__getattr__("FallBack2FAAuthTime")
			
	def disable(self):
		'''Disable a RADIUS user'''
		return self._callMethod('/disable')
			
	def enable(self):
		'''Enable a RADIUS user'''
		return self._callMethod('/enable')
			
	def call_2fa_fallback(self, Duration, Passcode=None):
		'''Enable 2FA fall back for a RADIUS user
			Duration : integer
				Duration (sec)
			Passcode : string
				Passcode
		'''
		return self._callMethod('/2fa-fallback', Duration=Duration, Passcode=Passcode)
	

class RadiusSessionsHandler(BaseListDeleteHandler):
	'''Status of RADIUS sessions

	Methods
	-------
		createEntry()
			Creates a new RadiusSession entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "radius-mgm/{groupid}/sessions".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new RadiusSession entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusSession(self, self._groupid)
	

class RadiusSession(ListEntry):
	'''Parameters of RADIUS session

	Attributes [read-only]
	----------------------
		Id : integer
			Id
		Username : string
			Username
		RadiusClient : string
			Radius client
		StartTime : time
			Start time
		Duration : integer
			Duration
		SemServerName : string
			SEM Server Name
	'''

	def __init__(self, getHandler, groupid):
		ListEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Username" : "",
			"RadiusClient" : "",
			"StartTime" : "",
			"Duration" : 0,
			"SemServerName" : "",
		}
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def Username(self):
		return self.__getattr__("Username")
	
	@cached_property
	def RadiusClient(self):
		return self.__getattr__("RadiusClient")
	
	@cached_property
	def StartTime(self):
		return self.__getattr__("StartTime")
	
	@cached_property
	def Duration(self):
		return self.__getattr__("Duration")
	
	@cached_property
	def SemServerName(self):
		return self.__getattr__("SemServerName")
	

class RadiusAccountingDetailsHandler(BaseListHandler):
	'''Accounting from RADIUS users

	Methods
	-------
		createEntry()
			Creates a new RadiusAccountingDetail entry object.
	
	Inherited Methods
	-----------------
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "radius-mgm/{groupid}/accounting-details".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new RadiusAccountingDetail entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return RadiusAccountingDetail(self, self._groupid)
	

class RadiusAccountingDetail(ListEntry):
	'''Parameters of RADIUS accounting detail

	Attributes [read-only]
	----------------------
		Username : string
			Username
		GroupName : string
			Group Name
		StartTime : time
			State
		ConnectionTime : integer
			Connection Time
		RxBytes : integer
			Rx Bytes
		TxBytes : integer
			Tx Bytes
		RadiusClient : string
			Radius Client
		CalledStationId : string
			Called Station ID
		CallingStationId : string
			Calling Station ID
		NasId : string
			NAS ID
		NasPortType : integer
			NAS Port Type
		ServerEndpoint : string
			Server Endpoint
		ClientEndpoint : string
			Client Endpoint
		FramedIpAddress : string
			Client Framed IP Address
		DnsName : string
			DNS Name
	'''

	def __init__(self, getHandler, groupid):
		ListEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Username" : "",
			"GroupName" : "",
			"StartTime" : "",
			"ConnectionTime" : 0,
			"RxBytes" : 0,
			"TxBytes" : 0,
			"RadiusClient" : "",
			"CalledStationId" : "",
			"CallingStationId" : "",
			"NasId" : "",
			"NasPortType" : 0,
			"ServerEndpoint" : "",
			"ClientEndpoint" : "",
			"FramedIpAddress" : "",
			"DnsName" : "",
		}
	
	@cached_property
	def Username(self):
		return self.__getattr__("Username")
	
	@cached_property
	def GroupName(self):
		return self.__getattr__("GroupName")
	
	@cached_property
	def StartTime(self):
		return self.__getattr__("StartTime")
	
	@cached_property
	def ConnectionTime(self):
		return self.__getattr__("ConnectionTime")
	
	@cached_property
	def RxBytes(self):
		return self.__getattr__("RxBytes")
	
	@cached_property
	def TxBytes(self):
		return self.__getattr__("TxBytes")
	
	@cached_property
	def RadiusClient(self):
		return self.__getattr__("RadiusClient")
	
	@cached_property
	def CalledStationId(self):
		return self.__getattr__("CalledStationId")
	
	@cached_property
	def CallingStationId(self):
		return self.__getattr__("CallingStationId")
	
	@cached_property
	def NasId(self):
		return self.__getattr__("NasId")
	
	@cached_property
	def NasPortType(self):
		return self.__getattr__("NasPortType")
	
	@cached_property
	def ServerEndpoint(self):
		return self.__getattr__("ServerEndpoint")
	
	@cached_property
	def ClientEndpoint(self):
		return self.__getattr__("ClientEndpoint")
	
	@cached_property
	def FramedIpAddress(self):
		return self.__getattr__("FramedIpAddress")
	
	@cached_property
	def DnsName(self):
		return self.__getattr__("DnsName")
	


class GetIdNameList(BaseEntry):
	'''Model GetIdNameList

	Attributes [writable]
	---------------------
		Id : integer
			ID of the entry
		Name : string
			Name of the entry
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Name" : "",
		}
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	

class RadiusTemplateAttribute(BaseEntry):
	'''Model RadiusTemplateAttribute

	Attributes [read-only]
	----------------------
		AttributeType : integer
			Attribute Type
			Enum Values: 1=integer, 2=string, 3=IPv4 address

	Attributes [writable]
	---------------------
		AttributeName : string
			Attribute Name
		AttributeValue : string
			Attribute Value
		UserSpefific : boolean
			User spefific
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"AttributeName" : "",
			"AttributeValue" : "",
			"AttributeType" : 0,
			"UserSpefific" : False,
		}
	
	@cached_property
	def AttributeName(self):
		return self.__getattr__("AttributeName")
	
	@cached_property
	def AttributeValue(self):
		return self.__getattr__("AttributeValue")
	
	@cached_property
	def AttributeType(self):
		return self.__getattr__("AttributeType")
	
	@cached_property
	def UserSpefific(self):
		return self.__getattr__("UserSpefific")
	

class RadiusTemplateAdd(BaseEntry):
	'''Parameters for adding a RADIUS template

	Attributes [writable]
	---------------------
		Name : string
			Name
		GenerateTotpSecrets : boolean
			Generate T-OTP Secrets
		TOTPlabel : string
			T-OTP Label
		ForceNCPAppAuth : boolean
			Force NCP App Authentication
		InheritedToSubgroups : boolean
			Entry inherited to subgroups
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Name" : "",
			"GenerateTotpSecrets" : False,
			"TOTPlabel" : "",
			"ForceNCPAppAuth" : False,
			"InheritedToSubgroups" : False,
		}
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def GenerateTotpSecrets(self):
		return self.__getattr__("GenerateTotpSecrets")
	
	@cached_property
	def TOTPlabel(self):
		return self.__getattr__("TOTPlabel")
	
	@cached_property
	def ForceNCPAppAuth(self):
		return self.__getattr__("ForceNCPAppAuth")
	
	@cached_property
	def InheritedToSubgroups(self):
		return self.__getattr__("InheritedToSubgroups")
	

class RadiusUserConfigList(BaseEntry):
	'''List of RADIUS user configuration

	Attributes [read-only]
	----------------------
		GroupName : string
			Group Name
		LastChangeTime : time
			Last change time
		LastCreationTime : time
			Last creation time

	Attributes [writable]
	---------------------
		Id : integer
			Id
		Name : string
			Name
		UserName : string
			User Name
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Name" : "",
			"UserName" : "",
			"GroupName" : "",
			"LastChangeTime" : "",
			"LastCreationTime" : "",
		}
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def UserName(self):
		return self.__getattr__("UserName")
	
	@cached_property
	def GroupName(self):
		return self.__getattr__("GroupName")
	
	@cached_property
	def LastChangeTime(self):
		return self.__getattr__("LastChangeTime")
	
	@cached_property
	def LastCreationTime(self):
		return self.__getattr__("LastCreationTime")
	

class RadiusAttribute(BaseEntry):
	'''Model RadiusAttribute

	Attributes [read-only]
	----------------------
		AttributeType : integer
			Attribute Type
			Enum Values: 1=integer, 2=string, 3=IPv4 address
		UserSpefific : boolean
			User spefific

	Attributes [writable]
	---------------------
		AttributeName : string
			Attribute Name
		AttributeValue : string
			Attribute Value
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"AttributeName" : "",
			"AttributeValue" : "",
			"AttributeType" : 0,
			"UserSpefific" : False,
		}
	
	@cached_property
	def AttributeName(self):
		return self.__getattr__("AttributeName")
	
	@cached_property
	def AttributeValue(self):
		return self.__getattr__("AttributeValue")
	
	@cached_property
	def AttributeType(self):
		return self.__getattr__("AttributeType")
	
	@cached_property
	def UserSpefific(self):
		return self.__getattr__("UserSpefific")
	

class RadiusUser2FAFallBack(BaseEntry):
	'''Model RadiusUser2FAFallBack

	Attributes [writable]
	---------------------
		Passcode : string
			Passcode
		Duration : integer
			Duration (sec)
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Passcode" : "",
			"Duration" : 0,
		}
	
	@cached_property
	def Passcode(self):
		return self.__getattr__("Passcode")
	
	@cached_property
	def Duration(self):
		return self.__getattr__("Duration")
	

class RadiusClientList(BaseEntry):
	'''Parameters of list RADIUS clients

	Attributes [writable]
	---------------------
		Id : integer
			Id
		Name : string
			Name
		Enabled : boolean
			Enabled
		IpAddress : string
			IP address
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Name" : "",
			"Enabled" : False,
			"IpAddress" : "",
		}
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Enabled(self):
		return self.__getattr__("Enabled")
	
	@cached_property
	def IpAddress(self):
		return self.__getattr__("IpAddress")
	

class RadiusConfigurationAttribute(BaseEntry):
	'''Parameters of Radius RADIUS configuration entry

	Attributes [writable]
	---------------------
		AttributeName : string
			Attribute Name
		AttributeValue : string
			Attribute Value
		AttributeNr : string
			Attribute Number
		VendorId : integer
			Vendor Id
		AttributeType : integer
			Attribut  Type
			Enum Values: 1=integer, 2=string, 3=IPv4 address
		UserType : integer
			User Type
			Enum Values: 1=only for VPN, 2=only for NAS, 3=both
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"AttributeName" : "",
			"AttributeValue" : "",
			"AttributeNr" : "",
			"VendorId" : 0,
			"AttributeType" : 0,
			"UserType" : "only for VPN",
		}
	
	@cached_property
	def AttributeName(self):
		return self.__getattr__("AttributeName")
	
	@cached_property
	def AttributeValue(self):
		return self.__getattr__("AttributeValue")
	
	@cached_property
	def AttributeNr(self):
		return self.__getattr__("AttributeNr")
	
	@cached_property
	def VendorId(self):
		return self.__getattr__("VendorId")
	
	@cached_property
	def AttributeType(self):
		return self.__getattr__("AttributeType")
	
	@cached_property
	def UserType(self):
		return self.__getattr__("UserType")
	

class RadiusDictionaryAttribute(BaseEntry):
	'''Parameters of Radius Dictionary Attribute

	Attributes [writable]
	---------------------
		Id : integer
			Id
		AttributeName : string
			Attribute Name
		AttributeNr : integer
			Attribute Number
		VendorId : integer
			Vendor Id
		AttributeType : integer
			Attribut  Type
			Enum Values: 1=integer, 2=string, 3=IPv4 address
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)		# Default values
		self._defaultValues = {
			"Id" : 0,
			"AttributeName" : "",
			"AttributeNr" : 0,
			"VendorId" : 0,
			"AttributeType" : 0,
		}
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def AttributeName(self):
		return self.__getattr__("AttributeName")
	
	@cached_property
	def AttributeNr(self):
		return self.__getattr__("AttributeNr")
	
	@cached_property
	def VendorId(self):
		return self.__getattr__("VendorId")
	
	@cached_property
	def AttributeType(self):
		return self.__getattr__("AttributeType")
	
