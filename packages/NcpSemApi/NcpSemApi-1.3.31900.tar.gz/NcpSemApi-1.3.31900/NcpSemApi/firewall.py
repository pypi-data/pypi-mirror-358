
#---------------------------------------------------------------
# This file is generated! Dont make any changes in this file.
#---------------------------------------------------------------
from .base import *
from .cached_property import cached_property



class FirewallTemplatesHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Management of firewall templates

	Methods
	-------
		createEntry()
			Creates a new FirewallTemplate entry object.
	
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
		url = "fw-mgm/{groupid}/templates".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new FirewallTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return FirewallTemplate(self, self._groupid)


class FirewallTemplate(LazyModifiableListEntry):
	'''Firewall Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		ConfiguredIn : string
			Configured In

	Attributes [writable]
	---------------------
		Name : string
			Name
		TemplateType : integer
			Template Type
			Enum Values: 1=Enterprise, 2=Telekom, 3=NCP Exclusive Remote Access Client, 4=VS GovNet Connector 2.0, 5=VS GovNet Connector >=2.1
		Activate : boolean
			Enable Firewall
		PermitIPsec : boolean
			Permit IPsec protocol
		FndNetworks : array from model FndNetwork
			FND Networks
		FndMethod : integer
			FND Method
			Enum Values: 0=eap, 1=tls
		FndMode : integer
			IP address automatically over DHCP assigned
			Enum Values: 0=manually, 1=automatic, 2=DHCP
		FndServer : string
			IP address of FND Server
		FndUserId : string
			User ID
		FndPassword : string
			Password
		FndCertSubject : string
			Incoming Certificate's Subject
		FndCertFingerprint : string
			Issuers Certificate's Fingerprint
		FndPeriodicallyTimer : integer
			Check for friendly net detection periodically
		VpnDenyInFnd : boolean
			Connection set up not permitted in detected friendly network
		HideCredentialProvFnd : boolean
			Mask out logon options in detected friendly network
		FndVpnTimeout : integer
			Timeout for FND before Windows logon
		FndActions : array from model FndAction
			Actions
		StatefulBootOption : integer
			Enable Stateful Boot Option
			Enum Values: 0=unlocked, 1=locked, 2=Statefull boot option
		UdpPreFiltering : integer
			UDP Pre-filtering
			Enum Values: 0=off, 1=always, 2=fnd off
		VmGuestLock : boolean
			Protect VMware guest operating systems
		OutgoingDropReset : boolean
			Reject outgoing traffic
		HomeZoneMode : boolean
			Enable Home Zone
		HomeZoneExitOnLinkDown : boolean
			Exit Home Zone on link status down for more than 10s.
		LogLevel : integer
			Enable firewall log
			Enum Values: 0=off, 2=log drop, 4=log accept, 6=log accept and drop
		LogHoldTime : integer
			Days of logging
		LogPath : string
			Path for log files
		InheritedToSubgroups : boolean
			Entry inherited to subgroups

	Sub-Handlers
	------------
		firewallRules
			Access FirewallRulesHandler
	'''

	def __init__(self, getHandler, groupid):
		LazyModifiableListEntry.__init__(self, getHandler)
		self._groupid = groupid
		self._api = getHandler._api
		# Default values
		self._defaultValues = {
			"Name" : "",
			"TemplateType" : 0,
			"Activate" : False,
			"PermitIPsec" : True,
			"FndNetworks" : [],
			"FndMethod" : "eap",
			"FndMode" : "manually",
			"FndServer" : "",
			"FndUserId" : "",
			"FndPassword" : "",
			"FndCertSubject" : "",
			"FndCertFingerprint" : "",
			"FndPeriodicallyTimer" : 3600,
			"VpnDenyInFnd" : False,
			"HideCredentialProvFnd" : False,
			"FndVpnTimeout" : 60,
			"FndActions" : [],
			"StatefulBootOption" : "unlocked",
			"UdpPreFiltering" : "off",
			"VmGuestLock" : False,
			"OutgoingDropReset" : False,
			"HomeZoneMode" : False,
			"HomeZoneExitOnLinkDown" : False,
			"LogLevel" : "off",
			"LogHoldTime" : 30,
			"LogPath" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"ConfiguredIn" : "",
			"InheritedToSubgroups" : False,
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def TemplateType(self):
		return self.__getattr__("TemplateType")

	@cached_property
	def Activate(self):
		return self.__getattr__("Activate")

	@cached_property
	def PermitIPsec(self):
		return self.__getattr__("PermitIPsec")

	@cached_property
	def FndNetworks(self):
		return self.__getattr__("FndNetworks")

	@cached_property
	def FndMethod(self):
		return self.__getattr__("FndMethod")

	@cached_property
	def FndMode(self):
		return self.__getattr__("FndMode")

	@cached_property
	def FndServer(self):
		return self.__getattr__("FndServer")

	@cached_property
	def FndUserId(self):
		return self.__getattr__("FndUserId")

	@cached_property
	def FndPassword(self):
		return self.__getattr__("FndPassword")

	@cached_property
	def FndCertSubject(self):
		return self.__getattr__("FndCertSubject")

	@cached_property
	def FndCertFingerprint(self):
		return self.__getattr__("FndCertFingerprint")

	@cached_property
	def FndPeriodicallyTimer(self):
		return self.__getattr__("FndPeriodicallyTimer")

	@cached_property
	def VpnDenyInFnd(self):
		return self.__getattr__("VpnDenyInFnd")

	@cached_property
	def HideCredentialProvFnd(self):
		return self.__getattr__("HideCredentialProvFnd")

	@cached_property
	def FndVpnTimeout(self):
		return self.__getattr__("FndVpnTimeout")

	@cached_property
	def FndActions(self):
		return self.__getattr__("FndActions")

	@cached_property
	def StatefulBootOption(self):
		return self.__getattr__("StatefulBootOption")

	@cached_property
	def UdpPreFiltering(self):
		return self.__getattr__("UdpPreFiltering")

	@cached_property
	def VmGuestLock(self):
		return self.__getattr__("VmGuestLock")

	@cached_property
	def OutgoingDropReset(self):
		return self.__getattr__("OutgoingDropReset")

	@cached_property
	def HomeZoneMode(self):
		return self.__getattr__("HomeZoneMode")

	@cached_property
	def HomeZoneExitOnLinkDown(self):
		return self.__getattr__("HomeZoneExitOnLinkDown")

	@cached_property
	def LogLevel(self):
		return self.__getattr__("LogLevel")

	@cached_property
	def LogHoldTime(self):
		return self.__getattr__("LogHoldTime")

	@cached_property
	def LogPath(self):
		return self.__getattr__("LogPath")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")

	@cached_property
	def InheritedToSubgroups(self):
		return self.__getattr__("InheritedToSubgroups")

	@cached_property
	def firewallRules(self):
		'''Returns handler to access FirewallRules'''
		return FirewallRulesHandler(self._api, self._groupid, self.Id)


class FirewallRulesHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of firewall template rules

	Methods
	-------
		createEntry()
			Creates a new FirewallRule entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, fwtemplid):
		url = "fw-mgm/{groupid}/templates/{fwtemplid}/rules".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._fwtemplid = fwtemplid

	def createEntry(self):
		'''Creates a new FirewallRule entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return FirewallRule(self, self._groupid, self._fwtemplid)


class FirewallRule(LazyModifiableListEntry):
	'''Firewall rule

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
		Direction : integer
			Direction
			Enum Values: 0=bidirectional, 1=out, 2=in
		State : boolean
			Action
		LocalIpAddrs : ipaddr.range
			Local IP Addresses
		RemoteIpAddrs : ipaddr.range
			Remote IP Addresses
		LocalPorts : port.range
			Local Ports
		RemotePorts : port.range
			Remote Ports
		TypeVPN : boolean
			Network type VPN
		TypeFriendly : boolean
			Network type friendly
		TypeUnknown : boolean
			Network type unknown
		TypeHomeZone : boolean
			Network type home zone
		Protocol : string
			Protocol
		Application : string
			Application
		NoAutoConnectMobileNetwork : boolean
			No auto connect via mobile network
		ValidNoVpnConnection : boolean
			Only valid with an inactive VPN Connection
	'''

	def __init__(self, getHandler, groupid, fwtemplid):
		LazyModifiableListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"Direction" : "bidirectional",
			"State" : True,
			"LocalIpAddrs" : "",
			"RemoteIpAddrs" : "",
			"LocalPorts" : "",
			"RemotePorts" : "",
			"TypeVPN" : False,
			"TypeFriendly" : False,
			"TypeUnknown" : False,
			"TypeHomeZone" : False,
			"Protocol" : "",
			"Application" : "",
			"NoAutoConnectMobileNetwork" : False,
			"ValidNoVpnConnection" : False,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def Direction(self):
		return self.__getattr__("Direction")

	@cached_property
	def State(self):
		return self.__getattr__("State")

	@cached_property
	def LocalIpAddrs(self):
		return self.__getattr__("LocalIpAddrs")

	@cached_property
	def RemoteIpAddrs(self):
		return self.__getattr__("RemoteIpAddrs")

	@cached_property
	def LocalPorts(self):
		return self.__getattr__("LocalPorts")

	@cached_property
	def RemotePorts(self):
		return self.__getattr__("RemotePorts")

	@cached_property
	def TypeVPN(self):
		return self.__getattr__("TypeVPN")

	@cached_property
	def TypeFriendly(self):
		return self.__getattr__("TypeFriendly")

	@cached_property
	def TypeUnknown(self):
		return self.__getattr__("TypeUnknown")

	@cached_property
	def TypeHomeZone(self):
		return self.__getattr__("TypeHomeZone")

	@cached_property
	def Protocol(self):
		return self.__getattr__("Protocol")

	@cached_property
	def Application(self):
		return self.__getattr__("Application")

	@cached_property
	def NoAutoConnectMobileNetwork(self):
		return self.__getattr__("NoAutoConnectMobileNetwork")

	@cached_property
	def ValidNoVpnConnection(self):
		return self.__getattr__("ValidNoVpnConnection")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")



class FirewallTemplateList(BaseEntry):
	'''Model for firewall template get list operation

	Attributes [writable]
	---------------------
		Id : integer
			REST ID
		Name : string
			Name
		GroupId : integer
			Group ID
		ConfiguredIn : string
			Configured in
		TemplateType : integer
			Template Type
			Enum Values: 1=Enterprise, 2=Telekom, 3=NCP Exclusive Remote Access Client, 4=VS GovNet Connector 2.0, 5=VS GovNet Connector >=2.1
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Name" : "",
			"GroupId" : 0,
			"ConfiguredIn" : "",
			"TemplateType" : 0,
		}

	@cached_property
	def Id(self):
		return self.__getattr__("Id")

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")

	@cached_property
	def TemplateType(self):
		return self.__getattr__("TemplateType")


class FndNetwork(BaseEntry):
	'''FND Network

	Attributes [writable]
	---------------------
		FndNetwork : ipaddr.range
			IP Network
		FndNetmask : ipaddr.range
			Netmask
		DhcpIpAddrRanges : ipaddr.range
			Dhcp Ip Addr Ranges
		FndDescription : string
			DHCP Server
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"FndNetwork" : "",
			"FndNetmask" : "",
			"DhcpIpAddrRanges" : "",
			"FndDescription" : "",
		}

	@cached_property
	def FndNetwork(self):
		return self.__getattr__("FndNetwork")

	@cached_property
	def FndNetmask(self):
		return self.__getattr__("FndNetmask")

	@cached_property
	def DhcpIpAddrRanges(self):
		return self.__getattr__("DhcpIpAddrRanges")

	@cached_property
	def FndDescription(self):
		return self.__getattr__("FndDescription")


class FndAction(BaseEntry):
	'''FND Action

	Attributes [writable]
	---------------------
		Application : string
			Applications
		Attribute : integer
			Start
			Enum Values: 131072=friendlyNet, 262144=unknown, 8388608=homeZone
		Wait : boolean
			Wait application finished
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Application" : "",
			"Attribute" : "friendlyNet",
			"Wait" : True,
		}

	@cached_property
	def Application(self):
		return self.__getattr__("Application")

	@cached_property
	def Attribute(self):
		return self.__getattr__("Attribute")

	@cached_property
	def Wait(self):
		return self.__getattr__("Wait")


class FirewallRuleList(BaseEntry):
	'''Firewall rule list entry

	Attributes [read-only]
	----------------------
		ConfiguredIn : string
			Configured In

	Attributes [writable]
	---------------------
		FWPOL_C_INDEX : integer
			FWPOL_C_INDEX
		Name : string
			Name
		GroupId : integer
			Group ID
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"FWPOL_C_INDEX" : 0,
			"Name" : "",
			"GroupId" : 0,
			"ConfiguredIn" : "",
		}

	@cached_property
	def FWPOL_C_INDEX(self):
		return self.__getattr__("FWPOL_C_INDEX")

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")

