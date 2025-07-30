
#---------------------------------------------------------------
# This file is generated! Dont make any changes in this file.
#---------------------------------------------------------------
from .base import *
from .cached_property import cached_property



class SecureServerTemplatesHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of Secure Server Templates

	Methods
	-------
		createEntry()
			Creates a new SecureServerTemplate entry object.
	
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
		url = "srv-mgm/{groupid}/server-templs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new SecureServerTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SecureServerTemplate(self, self._groupid)
	

class SecureServerTemplate(LazyModifiableListEntry):
	'''Model SecureServerTemplate

	Attributes [read-only]
	----------------------
		CurrentTime : str
			Current Time
		CurrentDate : str
			Current Date
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by
		ConfiguredIn : str
			Configured in

	Attributes [writable]
	---------------------
		Name : str
			Name
			Parameter Group: General
		ServerType : int
			Server Type
			Parameter Group: General
			Enum Values: 0=NCP Secure Server, 2=NCP Virtual Secure Server, 1=Outpost Secure Server
		ManagedVersion : int
			Managed Secure Server Version
			Parameter Group: General
			Enum Values: 65=12.x, 54=11.x, 36=10.0
		UseInHaLbMode : int
			Use VPN Gateway in HA LB Mode
			Parameter Group: License
		AdminPassword : str
			Adminsitrator Password
			Parameter Group: Access Management
		OtherAdmins : sem.arrmifint
			Other Adminsitrators
			Parameter Group: Access Management
		EnableNtpSynchronization : bool
			Enable NTP Synchronization
		NtpServer1 : str
			1. NTP Server
		NtpServer2 : str
			2. NTP Server
		NtpServer3 : str
			3. NTP Server
		NtpServer4 : str
			4. NTP Server
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server Parameters

	Sub-Handlers
	------------
		templSrvLocalSystem
			Access TemplSrvLocalSystemHandler
		templSrvNetworkInterfaces
			Access TemplSrvNetworkInterfacesHandler
		templSrvIKEv1s
			Access TemplSrvIKEv1sHandler
		templSrvIKEv2s
			Access TemplSrvIKEv2sHandler
		tempSrvlPsecs
			Access TempSrvlPsecsHandler
		templSrvLinks
			Access TemplSrvLinksHandler
		templSrvFilterNetworks
			Access TemplSrvFilterNetworksHandler
		templSrvFilters
			Access TemplSrvFiltersHandler
		templSrvFilterGroups
			Access TemplSrvFilterGroupsHandler
		templSrvServerCerts
			Access TemplSrvServerCertsHandler
		templSrvCACerts
			Access TemplSrvCACertsHandler
		templSrvDomainGroups
			Access TemplSrvDomainGroupsHandler
		templSrvStaticRoutes
			Access TemplSrvStaticRoutesHandler
		templSrvListeners
			Access TemplSrvListenersHandler
	'''

	def __init__(self, getHandler, groupid):
		LazyModifiableListEntry.__init__(self, getHandler)
		self._groupid = groupid
		self._api = getHandler._api
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def ServerType(self):
		return self.__getattr__("ServerType")
	
	@cached_property
	def ManagedVersion(self):
		return self.__getattr__("ManagedVersion")
	
	@cached_property
	def UseInHaLbMode(self):
		return self.__getattr__("UseInHaLbMode")
	
	@cached_property
	def AdminPassword(self):
		return self.__getattr__("AdminPassword")
	
	@cached_property
	def OtherAdmins(self):
		return self.__getattr__("OtherAdmins")
	
	@cached_property
	def CurrentTime(self):
		return self.__getattr__("CurrentTime")
	
	@cached_property
	def CurrentDate(self):
		return self.__getattr__("CurrentDate")
	
	@cached_property
	def EnableNtpSynchronization(self):
		return self.__getattr__("EnableNtpSynchronization")
	
	@cached_property
	def NtpServer1(self):
		return self.__getattr__("NtpServer1")
	
	@cached_property
	def NtpServer2(self):
		return self.__getattr__("NtpServer2")
	
	@cached_property
	def NtpServer3(self):
		return self.__getattr__("NtpServer3")
	
	@cached_property
	def NtpServer4(self):
		return self.__getattr__("NtpServer4")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
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
	def templSrvLocalSystem(self):
		'''Returns handler to access TemplSrvLocalSystem'''
		return TemplSrvLocalSystemHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvNetworkInterfaces(self):
		'''Returns handler to access TemplSrvNetworkInterfaces'''
		return TemplSrvNetworkInterfacesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvIKEv1s(self):
		'''Returns handler to access TemplSrvIKEv1s'''
		return TemplSrvIKEv1sHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvIKEv2s(self):
		'''Returns handler to access TemplSrvIKEv2s'''
		return TemplSrvIKEv2sHandler(self._api, self._groupid, self.Id)

	@cached_property
	def tempSrvlPsecs(self):
		'''Returns handler to access TempSrvlPsecs'''
		return TempSrvlPsecsHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvLinks(self):
		'''Returns handler to access TemplSrvLinks'''
		return TemplSrvLinksHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvFilterNetworks(self):
		'''Returns handler to access TemplSrvFilterNetworks'''
		return TemplSrvFilterNetworksHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvFilters(self):
		'''Returns handler to access TemplSrvFilters'''
		return TemplSrvFiltersHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvFilterGroups(self):
		'''Returns handler to access TemplSrvFilterGroups'''
		return TemplSrvFilterGroupsHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvServerCerts(self):
		'''Returns handler to access TemplSrvServerCerts'''
		return TemplSrvServerCertsHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvCACerts(self):
		'''Returns handler to access TemplSrvCACerts'''
		return TemplSrvCACertsHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvDomainGroups(self):
		'''Returns handler to access TemplSrvDomainGroups'''
		return TemplSrvDomainGroupsHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvStaticRoutes(self):
		'''Returns handler to access TemplSrvStaticRoutes'''
		return TemplSrvStaticRoutesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templSrvListeners(self):
		'''Returns handler to access TemplSrvListeners'''
		return TemplSrvListenersHandler(self._api, self._groupid, self.Id)
	

class TemplSrvLocalSystemHandler(BaseUpdateHandler, BaseGetHandler):
	'''Configuration of local system in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvLocalSystem entry object.
	
	Inherited Methods
	-----------------
		get (BaseGetHandler)
		update (BaseUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/local-system".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvLocalSystem entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvLocalSystem(self, self._groupid, self._templid)
	

class TemplSrvLocalSystem(LazyEntry):
	'''Configuration of local system in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		DenyIncomingCall : bool
			Deny incoming call
		UseDNSProxy : bool
			Use DNS / WINS Proxy
		EnableL2TP : bool
			Enable L2TP
		EnableIPSec : bool
			Enable IPSec
		TunnelEndpoint : ipv4
			Local Tunnel Endpoint IP Address
		L2TPTunnelSecret : str
			Tunnel Secret
		L2TPDPDTimeout : int
			L2TP DPD Timeout
		AlternativeIPSecPort : int
			Alternative IKE Port
		UseOnlyAlternativePort : bool
			Use only alternative port
		IkePolicy : uintkey
			IKE Policy
		IkeV2Policy : uintkey
			IKEv2 Policy
		IPSecPolicy : uintkey
			IPSec Policy
		IkeV1Enable : bool
			Enable IKEv1
		IkeV2Enable : bool
			Enable IKEv2
		IpSecPreSharedKey : str
			IPSec pre-shared Key
		IkeV2Auth : int
			IKEv2 Authentication
			Enum Values: 0=none, 1=Certificate, 2=PSK, 3=EAP
		IKEEapType : int
			IKEv2 EAP Type
			Enum Values: 0=none, 1=PAP, 2=MD5, 3=MSCHAP2, 4=TLS, 5=Relay RADIUS
		PathFinderListener1 : ipv4
			1. Path Finder Listener IP Address
		PathFinderListener2 : ipv4
			2. Path Finder Listener IP Address
		AntiReplayProtection : bool
			Anti-replay Protection
		IkeLBIPAddrV4 : ipv4
			IKE Load Balancing IPv4 Address
		IkeLBIPAddrV6 : ipv6
			IKE Load Balancing IPv6 Address
		CheckIncorrectPW : bool
			Check incorrect password entries
		NbrOfIncorrectPW : int
			Permitted number of incorrect password entries
		OnlyWithConfCertCheck : bool
			Only access with configured certificate check allowed
		OnlyCertBasedAuth : bool
			Only certificate based authentication allowed
		OnlyL2TPOverIPsec : bool
			L2TP connections only over IPSec allowed
		EPSecOnlyForNcpClient : bool
			Endpoint Security only for NCP Clients
		OnlyNcpClients : bool
			Only NCP VPN Clients allowed
		AuthProtocol : int
			Authentication Protocol
			Enum Values: 0=CHAP, 1=PAP
		ValidateFullIssuerHierarchy : bool
			Validate full issuer hierarchy
		UseChainModel : bool
			Validate certificate using 'chain model'
		UseHttpProxy : bool
			Use HTTP Proxy
		HttpProxyHost : str
			HTTP Proxy IP Address
		HttpProxyPort : int
			HTTP Proxy Port
		HttpProxyUsername : str
			HTTP Proxy Username
		HttpProxyPassword : str
			HTTP Proxy Password
		RelayExceptions : object(Model)
			Relay Exceptions
		EnableFIPS : bool
			Enable FIPS Mode
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyEntry.__init__(self, getHandler)
	
	@cached_property
	def DenyIncomingCall(self):
		return self.__getattr__("DenyIncomingCall")
	
	@cached_property
	def UseDNSProxy(self):
		return self.__getattr__("UseDNSProxy")
	
	@cached_property
	def EnableL2TP(self):
		return self.__getattr__("EnableL2TP")
	
	@cached_property
	def EnableIPSec(self):
		return self.__getattr__("EnableIPSec")
	
	@cached_property
	def TunnelEndpoint(self):
		return self.__getattr__("TunnelEndpoint")
	
	@cached_property
	def L2TPTunnelSecret(self):
		return self.__getattr__("L2TPTunnelSecret")
	
	@cached_property
	def L2TPDPDTimeout(self):
		return self.__getattr__("L2TPDPDTimeout")
	
	@cached_property
	def AlternativeIPSecPort(self):
		return self.__getattr__("AlternativeIPSecPort")
	
	@cached_property
	def UseOnlyAlternativePort(self):
		return self.__getattr__("UseOnlyAlternativePort")
	
	@cached_property
	def IkePolicy(self):
		return self.__getattr__("IkePolicy")
	
	@cached_property
	def IkeV2Policy(self):
		return self.__getattr__("IkeV2Policy")
	
	@cached_property
	def IPSecPolicy(self):
		return self.__getattr__("IPSecPolicy")
	
	@cached_property
	def IkeV1Enable(self):
		return self.__getattr__("IkeV1Enable")
	
	@cached_property
	def IkeV2Enable(self):
		return self.__getattr__("IkeV2Enable")
	
	@cached_property
	def IpSecPreSharedKey(self):
		return self.__getattr__("IpSecPreSharedKey")
	
	@cached_property
	def IkeV2Auth(self):
		return self.__getattr__("IkeV2Auth")
	
	@cached_property
	def IKEEapType(self):
		return self.__getattr__("IKEEapType")
	
	@cached_property
	def PathFinderListener1(self):
		return self.__getattr__("PathFinderListener1")
	
	@cached_property
	def PathFinderListener2(self):
		return self.__getattr__("PathFinderListener2")
	
	@cached_property
	def AntiReplayProtection(self):
		return self.__getattr__("AntiReplayProtection")
	
	@cached_property
	def IkeLBIPAddrV4(self):
		return self.__getattr__("IkeLBIPAddrV4")
	
	@cached_property
	def IkeLBIPAddrV6(self):
		return self.__getattr__("IkeLBIPAddrV6")
	
	@cached_property
	def CheckIncorrectPW(self):
		return self.__getattr__("CheckIncorrectPW")
	
	@cached_property
	def NbrOfIncorrectPW(self):
		return self.__getattr__("NbrOfIncorrectPW")
	
	@cached_property
	def OnlyWithConfCertCheck(self):
		return self.__getattr__("OnlyWithConfCertCheck")
	
	@cached_property
	def OnlyCertBasedAuth(self):
		return self.__getattr__("OnlyCertBasedAuth")
	
	@cached_property
	def OnlyL2TPOverIPsec(self):
		return self.__getattr__("OnlyL2TPOverIPsec")
	
	@cached_property
	def EPSecOnlyForNcpClient(self):
		return self.__getattr__("EPSecOnlyForNcpClient")
	
	@cached_property
	def OnlyNcpClients(self):
		return self.__getattr__("OnlyNcpClients")
	
	@cached_property
	def AuthProtocol(self):
		return self.__getattr__("AuthProtocol")
	
	@cached_property
	def ValidateFullIssuerHierarchy(self):
		return self.__getattr__("ValidateFullIssuerHierarchy")
	
	@cached_property
	def UseChainModel(self):
		return self.__getattr__("UseChainModel")
	
	@cached_property
	def UseHttpProxy(self):
		return self.__getattr__("UseHttpProxy")
	
	@cached_property
	def HttpProxyHost(self):
		return self.__getattr__("HttpProxyHost")
	
	@cached_property
	def HttpProxyPort(self):
		return self.__getattr__("HttpProxyPort")
	
	@cached_property
	def HttpProxyUsername(self):
		return self.__getattr__("HttpProxyUsername")
	
	@cached_property
	def HttpProxyPassword(self):
		return self.__getattr__("HttpProxyPassword")
	
	@cached_property
	def RelayExceptions(self):
		return self.__getattr__("RelayExceptions")
	
	@cached_property
	def EnableFIPS(self):
		return self.__getattr__("EnableFIPS")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvNetworkInterfacesHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of network interfaces in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvNetworkInterface entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/net-if".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvNetworkInterface entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvNetworkInterface(self, self._groupid, self._templid)
	

class TemplSrvNetworkInterface(LazyModifiableListEntry):
	'''Configuration of network interfaces in Secure Server Template

	Attributes [read-only]
	----------------------
		IpAddresses : str
			Current IPv4 Addresses
		IpV6Addresses : str
			current IPv6 Addresses
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Display Name
		MacAddr : macaddr
			MAC Address
		AdapterName : str
			Adapter Name
		Comment : str
			Comment
		ProtectLanAdapter : bool
			Protect Lan Adapter
		IPNAT : bool
			IP Network Address Translation
		StatefulInspection : bool
			Stateful Inspection
		ARRE : bool
			Automatic Reverse Route Determination (ARRD)
		ActivateVRRP : bool
			Enable VRRP
		VrrpId1 : int
			VRRP ID for IPv4
		VrrpIpAddress1 : ipv4
			Virtual IPv4 Address
		VrrpV6Id1 : int
			VRRP ID for IPv6
		VrrpIPv6Address1 : ipv6
			Virtual IPv6 Address
		VLANs : object(Model)
			VLANs
		IPNatDefaultMode : int
			IP NAT Default Mode
			Enum Values: 0=passthru, 1=IP NAT
		IPNatSEM : bool
			IP NAT SEM
		IPNatEntries : object(Model)
			IP NAT Entries
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def MacAddr(self):
		return self.__getattr__("MacAddr")
	
	@cached_property
	def AdapterName(self):
		return self.__getattr__("AdapterName")
	
	@cached_property
	def IpAddresses(self):
		return self.__getattr__("IpAddresses")
	
	@cached_property
	def IpV6Addresses(self):
		return self.__getattr__("IpV6Addresses")
	
	@cached_property
	def Comment(self):
		return self.__getattr__("Comment")
	
	@cached_property
	def ProtectLanAdapter(self):
		return self.__getattr__("ProtectLanAdapter")
	
	@cached_property
	def IPNAT(self):
		return self.__getattr__("IPNAT")
	
	@cached_property
	def StatefulInspection(self):
		return self.__getattr__("StatefulInspection")
	
	@cached_property
	def ARRE(self):
		return self.__getattr__("ARRE")
	
	@cached_property
	def ActivateVRRP(self):
		return self.__getattr__("ActivateVRRP")
	
	@cached_property
	def VrrpId1(self):
		return self.__getattr__("VrrpId1")
	
	@cached_property
	def VrrpIpAddress1(self):
		return self.__getattr__("VrrpIpAddress1")
	
	@cached_property
	def VrrpV6Id1(self):
		return self.__getattr__("VrrpV6Id1")
	
	@cached_property
	def VrrpIPv6Address1(self):
		return self.__getattr__("VrrpIPv6Address1")
	
	@cached_property
	def VLANs(self):
		return self.__getattr__("VLANs")
	
	@cached_property
	def IPNatDefaultMode(self):
		return self.__getattr__("IPNatDefaultMode")
	
	@cached_property
	def IPNatSEM(self):
		return self.__getattr__("IPNatSEM")
	
	@cached_property
	def IPNatEntries(self):
		return self.__getattr__("IPNatEntries")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvIKEv1sHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of IKEv1 policies in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvIKEv1 entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/ike-cgfs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvIKEv1 entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvIKEv1(self, self._groupid, self._templid)
	

class TemplSrvIKEv1(LazyModifiableListEntry):
	'''Configuration of IKEv1 policies in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		Proposals : object(Model)
			Proposals
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Proposals(self):
		return self.__getattr__("Proposals")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvIKEv2sHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of IKEv2 policies in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvIKEv2 entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/ikev2-cfgs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvIKEv2 entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvIKEv2(self, self._groupid, self._templid)
	

class TemplSrvIKEv2(LazyModifiableListEntry):
	'''Configuration of IKEv2 policies in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		Proposals : object(Model)
			Proposals
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Proposals(self):
		return self.__getattr__("Proposals")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TempSrvlPsecsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of IPsec policies in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TempSrvlPsec entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/ipsec-cfgs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TempSrvlPsec entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TempSrvlPsec(self, self._groupid, self._templid)
	

class TempSrvlPsec(LazyModifiableListEntry):
	'''Configuration of IPsec policies in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		Proposals : object(Model)
			Proposals
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Proposals(self):
		return self.__getattr__("Proposals")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvLinksHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of link profiles in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvLink entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/links".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvLink entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvLink(self, self._groupid, self._templid)
	

class TemplSrvLink(LazyModifiableListEntry):
	'''Configuration of link profiles in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Link Profile Name
		State : bool
			State
		FilterGroup : uintkey
			Filtergroup Name
		Direction : int
			Direction
			Enum Values: 0=incoming, 1=outgoing, 2=bidirectional
		LinkType : int
			Link Type
			Enum Values: 5=L2TP, 10=IPSec
		VpnMode : int
			VPN Mode
			Enum Values: 0=NativeVPN, 1=SslVpn, 2=both
		Timeout : int
			Inactivity Timeout
		TimeoutDir : int
			Timeout Direction
			Enum Values: 0=TxRx, 1=Rx, 2=Tx
		Compression : int
			Compression
			Enum Values: 0=off, 2=StackerH, 1=Stacker
		MaxConnTime : int
			Max Connection Time
		MaxRxBandwidth : int
			Max Rx Bandwidth
		MaxTxBandwidth : int
			Max Tx Bandwidth
		UserPriority : int
			User Priority
		DebugLevel : int
			Debug Level
		LocalUserId : str
			User ID (outgoing)
		LocalPassword : str
			Password (outgoing)
		RemoteUserId : str
			User ID (incoming)
		RemotePassword : str
			Password (incoming)
		MultiUser : bool
			Multi User Profile
		ExchangeMode : int
			Exchange Mode
			Enum Values: 2=main, 4=aggressive, 34=IKEv2
		IkePolicy : uintkey
			IKE Policy
		IkeV2Policy : uintkey
			IKEv2 Policy
		IPSecPolicy : uintkey
			IPSec Policy
		IpSecPreSharedKey : str
			IPSec Pre-shared key
		CertSerNr : str
			Certificate Serial Number
		CertCommonName : str
			Certificate Common Name
		CertEMail : str
			Certificate E-Mail
		CertSubjectUniqueId : str
			Certificate Subject Unique ID
		CertOrgUnit : str
			Certificate Organization Unit (OU)
		CertUPN : str
			Certificate User Principal Name
		CertSubAltNameEmail : str
			Certificate Subject Alternative Name (E-Mail)
		CertHardwareCN : str
			Hardware Certificate CN
		VpnTunnelEndpoint : str
			Tunnel Endpoint
		TunnelSecret : str
			Tunnel Secret
		TunnelEndpNextHop1 : str
			Primary Gateway for Tunnel Endpoint
		TunnelEndpNextHop2 : str
			Secondary Gateway for Tunnel Endpoint
		TunnelEndpNextHop3 : str
			Thrid Gateway for Tunnel Endpoint
		TunnelEndpNextHop4 : str
			Fourth Gateway for Tunnel Endpoint
		TunnelEndpNextHop5 : str
			Fifth Gateway for Tunnel Endpoint
		UseGRE : bool
			GRE
		GreEndpoint : ipv4
			GRE Endpoint
		UseDve : bool
			DVE (Dynamic VPN Endpoint)
		DveServer1 : str
			Primary HA Server
		DveServer2 : str
			Secondary HA Server
		DveSecret : str
			DVE Secret
		IPAddress : ipv4
			IPv4 Address
		IPPool : int
			IP Address Pool
		IPPoolMetered : int
			IP Address Pool (metered connections)
		IPAddressV6 : ipv6
			IPv6 Address
		IPNat : bool
			IP Network Address Translation
		SetNetworkRoutes : bool
			Adopt Network Routes
		DNSName : str
			DNS Name
		NetRelayEntries : object(Model)
			Net Relay
		DHCPSrcIpAddr : ipv4
			DHCP Source IP Address
		DHCPSrcNetworkMask : ipv4
			DHCP Source Network Mask
		DHCPSrcIpAddrMetered : ipv4
			DHCP Source IP Address (metered connection)
		DHCPSrcNetworkMaskMetered : ipv4
			DHCP Source Network Mask (metered connection)
		IpSelectors : object(Model)
			IP Selectors
		PrivateIpAddress : ipv4
			Private IPv4 Address
		PrivateIpAddressV6 : ipv6
			Private IPv6 Address
		IkeIdType : int
			IKE ID Type
			Enum Values: 1=IpAddr, 2=DomainName, 3=UserId, 4=IpSubNet, 7=IpAddrRange, 9=X500DistingName, 10=X500GeneralName, 11=KeyId
		IkeId : str
			IKE ID
		UdpEncapsulation : bool
			UDP Encapsulation
		XAuth : bool
			Extended Authentication (XAuth)
		DPDInterval : int
			DPD Interval
		IkeDhGroup : int
			IKE DH Group
			Enum Values: 0=none, 1=DH-Group-1, 2=DH-Group-2, 5=DH-Group-5, 14=DH-Group-14, 15=DH-Group-15, 16=DH-Group-16, 17=DH-Group-17, 18=DH-Group-18, 19=DH-Group-19, 20=DH-Group-20, 21=DH-Group-21, 25=DH-Group-25, 26=DH-Group-26
		PFSGroup : int
			PFS Group
			Enum Values: 0=none, 1=DH-Group-1, 2=DH-Group-2, 5=DH-Group-5, 14=DH-Group-14, 15=DH-Group-15, 16=DH-Group-16, 17=DH-Group-17, 18=DH-Group-18, 19=DH-Group-19, 20=DH-Group-20, 21=DH-Group-21, 25=DH-Group-25, 26=DH-Group-26
		IkeV2Auth : int
			IKEv2 Authentication
			Enum Values: 0=none, 1=Certificate, 2=PSK, 3=EAP
		ServerCertificate : uintkey
			Server Certificate
		IkePolicyLifeTime : int
			IKE Policy Lifetime
		IPsecPolicyLifeTime : int
			IPsec Policy Lifetime
		PolicyName : str
			Policy Name
		PolicyParameter : str
			Policy Parameter
		PolicyFilterGroup : uintkey
			Policy Filtergroup Name
		DnsServer1 : ipv4
			1. DNS Server
		DnsServer2 : ipv4
			2. DNS Server
		MgmServer1 : ipv4
			1. Management Server
		MgmServer2 : ipv4
			2. Management Server
		GroupSuffix : str
			Domain Group Suffix
		DNSSuffix : str
			DNS Suffix
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def FilterGroup(self):
		return self.__getattr__("FilterGroup")
	
	@cached_property
	def Direction(self):
		return self.__getattr__("Direction")
	
	@cached_property
	def LinkType(self):
		return self.__getattr__("LinkType")
	
	@cached_property
	def VpnMode(self):
		return self.__getattr__("VpnMode")
	
	@cached_property
	def Timeout(self):
		return self.__getattr__("Timeout")
	
	@cached_property
	def TimeoutDir(self):
		return self.__getattr__("TimeoutDir")
	
	@cached_property
	def Compression(self):
		return self.__getattr__("Compression")
	
	@cached_property
	def MaxConnTime(self):
		return self.__getattr__("MaxConnTime")
	
	@cached_property
	def MaxRxBandwidth(self):
		return self.__getattr__("MaxRxBandwidth")
	
	@cached_property
	def MaxTxBandwidth(self):
		return self.__getattr__("MaxTxBandwidth")
	
	@cached_property
	def UserPriority(self):
		return self.__getattr__("UserPriority")
	
	@cached_property
	def DebugLevel(self):
		return self.__getattr__("DebugLevel")
	
	@cached_property
	def LocalUserId(self):
		return self.__getattr__("LocalUserId")
	
	@cached_property
	def LocalPassword(self):
		return self.__getattr__("LocalPassword")
	
	@cached_property
	def RemoteUserId(self):
		return self.__getattr__("RemoteUserId")
	
	@cached_property
	def RemotePassword(self):
		return self.__getattr__("RemotePassword")
	
	@cached_property
	def MultiUser(self):
		return self.__getattr__("MultiUser")
	
	@cached_property
	def ExchangeMode(self):
		return self.__getattr__("ExchangeMode")
	
	@cached_property
	def IkePolicy(self):
		return self.__getattr__("IkePolicy")
	
	@cached_property
	def IkeV2Policy(self):
		return self.__getattr__("IkeV2Policy")
	
	@cached_property
	def IPSecPolicy(self):
		return self.__getattr__("IPSecPolicy")
	
	@cached_property
	def IpSecPreSharedKey(self):
		return self.__getattr__("IpSecPreSharedKey")
	
	@cached_property
	def CertSerNr(self):
		return self.__getattr__("CertSerNr")
	
	@cached_property
	def CertCommonName(self):
		return self.__getattr__("CertCommonName")
	
	@cached_property
	def CertEMail(self):
		return self.__getattr__("CertEMail")
	
	@cached_property
	def CertSubjectUniqueId(self):
		return self.__getattr__("CertSubjectUniqueId")
	
	@cached_property
	def CertOrgUnit(self):
		return self.__getattr__("CertOrgUnit")
	
	@cached_property
	def CertUPN(self):
		return self.__getattr__("CertUPN")
	
	@cached_property
	def CertSubAltNameEmail(self):
		return self.__getattr__("CertSubAltNameEmail")
	
	@cached_property
	def CertHardwareCN(self):
		return self.__getattr__("CertHardwareCN")
	
	@cached_property
	def VpnTunnelEndpoint(self):
		return self.__getattr__("VpnTunnelEndpoint")
	
	@cached_property
	def TunnelSecret(self):
		return self.__getattr__("TunnelSecret")
	
	@cached_property
	def TunnelEndpNextHop1(self):
		return self.__getattr__("TunnelEndpNextHop1")
	
	@cached_property
	def TunnelEndpNextHop2(self):
		return self.__getattr__("TunnelEndpNextHop2")
	
	@cached_property
	def TunnelEndpNextHop3(self):
		return self.__getattr__("TunnelEndpNextHop3")
	
	@cached_property
	def TunnelEndpNextHop4(self):
		return self.__getattr__("TunnelEndpNextHop4")
	
	@cached_property
	def TunnelEndpNextHop5(self):
		return self.__getattr__("TunnelEndpNextHop5")
	
	@cached_property
	def UseGRE(self):
		return self.__getattr__("UseGRE")
	
	@cached_property
	def GreEndpoint(self):
		return self.__getattr__("GreEndpoint")
	
	@cached_property
	def UseDve(self):
		return self.__getattr__("UseDve")
	
	@cached_property
	def DveServer1(self):
		return self.__getattr__("DveServer1")
	
	@cached_property
	def DveServer2(self):
		return self.__getattr__("DveServer2")
	
	@cached_property
	def DveSecret(self):
		return self.__getattr__("DveSecret")
	
	@cached_property
	def IPAddress(self):
		return self.__getattr__("IPAddress")
	
	@cached_property
	def IPPool(self):
		return self.__getattr__("IPPool")
	
	@cached_property
	def IPPoolMetered(self):
		return self.__getattr__("IPPoolMetered")
	
	@cached_property
	def IPAddressV6(self):
		return self.__getattr__("IPAddressV6")
	
	@cached_property
	def IPNat(self):
		return self.__getattr__("IPNat")
	
	@cached_property
	def SetNetworkRoutes(self):
		return self.__getattr__("SetNetworkRoutes")
	
	@cached_property
	def DNSName(self):
		return self.__getattr__("DNSName")
	
	@cached_property
	def NetRelayEntries(self):
		return self.__getattr__("NetRelayEntries")
	
	@cached_property
	def DHCPSrcIpAddr(self):
		return self.__getattr__("DHCPSrcIpAddr")
	
	@cached_property
	def DHCPSrcNetworkMask(self):
		return self.__getattr__("DHCPSrcNetworkMask")
	
	@cached_property
	def DHCPSrcIpAddrMetered(self):
		return self.__getattr__("DHCPSrcIpAddrMetered")
	
	@cached_property
	def DHCPSrcNetworkMaskMetered(self):
		return self.__getattr__("DHCPSrcNetworkMaskMetered")
	
	@cached_property
	def IpSelectors(self):
		return self.__getattr__("IpSelectors")
	
	@cached_property
	def PrivateIpAddress(self):
		return self.__getattr__("PrivateIpAddress")
	
	@cached_property
	def PrivateIpAddressV6(self):
		return self.__getattr__("PrivateIpAddressV6")
	
	@cached_property
	def IkeIdType(self):
		return self.__getattr__("IkeIdType")
	
	@cached_property
	def IkeId(self):
		return self.__getattr__("IkeId")
	
	@cached_property
	def UdpEncapsulation(self):
		return self.__getattr__("UdpEncapsulation")
	
	@cached_property
	def XAuth(self):
		return self.__getattr__("XAuth")
	
	@cached_property
	def DPDInterval(self):
		return self.__getattr__("DPDInterval")
	
	@cached_property
	def IkeDhGroup(self):
		return self.__getattr__("IkeDhGroup")
	
	@cached_property
	def PFSGroup(self):
		return self.__getattr__("PFSGroup")
	
	@cached_property
	def IkeV2Auth(self):
		return self.__getattr__("IkeV2Auth")
	
	@cached_property
	def ServerCertificate(self):
		return self.__getattr__("ServerCertificate")
	
	@cached_property
	def IkePolicyLifeTime(self):
		return self.__getattr__("IkePolicyLifeTime")
	
	@cached_property
	def IPsecPolicyLifeTime(self):
		return self.__getattr__("IPsecPolicyLifeTime")
	
	@cached_property
	def PolicyName(self):
		return self.__getattr__("PolicyName")
	
	@cached_property
	def PolicyParameter(self):
		return self.__getattr__("PolicyParameter")
	
	@cached_property
	def PolicyFilterGroup(self):
		return self.__getattr__("PolicyFilterGroup")
	
	@cached_property
	def DnsServer1(self):
		return self.__getattr__("DnsServer1")
	
	@cached_property
	def DnsServer2(self):
		return self.__getattr__("DnsServer2")
	
	@cached_property
	def MgmServer1(self):
		return self.__getattr__("MgmServer1")
	
	@cached_property
	def MgmServer2(self):
		return self.__getattr__("MgmServer2")
	
	@cached_property
	def GroupSuffix(self):
		return self.__getattr__("GroupSuffix")
	
	@cached_property
	def DNSSuffix(self):
		return self.__getattr__("DNSSuffix")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvFilterNetworksHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of filter networks in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvFilterNetwork entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/flt-nets".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvFilterNetwork entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvFilterNetwork(self, self._groupid, self._templid)
	

class TemplSrvFilterNetwork(LazyModifiableListEntry):
	'''Configuration of filter networks in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		IPRanges : object(Model)
			IP Ranges
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def IPRanges(self):
		return self.__getattr__("IPRanges")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvFiltersHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of filters in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvFilter entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/filters".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvFilter entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvFilter(self, self._groupid, self._templid)
	

class TemplSrvFilter(LazyModifiableListEntry):
	'''Configuration of filters in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		State : bool
			State
		Command : int
			Command
			Enum Values: 1=permit, 0=deny
		Direction : int
			Direction
			Enum Values: 0=incoming, 1=outgoing, 2=bidirection
		IpProtocol : int
			IP Protocol
			Enum Values: 0=any, 1=ICMP, 17=UDP, 6=TCP, 50=ESP
		SourceFilterNetwork : uintkey
			Source Filter Network
		SourceIpAddressBegin : ipaddr
			Source IP Address Begin
		SourceIpAddressEnd : ipaddr
			Source IP Address End
		DestFilterNetwork : uintkey
			Destination Filter Network
		DestIpAddressBegin : ipaddr
			Destination IP Address Begin
		DestIpAddressEnd : ipaddr
			Destination IP Address End
		SourcePort : ses.portrange
			Source Port
		DestPort : ses.portrange
			Destination Port
		IpPriority : int
			IP Priority
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def Command(self):
		return self.__getattr__("Command")
	
	@cached_property
	def Direction(self):
		return self.__getattr__("Direction")
	
	@cached_property
	def IpProtocol(self):
		return self.__getattr__("IpProtocol")
	
	@cached_property
	def SourceFilterNetwork(self):
		return self.__getattr__("SourceFilterNetwork")
	
	@cached_property
	def SourceIpAddressBegin(self):
		return self.__getattr__("SourceIpAddressBegin")
	
	@cached_property
	def SourceIpAddressEnd(self):
		return self.__getattr__("SourceIpAddressEnd")
	
	@cached_property
	def DestFilterNetwork(self):
		return self.__getattr__("DestFilterNetwork")
	
	@cached_property
	def DestIpAddressBegin(self):
		return self.__getattr__("DestIpAddressBegin")
	
	@cached_property
	def DestIpAddressEnd(self):
		return self.__getattr__("DestIpAddressEnd")
	
	@cached_property
	def SourcePort(self):
		return self.__getattr__("SourcePort")
	
	@cached_property
	def DestPort(self):
		return self.__getattr__("DestPort")
	
	@cached_property
	def IpPriority(self):
		return self.__getattr__("IpPriority")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvFilterGroupsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of filter groups in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvFilterGroup entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/fltgrps".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvFilterGroup entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvFilterGroup(self, self._groupid, self._templid)
	

class TemplSrvFilterGroup(LazyModifiableListEntry):
	'''Configuration of filter groups in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		State : bool
			State
		Filters : ses.idxlist
			Selected Filters
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def Filters(self):
		return self.__getattr__("Filters")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvServerCertsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of server Certificates in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvServerCert entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/srv-certs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvServerCert entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvServerCert(self, self._groupid, self._templid)
	

class TemplSrvServerCert(LazyModifiableListEntry):
	'''Configuration of server Certificates in Secure Server Template

	Attributes [read-only]
	----------------------
		Certificate : cert
			Certificate
		PrivKeyState : int
			State Private Key
		FipsConform : int
			Is certificate FIPS conform
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		PkiType : int
			PKI Type
			Enum Values: 0=disabled, 9=NCPKeyStore, 1=PKCS12File, 3=PKCS11, 5=CSP
		PIN : str
			PIN
		PKCS12Filename : str
			PKCS#12 File Name
		PKCS11Modul : str
			PKCS#11 Modul
		PKCS11SlotIdx : int
			PKCS#11 Slot Index
		CspSubjectCN : str
			Matching Subject
		CspIssuerCN : str
			Matching Issuer
		CspId : str
			Matching Fingerprint
		CertNr : int
			Certificate number
		EnabledForIPsec : bool
			Enabled for IPsec
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def PkiType(self):
		return self.__getattr__("PkiType")
	
	@cached_property
	def PIN(self):
		return self.__getattr__("PIN")
	
	@cached_property
	def PKCS12Filename(self):
		return self.__getattr__("PKCS12Filename")
	
	@cached_property
	def PKCS11Modul(self):
		return self.__getattr__("PKCS11Modul")
	
	@cached_property
	def PKCS11SlotIdx(self):
		return self.__getattr__("PKCS11SlotIdx")
	
	@cached_property
	def CspSubjectCN(self):
		return self.__getattr__("CspSubjectCN")
	
	@cached_property
	def CspIssuerCN(self):
		return self.__getattr__("CspIssuerCN")
	
	@cached_property
	def CspId(self):
		return self.__getattr__("CspId")
	
	@cached_property
	def CertNr(self):
		return self.__getattr__("CertNr")
	
	@cached_property
	def EnabledForIPsec(self):
		return self.__getattr__("EnabledForIPsec")
	
	@cached_property
	def Certificate(self):
		return self.__getattr__("Certificate")
	
	@cached_property
	def PrivKeyState(self):
		return self.__getattr__("PrivKeyState")
	
	@cached_property
	def FipsConform(self):
		return self.__getattr__("FipsConform")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvCACertsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of CA certificates in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvCACert entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/ca-certs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvCACert entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvCACert(self, self._groupid, self._templid)
	

class TemplSrvCACert(LazyModifiableListEntry):
	'''Configuration of CA certificates in Secure Server Template

	Attributes [read-only]
	----------------------
		CrlIssuer : str
			CRL Issuer
		CrlValidFrom : str
			CRL Valid from
		CrlValidTo : str
			CRL Valid to
		CrlAKID : str
			CRL AKID
		CrlError : int
			CRL Error
		CrlNbrOfEntries : int
			CRL number of entries
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		Validity : int
			Validity
			Enum Values: 0=deny, 1=permit
		Certificate : cert
			Certificate
		AllowVpnUser : bool
			Permitted for Authentication of VPN Connections
		AllowHwCert : bool
			Permitted for Authentication with Hardware Certificates
		AllowSslVpn : bool
			Permitted for Authentication of SSL VPN Connections
		AllowWebProxy : bool
			Permitted for Authentication of outgoing SSL VPN Web Proxy Connections
		AllowWebCfg : bool
			Permitted for Authentication of Configuration
		AllowIFMAP : bool
			Permitted for Authentication on IF-MAP Server
		OcspProtocol : int
			OCSP Protocol
			Enum Values: 0=disabled, 1=ocspHttp
		OcspURL : str
			OCSP URL
		OcspInErrorCase : int
			OCSP in Error Case
			Enum Values: 0=denyUser, 1=permitUser
		CrlState : bool
			CRL State
		CrlFileName : str
			CRL Path / Filename
		CrlInErrorCase : int
			CRL in Error Case
			Enum Values: 0=denyUser, 1=permitUser
		CrlDownload : bool
			Use CRL Download
		CrlDownloadUrl1 : str
			1. CRL Download URL
		CrlDownloadUrl2 : str
			2. CRL Download URL
		CrlInterval : int
			CRL Download Interval
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Validity(self):
		return self.__getattr__("Validity")
	
	@cached_property
	def Certificate(self):
		return self.__getattr__("Certificate")
	
	@cached_property
	def AllowVpnUser(self):
		return self.__getattr__("AllowVpnUser")
	
	@cached_property
	def AllowHwCert(self):
		return self.__getattr__("AllowHwCert")
	
	@cached_property
	def AllowSslVpn(self):
		return self.__getattr__("AllowSslVpn")
	
	@cached_property
	def AllowWebProxy(self):
		return self.__getattr__("AllowWebProxy")
	
	@cached_property
	def AllowWebCfg(self):
		return self.__getattr__("AllowWebCfg")
	
	@cached_property
	def AllowIFMAP(self):
		return self.__getattr__("AllowIFMAP")
	
	@cached_property
	def OcspProtocol(self):
		return self.__getattr__("OcspProtocol")
	
	@cached_property
	def OcspURL(self):
		return self.__getattr__("OcspURL")
	
	@cached_property
	def OcspInErrorCase(self):
		return self.__getattr__("OcspInErrorCase")
	
	@cached_property
	def CrlState(self):
		return self.__getattr__("CrlState")
	
	@cached_property
	def CrlFileName(self):
		return self.__getattr__("CrlFileName")
	
	@cached_property
	def CrlInErrorCase(self):
		return self.__getattr__("CrlInErrorCase")
	
	@cached_property
	def CrlDownload(self):
		return self.__getattr__("CrlDownload")
	
	@cached_property
	def CrlDownloadUrl1(self):
		return self.__getattr__("CrlDownloadUrl1")
	
	@cached_property
	def CrlDownloadUrl2(self):
		return self.__getattr__("CrlDownloadUrl2")
	
	@cached_property
	def CrlInterval(self):
		return self.__getattr__("CrlInterval")
	
	@cached_property
	def CrlIssuer(self):
		return self.__getattr__("CrlIssuer")
	
	@cached_property
	def CrlValidFrom(self):
		return self.__getattr__("CrlValidFrom")
	
	@cached_property
	def CrlValidTo(self):
		return self.__getattr__("CrlValidTo")
	
	@cached_property
	def CrlAKID(self):
		return self.__getattr__("CrlAKID")
	
	@cached_property
	def CrlError(self):
		return self.__getattr__("CrlError")
	
	@cached_property
	def CrlNbrOfEntries(self):
		return self.__getattr__("CrlNbrOfEntries")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvDomainGroupsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of domain groups in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvDomainGroup entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/dom-grps".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvDomainGroup entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvDomainGroup(self, self._groupid, self._templid)
	

class TemplSrvDomainGroup(LazyModifiableListEntry):
	'''Configuration of domain groups in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		State : bool
			State
		Suffix : str
			Suffix
		CertificateMatching : str
			Certificate matching
		DNS1 : ipv4
			Primary DNS Server
		DNS2 : ipv4
			Secondary DNS Server
		WINS1 : ipv4
			Primary WINS Server
		WINS2 : ipv4
			Secondary WINS Server
		SEM1 : ipv4
			Primary Management Server
		SEM2 : ipv4
			Secondary Management Server
		DNSSuffix : str
			DNS Suffix
		SslVpnDnsSuffix : str
			SSL VPN DNS Suffix
		MSWPAD : str
			Windows Proxy Auto Discovery
		DomainSearchOrder : str
			Windows Domain Search Order
		IpSecPreSharedKey : str
			IPSec Pre-shared Key
		IKev2Auth : int
			IKEv2 Authentication
			Enum Values: 0=none, 1=Certificate, 2=PSK, 3=EAP
		IKEEapType : int
			IKEv2 EAP Type
			Enum Values: 0=none, 1=PAP, 2=MD5, 3=MSCHAP2, 4=TLS, 5=Relay RADIUS
		IKEv2AllowAuthCert : bool
			Allow certificate based authentication
		IKEv2AllowAuthPSK : bool
			Allow PSK based authentication
		IKEv2AllowAuthEAP : bool
			Allow EAP based authentication
		AllowRsaPkcs15Padding : bool
			Allow RSA authentication with PKCS#v1_5 padding
		ServerCertificate : uintkey
			Server Certificate
		UserMappings : object(Model)
			User Mapping
		OtpState1 : bool
			State 1. OTP Server
		OtpHost1 : ipaddr
			IP Address 1. OTP Server
		OtpPort1 : int
			Port 1. OTP Server
		OtpPassword1 : str
			Password 1. OTP Server
		OtpState2 : bool
			State 2. OTP Server
		OtpHost2 : ipaddr
			IP Address 2. OTP Server
		OtpPort2 : int
			Port 2. OTP Server
		OtpPassword2 : str
			Password 2. OTP Server
		OtpLeaseTime : int
			Leasetime OTP Server
		RadiusState1 : bool
			State 1. RADIUS Server
		RadiusAuthHost1 : ipaddr
			IP Address 1. Authentication RADIUS Server
		RadiusAuthPort1 : int
			Port IP 1. Authentication RADIUS Server
		RadiusAuthPassword1 : str
			Password 1. Authentication RADIUS Server
		RadiusAccHost1 : ipaddr
			IP Address 1. Accounting RADIUS Server
		RadiusAccPort1 : int
			Port IP 1. Accounting RADIUS Server
		RadiusAccPassword1 : str
			Password 1. Accounting RADIUS Server
		RadiusRetryInterval : int
			RADIUS Retry Interval
		RadiusForwardEAP : bool
			RADIUS forward EAP messages
		RadiusNasId : str
			RADIUS NAS ID
		RadiusState2 : bool
			State 2. RADIUS Server
		RadiusAuthHost2 : ipaddr
			IP Addresse 2. Authentication RADIUS Server
		RadiusAuthPort2 : int
			Port IP 2. Authentication RADIUS Server
		RadiusAuthPassword2 : str
			Password 2. Authentication RADIUS Server
		RadiusAccHost2 : ipaddr
			IP Addresse 2. Accounting RADIUS Server
		RadiusAccPort2 : int
			Port IP 2. Accounting RADIUS Server
		RadiusAccPassword2 : str
			Password 2. Accounting RADIUS Server
		LdapState1 : bool
			State 1. LDAP Server
		LdapProtocol1 : int
			Protocol 1. LDAP Server
			Enum Values: 0=ldap, 1=LDAP over SSL
		LdapHost1 : str
			Host 1. LDAP Server
		LdapPort1 : int
			Port 1. LDAP Server
		LdapVersion1 : int
			Version 1. LDAP Server
		LdapAdminDN1 : str
			Adminstrator DN 1. LDAP Server
		LdapAdminPassword1 : str
			Adminstrator Password 1. LDAP Server
		LdapLinkProfileDN1 : str
			Link Profile DN 1. LDAP Server
		LdapDefLinkProfileDN1 : str
			Default Link Profile DN 1. LDAP Server
		ldapLinkProfileAttrFilter : str
			LDAP Link Profile Attribute Filter
		ldapLinkProfileMemberOf : str
			LDAP Link Profile MemberOf
		ldapAuthType : bool
			Use LDAP Bind for authenication
		LdapState2 : bool
			State 2. LDAP Server
		LdapProtocol2 : int
			Protocol 2. LDAP Server
			Enum Values: 0=ldap, 1=LDAP over SSL
		LdapHost2 : str
			Host 2. LDAP Server
		LdapPort2 : int
			Port 2. LDAP Server
		LdapVersion2 : int
			Version 2. LDAP Server
		LdapAdminDN2 : str
			Adminstrator DN 2. LDAP Server
		LdapAdminPassword2 : str
			Adminstrator Password 2. LDAP Server
		LdapLinkProfileDN2 : str
			Link Profile DN 2. LDAP Server
		LdapDefLinkProfileDN2 : str
			Default Link Profile DN 2. LDAP Server
		DDNSProtocol : int
			DDNS Protocol
			Enum Values: 0=disabled, 1=DDNS
		DDNSHost1 : ipv4
			IP Address Primary DDNS Server
		DDNSHost2 : ipv4
			IP Address Secondary DDNS Server
		DDNSZone : str
			DDNS Zone
		DDNSUpdTimer : int
			DDNS Regular Update Timer
		DDNSNetworkMask : ipv4
			DDNS Reverse PTR Network Mask
		DDNSTTL : int
			DDNS Expire Time
		DHCPServer : ipv4
			DHCP Server
		DHCPServer2 : ipv4
			Backup DHCP Server
		DHCPSrcIpAddr : ipv4
			DHCP Source IP Address
		DHCPSrcNetworkMask : ipv4
			DHCP Source Network Mask
		DHCPAgentCircuitID : str
			DHCP Agent Circuit ID
		DHCPAgentRemoteID : str
			DHCP Agent Remote ID
		DHCPSrcIpAddrMetered : ipv4
			DHCP Source IP Address (metered connection)
		DHCPSrcNetworkMaskMetered : ipv4
			DHCP Source Network Mask (metered connection)
		DHCPAgentCircuitIDMetered : str
			DHCP Agent Circuit ID (metered connection)
		DHCPAgentRemoteIDMetered : str
			DHCP Agent Remote ID (metered connection)
		IPPools : object(Model)
			IP Pools
		IPv6PoolNetworkAddress : ipv6
			IPv6 Pool Network Address
		IPV6PoolPrefixLen : int
			IPv6 Pool Prefix length
		CertCheckCountry : str
			Country (C)
		CertCheckState : str
			State / Province (ST)
		CertCheckLocation : str
			Location (L)
		CertCheckOrg : str
			Organization (O)
		CertCheckOrgUnit : str
			Organization Unit (OU)
		CertCheckDC : str
			Domain Component (DC)
		OnlyWithHwCert : bool
			Connections only allowed with hardware certificate
		ValidCaCerts : ses.idxlist
			ValidCaCerts
		CertRsaKey : bool
			Allow certificates with RSA key
		CertRsaMinKeyLen : int
			Minimum RSA key length
		CertECP256 : bool
			Allow certificates with NIST ECP-256 key
		CertECP384 : bool
			Allow certificates with NIST ECP-384 key
		CertECP521 : bool
			Allow certificates with NIST ECP-521 key
		CertECBP256 : bool
			Allow certificates with Brainpool EC-256 key
		CertECBP384 : bool
			Allow certificates with Brainpool EC-384 key
		CertECBP521 : bool
			Allow certificates with Brainpool EC-521 key
		SubSystemRoutingMode : int
			Sub System Routing Mode
			Enum Values: 0=disabled, 1=ICMP Redirect, 2=RIP
		SubSystemLanIpAddr : ipv4
			Sub System LAN IP Address
		SubSystemRouter1 : ipv4
			Sub System 1. Master Router
		SubSystemRouter2 : ipv4
			Sub System 2. Master Router
		SubSystemRouter3 : ipv4
			Sub System 3. Master Router
		SubSystemRouter4 : ipv4
			Sub System 4. Master Router
		NoTransferOfRoutes : bool
			No transfer of network routes
		FilterGroupName : uintkey
			Filtergroup Name
		MaxConnectionTime : int
			Max Connection Time
		MaxVpnTunnels : int
			Max Number of VPN Tunnels
		MaxRxBandwidth : int
			Max Rx Bandwidth
		MaxTxBandwidth : int
			Max Tx Bandwidth
		OnlyNcpClients : bool
			Only NCP VPN Clients allowed
		SendSysLogsSystem : bool
			Send Syslogs (System Log)
		SysLogHost1System : ipaddr
			1. IP Address Syslog Server (System Log)
		SysLogHost2System : ipaddr
			2. IP Address Syslog Server (System Log)
		SysLogPortSystem : int
			Port Syslog Server (System Log)
		SysLogFacilitySystem : int
			Syslog Facility (System Log)
		SysLogSeveritySystem : int
			Syslog Severity (System Log)
		SysLogProtoSystem : int
			Syslog Protocol (System Log)
			Enum Values: 0=UDP, 1=TCP
		SendSysLogsError : bool
			Send Syslogs (Error Log )
		SysLogHost1Error : ipaddr
			1. IP Address Syslog Server (Error Log)
		SysLogHost2Error : ipaddr
			2. IP Address Syslog Server (Error Log)
		SysLogPortError : int
			Port Syslog Server (Error Log)
		SysLogFacilityError : int
			Syslog Facility (Error Log)
		SysLogSeverityError : int
			Syslog Severity (Error Log)
		SysLogProtoError : int
			Syslog Protocol (Error Log)
			Enum Values: 0=UDP, 1=TCP
		SendSysLogsConfig : bool
			Send Syslogs (Config Log)
		SysLogHost1Config : ipaddr
			1. IP Address Syslog Server (Config Log)
		SysLogHost2Config : ipaddr
			2. IP Address Syslog Server (Config Log)
		SysLogPortConfig : int
			Port Syslog Server (Config Log)
		SysLogFacilityConfig : int
			Syslog Facility (Config Log)
		SysLogSeverityConfig : int
			Syslog Severity (Config Log)
		SysLogProtoConfig : int
			Syslog Protocol (Config Log)
			Enum Values: 0=UDP, 1=TCP
		SendSysLogsAccount : bool
			Send Syslogs (Account Log)
		SysLogHost1Account : ipaddr
			1. IP Address Syslog Server (Account Log)
		SysLogHost2Account : ipaddr
			2. IP Address Syslog Server (Account Log)
		SysLogPortAccount : int
			Port Syslog Server (Account Log)
		SysLogFacilityAccount : int
			Syslog Facility (Account Log)
		SysLogSeverityAccount : int
			Syslog Severity (Account Log)
		SysLogProtoAccount : int
			Syslog Protocol (Account Log)
			Enum Values: 0=UDP, 1=TCP
		SendSysLogsProtocol : bool
			Send Syslogs (Protocol Log)
		SysLogHost1Protocol : ipaddr
			1. IP Address Syslog Server (Protocol Log)
		SysLogHost2Protocol : ipaddr
			2. IP Address Syslog Server (Protocol Log)
		SysLogPortProtocol : int
			Port Syslog Server (Protocol Log)
		SysLogFacilityProtocol : int
			Syslog Facility (Protocol Log)
		SysLogSeverityProtocol : int
			Syslog Severity (Protocol Log)
		SysLogProtoProtocol : int
			Syslog Protocol (Protocol Log)
			Enum Values: 0=UDP, 1=TCP
		SendSysLogsFilter : bool
			Send Syslogs (Filter Log)
		SysLogHost1Filter : ipaddr
			1. IP Address Syslog Server (Filter Log)
		SysLogHost2Filter : ipaddr
			2. IP Address Syslog Server (Filter Log)
		SysLogPortFilter : int
			Port Syslog Server (Filter Log)
		SysLogFacilityFilter : int
			Syslog Facility (Filter Log)
		SysLogSeverityFilter : int
			Syslog Severity (Filter Log)
		SysLogProtoFilter : int
			Syslog Protocol (Filter Log)
			Enum Values: 0=UDP, 1=TCP
		SendSysLogsTrace : bool
			Send Syslogs (Trace Log)
		SysLogHost1Trace : ipaddr
			1. IP Address Syslog Server (Trace Log)
		SysLogHost2Trace : ipaddr
			2. IP Address Syslog Server (Trace Log)
		SysLogPortTrace : int
			Port Syslog Server (Trace Log)
		SysLogFacilityTrace : int
			Syslog Facility (Trace Log)
		SysLogSeverityTrace : int
			Syslog Severity (Trace Log)
		SysLogProtoTrace : int
			Syslog Protocol (Trace Log)
			Enum Values: 0=UDP, 1=TCP
		IfmapURL : str
			IF-MAP URL
		GreEndpoint : ipv4
			GRE IP Address
		VpnEndpoint : uintkey
			Link Profile Name
		RelayGroupMembersOnly : bool
			Relay group members only
		VLANID : int
			VLAN ID
		RadiusRelay : bool
			Relay Radius Requests
		ldapRelay : bool
			Relay LDAP Requests
		semRelay : bool
			Relay SEM Requests
		DHCPRelay : bool
			Relay DHCP Requests
		AdvCfgRlState : bool
			ACR State
		AdvCfgRlLdapHost1 : str
			ACR Hostname 1. LDAP Server
		AdvCfgRlLdapHost2 : str
			ACR Hostname 2. LDAP Server
		AdvCfgRlLdapPort : int
			ACR Port LDAP Server
		AdvCfgRlLdapAdminDN : str
			ACR Adminstrator DN LDAP Server
		AdvCfgRlLdapAdminPassword : str
			ACR Adminstrator Password LDAP Server
		AdvCfgRlLdapSearchDN : str
			ACR Search DN LDAP Server
		AdvCfgRlModUsernameSearch : str
			ACR Modification VPN Username (regex search)
		AdvCfgRlModUsernameRepl : str
			ACR Modification VPN Username (regex replace)
		AdvCfgRlVLanRelay : bool
			ACR VLAN relay
		AdvCfgRules : object(Model)
			ACR Rules
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def Suffix(self):
		return self.__getattr__("Suffix")
	
	@cached_property
	def CertificateMatching(self):
		return self.__getattr__("CertificateMatching")
	
	@cached_property
	def DNS1(self):
		return self.__getattr__("DNS1")
	
	@cached_property
	def DNS2(self):
		return self.__getattr__("DNS2")
	
	@cached_property
	def WINS1(self):
		return self.__getattr__("WINS1")
	
	@cached_property
	def WINS2(self):
		return self.__getattr__("WINS2")
	
	@cached_property
	def SEM1(self):
		return self.__getattr__("SEM1")
	
	@cached_property
	def SEM2(self):
		return self.__getattr__("SEM2")
	
	@cached_property
	def DNSSuffix(self):
		return self.__getattr__("DNSSuffix")
	
	@cached_property
	def SslVpnDnsSuffix(self):
		return self.__getattr__("SslVpnDnsSuffix")
	
	@cached_property
	def MSWPAD(self):
		return self.__getattr__("MSWPAD")
	
	@cached_property
	def DomainSearchOrder(self):
		return self.__getattr__("DomainSearchOrder")
	
	@cached_property
	def IpSecPreSharedKey(self):
		return self.__getattr__("IpSecPreSharedKey")
	
	@cached_property
	def IKev2Auth(self):
		return self.__getattr__("IKev2Auth")
	
	@cached_property
	def IKEEapType(self):
		return self.__getattr__("IKEEapType")
	
	@cached_property
	def IKEv2AllowAuthCert(self):
		return self.__getattr__("IKEv2AllowAuthCert")
	
	@cached_property
	def IKEv2AllowAuthPSK(self):
		return self.__getattr__("IKEv2AllowAuthPSK")
	
	@cached_property
	def IKEv2AllowAuthEAP(self):
		return self.__getattr__("IKEv2AllowAuthEAP")
	
	@cached_property
	def AllowRsaPkcs15Padding(self):
		return self.__getattr__("AllowRsaPkcs15Padding")
	
	@cached_property
	def ServerCertificate(self):
		return self.__getattr__("ServerCertificate")
	
	@cached_property
	def UserMappings(self):
		return self.__getattr__("UserMappings")
	
	@cached_property
	def OtpState1(self):
		return self.__getattr__("OtpState1")
	
	@cached_property
	def OtpHost1(self):
		return self.__getattr__("OtpHost1")
	
	@cached_property
	def OtpPort1(self):
		return self.__getattr__("OtpPort1")
	
	@cached_property
	def OtpPassword1(self):
		return self.__getattr__("OtpPassword1")
	
	@cached_property
	def OtpState2(self):
		return self.__getattr__("OtpState2")
	
	@cached_property
	def OtpHost2(self):
		return self.__getattr__("OtpHost2")
	
	@cached_property
	def OtpPort2(self):
		return self.__getattr__("OtpPort2")
	
	@cached_property
	def OtpPassword2(self):
		return self.__getattr__("OtpPassword2")
	
	@cached_property
	def OtpLeaseTime(self):
		return self.__getattr__("OtpLeaseTime")
	
	@cached_property
	def RadiusState1(self):
		return self.__getattr__("RadiusState1")
	
	@cached_property
	def RadiusAuthHost1(self):
		return self.__getattr__("RadiusAuthHost1")
	
	@cached_property
	def RadiusAuthPort1(self):
		return self.__getattr__("RadiusAuthPort1")
	
	@cached_property
	def RadiusAuthPassword1(self):
		return self.__getattr__("RadiusAuthPassword1")
	
	@cached_property
	def RadiusAccHost1(self):
		return self.__getattr__("RadiusAccHost1")
	
	@cached_property
	def RadiusAccPort1(self):
		return self.__getattr__("RadiusAccPort1")
	
	@cached_property
	def RadiusAccPassword1(self):
		return self.__getattr__("RadiusAccPassword1")
	
	@cached_property
	def RadiusRetryInterval(self):
		return self.__getattr__("RadiusRetryInterval")
	
	@cached_property
	def RadiusForwardEAP(self):
		return self.__getattr__("RadiusForwardEAP")
	
	@cached_property
	def RadiusNasId(self):
		return self.__getattr__("RadiusNasId")
	
	@cached_property
	def RadiusState2(self):
		return self.__getattr__("RadiusState2")
	
	@cached_property
	def RadiusAuthHost2(self):
		return self.__getattr__("RadiusAuthHost2")
	
	@cached_property
	def RadiusAuthPort2(self):
		return self.__getattr__("RadiusAuthPort2")
	
	@cached_property
	def RadiusAuthPassword2(self):
		return self.__getattr__("RadiusAuthPassword2")
	
	@cached_property
	def RadiusAccHost2(self):
		return self.__getattr__("RadiusAccHost2")
	
	@cached_property
	def RadiusAccPort2(self):
		return self.__getattr__("RadiusAccPort2")
	
	@cached_property
	def RadiusAccPassword2(self):
		return self.__getattr__("RadiusAccPassword2")
	
	@cached_property
	def LdapState1(self):
		return self.__getattr__("LdapState1")
	
	@cached_property
	def LdapProtocol1(self):
		return self.__getattr__("LdapProtocol1")
	
	@cached_property
	def LdapHost1(self):
		return self.__getattr__("LdapHost1")
	
	@cached_property
	def LdapPort1(self):
		return self.__getattr__("LdapPort1")
	
	@cached_property
	def LdapVersion1(self):
		return self.__getattr__("LdapVersion1")
	
	@cached_property
	def LdapAdminDN1(self):
		return self.__getattr__("LdapAdminDN1")
	
	@cached_property
	def LdapAdminPassword1(self):
		return self.__getattr__("LdapAdminPassword1")
	
	@cached_property
	def LdapLinkProfileDN1(self):
		return self.__getattr__("LdapLinkProfileDN1")
	
	@cached_property
	def LdapDefLinkProfileDN1(self):
		return self.__getattr__("LdapDefLinkProfileDN1")
	
	@cached_property
	def ldapLinkProfileAttrFilter(self):
		return self.__getattr__("ldapLinkProfileAttrFilter")
	
	@cached_property
	def ldapLinkProfileMemberOf(self):
		return self.__getattr__("ldapLinkProfileMemberOf")
	
	@cached_property
	def ldapAuthType(self):
		return self.__getattr__("ldapAuthType")
	
	@cached_property
	def LdapState2(self):
		return self.__getattr__("LdapState2")
	
	@cached_property
	def LdapProtocol2(self):
		return self.__getattr__("LdapProtocol2")
	
	@cached_property
	def LdapHost2(self):
		return self.__getattr__("LdapHost2")
	
	@cached_property
	def LdapPort2(self):
		return self.__getattr__("LdapPort2")
	
	@cached_property
	def LdapVersion2(self):
		return self.__getattr__("LdapVersion2")
	
	@cached_property
	def LdapAdminDN2(self):
		return self.__getattr__("LdapAdminDN2")
	
	@cached_property
	def LdapAdminPassword2(self):
		return self.__getattr__("LdapAdminPassword2")
	
	@cached_property
	def LdapLinkProfileDN2(self):
		return self.__getattr__("LdapLinkProfileDN2")
	
	@cached_property
	def LdapDefLinkProfileDN2(self):
		return self.__getattr__("LdapDefLinkProfileDN2")
	
	@cached_property
	def DDNSProtocol(self):
		return self.__getattr__("DDNSProtocol")
	
	@cached_property
	def DDNSHost1(self):
		return self.__getattr__("DDNSHost1")
	
	@cached_property
	def DDNSHost2(self):
		return self.__getattr__("DDNSHost2")
	
	@cached_property
	def DDNSZone(self):
		return self.__getattr__("DDNSZone")
	
	@cached_property
	def DDNSUpdTimer(self):
		return self.__getattr__("DDNSUpdTimer")
	
	@cached_property
	def DDNSNetworkMask(self):
		return self.__getattr__("DDNSNetworkMask")
	
	@cached_property
	def DDNSTTL(self):
		return self.__getattr__("DDNSTTL")
	
	@cached_property
	def DHCPServer(self):
		return self.__getattr__("DHCPServer")
	
	@cached_property
	def DHCPServer2(self):
		return self.__getattr__("DHCPServer2")
	
	@cached_property
	def DHCPSrcIpAddr(self):
		return self.__getattr__("DHCPSrcIpAddr")
	
	@cached_property
	def DHCPSrcNetworkMask(self):
		return self.__getattr__("DHCPSrcNetworkMask")
	
	@cached_property
	def DHCPAgentCircuitID(self):
		return self.__getattr__("DHCPAgentCircuitID")
	
	@cached_property
	def DHCPAgentRemoteID(self):
		return self.__getattr__("DHCPAgentRemoteID")
	
	@cached_property
	def DHCPSrcIpAddrMetered(self):
		return self.__getattr__("DHCPSrcIpAddrMetered")
	
	@cached_property
	def DHCPSrcNetworkMaskMetered(self):
		return self.__getattr__("DHCPSrcNetworkMaskMetered")
	
	@cached_property
	def DHCPAgentCircuitIDMetered(self):
		return self.__getattr__("DHCPAgentCircuitIDMetered")
	
	@cached_property
	def DHCPAgentRemoteIDMetered(self):
		return self.__getattr__("DHCPAgentRemoteIDMetered")
	
	@cached_property
	def IPPools(self):
		return self.__getattr__("IPPools")
	
	@cached_property
	def IPv6PoolNetworkAddress(self):
		return self.__getattr__("IPv6PoolNetworkAddress")
	
	@cached_property
	def IPV6PoolPrefixLen(self):
		return self.__getattr__("IPV6PoolPrefixLen")
	
	@cached_property
	def CertCheckCountry(self):
		return self.__getattr__("CertCheckCountry")
	
	@cached_property
	def CertCheckState(self):
		return self.__getattr__("CertCheckState")
	
	@cached_property
	def CertCheckLocation(self):
		return self.__getattr__("CertCheckLocation")
	
	@cached_property
	def CertCheckOrg(self):
		return self.__getattr__("CertCheckOrg")
	
	@cached_property
	def CertCheckOrgUnit(self):
		return self.__getattr__("CertCheckOrgUnit")
	
	@cached_property
	def CertCheckDC(self):
		return self.__getattr__("CertCheckDC")
	
	@cached_property
	def OnlyWithHwCert(self):
		return self.__getattr__("OnlyWithHwCert")
	
	@cached_property
	def ValidCaCerts(self):
		return self.__getattr__("ValidCaCerts")
	
	@cached_property
	def CertRsaKey(self):
		return self.__getattr__("CertRsaKey")
	
	@cached_property
	def CertRsaMinKeyLen(self):
		return self.__getattr__("CertRsaMinKeyLen")
	
	@cached_property
	def CertECP256(self):
		return self.__getattr__("CertECP256")
	
	@cached_property
	def CertECP384(self):
		return self.__getattr__("CertECP384")
	
	@cached_property
	def CertECP521(self):
		return self.__getattr__("CertECP521")
	
	@cached_property
	def CertECBP256(self):
		return self.__getattr__("CertECBP256")
	
	@cached_property
	def CertECBP384(self):
		return self.__getattr__("CertECBP384")
	
	@cached_property
	def CertECBP521(self):
		return self.__getattr__("CertECBP521")
	
	@cached_property
	def SubSystemRoutingMode(self):
		return self.__getattr__("SubSystemRoutingMode")
	
	@cached_property
	def SubSystemLanIpAddr(self):
		return self.__getattr__("SubSystemLanIpAddr")
	
	@cached_property
	def SubSystemRouter1(self):
		return self.__getattr__("SubSystemRouter1")
	
	@cached_property
	def SubSystemRouter2(self):
		return self.__getattr__("SubSystemRouter2")
	
	@cached_property
	def SubSystemRouter3(self):
		return self.__getattr__("SubSystemRouter3")
	
	@cached_property
	def SubSystemRouter4(self):
		return self.__getattr__("SubSystemRouter4")
	
	@cached_property
	def NoTransferOfRoutes(self):
		return self.__getattr__("NoTransferOfRoutes")
	
	@cached_property
	def FilterGroupName(self):
		return self.__getattr__("FilterGroupName")
	
	@cached_property
	def MaxConnectionTime(self):
		return self.__getattr__("MaxConnectionTime")
	
	@cached_property
	def MaxVpnTunnels(self):
		return self.__getattr__("MaxVpnTunnels")
	
	@cached_property
	def MaxRxBandwidth(self):
		return self.__getattr__("MaxRxBandwidth")
	
	@cached_property
	def MaxTxBandwidth(self):
		return self.__getattr__("MaxTxBandwidth")
	
	@cached_property
	def OnlyNcpClients(self):
		return self.__getattr__("OnlyNcpClients")
	
	@cached_property
	def SendSysLogsSystem(self):
		return self.__getattr__("SendSysLogsSystem")
	
	@cached_property
	def SysLogHost1System(self):
		return self.__getattr__("SysLogHost1System")
	
	@cached_property
	def SysLogHost2System(self):
		return self.__getattr__("SysLogHost2System")
	
	@cached_property
	def SysLogPortSystem(self):
		return self.__getattr__("SysLogPortSystem")
	
	@cached_property
	def SysLogFacilitySystem(self):
		return self.__getattr__("SysLogFacilitySystem")
	
	@cached_property
	def SysLogSeveritySystem(self):
		return self.__getattr__("SysLogSeveritySystem")
	
	@cached_property
	def SysLogProtoSystem(self):
		return self.__getattr__("SysLogProtoSystem")
	
	@cached_property
	def SendSysLogsError(self):
		return self.__getattr__("SendSysLogsError")
	
	@cached_property
	def SysLogHost1Error(self):
		return self.__getattr__("SysLogHost1Error")
	
	@cached_property
	def SysLogHost2Error(self):
		return self.__getattr__("SysLogHost2Error")
	
	@cached_property
	def SysLogPortError(self):
		return self.__getattr__("SysLogPortError")
	
	@cached_property
	def SysLogFacilityError(self):
		return self.__getattr__("SysLogFacilityError")
	
	@cached_property
	def SysLogSeverityError(self):
		return self.__getattr__("SysLogSeverityError")
	
	@cached_property
	def SysLogProtoError(self):
		return self.__getattr__("SysLogProtoError")
	
	@cached_property
	def SendSysLogsConfig(self):
		return self.__getattr__("SendSysLogsConfig")
	
	@cached_property
	def SysLogHost1Config(self):
		return self.__getattr__("SysLogHost1Config")
	
	@cached_property
	def SysLogHost2Config(self):
		return self.__getattr__("SysLogHost2Config")
	
	@cached_property
	def SysLogPortConfig(self):
		return self.__getattr__("SysLogPortConfig")
	
	@cached_property
	def SysLogFacilityConfig(self):
		return self.__getattr__("SysLogFacilityConfig")
	
	@cached_property
	def SysLogSeverityConfig(self):
		return self.__getattr__("SysLogSeverityConfig")
	
	@cached_property
	def SysLogProtoConfig(self):
		return self.__getattr__("SysLogProtoConfig")
	
	@cached_property
	def SendSysLogsAccount(self):
		return self.__getattr__("SendSysLogsAccount")
	
	@cached_property
	def SysLogHost1Account(self):
		return self.__getattr__("SysLogHost1Account")
	
	@cached_property
	def SysLogHost2Account(self):
		return self.__getattr__("SysLogHost2Account")
	
	@cached_property
	def SysLogPortAccount(self):
		return self.__getattr__("SysLogPortAccount")
	
	@cached_property
	def SysLogFacilityAccount(self):
		return self.__getattr__("SysLogFacilityAccount")
	
	@cached_property
	def SysLogSeverityAccount(self):
		return self.__getattr__("SysLogSeverityAccount")
	
	@cached_property
	def SysLogProtoAccount(self):
		return self.__getattr__("SysLogProtoAccount")
	
	@cached_property
	def SendSysLogsProtocol(self):
		return self.__getattr__("SendSysLogsProtocol")
	
	@cached_property
	def SysLogHost1Protocol(self):
		return self.__getattr__("SysLogHost1Protocol")
	
	@cached_property
	def SysLogHost2Protocol(self):
		return self.__getattr__("SysLogHost2Protocol")
	
	@cached_property
	def SysLogPortProtocol(self):
		return self.__getattr__("SysLogPortProtocol")
	
	@cached_property
	def SysLogFacilityProtocol(self):
		return self.__getattr__("SysLogFacilityProtocol")
	
	@cached_property
	def SysLogSeverityProtocol(self):
		return self.__getattr__("SysLogSeverityProtocol")
	
	@cached_property
	def SysLogProtoProtocol(self):
		return self.__getattr__("SysLogProtoProtocol")
	
	@cached_property
	def SendSysLogsFilter(self):
		return self.__getattr__("SendSysLogsFilter")
	
	@cached_property
	def SysLogHost1Filter(self):
		return self.__getattr__("SysLogHost1Filter")
	
	@cached_property
	def SysLogHost2Filter(self):
		return self.__getattr__("SysLogHost2Filter")
	
	@cached_property
	def SysLogPortFilter(self):
		return self.__getattr__("SysLogPortFilter")
	
	@cached_property
	def SysLogFacilityFilter(self):
		return self.__getattr__("SysLogFacilityFilter")
	
	@cached_property
	def SysLogSeverityFilter(self):
		return self.__getattr__("SysLogSeverityFilter")
	
	@cached_property
	def SysLogProtoFilter(self):
		return self.__getattr__("SysLogProtoFilter")
	
	@cached_property
	def SendSysLogsTrace(self):
		return self.__getattr__("SendSysLogsTrace")
	
	@cached_property
	def SysLogHost1Trace(self):
		return self.__getattr__("SysLogHost1Trace")
	
	@cached_property
	def SysLogHost2Trace(self):
		return self.__getattr__("SysLogHost2Trace")
	
	@cached_property
	def SysLogPortTrace(self):
		return self.__getattr__("SysLogPortTrace")
	
	@cached_property
	def SysLogFacilityTrace(self):
		return self.__getattr__("SysLogFacilityTrace")
	
	@cached_property
	def SysLogSeverityTrace(self):
		return self.__getattr__("SysLogSeverityTrace")
	
	@cached_property
	def SysLogProtoTrace(self):
		return self.__getattr__("SysLogProtoTrace")
	
	@cached_property
	def IfmapURL(self):
		return self.__getattr__("IfmapURL")
	
	@cached_property
	def GreEndpoint(self):
		return self.__getattr__("GreEndpoint")
	
	@cached_property
	def VpnEndpoint(self):
		return self.__getattr__("VpnEndpoint")
	
	@cached_property
	def RelayGroupMembersOnly(self):
		return self.__getattr__("RelayGroupMembersOnly")
	
	@cached_property
	def VLANID(self):
		return self.__getattr__("VLANID")
	
	@cached_property
	def RadiusRelay(self):
		return self.__getattr__("RadiusRelay")
	
	@cached_property
	def ldapRelay(self):
		return self.__getattr__("ldapRelay")
	
	@cached_property
	def semRelay(self):
		return self.__getattr__("semRelay")
	
	@cached_property
	def DHCPRelay(self):
		return self.__getattr__("DHCPRelay")
	
	@cached_property
	def AdvCfgRlState(self):
		return self.__getattr__("AdvCfgRlState")
	
	@cached_property
	def AdvCfgRlLdapHost1(self):
		return self.__getattr__("AdvCfgRlLdapHost1")
	
	@cached_property
	def AdvCfgRlLdapHost2(self):
		return self.__getattr__("AdvCfgRlLdapHost2")
	
	@cached_property
	def AdvCfgRlLdapPort(self):
		return self.__getattr__("AdvCfgRlLdapPort")
	
	@cached_property
	def AdvCfgRlLdapAdminDN(self):
		return self.__getattr__("AdvCfgRlLdapAdminDN")
	
	@cached_property
	def AdvCfgRlLdapAdminPassword(self):
		return self.__getattr__("AdvCfgRlLdapAdminPassword")
	
	@cached_property
	def AdvCfgRlLdapSearchDN(self):
		return self.__getattr__("AdvCfgRlLdapSearchDN")
	
	@cached_property
	def AdvCfgRlModUsernameSearch(self):
		return self.__getattr__("AdvCfgRlModUsernameSearch")
	
	@cached_property
	def AdvCfgRlModUsernameRepl(self):
		return self.__getattr__("AdvCfgRlModUsernameRepl")
	
	@cached_property
	def AdvCfgRlVLanRelay(self):
		return self.__getattr__("AdvCfgRlVLanRelay")
	
	@cached_property
	def AdvCfgRules(self):
		return self.__getattr__("AdvCfgRules")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvStaticRoutesHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of static routes in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvStaticRoute entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/routes".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvStaticRoute entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvStaticRoute(self, self._groupid, self._templid)
	

class TemplSrvStaticRoute(LazyModifiableListEntry):
	'''Configuration of static routes in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Network : ipv4
			Network Address
		NetworkMask : ipv4
			Network Mask
		NextHop : ipv4
			Next Hop
		Metric : int
			Metric
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Network(self):
		return self.__getattr__("Network")
	
	@cached_property
	def NetworkMask(self):
		return self.__getattr__("NetworkMask")
	
	@cached_property
	def NextHop(self):
		return self.__getattr__("NextHop")
	
	@cached_property
	def Metric(self):
		return self.__getattr__("Metric")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class TemplSrvListenersHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of listeners in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvListener entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/server-templs/{templid}/listeners".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplSrvListener entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvListener(self, self._groupid, self._templid)
	

class TemplSrvListener(LazyModifiableListEntry):
	'''Configuration of listeners in Secure Server Template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by

	Attributes [writable]
	---------------------
		Name : str
			Name
		State : bool
			State
		ListenIpAddr : ipaddr
			IP Address (Listener)
		ListenPort : int
			Port
		Type : int
			Type
			Enum Values: 0=SSL VPN and Path Finder, 1=only Path Finder, 2=only SSL VPN
		ServerCertificate : uintkey
			Server Certificate
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server specific
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def ListenIpAddr(self):
		return self.__getattr__("ListenIpAddr")
	
	@cached_property
	def ListenPort(self):
		return self.__getattr__("ListenPort")
	
	@cached_property
	def Type(self):
		return self.__getattr__("Type")
	
	@cached_property
	def ServerCertificate(self):
		return self.__getattr__("ServerCertificate")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	

class SecureServersHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of Secure Server

	Methods
	-------
		createEntry()
			Creates a new SecureServerTemplate entry object.
	
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
		url = "srv-mgm/{groupid}/servers".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new SecureServerTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SecureServerTemplate(self, self._groupid)
	

class SrvLocalSystemHandler(BaseUpdateHandler, BaseGetHandler):
	'''Configuration of local system in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvLocalSystem entry object.
	
	Inherited Methods
	-----------------
		get (BaseGetHandler)
		update (BaseUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/local-system".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvLocalSystem entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvLocalSystem(self, self._groupid, self._srvid)
	

class SrvNetworkInterfacesHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of network interfaces in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvNetworkInterface entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/net-if".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvNetworkInterface entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvNetworkInterface(self, self._groupid, self._srvid)
	

class SrvLinksHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of Link Profiles in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvLink entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/links".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvLink entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvLink(self, self._groupid, self._srvid)
	

class SrvFilterNetworksHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of Filter Networks in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvFilterNetwork entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/flt-nets".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvFilterNetwork entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvFilterNetwork(self, self._groupid, self._srvid)
	

class SrvFiltersHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of Filters in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvFilter entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/filters".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvFilter entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvFilter(self, self._groupid, self._srvid)
	

class SrvFilterGroupsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of Filter Group in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvFilterGroup entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/fltgrps".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvFilterGroup entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvFilterGroup(self, self._groupid, self._srvid)
	

class SrvServerCertsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of server certificates in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvServerCert entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/srv-certs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvServerCert entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvServerCert(self, self._groupid, self._srvid)
	

class SrvCACertsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of CA certificates in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvCACert entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/ca-certs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvCACert entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvCACert(self, self._groupid, self._srvid)
	

class SrvDomainGroupsHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of domain groups in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvDomainGroup entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/dom-grps".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvDomainGroup entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvDomainGroup(self, self._groupid, self._srvid)
	

class SrvStaticRoutesHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of static routes in Secure Server

	Methods
	-------
		createEntry()
			Creates a new TemplSrvStaticRoute entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/routes".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvStaticRoute entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvStaticRoute(self, self._groupid, self._srvid)
	

class SrvListenersHandler(BaseListGetHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of listener in Secure Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplSrvListener entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/listeners".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new TemplSrvListener entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplSrvListener(self, self._groupid, self._srvid)
	

class SrvStatusLocalSystemHandler(BaseGetHandler):
	'''Statistics of Local System in Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvStatusLocalSystem entry object.
	
	Inherited Methods
	-----------------
		get (BaseGetHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/stat/local-system".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvStatusLocalSystem entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvStatusLocalSystem(self, self._groupid, self._srvid)
	

class SrvStatusLocalSystem(BaseEntry):
	'''Statistics of Local System in Secure Server

	Attributes [read-only]
	----------------------
		UpTime : int
			Up Time
		VpnHaOpMode : int
			VPN HA Operation Mode
			Enum Values: 1=without HA Service, 2=not available, 3=FS Primary, 4=FS Backup, 5=LB Available, 6=locked
		SslVpnHaOpMode : int
			SSL VPN HA Operation Mode
			Enum Values: 1=without HA Service, 2=not available, 3=FS Primary, 4=FS Backup, 5=LB Available, 6=locked
		VrrpOpMode : int
			VRRP Operation Mode
			Enum Values: 1=disabled, 2=not available, 11=VRRP Master, 12=VRRP Backup
		CPULoad : int
			CPU Load
		FipsState : int
			FIPS State
			Enum Values: 0=disabled, 1=enabled, 2=failed
		VpnTotalRxBytes : int
			VPN Total Rx Bytes
		VpnTotalTxBytes : int
			VPN Total Tx Bytes
		VpnRxRate : int
			VPN Rx Rate
		VpnTxRate : int
			VPN Tx Rate
		MaxWanPorts : int
			MAX WAN Ports
		NbrOfBuffers : int
			Number of Buffers in use
		NbrOfMessages : int
			Number of Messages in use
		NbrOfLCP : int
			Number of LCP Objects in use
		NbrOfPAPCHAP : int
			Number of PAP and CHAP Objects in use
		NbrOfCBCP : int
			Number of CBCP Objects in use
		NbrOfMLCP : int
			Number of MLCP Objects in use
		NbrOfIPCP : int
			Number of IPCP Objects in use
		NbrOfCCP : int
			Number of CCP Objects in use
		NbrOfL2TpObjects : int
			Number of L2TP Tunnel objects in use
		NbrOfL2TpClients : int
			Number of L2TP Clients objects in use
		NbrOfL2TpBuffers : int
			Number of L2TP Buffer objects in use
		NbrOfECP : int
			Number of ECP objects in use
		NbrOfSSLCP : int
			Number of SSLCP objects in use
		NbrOfIPSecObjects : int
			Number of IPSec Objects in use
		NbrOfResPoolIpAddresses : int
			Number of res. POOL IP addresses in use
		SslVpnTotalRxBytes : int
			SSL VPN Total Rx Bytes
		SslVpnTotalTxBytes : int
			SSL VPN Total Tx Bytes
		NbrOfSslVpnSessions : int
			Number of SSL VPN Sessions
	'''

	def __init__(self, getHandler, groupid, srvid):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def UpTime(self):
		return self.__getattr__("UpTime")
	
	@cached_property
	def VpnHaOpMode(self):
		return self.__getattr__("VpnHaOpMode")
	
	@cached_property
	def SslVpnHaOpMode(self):
		return self.__getattr__("SslVpnHaOpMode")
	
	@cached_property
	def VrrpOpMode(self):
		return self.__getattr__("VrrpOpMode")
	
	@cached_property
	def CPULoad(self):
		return self.__getattr__("CPULoad")
	
	@cached_property
	def FipsState(self):
		return self.__getattr__("FipsState")
	
	@cached_property
	def VpnTotalRxBytes(self):
		return self.__getattr__("VpnTotalRxBytes")
	
	@cached_property
	def VpnTotalTxBytes(self):
		return self.__getattr__("VpnTotalTxBytes")
	
	@cached_property
	def VpnRxRate(self):
		return self.__getattr__("VpnRxRate")
	
	@cached_property
	def VpnTxRate(self):
		return self.__getattr__("VpnTxRate")
	
	@cached_property
	def MaxWanPorts(self):
		return self.__getattr__("MaxWanPorts")
	
	@cached_property
	def NbrOfBuffers(self):
		return self.__getattr__("NbrOfBuffers")
	
	@cached_property
	def NbrOfMessages(self):
		return self.__getattr__("NbrOfMessages")
	
	@cached_property
	def NbrOfLCP(self):
		return self.__getattr__("NbrOfLCP")
	
	@cached_property
	def NbrOfPAPCHAP(self):
		return self.__getattr__("NbrOfPAPCHAP")
	
	@cached_property
	def NbrOfCBCP(self):
		return self.__getattr__("NbrOfCBCP")
	
	@cached_property
	def NbrOfMLCP(self):
		return self.__getattr__("NbrOfMLCP")
	
	@cached_property
	def NbrOfIPCP(self):
		return self.__getattr__("NbrOfIPCP")
	
	@cached_property
	def NbrOfCCP(self):
		return self.__getattr__("NbrOfCCP")
	
	@cached_property
	def NbrOfL2TpObjects(self):
		return self.__getattr__("NbrOfL2TpObjects")
	
	@cached_property
	def NbrOfL2TpClients(self):
		return self.__getattr__("NbrOfL2TpClients")
	
	@cached_property
	def NbrOfL2TpBuffers(self):
		return self.__getattr__("NbrOfL2TpBuffers")
	
	@cached_property
	def NbrOfECP(self):
		return self.__getattr__("NbrOfECP")
	
	@cached_property
	def NbrOfSSLCP(self):
		return self.__getattr__("NbrOfSSLCP")
	
	@cached_property
	def NbrOfIPSecObjects(self):
		return self.__getattr__("NbrOfIPSecObjects")
	
	@cached_property
	def NbrOfResPoolIpAddresses(self):
		return self.__getattr__("NbrOfResPoolIpAddresses")
	
	@cached_property
	def SslVpnTotalRxBytes(self):
		return self.__getattr__("SslVpnTotalRxBytes")
	
	@cached_property
	def SslVpnTotalTxBytes(self):
		return self.__getattr__("SslVpnTotalTxBytes")
	
	@cached_property
	def NbrOfSslVpnSessions(self):
		return self.__getattr__("NbrOfSslVpnSessions")
	

class SrvStatusLocalLinksHandler(BaseListGetHandler):
	'''Status of local link profiles in Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvStatusLocalLink entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/stat/local-links".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvStatusLocalLink entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvStatusLocalLink(self, self._groupid, self._srvid)
	

class SrvStatusLocalLink(LazyListEntry):
	'''Status of local link profiles in Secure Server

	Attributes [read-only]
	----------------------
		Name : str
			Link Profile Name
		ConnectionState : int
			Connection State
			Enum Values: 1=Disconnected, 2=Connected, 3=Pending, 4=Timeout
		IncorrectPasswordEntries : int
			Incorrect Password Entries
		Encryption : int
			Encryption
			Enum Values: 0=off, 2=DES, 3=3DES, 4=Blowfish, 5=Blowfish_448, 6=AES128, 7=AES192, 8=AES256, 9=AESCTR128, 10=AESCTR192, 11=AESCTR256, 19=AESGCM128-16-ICV, 21=AESGCM256-16-ICV
		Direction : int
			Direction
			Enum Values: 1=none, 2=Negotiation, 3=Outbound, 4=Inbound
		Uptime : int
			Up Time
		RxBytes : int
			Rx Bytes
		TxBytes : int
			Tx Bytes
		IncomingCalls : int
			Incoming Calls
		IncomingCallsFailed : int
			Incoming Calls failed
		OutgoingCalls : int
			Outgoing Calls
		OutgoingCallsFailed : int
			Outgoing Calls failed
		PortIndex : int
			Port Index
		TimeToLeftDisconnect : int
			Time to left disconnect
		IPAddress : ipv4
			IPv4 Address
		IPAddressV6 : ipv6
			IPv6 Address
		DomainGroupName : str
			Domain Group Name
		FiltergroupName : str
			Filtergroup Name
		NcpPathFinder : int
			NCP Path Finder
			Enum Values: 0=inactive, 1=Path Finder (V1), 2=Path Finder (V2)
		SeamlessRoamingConnection : int
			Is Seamless Roaming Connection
			Enum Values: 0=inactive, 1=active
		EpSecData1 : str
			Endpoint Security User-defined parameter 1
		EpSecData2 : str
			Endpoint Security User-defined parameter 2
		EpSecData3 : str
			Endpoint Security User-defined parameter 3
	'''

	def __init__(self, getHandler, groupid, srvid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def ConnectionState(self):
		return self.__getattr__("ConnectionState")
	
	@cached_property
	def IncorrectPasswordEntries(self):
		return self.__getattr__("IncorrectPasswordEntries")
	
	@cached_property
	def Encryption(self):
		return self.__getattr__("Encryption")
	
	@cached_property
	def Direction(self):
		return self.__getattr__("Direction")
	
	@cached_property
	def Uptime(self):
		return self.__getattr__("Uptime")
	
	@cached_property
	def RxBytes(self):
		return self.__getattr__("RxBytes")
	
	@cached_property
	def TxBytes(self):
		return self.__getattr__("TxBytes")
	
	@cached_property
	def IncomingCalls(self):
		return self.__getattr__("IncomingCalls")
	
	@cached_property
	def IncomingCallsFailed(self):
		return self.__getattr__("IncomingCallsFailed")
	
	@cached_property
	def OutgoingCalls(self):
		return self.__getattr__("OutgoingCalls")
	
	@cached_property
	def OutgoingCallsFailed(self):
		return self.__getattr__("OutgoingCallsFailed")
	
	@cached_property
	def PortIndex(self):
		return self.__getattr__("PortIndex")
	
	@cached_property
	def TimeToLeftDisconnect(self):
		return self.__getattr__("TimeToLeftDisconnect")
	
	@cached_property
	def IPAddress(self):
		return self.__getattr__("IPAddress")
	
	@cached_property
	def IPAddressV6(self):
		return self.__getattr__("IPAddressV6")
	
	@cached_property
	def DomainGroupName(self):
		return self.__getattr__("DomainGroupName")
	
	@cached_property
	def FiltergroupName(self):
		return self.__getattr__("FiltergroupName")
	
	@cached_property
	def NcpPathFinder(self):
		return self.__getattr__("NcpPathFinder")
	
	@cached_property
	def SeamlessRoamingConnection(self):
		return self.__getattr__("SeamlessRoamingConnection")
	
	@cached_property
	def EpSecData1(self):
		return self.__getattr__("EpSecData1")
	
	@cached_property
	def EpSecData2(self):
		return self.__getattr__("EpSecData2")
	
	@cached_property
	def EpSecData3(self):
		return self.__getattr__("EpSecData3")
	

class SrvStatusRadiusLinksHandler(BaseListGetHandler):
	'''Status of RADIUS/LDAP link profiles in Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvStatusRadiusLink entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/stat/radius-links".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvStatusRadiusLink entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvStatusRadiusLink(self, self._groupid, self._srvid)
	

class SrvStatusRadiusLink(LazyListEntry):
	'''Status of RADIUS/LDAP link profiles in Secure Server

	Attributes [read-only]
	----------------------
		Name : str
			Link Profile Name
		ConnectionState : int
			Connection State
			Enum Values: 1=Disconnected, 2=Connected, 3=Pending, 4=Timeout
		IncorrectPasswordEntries : int
			Incorrect Password Entries
		Encryption : int
			Encryption
			Enum Values: 0=off, 2=DES, 3=3DES, 4=Blowfish, 5=Blowfish_448, 6=AES128, 7=AES192, 8=AES256, 9=AESCTR128, 10=AESCTR192, 11=AESCTR256, 19=AESGCM128-16-ICV, 21=AESGCM256-16-ICV
		Direction : int
			Direction
			Enum Values: 1=none, 2=Negotiation, 3=Outbound, 4=Inbound
		Uptime : int
			Up Time
		RxBytes : int
			Rx Bytes
		TxBytes : int
			Tx Bytes
		IncomingCalls : int
			Incoming Calls
		IncomingCallsFailed : int
			Incoming Calls failed
		OutgoingCalls : int
			Outgoing Calls
		OutgoingCallsFailed : int
			Outgoing Calls failed
		PortIndex : int
			Port Index
		TimeToLeftDisconnect : int
			Time to left disconnect
		IPAddress : ipv4
			IPv4 Address
		IPAddressV6 : ipv6
			IPv6 Address
		DomainGroupName : str
			Domain Group Name
		FiltergroupName : str
			Filtergroup Name
		NcpPathFinder : int
			NCP Path Finder
			Enum Values: 0=inactive, 1=Path Finder (V1), 2=Path Finder (V2)
		SeamlessRoamingConnection : int
			Is Seamless Roaming Connection
			Enum Values: 0=inactive, 1=active
		EpSecData1 : str
			Endpoint Security User-defined parameter 1
		EpSecData2 : str
			Endpoint Security User-defined parameter 2
		EpSecData3 : str
			Endpoint Security User-defined parameter 3
	'''

	def __init__(self, getHandler, groupid, srvid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def ConnectionState(self):
		return self.__getattr__("ConnectionState")
	
	@cached_property
	def IncorrectPasswordEntries(self):
		return self.__getattr__("IncorrectPasswordEntries")
	
	@cached_property
	def Encryption(self):
		return self.__getattr__("Encryption")
	
	@cached_property
	def Direction(self):
		return self.__getattr__("Direction")
	
	@cached_property
	def Uptime(self):
		return self.__getattr__("Uptime")
	
	@cached_property
	def RxBytes(self):
		return self.__getattr__("RxBytes")
	
	@cached_property
	def TxBytes(self):
		return self.__getattr__("TxBytes")
	
	@cached_property
	def IncomingCalls(self):
		return self.__getattr__("IncomingCalls")
	
	@cached_property
	def IncomingCallsFailed(self):
		return self.__getattr__("IncomingCallsFailed")
	
	@cached_property
	def OutgoingCalls(self):
		return self.__getattr__("OutgoingCalls")
	
	@cached_property
	def OutgoingCallsFailed(self):
		return self.__getattr__("OutgoingCallsFailed")
	
	@cached_property
	def PortIndex(self):
		return self.__getattr__("PortIndex")
	
	@cached_property
	def TimeToLeftDisconnect(self):
		return self.__getattr__("TimeToLeftDisconnect")
	
	@cached_property
	def IPAddress(self):
		return self.__getattr__("IPAddress")
	
	@cached_property
	def IPAddressV6(self):
		return self.__getattr__("IPAddressV6")
	
	@cached_property
	def DomainGroupName(self):
		return self.__getattr__("DomainGroupName")
	
	@cached_property
	def FiltergroupName(self):
		return self.__getattr__("FiltergroupName")
	
	@cached_property
	def NcpPathFinder(self):
		return self.__getattr__("NcpPathFinder")
	
	@cached_property
	def SeamlessRoamingConnection(self):
		return self.__getattr__("SeamlessRoamingConnection")
	
	@cached_property
	def EpSecData1(self):
		return self.__getattr__("EpSecData1")
	
	@cached_property
	def EpSecData2(self):
		return self.__getattr__("EpSecData2")
	
	@cached_property
	def EpSecData3(self):
		return self.__getattr__("EpSecData3")
	

class SrvStatusBlockedLinksHandler(BaseListGetHandler):
	'''Status of blocked link profiles in Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvStatusBlockedLink entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/stat/blocked-links".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvStatusBlockedLink entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvStatusBlockedLink(self, self._groupid, self._srvid)
	

class SrvStatusBlockedLink(LazyListEntry):
	'''Status of blocked link profiles in Secure Server

	Attributes [read-only]
	----------------------
		Name : str
			Link Profile Name
		BlockedTime : time
			Blocked Time
	'''

	def __init__(self, getHandler, groupid, srvid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def BlockedTime(self):
		return self.__getattr__("BlockedTime")
	

class SrvStatusDomainGroupsHandler(BaseListGetHandler):
	'''Status of domain groups in Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvStatusDomainGroup entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/stat/dom-grps".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvStatusDomainGroup entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvStatusDomainGroup(self, self._groupid, self._srvid)
	

class SrvStatusDomainGroup(LazyListEntry):
	'''Status of domain groups in Secure Server

	Attributes [read-only]
	----------------------
		DomainGroupName : str
			Domain Group Name
		UsedVpnTunnels : int
			Used VPN Tunnels
		VpnGroupLock : int
			VPN Group Lock
			Enum Values: 0=no, 1=yes
		UsedSslVpnCUs : int
			Used SSL VPN CUs
		SslVpnLock : int
			SSL VPN Group Lock
			Enum Values: 0=no, 1=yes
		UserPriority : int
			User Priority
	'''

	def __init__(self, getHandler, groupid, srvid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def DomainGroupName(self):
		return self.__getattr__("DomainGroupName")
	
	@cached_property
	def UsedVpnTunnels(self):
		return self.__getattr__("UsedVpnTunnels")
	
	@cached_property
	def VpnGroupLock(self):
		return self.__getattr__("VpnGroupLock")
	
	@cached_property
	def UsedSslVpnCUs(self):
		return self.__getattr__("UsedSslVpnCUs")
	
	@cached_property
	def SslVpnLock(self):
		return self.__getattr__("SslVpnLock")
	
	@cached_property
	def UserPriority(self):
		return self.__getattr__("UserPriority")
	

class SrvStatusInvalidCertsHandler(BaseListGetHandler):
	'''Status of invalid incoming certificates in Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvStatusInvalidCert entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/stat/invalid-certs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvStatusInvalidCert entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvStatusInvalidCert(self, self._groupid, self._srvid)
	

class SrvStatusInvalidCert(LazyListEntry):
	'''Status of invalid incoming certificates in Secure Server

	Attributes [read-only]
	----------------------
		LoginTime : time
			Login Time
		UserId : str
			User ID
		ErrorCode : int
			Error Code
		Subject : str
			IP Address
		Certificate : cert
			Certificate
	'''

	def __init__(self, getHandler, groupid, srvid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def LoginTime(self):
		return self.__getattr__("LoginTime")
	
	@cached_property
	def UserId(self):
		return self.__getattr__("UserId")
	
	@cached_property
	def ErrorCode(self):
		return self.__getattr__("ErrorCode")
	
	@cached_property
	def Subject(self):
		return self.__getattr__("Subject")
	
	@cached_property
	def Certificate(self):
		return self.__getattr__("Certificate")
	

class SrvStatusSystemServicessHandler(BaseListGetHandler):
	'''Status of system services in Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvStatusSystemServices entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/stat/system-services".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvStatusSystemServices entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvStatusSystemServices(self, self._groupid, self._srvid)
	

class SrvStatusSystemServices(LazyListEntry):
	'''Status of system services in Secure Server

	Attributes [read-only]
	----------------------
		ServiceName : str
			Service Name
		AutoStart : str
			Auto Start
		State : str
			State
		Desc : str
			Description
	'''

	def __init__(self, getHandler, groupid, srvid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def ServiceName(self):
		return self.__getattr__("ServiceName")
	
	@cached_property
	def AutoStart(self):
		return self.__getattr__("AutoStart")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def Desc(self):
		return self.__getattr__("Desc")
	

class SrvLogErrorSystemsHandler(BaseListHandler):
	'''Error / system logs of Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvLogErrorSystems entry object.
	
	Inherited Methods
	-----------------
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/logs/error-system".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvLogErrorSystems entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvLogErrorSystems(self, self._groupid, self._srvid)
	

class SrvLogErrorSystems(ListEntry):
	'''Model SrvLogErrorSystems

	Attributes [writable]
	---------------------
		Id : int
			Id
		LogTime : time
			Log Time
		ErrorNr : int
			Error Nr
		LogText : str
			LogText
	'''

	def __init__(self, getHandler, groupid, srvid):
		ListEntry.__init__(self, getHandler)
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def LogTime(self):
		return self.__getattr__("LogTime")
	
	@cached_property
	def ErrorNr(self):
		return self.__getattr__("ErrorNr")
	
	@cached_property
	def LogText(self):
		return self.__getattr__("LogText")
	

class SrvLogTraceHandler(BaseListHandler):
	'''Trace logs of Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvLogTrace entry object.
	
	Inherited Methods
	-----------------
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/logs/traces".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvLogTrace entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvLogTrace(self, self._groupid, self._srvid)
	

class SrvLogTrace(ListEntry):
	'''Model SrvLogTrace

	Attributes [writable]
	---------------------
		Id : int
			Id
		LogTime : time
			Log Time
		LogText : str
			LogText
	'''

	def __init__(self, getHandler, groupid, srvid):
		ListEntry.__init__(self, getHandler)
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def LogTime(self):
		return self.__getattr__("LogTime")
	
	@cached_property
	def LogText(self):
		return self.__getattr__("LogText")
	

class SrvLogLevelHandler(BaseListUpdateHandler):
	'''Trace log levels of Secure Server

	Methods
	-------
		createEntry()
			Creates a new SrvLogLevel entry object.
	
	Inherited Methods
	-----------------
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/servers/{srvid}/logs/log-levels".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new SrvLogLevel entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return SrvLogLevel(self, self._groupid, self._srvid)
	

class SrvLogLevel(ModifiableListEntry):
	'''Model SrvLogLevel

	Attributes [read-only]
	----------------------
		Process : str
			Process
		Logger : str
			Logger
		ModifiedOn : int
			Modified on

	Attributes [writable]
	---------------------
		LogLevel : int
			Log Level
	'''

	def __init__(self, getHandler, groupid, srvid):
		ModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Process(self):
		return self.__getattr__("Process")
	
	@cached_property
	def Logger(self):
		return self.__getattr__("Logger")
	
	@cached_property
	def LogLevel(self):
		return self.__getattr__("LogLevel")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	

class HAServerTemplatesHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of HA Server Templates

	Methods
	-------
		createEntry()
			Creates a new HAServerTemplate entry object.
	
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
		url = "srv-mgm/{groupid}/ha-templs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new HAServerTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return HAServerTemplate(self, self._groupid)
	

class HAServerTemplate(LazyModifiableListEntry):
	'''Model HAServerTemplate

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by
		ConfiguredIn : str
			Configured in

	Attributes [writable]
	---------------------
		Name : str
			Name
			Parameter Group: General
		ServerType : int
			Server Type
			Parameter Group: General
			Enum Values: 0=NCP Secure HA Server, 2=NCP Virtual HA Secure Server
		AdminPassword : str
			Adminsitrator Password
			Parameter Group: Access Management
		OtherAdmins : sem.arrmifint
			Other Adminsitrators
			Parameter Group: Access Management
		SystemLogSaveToFile : bool
			Write system log into file
		ErrorLogSaveToFile : bool
			Write error log into file
		ConfigLogSaveToFile : bool
			Write config log into file
		StatLogSaveToFile : bool
			Write statistic log into file
		TraceLogSaveToFile : bool
			Write trace log into file
		SystemLogFileSize : int
			Max. system log file size
		ErrorLogFileSize : int
			Max. error log file size
		TraceLogFileSize : int
			Max. trace log file size
		SendSnmpTrapSystemLog : bool
			Send SNMP trap by system log
		SendSnmpTrapErrorLog : bool
			Send SNMP trap by error log
		IgnoreErrNr : str
			Ignore Error Nummer
		SendSysLogsSystem : bool
			Send Syslogs (System Log)
		SysLogHost1System : ipaddr
			1. IP Address Syslog Server (System Log)
		SysLogHost2System : ipaddr
			2. IP Address Syslog Server (System Log)
		SysLogPortSystem : int
			Port Syslog Server (System Log)
		SysLogProtoSystem : int
			Protocol Syslog Server (System Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilitySystem : int
			Syslog Facility (System Log)
		SysLogSeveritySystem : int
			Syslog Severity (System Log)
		SendSysLogsError : bool
			Send Syslogs (Error Log )
		SysLogHost1Error : ipaddr
			1. IP Address Syslog Server (Error Log)
		SysLogHost2Error : ipaddr
			2. IP Address Syslog Server (Error Log)
		SysLogPortError : int
			Port Syslog Server (Error Log)
		SysLogProtoError : int
			Protcol Syslog Server (Error Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilityError : int
			Syslog Facility (Error Log)
		SysLogSeverityError : int
			Syslog Severity (Error Log)
		SendSysLogsConfig : bool
			Send Syslogs (Configuration Log )
		SysLogHost1Config : ipaddr
			1. IP Address Syslog Server (Configuration Log)
		SysLogHost2Config : ipaddr
			2. IP Address Syslog Server (Configuration Log)
		SysLogPortConfig : int
			Port Syslog Server (Configuration Log)
		SysLogProtoConfig : int
			Protocol Syslog Server (Configuration Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilityConfig : int
			Syslog Facility (Configuration Log)
		SysLogSeverityConfig : int
			Syslog Severity (Configuration Log)
		SendSysLogsStat : bool
			Send Syslogs (Statistic Log)
		SysLogHost1Stat : ipaddr
			1. IP Address Syslog Server (Statistic Log)
		SysLogHost2Stat : ipaddr
			2. IP Address Syslog Server (Statistic Log)
		SysLogPortStat : int
			Port Syslog Server (Statistic Log)
		SysLogProtoStat : int
			Protocol Syslog Server (Statistic Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilityStat : int
			Syslog Facility (Statistic Log)
		SysLogSeverityStat : int
			Syslog Severity (Statistic Log)
		SendSysLogsTrace : bool
			Send Syslogs (Trace Log)
		SysLogHost1Trace : ipaddr
			1. IP Address Syslog Server (Trace Log)
		SysLogHost2Trace : ipaddr
			2. IP Address Syslog Server (Trace Log)
		SysLogPortTrace : int
			Port Syslog Server (Trace Log)
		SysLogProtoTrace : int
			Protocol Syslog Server (Trace Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilityTrace : int
			Syslog Facility (Trace Log)
		SysLogSeverityTrace : int
			Syslog Severity (Trace Log)
		DveSecret : str
			DVE Secret
		IPAddrLocHASrv : ipv4
			IP Address local HA Server
		IPAddrOtherHASrv : ipv4
			IP Address other HA Server
		HAServerType : int
			HA Server Type
			Enum Values: 0=Primary HA Server, 1=Secondary HA Server
		ThrougputVpnFactor : int
			Throughput VPN Rate Factor
		ActiveVpnTunnelFactor : int
			Active VPN Tunnel Factor
		ThrougputSslVpnFactor : int
			Througput SSL VPN Rate Factor
		ActiveSslVpnTunnelFactor : int
			Active SSL VPN Tunnel Factor
		ResPoolIpAddrFactor : int
			Res. Pool IP Addresses Factor
		CpuLoadFactor : int
			CPU Load Factor
		PollingTimeInterval : int
			Polling Time Interval
		AlternativeIPSecPort : int
			Alternative IPSec Port
		ForceSingleConnection : bool
			Force single VPN connection
		HoldMasterMode : int
			Hold Master Mode
			Enum Values: 0=inactive, 1=active
		AllPrivIpAddrAsIntNet : bool
			Define all private IP Addresses as internal net
		BeginInternalNet1 : ipaddr
			Begin 1. Internal Network
		EndInternalNet1 : ipaddr
			End 1. Internal Network
		BeginInternalNet2 : ipaddr
			Begin 2. Internal Network
		EndInternalNet2 : ipaddr
			End 2. Internal Network
		BeginInternalNet3 : ipaddr
			Begin 3. Internal Network
		EndInternalNet3 : ipaddr
			End 3. Internal Network
		BeginInternalNet4 : ipaddr
			Begin 4. Internal Network
		EndInternalNet4 : ipaddr
			End 4. Internal Network
		BeginInternalNet5 : ipaddr
			Begin 5. Internal Network
		EndInternalNet5 : ipaddr
			End 5. Internal Network
		ExtIpCheck : str
			IP Availability Check (External)
		IntIpCheck : str
			IP Availability Check (Internal)
		ServerSpecific : str[]
			Server Specific Parameters
			Parameter Group: Server Parameters

	Sub-Handlers
	------------
		templHaSrvVpnGWs
			Access TemplHaSrvVpnGWsHandler
		templHaSrvDomainGroups
			Access TemplHaSrvDomainGroupsHandler
	'''

	def __init__(self, getHandler, groupid):
		LazyModifiableListEntry.__init__(self, getHandler)
		self._groupid = groupid
		self._api = getHandler._api
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def ServerType(self):
		return self.__getattr__("ServerType")
	
	@cached_property
	def AdminPassword(self):
		return self.__getattr__("AdminPassword")
	
	@cached_property
	def OtherAdmins(self):
		return self.__getattr__("OtherAdmins")
	
	@cached_property
	def SystemLogSaveToFile(self):
		return self.__getattr__("SystemLogSaveToFile")
	
	@cached_property
	def ErrorLogSaveToFile(self):
		return self.__getattr__("ErrorLogSaveToFile")
	
	@cached_property
	def ConfigLogSaveToFile(self):
		return self.__getattr__("ConfigLogSaveToFile")
	
	@cached_property
	def StatLogSaveToFile(self):
		return self.__getattr__("StatLogSaveToFile")
	
	@cached_property
	def TraceLogSaveToFile(self):
		return self.__getattr__("TraceLogSaveToFile")
	
	@cached_property
	def SystemLogFileSize(self):
		return self.__getattr__("SystemLogFileSize")
	
	@cached_property
	def ErrorLogFileSize(self):
		return self.__getattr__("ErrorLogFileSize")
	
	@cached_property
	def TraceLogFileSize(self):
		return self.__getattr__("TraceLogFileSize")
	
	@cached_property
	def SendSnmpTrapSystemLog(self):
		return self.__getattr__("SendSnmpTrapSystemLog")
	
	@cached_property
	def SendSnmpTrapErrorLog(self):
		return self.__getattr__("SendSnmpTrapErrorLog")
	
	@cached_property
	def IgnoreErrNr(self):
		return self.__getattr__("IgnoreErrNr")
	
	@cached_property
	def SendSysLogsSystem(self):
		return self.__getattr__("SendSysLogsSystem")
	
	@cached_property
	def SysLogHost1System(self):
		return self.__getattr__("SysLogHost1System")
	
	@cached_property
	def SysLogHost2System(self):
		return self.__getattr__("SysLogHost2System")
	
	@cached_property
	def SysLogPortSystem(self):
		return self.__getattr__("SysLogPortSystem")
	
	@cached_property
	def SysLogProtoSystem(self):
		return self.__getattr__("SysLogProtoSystem")
	
	@cached_property
	def SysLogFacilitySystem(self):
		return self.__getattr__("SysLogFacilitySystem")
	
	@cached_property
	def SysLogSeveritySystem(self):
		return self.__getattr__("SysLogSeveritySystem")
	
	@cached_property
	def SendSysLogsError(self):
		return self.__getattr__("SendSysLogsError")
	
	@cached_property
	def SysLogHost1Error(self):
		return self.__getattr__("SysLogHost1Error")
	
	@cached_property
	def SysLogHost2Error(self):
		return self.__getattr__("SysLogHost2Error")
	
	@cached_property
	def SysLogPortError(self):
		return self.__getattr__("SysLogPortError")
	
	@cached_property
	def SysLogProtoError(self):
		return self.__getattr__("SysLogProtoError")
	
	@cached_property
	def SysLogFacilityError(self):
		return self.__getattr__("SysLogFacilityError")
	
	@cached_property
	def SysLogSeverityError(self):
		return self.__getattr__("SysLogSeverityError")
	
	@cached_property
	def SendSysLogsConfig(self):
		return self.__getattr__("SendSysLogsConfig")
	
	@cached_property
	def SysLogHost1Config(self):
		return self.__getattr__("SysLogHost1Config")
	
	@cached_property
	def SysLogHost2Config(self):
		return self.__getattr__("SysLogHost2Config")
	
	@cached_property
	def SysLogPortConfig(self):
		return self.__getattr__("SysLogPortConfig")
	
	@cached_property
	def SysLogProtoConfig(self):
		return self.__getattr__("SysLogProtoConfig")
	
	@cached_property
	def SysLogFacilityConfig(self):
		return self.__getattr__("SysLogFacilityConfig")
	
	@cached_property
	def SysLogSeverityConfig(self):
		return self.__getattr__("SysLogSeverityConfig")
	
	@cached_property
	def SendSysLogsStat(self):
		return self.__getattr__("SendSysLogsStat")
	
	@cached_property
	def SysLogHost1Stat(self):
		return self.__getattr__("SysLogHost1Stat")
	
	@cached_property
	def SysLogHost2Stat(self):
		return self.__getattr__("SysLogHost2Stat")
	
	@cached_property
	def SysLogPortStat(self):
		return self.__getattr__("SysLogPortStat")
	
	@cached_property
	def SysLogProtoStat(self):
		return self.__getattr__("SysLogProtoStat")
	
	@cached_property
	def SysLogFacilityStat(self):
		return self.__getattr__("SysLogFacilityStat")
	
	@cached_property
	def SysLogSeverityStat(self):
		return self.__getattr__("SysLogSeverityStat")
	
	@cached_property
	def SendSysLogsTrace(self):
		return self.__getattr__("SendSysLogsTrace")
	
	@cached_property
	def SysLogHost1Trace(self):
		return self.__getattr__("SysLogHost1Trace")
	
	@cached_property
	def SysLogHost2Trace(self):
		return self.__getattr__("SysLogHost2Trace")
	
	@cached_property
	def SysLogPortTrace(self):
		return self.__getattr__("SysLogPortTrace")
	
	@cached_property
	def SysLogProtoTrace(self):
		return self.__getattr__("SysLogProtoTrace")
	
	@cached_property
	def SysLogFacilityTrace(self):
		return self.__getattr__("SysLogFacilityTrace")
	
	@cached_property
	def SysLogSeverityTrace(self):
		return self.__getattr__("SysLogSeverityTrace")
	
	@cached_property
	def DveSecret(self):
		return self.__getattr__("DveSecret")
	
	@cached_property
	def IPAddrLocHASrv(self):
		return self.__getattr__("IPAddrLocHASrv")
	
	@cached_property
	def IPAddrOtherHASrv(self):
		return self.__getattr__("IPAddrOtherHASrv")
	
	@cached_property
	def HAServerType(self):
		return self.__getattr__("HAServerType")
	
	@cached_property
	def ThrougputVpnFactor(self):
		return self.__getattr__("ThrougputVpnFactor")
	
	@cached_property
	def ActiveVpnTunnelFactor(self):
		return self.__getattr__("ActiveVpnTunnelFactor")
	
	@cached_property
	def ThrougputSslVpnFactor(self):
		return self.__getattr__("ThrougputSslVpnFactor")
	
	@cached_property
	def ActiveSslVpnTunnelFactor(self):
		return self.__getattr__("ActiveSslVpnTunnelFactor")
	
	@cached_property
	def ResPoolIpAddrFactor(self):
		return self.__getattr__("ResPoolIpAddrFactor")
	
	@cached_property
	def CpuLoadFactor(self):
		return self.__getattr__("CpuLoadFactor")
	
	@cached_property
	def PollingTimeInterval(self):
		return self.__getattr__("PollingTimeInterval")
	
	@cached_property
	def AlternativeIPSecPort(self):
		return self.__getattr__("AlternativeIPSecPort")
	
	@cached_property
	def ForceSingleConnection(self):
		return self.__getattr__("ForceSingleConnection")
	
	@cached_property
	def HoldMasterMode(self):
		return self.__getattr__("HoldMasterMode")
	
	@cached_property
	def AllPrivIpAddrAsIntNet(self):
		return self.__getattr__("AllPrivIpAddrAsIntNet")
	
	@cached_property
	def BeginInternalNet1(self):
		return self.__getattr__("BeginInternalNet1")
	
	@cached_property
	def EndInternalNet1(self):
		return self.__getattr__("EndInternalNet1")
	
	@cached_property
	def BeginInternalNet2(self):
		return self.__getattr__("BeginInternalNet2")
	
	@cached_property
	def EndInternalNet2(self):
		return self.__getattr__("EndInternalNet2")
	
	@cached_property
	def BeginInternalNet3(self):
		return self.__getattr__("BeginInternalNet3")
	
	@cached_property
	def EndInternalNet3(self):
		return self.__getattr__("EndInternalNet3")
	
	@cached_property
	def BeginInternalNet4(self):
		return self.__getattr__("BeginInternalNet4")
	
	@cached_property
	def EndInternalNet4(self):
		return self.__getattr__("EndInternalNet4")
	
	@cached_property
	def BeginInternalNet5(self):
		return self.__getattr__("BeginInternalNet5")
	
	@cached_property
	def EndInternalNet5(self):
		return self.__getattr__("EndInternalNet5")
	
	@cached_property
	def ExtIpCheck(self):
		return self.__getattr__("ExtIpCheck")
	
	@cached_property
	def IntIpCheck(self):
		return self.__getattr__("IntIpCheck")
	
	@cached_property
	def ServerSpecific(self):
		return self.__getattr__("ServerSpecific")
	
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
	def templHaSrvVpnGWs(self):
		'''Returns handler to access TemplHaSrvVpnGWs'''
		return TemplHaSrvVpnGWsHandler(self._api, self._groupid, self.Id)

	@cached_property
	def templHaSrvDomainGroups(self):
		'''Returns handler to access TemplHaSrvDomainGroups'''
		return TemplHaSrvDomainGroupsHandler(self._api, self._groupid, self.Id)
	

class TemplHaSrvVpnGWsHandler(BaseListGetHandler):
	'''Configuration of VPN gateways in HA Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplHaSrvVpnGW entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/ha-templs/{templid}/vpngws".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplHaSrvVpnGW entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplHaSrvVpnGW(self, self._groupid, self._templid)
	

class TemplHaSrvVpnGW(LazyListEntry):
	'''Configuration of VPN gateways in HA Server Template

	Attributes [writable]
	---------------------
		Name : str
			Name
		State : bool
			State
		LanIPAddr : ipv4
			LAN IP Address
		VpnMode : int
			VPN Mode
			Enum Values: 0=native VPN, 1=only SSL VPN, 2=both, 3=only VRRP
		FailsafeType : int
			Failsafe Type
			Enum Values: 0=Master, 1=Backup
		VrrpMode : int
			VRRP Mode
			Enum Values: 0=Disabled, 1=VRRP Master, 2=VRRP Backup
		VRRPId : int
			VRRP Id
		ExtVpnIpAddr : ipv4
			VPN Endpoint (External)
		ExtVpnIpAddrV6 : ipv6
			VPN Endpoint (External)
		ExtDnsName : str
			DNS Name (External)
		IntVpnIpAddr : ipv4
			VPN Endpoint (Internal)
		IntVpnIpAddrV6 : ipv6
			VPN Endpoint (Internal)
		IntDnsName : str
			DNS Name (Internal)
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def LanIPAddr(self):
		return self.__getattr__("LanIPAddr")
	
	@cached_property
	def VpnMode(self):
		return self.__getattr__("VpnMode")
	
	@cached_property
	def FailsafeType(self):
		return self.__getattr__("FailsafeType")
	
	@cached_property
	def VrrpMode(self):
		return self.__getattr__("VrrpMode")
	
	@cached_property
	def VRRPId(self):
		return self.__getattr__("VRRPId")
	
	@cached_property
	def ExtVpnIpAddr(self):
		return self.__getattr__("ExtVpnIpAddr")
	
	@cached_property
	def ExtVpnIpAddrV6(self):
		return self.__getattr__("ExtVpnIpAddrV6")
	
	@cached_property
	def ExtDnsName(self):
		return self.__getattr__("ExtDnsName")
	
	@cached_property
	def IntVpnIpAddr(self):
		return self.__getattr__("IntVpnIpAddr")
	
	@cached_property
	def IntVpnIpAddrV6(self):
		return self.__getattr__("IntVpnIpAddrV6")
	
	@cached_property
	def IntDnsName(self):
		return self.__getattr__("IntDnsName")
	

class TemplHaSrvDomainGroupsHandler(BaseListGetHandler):
	'''Configuration of domain groups in HA Server Template

	Methods
	-------
		createEntry()
			Creates a new TemplHaSrvDomainGroup entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, templid):
		url = "srv-mgm/{groupid}/ha-templs/{templid}/dom-grps".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._templid = templid

	def createEntry(self):
		'''Creates a new TemplHaSrvDomainGroup entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return TemplHaSrvDomainGroup(self, self._groupid, self._templid)
	

class TemplHaSrvDomainGroup(LazyListEntry):
	'''Configuration of domain groups in HA Server Template

	Attributes [writable]
	---------------------
		Name : str
			Name
		MaxVpnTunnels : int
			Max. Number of VPN Tunnels
		MaxSslVpnCUs : int
			Max. Number of SSL VPN CUs
		UserPriority : int
			Priority
	'''

	def __init__(self, getHandler, groupid, templid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def MaxVpnTunnels(self):
		return self.__getattr__("MaxVpnTunnels")
	
	@cached_property
	def MaxSslVpnCUs(self):
		return self.__getattr__("MaxSslVpnCUs")
	
	@cached_property
	def UserPriority(self):
		return self.__getattr__("UserPriority")
	

class HAServersHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of HA Servers

	Methods
	-------
		createEntry()
			Creates a new HAServer entry object.
	
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
		url = "srv-mgm/{groupid}/ha-srvs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new HAServer entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return HAServer(self, self._groupid)
	

class HAServer(LazyModifiableListEntry):
	'''Model HAServer

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : str
			Modified by
		ConfiguredIn : str
			Configured in

	Attributes [writable]
	---------------------
		Name : str
			Name
			Parameter Group: General
		Template : uintkey
			Template
			Parameter Group: General
		AdminPassword : str
			Adminsitrator Password
			Parameter Group: Access Management
		OtherAdmins : sem.arrmifint
			Other Adminsitrators
			Parameter Group: Access Management
		SystemLogSaveToFile : bool
			Write system log into file
		ErrorLogSaveToFile : bool
			Write error log into file
		ConfigLogSaveToFile : bool
			Write config log into file
		StatLogSaveToFile : bool
			Write statistic log into file
		TraceLogSaveToFile : bool
			Write trace log into file
		SystemLogFileSize : int
			Max. system log file size
		ErrorLogFileSize : int
			Max. error log file size
		TraceLogFileSize : int
			Max. trace log file size
		SendSnmpTrapSystemLog : bool
			Send SNMP trap by system log
		SendSnmpTrapErrorLog : bool
			Send SNMP trap by error log
		IgnoreErrNr : str
			Ignore Error Nummer
		SendSysLogsSystem : bool
			Send Syslogs (System Log)
		SysLogHost1System : ipaddr
			1. IP Address Syslog Server (System Log)
		SysLogHost2System : ipaddr
			2. IP Address Syslog Server (System Log)
		SysLogPortSystem : int
			Port Syslog Server (System Log)
		SysLogProtoSystem : int
			Protocol Syslog Server (System Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilitySystem : int
			Syslog Facility (System Log)
		SysLogSeveritySystem : int
			Syslog Severity (System Log)
		SendSysLogsError : bool
			Send Syslogs (Error Log )
		SysLogHost1Error : ipaddr
			1. IP Address Syslog Server (Error Log)
		SysLogHost2Error : ipaddr
			2. IP Address Syslog Server (Error Log)
		SysLogPortError : int
			Port Syslog Server (Error Log)
		SysLogProtoError : int
			Protcol Syslog Server (Error Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilityError : int
			Syslog Facility (Error Log)
		SysLogSeverityError : int
			Syslog Severity (Error Log)
		SendSysLogsConfig : bool
			Send Syslogs (Configuration Log )
		SysLogHost1Config : ipaddr
			1. IP Address Syslog Server (Configuration Log)
		SysLogHost2Config : ipaddr
			2. IP Address Syslog Server (Configuration Log)
		SysLogPortConfig : int
			Port Syslog Server (Configuration Log)
		SysLogProtoConfig : int
			Protocol Syslog Server (Configuration Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilityConfig : int
			Syslog Facility (Configuration Log)
		SysLogSeverityConfig : int
			Syslog Severity (Configuration Log)
		SendSysLogsStat : bool
			Send Syslogs (Statistic Log)
		SysLogHost1Stat : ipaddr
			1. IP Address Syslog Server (Statistic Log)
		SysLogHost2Stat : ipaddr
			2. IP Address Syslog Server (Statistic Log)
		SysLogPortStat : int
			Port Syslog Server (Statistic Log)
		SysLogProtoStat : int
			Protocol Syslog Server (Statistic Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilityStat : int
			Syslog Facility (Statistic Log)
		SysLogSeverityStat : int
			Syslog Severity (Statistic Log)
		SendSysLogsTrace : bool
			Send Syslogs (Trace Log)
		SysLogHost1Trace : ipaddr
			1. IP Address Syslog Server (Trace Log)
		SysLogHost2Trace : ipaddr
			2. IP Address Syslog Server (Trace Log)
		SysLogPortTrace : int
			Port Syslog Server (Trace Log)
		SysLogProtoTrace : int
			Protocol Syslog Server (Trace Log)
			Enum Values: 0=UDP, 1=TCP
		SysLogFacilityTrace : int
			Syslog Facility (Trace Log)
		SysLogSeverityTrace : int
			Syslog Severity (Trace Log)

	Methods
	-------
		generate()
			Generates this HA Server configuration
		set_authcode(Authcode)
			Sets the authentication code of the Secure Server
		reset_authcode()
			Resets the authentication code of the Secure Server
	'''

	def __init__(self, getHandler, groupid):
		LazyModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def Template(self):
		return self.__getattr__("Template")
	
	@cached_property
	def AdminPassword(self):
		return self.__getattr__("AdminPassword")
	
	@cached_property
	def OtherAdmins(self):
		return self.__getattr__("OtherAdmins")
	
	@cached_property
	def SystemLogSaveToFile(self):
		return self.__getattr__("SystemLogSaveToFile")
	
	@cached_property
	def ErrorLogSaveToFile(self):
		return self.__getattr__("ErrorLogSaveToFile")
	
	@cached_property
	def ConfigLogSaveToFile(self):
		return self.__getattr__("ConfigLogSaveToFile")
	
	@cached_property
	def StatLogSaveToFile(self):
		return self.__getattr__("StatLogSaveToFile")
	
	@cached_property
	def TraceLogSaveToFile(self):
		return self.__getattr__("TraceLogSaveToFile")
	
	@cached_property
	def SystemLogFileSize(self):
		return self.__getattr__("SystemLogFileSize")
	
	@cached_property
	def ErrorLogFileSize(self):
		return self.__getattr__("ErrorLogFileSize")
	
	@cached_property
	def TraceLogFileSize(self):
		return self.__getattr__("TraceLogFileSize")
	
	@cached_property
	def SendSnmpTrapSystemLog(self):
		return self.__getattr__("SendSnmpTrapSystemLog")
	
	@cached_property
	def SendSnmpTrapErrorLog(self):
		return self.__getattr__("SendSnmpTrapErrorLog")
	
	@cached_property
	def IgnoreErrNr(self):
		return self.__getattr__("IgnoreErrNr")
	
	@cached_property
	def SendSysLogsSystem(self):
		return self.__getattr__("SendSysLogsSystem")
	
	@cached_property
	def SysLogHost1System(self):
		return self.__getattr__("SysLogHost1System")
	
	@cached_property
	def SysLogHost2System(self):
		return self.__getattr__("SysLogHost2System")
	
	@cached_property
	def SysLogPortSystem(self):
		return self.__getattr__("SysLogPortSystem")
	
	@cached_property
	def SysLogProtoSystem(self):
		return self.__getattr__("SysLogProtoSystem")
	
	@cached_property
	def SysLogFacilitySystem(self):
		return self.__getattr__("SysLogFacilitySystem")
	
	@cached_property
	def SysLogSeveritySystem(self):
		return self.__getattr__("SysLogSeveritySystem")
	
	@cached_property
	def SendSysLogsError(self):
		return self.__getattr__("SendSysLogsError")
	
	@cached_property
	def SysLogHost1Error(self):
		return self.__getattr__("SysLogHost1Error")
	
	@cached_property
	def SysLogHost2Error(self):
		return self.__getattr__("SysLogHost2Error")
	
	@cached_property
	def SysLogPortError(self):
		return self.__getattr__("SysLogPortError")
	
	@cached_property
	def SysLogProtoError(self):
		return self.__getattr__("SysLogProtoError")
	
	@cached_property
	def SysLogFacilityError(self):
		return self.__getattr__("SysLogFacilityError")
	
	@cached_property
	def SysLogSeverityError(self):
		return self.__getattr__("SysLogSeverityError")
	
	@cached_property
	def SendSysLogsConfig(self):
		return self.__getattr__("SendSysLogsConfig")
	
	@cached_property
	def SysLogHost1Config(self):
		return self.__getattr__("SysLogHost1Config")
	
	@cached_property
	def SysLogHost2Config(self):
		return self.__getattr__("SysLogHost2Config")
	
	@cached_property
	def SysLogPortConfig(self):
		return self.__getattr__("SysLogPortConfig")
	
	@cached_property
	def SysLogProtoConfig(self):
		return self.__getattr__("SysLogProtoConfig")
	
	@cached_property
	def SysLogFacilityConfig(self):
		return self.__getattr__("SysLogFacilityConfig")
	
	@cached_property
	def SysLogSeverityConfig(self):
		return self.__getattr__("SysLogSeverityConfig")
	
	@cached_property
	def SendSysLogsStat(self):
		return self.__getattr__("SendSysLogsStat")
	
	@cached_property
	def SysLogHost1Stat(self):
		return self.__getattr__("SysLogHost1Stat")
	
	@cached_property
	def SysLogHost2Stat(self):
		return self.__getattr__("SysLogHost2Stat")
	
	@cached_property
	def SysLogPortStat(self):
		return self.__getattr__("SysLogPortStat")
	
	@cached_property
	def SysLogProtoStat(self):
		return self.__getattr__("SysLogProtoStat")
	
	@cached_property
	def SysLogFacilityStat(self):
		return self.__getattr__("SysLogFacilityStat")
	
	@cached_property
	def SysLogSeverityStat(self):
		return self.__getattr__("SysLogSeverityStat")
	
	@cached_property
	def SendSysLogsTrace(self):
		return self.__getattr__("SendSysLogsTrace")
	
	@cached_property
	def SysLogHost1Trace(self):
		return self.__getattr__("SysLogHost1Trace")
	
	@cached_property
	def SysLogHost2Trace(self):
		return self.__getattr__("SysLogHost2Trace")
	
	@cached_property
	def SysLogPortTrace(self):
		return self.__getattr__("SysLogPortTrace")
	
	@cached_property
	def SysLogProtoTrace(self):
		return self.__getattr__("SysLogProtoTrace")
	
	@cached_property
	def SysLogFacilityTrace(self):
		return self.__getattr__("SysLogFacilityTrace")
	
	@cached_property
	def SysLogSeverityTrace(self):
		return self.__getattr__("SysLogSeverityTrace")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	
	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
	
	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")
			
	def generate(self):
		'''Generates this HA Server configuration'''
		return self._callMethod('/generate')
			
	def set_authcode(self, Authcode):
		'''Sets the authentication code of the Secure Server
			Authcode : str
				
		'''
		return self._callMethod('/set-authcode', Authcode=Authcode)
			
	def reset_authcode(self):
		'''Resets the authentication code of the Secure Server'''
		return self._callMethod('/reset-authcode')
	

class HaSrvStatusHaServerHandler(BaseGetHandler):
	'''Status of the HA Server

	Methods
	-------
		createEntry()
			Creates a new HaSrvStatusHaServer entry object.
	
	Inherited Methods
	-----------------
		get (BaseGetHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/ha-srvs/{srvid}/stat/general".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new HaSrvStatusHaServer entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return HaSrvStatusHaServer(self, self._groupid, self._srvid)
	

class HaSrvStatusHaServer(BaseEntry):
	'''Status of the HA Server

	Attributes [writable]
	---------------------
		VpnTunnelsUsed : int
			Total VPN Tunnels in use
		VpnTunnelsUsedPersent : int
			Total VPN Tunnels in use (%)
		VpnNbrOfGwFor : int
			Number of Gateways for VPN
		SslVpnUsersUsed : int
			Total SSL VPN Concurrent Users in use
		SslVpnUsersUsedPersent : int
			Total SSL VPN concurrent users in use (%)
		SslVpnNbrOfGwFor : int
			Number of Gateways for SSL VPN
		OnlineState2HaSrv : int
			State of other HA Server
			Enum Values: 0=Offline, 1=Online
	'''

	def __init__(self, getHandler, groupid, srvid):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def VpnTunnelsUsed(self):
		return self.__getattr__("VpnTunnelsUsed")
	
	@cached_property
	def VpnTunnelsUsedPersent(self):
		return self.__getattr__("VpnTunnelsUsedPersent")
	
	@cached_property
	def VpnNbrOfGwFor(self):
		return self.__getattr__("VpnNbrOfGwFor")
	
	@cached_property
	def SslVpnUsersUsed(self):
		return self.__getattr__("SslVpnUsersUsed")
	
	@cached_property
	def SslVpnUsersUsedPersent(self):
		return self.__getattr__("SslVpnUsersUsedPersent")
	
	@cached_property
	def SslVpnNbrOfGwFor(self):
		return self.__getattr__("SslVpnNbrOfGwFor")
	
	@cached_property
	def OnlineState2HaSrv(self):
		return self.__getattr__("OnlineState2HaSrv")
	

class HaSrvStatusVpnGWsHandler(BaseListGetHandler):
	'''Status of VPN gateways in HA Server

	Methods
	-------
		createEntry()
			Creates a new HaSrvStatusVpnGW entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/ha-srvs/{srvid}/stat/vpngws".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new HaSrvStatusVpnGW entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return HaSrvStatusVpnGW(self, self._groupid, self._srvid)
	

class HaSrvStatusVpnGW(LazyListEntry):
	'''Status of VPN gateways in HA Server

	Attributes [writable]
	---------------------
		Name : str
			Name
		State : bool
			State
		LanIPAddr : ipv4
			LAN IP Address
		VpnMode : int
			VPN Mode
			Enum Values: 0=native VPN, 1=only SSL VPN, 2=both, 3=only VRRP
		FailsafeType : int
			Failsafe Type
			Enum Values: 0=Master, 1=Backup
		VrrpMode : int
			VRRP Mode
			Enum Values: 0=Disabled, 1=VRRP Master, 2=VRRP Backup
		VRRPId : int
			VRRP Id
		ExtVpnIpAddr : ipv4
			VPN Endpoint (External)
		ExtVpnIpAddrV6 : ipv6
			VPN Endpoint (External)
		ExtDnsName : str
			DNS Name (External)
		IntVpnIpAddr : ipv4
			VPN Endpoint (Internal)
		IntVpnIpAddrV6 : ipv6
			VPN Endpoint (Internal)
		IntDnsName : str
			DNS Name (Internal)
	'''

	def __init__(self, getHandler, groupid, srvid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def State(self):
		return self.__getattr__("State")
	
	@cached_property
	def LanIPAddr(self):
		return self.__getattr__("LanIPAddr")
	
	@cached_property
	def VpnMode(self):
		return self.__getattr__("VpnMode")
	
	@cached_property
	def FailsafeType(self):
		return self.__getattr__("FailsafeType")
	
	@cached_property
	def VrrpMode(self):
		return self.__getattr__("VrrpMode")
	
	@cached_property
	def VRRPId(self):
		return self.__getattr__("VRRPId")
	
	@cached_property
	def ExtVpnIpAddr(self):
		return self.__getattr__("ExtVpnIpAddr")
	
	@cached_property
	def ExtVpnIpAddrV6(self):
		return self.__getattr__("ExtVpnIpAddrV6")
	
	@cached_property
	def ExtDnsName(self):
		return self.__getattr__("ExtDnsName")
	
	@cached_property
	def IntVpnIpAddr(self):
		return self.__getattr__("IntVpnIpAddr")
	
	@cached_property
	def IntVpnIpAddrV6(self):
		return self.__getattr__("IntVpnIpAddrV6")
	
	@cached_property
	def IntDnsName(self):
		return self.__getattr__("IntDnsName")
	

class HaSrvStatusDomainGroupsHandler(BaseListGetHandler):
	'''Status of domain groups in HA Server

	Methods
	-------
		createEntry()
			Creates a new HaSrvStatusDomainGroup entry object.
	
	Inherited Methods
	-----------------
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/ha-srvs/{srvid}/stat/dom-grps".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new HaSrvStatusDomainGroup entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return HaSrvStatusDomainGroup(self, self._groupid, self._srvid)
	

class HaSrvStatusDomainGroup(LazyListEntry):
	'''Status of domain groups in HA Server

	Attributes [writable]
	---------------------
		Name : str
			Name
		VpnTunnels : int
			Number of VPN Tunnels
		SslVpnCUs : int
			Number of SSL VPN CUs
		VpnLocked : int
			VPN Group Lock
			Enum Values: 0=no, 1=yes
		SslVpnLocked : int
			SSL VPN Group Lock
			Enum Values: 0=no, 1=yes
	'''

	def __init__(self, getHandler, groupid, srvid):
		LazyListEntry.__init__(self, getHandler)
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	
	@cached_property
	def VpnTunnels(self):
		return self.__getattr__("VpnTunnels")
	
	@cached_property
	def SslVpnCUs(self):
		return self.__getattr__("SslVpnCUs")
	
	@cached_property
	def VpnLocked(self):
		return self.__getattr__("VpnLocked")
	
	@cached_property
	def SslVpnLocked(self):
		return self.__getattr__("SslVpnLocked")
	

class HaSrvLogErrorSystemsHandler(BaseListHandler):
	'''Error / system logs of HA Server

	Methods
	-------
		createEntry()
			Creates a new HaSrvLogErrorSystems entry object.
	
	Inherited Methods
	-----------------
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/ha-srvs/{srvid}/logs/error-system".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new HaSrvLogErrorSystems entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return HaSrvLogErrorSystems(self, self._groupid, self._srvid)
	

class HaSrvLogErrorSystems(ListEntry):
	'''Model HaSrvLogErrorSystems

	Attributes [writable]
	---------------------
		Id : int
			Id
		LogTime : time
			Log Time
		ErrorNr : int
			Error Nr
		LogText : str
			LogText
	'''

	def __init__(self, getHandler, groupid, srvid):
		ListEntry.__init__(self, getHandler)
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def LogTime(self):
		return self.__getattr__("LogTime")
	
	@cached_property
	def ErrorNr(self):
		return self.__getattr__("ErrorNr")
	
	@cached_property
	def LogText(self):
		return self.__getattr__("LogText")
	

class HaSrvLogTraceHandler(BaseListHandler):
	'''Trace logs of HA Server

	Methods
	-------
		createEntry()
			Creates a new HaSrvLogTrace entry object.
	
	Inherited Methods
	-----------------
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/ha-srvs/{srvid}/logs/traces".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new HaSrvLogTrace entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return HaSrvLogTrace(self, self._groupid, self._srvid)
	

class HaSrvLogTrace(ListEntry):
	'''Model HaSrvLogTrace

	Attributes [writable]
	---------------------
		Id : int
			Id
		LogTime : time
			Log Time
		LogText : str
			LogText
	'''

	def __init__(self, getHandler, groupid, srvid):
		ListEntry.__init__(self, getHandler)
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def LogTime(self):
		return self.__getattr__("LogTime")
	
	@cached_property
	def LogText(self):
		return self.__getattr__("LogText")
	

class HaSrvLogLevelHandler(BaseListUpdateHandler):
	'''Trace log levels of HA Server

	Methods
	-------
		createEntry()
			Creates a new HaSrvLogLevel entry object.
	
	Inherited Methods
	-----------------
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, srvid):
		url = "srv-mgm/{groupid}/ha-srvs/{srvid}/logs/log-levels".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._srvid = srvid

	def createEntry(self):
		'''Creates a new HaSrvLogLevel entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return HaSrvLogLevel(self, self._groupid, self._srvid)
	

class HaSrvLogLevel(ModifiableListEntry):
	'''Model HaSrvLogLevel

	Attributes [read-only]
	----------------------
		Process : str
			Process
		Logger : str
			Logger
		ModifiedOn : int
			Modified on

	Attributes [writable]
	---------------------
		LogLevel : int
			Log Level
	'''

	def __init__(self, getHandler, groupid, srvid):
		ModifiableListEntry.__init__(self, getHandler)
	
	@cached_property
	def Process(self):
		return self.__getattr__("Process")
	
	@cached_property
	def Logger(self):
		return self.__getattr__("Logger")
	
	@cached_property
	def LogLevel(self):
		return self.__getattr__("LogLevel")
	
	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")
	


class IpRangeCfg(BaseEntry):
	'''Model IpRangeCfg

	Attributes [writable]
	---------------------
		Begin : ipaddr
			IP Address Begin
		End : ipaddr
			IP Address End
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def Begin(self):
		return self.__getattr__("Begin")
	
	@cached_property
	def End(self):
		return self.__getattr__("End")
	

class AuthenticationCode(BaseEntry):
	'''Data for setting authentication code

	Attributes [writable]
	---------------------
		Authcode : str
			Authentication Code
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def Authcode(self):
		return self.__getattr__("Authcode")
	

class VLANCfg(BaseEntry):
	'''Model VLANCfg

	Attributes [writable]
	---------------------
		VLANID : int
			VLAN ID
		IpAddressDefGw : ipv4
			Default Gateway (VLAN)
		LocalIpAddress : ipv4
			Local IP Address(VLAN)
		NatSslVpnIpAddress : ipv4
			NAT IP Address (SSL VPN)
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def VLANID(self):
		return self.__getattr__("VLANID")
	
	@cached_property
	def IpAddressDefGw(self):
		return self.__getattr__("IpAddressDefGw")
	
	@cached_property
	def LocalIpAddress(self):
		return self.__getattr__("LocalIpAddress")
	
	@cached_property
	def NatSslVpnIpAddress(self):
		return self.__getattr__("NatSslVpnIpAddress")
	

class InsertBase(BaseEntry):
	'''Reponse data from insert

	Attributes [writable]
	---------------------
		Id : int
			REST ID of new entry
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	

class GetIdNameList(BaseEntry):
	'''Model GetIdNameList

	Attributes [writable]
	---------------------
		Id : int
			ID of the entry
		Name : str
			Name of the entry
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def Id(self):
		return self.__getattr__("Id")
	
	@cached_property
	def Name(self):
		return self.__getattr__("Name")
	

class RoutIfNatEntryCfg(BaseEntry):
	'''Model RoutIfNatEntryCfg

	Attributes [writable]
	---------------------
		VpnIpAddressBegin : ipv4
			VPN IP Address Begin
		VpnIpAddressEnd : ipv4
			VPN IP Address End
		LanIpAddressBegin : ipv4
			LAN IP Address Begin
		LanIpAddressEnd : ipv4
			LAN IP Address End
		ArpResponse : int
			ARP Responce
			Enum Values: 0=On Nat, 1=On Connect, 2=Always
		Timeout : int
			Timeout
		Description : str
			Description
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def VpnIpAddressBegin(self):
		return self.__getattr__("VpnIpAddressBegin")
	
	@cached_property
	def VpnIpAddressEnd(self):
		return self.__getattr__("VpnIpAddressEnd")
	
	@cached_property
	def LanIpAddressBegin(self):
		return self.__getattr__("LanIpAddressBegin")
	
	@cached_property
	def LanIpAddressEnd(self):
		return self.__getattr__("LanIpAddressEnd")
	
	@cached_property
	def ArpResponse(self):
		return self.__getattr__("ArpResponse")
	
	@cached_property
	def Timeout(self):
		return self.__getattr__("Timeout")
	
	@cached_property
	def Description(self):
		return self.__getattr__("Description")
	

class IkePropCfg(BaseEntry):
	'''Model IkePropCfg

	Attributes [writable]
	---------------------
		Authentication : int
			Authentication
			Enum Values: 1=Pre-Shared-Key, 3=RSA-Signature
		Cipher : int
			Cipher
			Enum Values: 65600=DES, 196736=Blowfish, 327872=3DES, 458880=AES128, 458944=AES192, 459008=AES256
		Hash : int
			Hash
			Enum Values: 1=MD5, 2=SHA, 4=SHA2-256, 5=SHA2-384, 6=SHA2-512
		DhGroup : int
			DH Group
			Enum Values: 1=DH-Group-1, 2=DH-Group-2, 5=DH-Group-5, 14=DH-Group-14, 15=DH-Group-15, 16=DH-Group-16, 17=DH-Group-17, 18=DH-Group-18
		LifeType : int
			Life Type
			Enum Values: 1=duration, 2=kBytes, 3=both
		Duration : int
			Duration
		kBytes : int
			kBytes
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def Authentication(self):
		return self.__getattr__("Authentication")
	
	@cached_property
	def Cipher(self):
		return self.__getattr__("Cipher")
	
	@cached_property
	def Hash(self):
		return self.__getattr__("Hash")
	
	@cached_property
	def DhGroup(self):
		return self.__getattr__("DhGroup")
	
	@cached_property
	def LifeType(self):
		return self.__getattr__("LifeType")
	
	@cached_property
	def Duration(self):
		return self.__getattr__("Duration")
	
	@cached_property
	def kBytes(self):
		return self.__getattr__("kBytes")
	

class IkeV2PropCfg(BaseEntry):
	'''Model IkeV2PropCfg

	Attributes [writable]
	---------------------
		Encryption : int
			Encryption
			Enum Values: 131136=DES, 196800=3DES, 458880=Blowfish, 786560=AES128, 786624=AES192, 786688=AES256, 852096=AESCTR128, 852160=AESCTR192, 852224=AESCTR256, 1310848=AESGCM128, 1310976=AESGCM256
		PRF : int
			PRF
			Enum Values: 1=HMAC-MD5, 2=HMAC-SHA1, 5=HMAC-SHA2-256, 6=HMAC-SHA2-384, 7=HMAC-SHA2-512
		IntegAlgo : int
			Integrity Algorithm
			Enum Values: 0=none, 1=MD5-96, 2=SHA1-96, 12=SHA2-256, 13=SHA2-384, 14=SHA2-512
		DhGroup : int
			DH Group
			Enum Values: 1=DH-Group-1, 2=DH-Group-2, 5=DH-Group-5, 14=DH-Group-14, 15=DH-Group-15, 16=DH-Group-16, 17=DH-Group-17, 18=DH-Group-18, 19=DH-Group-19, 20=DH-Group-20, 21=DH-Group-21, 25=DH-Group-25, 26=DH-Group-26
		LifeType : int
			Life Type
			Enum Values: 1=duration, 2=kBytes, 3=both
		Duration : int
			Duration
		kBytes : int
			kBytes
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def Encryption(self):
		return self.__getattr__("Encryption")
	
	@cached_property
	def PRF(self):
		return self.__getattr__("PRF")
	
	@cached_property
	def IntegAlgo(self):
		return self.__getattr__("IntegAlgo")
	
	@cached_property
	def DhGroup(self):
		return self.__getattr__("DhGroup")
	
	@cached_property
	def LifeType(self):
		return self.__getattr__("LifeType")
	
	@cached_property
	def Duration(self):
		return self.__getattr__("Duration")
	
	@cached_property
	def kBytes(self):
		return self.__getattr__("kBytes")
	

class IPSecPropCfg(BaseEntry):
	'''Model IPSecPropCfg

	Attributes [writable]
	---------------------
		ProtId : int
			Protocol
			Enum Values: 3=ESP
		EspTransform : int
			ESP Transform
			Enum Values: 720896=NULL, 131136=DES, 196800=3DES, 458880=Blowfish, 786560=AES128, 786624=AES192, 786688=AES256, 852096=AESCTR128, 852160=AESCTR192, 852224=AESCTR256, 1310848=AESGCM128, 1310976=AESGCM256
		EspAuth : int
			ESP Authentication
			Enum Values: 0=none, 1=MD5, 2=SHA, 5=SHA256, 6=SHA384, 7=SHA512
		DhGroup : int
			DH Group
			Enum Values: 0=none, 1=DH-Group-1, 2=DH-Group-2, 5=DH-Group-5, 14=DH-Group-14, 15=DH-Group-15, 16=DH-Group-16, 17=DH-Group-17, 18=DH-Group-18, 19=DH-Group-19, 20=DH-Group-20, 21=DH-Group-21, 25=DH-Group-25, 26=DH-Group-26
		EspComp : int
			Compression
			Enum Values: 0=disabled, 2=deflate
		LifeType : int
			Life Type
			Enum Values: 1=duration, 2=kBytes, 3=both
		Duration : int
			Duration
		kBytes : int
			kBytes
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def ProtId(self):
		return self.__getattr__("ProtId")
	
	@cached_property
	def EspTransform(self):
		return self.__getattr__("EspTransform")
	
	@cached_property
	def EspAuth(self):
		return self.__getattr__("EspAuth")
	
	@cached_property
	def DhGroup(self):
		return self.__getattr__("DhGroup")
	
	@cached_property
	def EspComp(self):
		return self.__getattr__("EspComp")
	
	@cached_property
	def LifeType(self):
		return self.__getattr__("LifeType")
	
	@cached_property
	def Duration(self):
		return self.__getattr__("Duration")
	
	@cached_property
	def kBytes(self):
		return self.__getattr__("kBytes")
	

class IpSelectorCfg(BaseEntry):
	'''Model IpSelectorCfg

	Attributes [writable]
	---------------------
		SourceNetwork : ipaddr
			Source Network
		SourceMask : ipv4
			Source Network Mask
		DestNetwork : ipaddr
			Destination Network
		DestMask : ipv4
			Destination Network Mask
		SourceIpV6PrefixLen : int
			Source IPv6 Prefix Length
		DestIpV6PrefixLen : int
			Source IPv6 Prefix Length
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def SourceNetwork(self):
		return self.__getattr__("SourceNetwork")
	
	@cached_property
	def SourceMask(self):
		return self.__getattr__("SourceMask")
	
	@cached_property
	def DestNetwork(self):
		return self.__getattr__("DestNetwork")
	
	@cached_property
	def DestMask(self):
		return self.__getattr__("DestMask")
	
	@cached_property
	def SourceIpV6PrefixLen(self):
		return self.__getattr__("SourceIpV6PrefixLen")
	
	@cached_property
	def DestIpV6PrefixLen(self):
		return self.__getattr__("DestIpV6PrefixLen")
	

class DomainGrpMappingCfg(BaseEntry):
	'''Model DomainGrpMappingCfg

	Attributes [writable]
	---------------------
		Username : str
			Username
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def Username(self):
		return self.__getattr__("Username")
	

class IpPoolCfg(BaseEntry):
	'''Model IpPoolCfg

	Attributes [writable]
	---------------------
		PoolNr : int
			Pool No.
		PoolBegin : ipv4
			Pool Begin
		PoolEnd : ipv4
			Pool End
		LeaseTime : int
			Leasetime
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def PoolNr(self):
		return self.__getattr__("PoolNr")
	
	@cached_property
	def PoolBegin(self):
		return self.__getattr__("PoolBegin")
	
	@cached_property
	def PoolEnd(self):
		return self.__getattr__("PoolEnd")
	
	@cached_property
	def LeaseTime(self):
		return self.__getattr__("LeaseTime")
	

class DomainGrpAdvCfgRuleCfg(BaseEntry):
	'''Model DomainGrpAdvCfgRuleCfg

	Attributes [writable]
	---------------------
		Attribute : str
			Attribute
		MatchString : str
			MatchString
		Parameter : int
			Parameter
			Enum Values: 50=IPPoolNr, 208=FilterGroup, 363=UserPriority, 303=PolicyName, 305=PolicyFilterGroup, 370=DHCPSourceAddress, 371=DHCPSourceMask, 331=IPPoolNrMetered, 382=DHCPSourceAddressMetered, 383=DHCPSourceMaskMetered
		CfgValue : str
			Value
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def Attribute(self):
		return self.__getattr__("Attribute")
	
	@cached_property
	def MatchString(self):
		return self.__getattr__("MatchString")
	
	@cached_property
	def Parameter(self):
		return self.__getattr__("Parameter")
	
	@cached_property
	def CfgValue(self):
		return self.__getattr__("CfgValue")
	

class Certificate(BaseEntry):
	'''Object with certificate content

	Attributes [read-only]
	----------------------
		Subject : str
			Subject of the certificate
		Issuer : str
			Issuer of the certificate
		SerNr : str
			Serial number of the certificate
		NotBefore : str
			NotBefore time stamp of the certificate
		NotAfter : str
			NotAfter time stamp of the certificate
		FingerPrintSHA1 : str
			SHA1 finger print of the certificate
		FingerPrintSHA256 : str
			SHA-256 finger print of the certificate

	Attributes [writable]
	---------------------
		DER : str
			Base64 encoded certificate
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
	
	@cached_property
	def DER(self):
		return self.__getattr__("DER")
	
	@cached_property
	def Subject(self):
		return self.__getattr__("Subject")
	
	@cached_property
	def Issuer(self):
		return self.__getattr__("Issuer")
	
	@cached_property
	def SerNr(self):
		return self.__getattr__("SerNr")
	
	@cached_property
	def NotBefore(self):
		return self.__getattr__("NotBefore")
	
	@cached_property
	def NotAfter(self):
		return self.__getattr__("NotAfter")
	
	@cached_property
	def FingerPrintSHA1(self):
		return self.__getattr__("FingerPrintSHA1")
	
	@cached_property
	def FingerPrintSHA256(self):
		return self.__getattr__("FingerPrintSHA256")
	
