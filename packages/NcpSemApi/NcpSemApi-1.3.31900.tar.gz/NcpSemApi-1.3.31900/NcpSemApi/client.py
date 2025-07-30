
#---------------------------------------------------------------
# This file is generated! Dont make any changes in this file.
#---------------------------------------------------------------
from .base import *
from .cached_property import cached_property



class ClientTemplatesHandler(BaseListFindHandler):
	'''Management of client templates

	Methods
	-------
		createEntry()
			Creates a new ClientTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "client-mgm/{groupid}/client-templs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new ClientTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientTemplate(self, self._groupid)


class ClientTemplate(LazyListEntry):
	'''Configuration of a client template

	Attributes [read-only]
	----------------------
		TemplateType : integer
			Template Type
			Enum Values: 0=Enterprise template, 11=VS GovNet Connector template
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		SoftwareUpdateList : string or integer from SoftwareUpdateLists
			Software Update List
		FirewallTemplate : string or integer from FirewallTemplates
			Firewall Template
		ShowCBO : integer
			Enable Custom Branding Option
		UnlockUserId : string
			Unlock User ID
		UnlockPassword : string
			Unlock Password
		ShowNewCfgMsg : boolean
			Show message if user has received a new configuration
		ProductGroup : integer
			Product Group
			Enum Values: 2=Client for Windows, 14=Client for Linux, 21=Client for macOS, 22=Client for Android, 25=Client for iOS
		ProductType : integer
			ProductType
			Enum Values: 3=NCP Secure Enterprise Client, 2=NCP Dynamic Net Guard, 11=NCP Secure GovNet Client, 259=NCP VS GovNet Connector, 1245187=NCP Exclusive Remote Access Client, 131075=Telekom Secure Client, 131074=Telekom Dynamic Net Guard
		SoftwareVersion : string
			Software Version
		UseLeaseLicense : boolean
			Use lease license
		DistribLicKeys : boolean
			Automatic distribution of license keys
		Restrictions : object
			Restrictions
		ModuleDialer : boolean
			Module Dialer
		ModuleWiFi : boolean
			Module Wi Fi
		ModuleEAP : boolean
			Module EAP
		ModuleFirewall : boolean
			Module Firewall
		ModuleVPN : boolean
			Module VPN
		WiFiActivate : boolean
			Wi-Fi
		WiFiDisableAdapter : boolean
			Disable Wi-Fi when LAN cable is connected
		WiFiEnableHotspot : boolean
			Enable Hotspot detection
		EapState : integer
			IEEE 802.1x authentication (EAP)
			Enum Values: 0=off, 1=all, 2=WiFi, 3=LAN
		EapId : string
			EAP identity
		EapPassword : string
			EAP password
		InstallCredProv : boolean
			Install NCP Credential Provider for connection dialog before Windows logon
		LogonShow : boolean
			Show connection dialog before Windows logon
		LogonUseVpnId : boolean
			Logon use VPN User ID
		LogonUseVpnPw : boolean
			Use VPN Password for Windows logon
		LogonUserId : string
			User ID
		LogonPassword : string
			Password
		LogonDomain : string
			Domain
		LogoffAfterDisconnect : boolean
			Disconnect after Logoff
		LogonResetPW : boolean
			Logon Reset PW
		LogonStartAppl : boolean
			External Applications or Batch Files
		LogonStartAppls : array
			Logon Start Applications
		LogonDomainWait : boolean
			Logon Domain Wait
		LogonDomainWaitTime : integer
			Logon Domain Wait Time
		LogonEAPWait : boolean
			Logon EAP Wait
		LogonVistaMax : boolean
			Logon Vista Max
		LogonShowPreSelIconMax : boolean
			Logon Show Pre Sel Icon Max
		LogonAutoDlgOpen : boolean
			Logon Auto Dlg Open
		LogonRights : boolean
			User rights
		LanUpdateMgmSrv1 : string
			Primary Management Server
		LanUpdateMgmSrv2 : string
			Secondary Management Server
		LanUpdAutoRsuID : string
			Lan Upd Auto Rsu ID
		LanUpdAutoAuthCode : string
			Lan Upd Auto Auth Code
		MonitorShowProfiles : boolean
			Monitor Show Profiles
		MonitorShowButtons : boolean
			Monitor Show Buttons
		MonitorShowStatistics : boolean
			Show Statistics
		MonitorShowWiFi : boolean
			Monitor Show Wi Fi
		MonitorAlwaysOnTop : boolean
			Monitor Always On Top
		AutoStart : integer
			Auto Start
			Enum Values: 0=off, 1=minimize, 2=maximize
		MonitorCloseMin : boolean
			Minimize when closing
		MonitorConnectMin : boolean
			Minimize when connected
		MonitorShowAvaiMedia : boolean
			Show dialog for aval. comm. media when connection failed
		ProxyActive : integer
			Proxy Active
		HttpProxies : array from model HttpProxy
			HTTP Proxies
		NetworkDiagnosticIPAddr : string with IP address
			Network Diagnostic IP Addr
		NetworkDiagnosticURL : string
			Network Diagnostic URL
		FreeDesc1 : string
			1. User Information
		FreeDesc2 : string
			2. User Information
		FreeDesc3 : string
			3. User Information
		FreeDesc4 : string
			4. User Information
		FreeDesc5 : string
			Free Desc5
		CustomParameters : string
			Custom Parameters
		AdminCertificates : array from uintkey
			Adminstrator Certificates
		CACertificates : array from uintkey
			CA Certificates
		UserParameters : object
			User parameters
		InheritedToSubgroups : boolean
			Entry inherited to subgroups
		ConfigDescription : string
			Description of configuration
		DistributeProfileVersion : integer
			Distribute the profile settings with the following version
		DistributeProfileSP : integer
			Distribute Profile ServicePack

	Sub-Handlers
	------------
		clientProfileTemplates
			Access ClientProfileTemplatesHandler
		clientIkePolicyTemplates
			Access ClientIkePolicyTemplatesHandler
		clientIkev2PolicyTemplates
			Access ClientIkev2PolicyTemplatesHandler
		clientIpsecPolicyTemplates
			Access ClientIpsecPolicyTemplatesHandler
		clientWifiTemplates
			Access ClientWifiTemplatesHandler
		clientPkiConfigurationTemplates
			Access ClientPkiConfigurationTemplatesHandler
		clientVpnByPassTemplates
			Access ClientVpnByPassTemplatesHandler
		clientQoSTemplates
			Access ClientQoSTemplatesHandler

	Methods
	-------
		generate_all_configs()
			Generates all client configurations from this template
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)
		self._groupid = groupid
		self._api = getHandler._api
		# Default values
		self._defaultValues = {
			"Name" : "",
			"TemplateType" : "Enterprise template",
			"SoftwareUpdateList" : "0",
			"FirewallTemplate" : "0",
			"ShowCBO" : 0,
			"UnlockUserId" : "",
			"UnlockPassword" : "",
			"ShowNewCfgMsg" : False,
			"ProductGroup" : 0,
			"ProductType" : "NCP Secure Enterprise Client",
			"SoftwareVersion" : "1210",
			"UseLeaseLicense" : False,
			"DistribLicKeys" : False,
			"Restrictions" : {},
			"ModuleDialer" : True,
			"ModuleWiFi" : True,
			"ModuleEAP" : True,
			"ModuleFirewall" : True,
			"ModuleVPN" : True,
			"WiFiActivate" : False,
			"WiFiDisableAdapter" : False,
			"WiFiEnableHotspot" : False,
			"EapState" : "off",
			"EapId" : "",
			"EapPassword" : "",
			"InstallCredProv" : False,
			"LogonShow" : False,
			"LogonUseVpnId" : False,
			"LogonUseVpnPw" : False,
			"LogonUserId" : "",
			"LogonPassword" : "",
			"LogonDomain" : "",
			"LogoffAfterDisconnect" : False,
			"LogonResetPW" : False,
			"LogonStartAppl" : False,
			"LogonStartAppls" : [],
			"LogonDomainWait" : False,
			"LogonDomainWaitTime" : 45,
			"LogonEAPWait" : False,
			"LogonVistaMax" : False,
			"LogonShowPreSelIconMax" : False,
			"LogonAutoDlgOpen" : False,
			"LogonRights" : False,
			"LanUpdateMgmSrv1" : "",
			"LanUpdateMgmSrv2" : "",
			"LanUpdAutoRsuID" : "",
			"LanUpdAutoAuthCode" : "",
			"MonitorShowProfiles" : True,
			"MonitorShowButtons" : True,
			"MonitorShowStatistics" : True,
			"MonitorShowWiFi" : False,
			"MonitorAlwaysOnTop" : False,
			"AutoStart" : "maximize",
			"MonitorCloseMin" : False,
			"MonitorConnectMin" : False,
			"MonitorShowAvaiMedia" : True,
			"ProxyActive" : 0,
			"HttpProxies" : [],
			"NetworkDiagnosticIPAddr" : "0.0.0.0",
			"NetworkDiagnosticURL" : "",
			"FreeDesc1" : "",
			"FreeDesc2" : "",
			"FreeDesc3" : "",
			"FreeDesc4" : "",
			"FreeDesc5" : "",
			"CustomParameters" : "",
			"AdminCertificates" : [],
			"CACertificates" : [],
			"UserParameters" : {},
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
			"InheritedToSubgroups" : False,
			"ConfigDescription" : "",
			"DistributeProfileVersion" : 0,
			"DistributeProfileSP" : 0,
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def TemplateType(self):
		return self.__getattr__("TemplateType")

	@cached_property
	def SoftwareUpdateList(self):
		return self.__getattr__("SoftwareUpdateList")

	@cached_property
	def FirewallTemplate(self):
		return self.__getattr__("FirewallTemplate")

	@cached_property
	def ShowCBO(self):
		return self.__getattr__("ShowCBO")

	@cached_property
	def UnlockUserId(self):
		return self.__getattr__("UnlockUserId")

	@cached_property
	def UnlockPassword(self):
		return self.__getattr__("UnlockPassword")

	@cached_property
	def ShowNewCfgMsg(self):
		return self.__getattr__("ShowNewCfgMsg")

	@cached_property
	def ProductGroup(self):
		return self.__getattr__("ProductGroup")

	@cached_property
	def ProductType(self):
		return self.__getattr__("ProductType")

	@cached_property
	def SoftwareVersion(self):
		return self.__getattr__("SoftwareVersion")

	@cached_property
	def UseLeaseLicense(self):
		return self.__getattr__("UseLeaseLicense")

	@cached_property
	def DistribLicKeys(self):
		return self.__getattr__("DistribLicKeys")

	@cached_property
	def Restrictions(self):
		return self.__getattr__("Restrictions")

	@cached_property
	def ModuleDialer(self):
		return self.__getattr__("ModuleDialer")

	@cached_property
	def ModuleWiFi(self):
		return self.__getattr__("ModuleWiFi")

	@cached_property
	def ModuleEAP(self):
		return self.__getattr__("ModuleEAP")

	@cached_property
	def ModuleFirewall(self):
		return self.__getattr__("ModuleFirewall")

	@cached_property
	def ModuleVPN(self):
		return self.__getattr__("ModuleVPN")

	@cached_property
	def WiFiActivate(self):
		return self.__getattr__("WiFiActivate")

	@cached_property
	def WiFiDisableAdapter(self):
		return self.__getattr__("WiFiDisableAdapter")

	@cached_property
	def WiFiEnableHotspot(self):
		return self.__getattr__("WiFiEnableHotspot")

	@cached_property
	def EapState(self):
		return self.__getattr__("EapState")

	@cached_property
	def EapId(self):
		return self.__getattr__("EapId")

	@cached_property
	def EapPassword(self):
		return self.__getattr__("EapPassword")

	@cached_property
	def InstallCredProv(self):
		return self.__getattr__("InstallCredProv")

	@cached_property
	def LogonShow(self):
		return self.__getattr__("LogonShow")

	@cached_property
	def LogonUseVpnId(self):
		return self.__getattr__("LogonUseVpnId")

	@cached_property
	def LogonUseVpnPw(self):
		return self.__getattr__("LogonUseVpnPw")

	@cached_property
	def LogonUserId(self):
		return self.__getattr__("LogonUserId")

	@cached_property
	def LogonPassword(self):
		return self.__getattr__("LogonPassword")

	@cached_property
	def LogonDomain(self):
		return self.__getattr__("LogonDomain")

	@cached_property
	def LogoffAfterDisconnect(self):
		return self.__getattr__("LogoffAfterDisconnect")

	@cached_property
	def LogonResetPW(self):
		return self.__getattr__("LogonResetPW")

	@cached_property
	def LogonStartAppl(self):
		return self.__getattr__("LogonStartAppl")

	@cached_property
	def LogonStartAppls(self):
		return self.__getattr__("LogonStartAppls")

	@cached_property
	def LogonDomainWait(self):
		return self.__getattr__("LogonDomainWait")

	@cached_property
	def LogonDomainWaitTime(self):
		return self.__getattr__("LogonDomainWaitTime")

	@cached_property
	def LogonEAPWait(self):
		return self.__getattr__("LogonEAPWait")

	@cached_property
	def LogonVistaMax(self):
		return self.__getattr__("LogonVistaMax")

	@cached_property
	def LogonShowPreSelIconMax(self):
		return self.__getattr__("LogonShowPreSelIconMax")

	@cached_property
	def LogonAutoDlgOpen(self):
		return self.__getattr__("LogonAutoDlgOpen")

	@cached_property
	def LogonRights(self):
		return self.__getattr__("LogonRights")

	@cached_property
	def LanUpdateMgmSrv1(self):
		return self.__getattr__("LanUpdateMgmSrv1")

	@cached_property
	def LanUpdateMgmSrv2(self):
		return self.__getattr__("LanUpdateMgmSrv2")

	@cached_property
	def LanUpdAutoRsuID(self):
		return self.__getattr__("LanUpdAutoRsuID")

	@cached_property
	def LanUpdAutoAuthCode(self):
		return self.__getattr__("LanUpdAutoAuthCode")

	@cached_property
	def MonitorShowProfiles(self):
		return self.__getattr__("MonitorShowProfiles")

	@cached_property
	def MonitorShowButtons(self):
		return self.__getattr__("MonitorShowButtons")

	@cached_property
	def MonitorShowStatistics(self):
		return self.__getattr__("MonitorShowStatistics")

	@cached_property
	def MonitorShowWiFi(self):
		return self.__getattr__("MonitorShowWiFi")

	@cached_property
	def MonitorAlwaysOnTop(self):
		return self.__getattr__("MonitorAlwaysOnTop")

	@cached_property
	def AutoStart(self):
		return self.__getattr__("AutoStart")

	@cached_property
	def MonitorCloseMin(self):
		return self.__getattr__("MonitorCloseMin")

	@cached_property
	def MonitorConnectMin(self):
		return self.__getattr__("MonitorConnectMin")

	@cached_property
	def MonitorShowAvaiMedia(self):
		return self.__getattr__("MonitorShowAvaiMedia")

	@cached_property
	def ProxyActive(self):
		return self.__getattr__("ProxyActive")

	@cached_property
	def HttpProxies(self):
		return self.__getattr__("HttpProxies")

	@cached_property
	def NetworkDiagnosticIPAddr(self):
		return self.__getattr__("NetworkDiagnosticIPAddr")

	@cached_property
	def NetworkDiagnosticURL(self):
		return self.__getattr__("NetworkDiagnosticURL")

	@cached_property
	def FreeDesc1(self):
		return self.__getattr__("FreeDesc1")

	@cached_property
	def FreeDesc2(self):
		return self.__getattr__("FreeDesc2")

	@cached_property
	def FreeDesc3(self):
		return self.__getattr__("FreeDesc3")

	@cached_property
	def FreeDesc4(self):
		return self.__getattr__("FreeDesc4")

	@cached_property
	def FreeDesc5(self):
		return self.__getattr__("FreeDesc5")

	@cached_property
	def CustomParameters(self):
		return self.__getattr__("CustomParameters")

	@cached_property
	def AdminCertificates(self):
		return self.__getattr__("AdminCertificates")

	@cached_property
	def CACertificates(self):
		return self.__getattr__("CACertificates")

	@cached_property
	def UserParameters(self):
		return self.__getattr__("UserParameters")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")

	@cached_property
	def InheritedToSubgroups(self):
		return self.__getattr__("InheritedToSubgroups")

	@cached_property
	def ConfigDescription(self):
		return self.__getattr__("ConfigDescription")

	@cached_property
	def DistributeProfileVersion(self):
		return self.__getattr__("DistributeProfileVersion")

	@cached_property
	def DistributeProfileSP(self):
		return self.__getattr__("DistributeProfileSP")

	@cached_property
	def clientProfileTemplates(self):
		'''Returns handler to access ClientProfileTemplates'''
		return ClientProfileTemplatesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientIkePolicyTemplates(self):
		'''Returns handler to access ClientIkePolicyTemplates'''
		return ClientIkePolicyTemplatesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientIkev2PolicyTemplates(self):
		'''Returns handler to access ClientIkev2PolicyTemplates'''
		return ClientIkev2PolicyTemplatesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientIpsecPolicyTemplates(self):
		'''Returns handler to access ClientIpsecPolicyTemplates'''
		return ClientIpsecPolicyTemplatesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientWifiTemplates(self):
		'''Returns handler to access ClientWifiTemplates'''
		return ClientWifiTemplatesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientPkiConfigurationTemplates(self):
		'''Returns handler to access ClientPkiConfigurationTemplates'''
		return ClientPkiConfigurationTemplatesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientVpnByPassTemplates(self):
		'''Returns handler to access ClientVpnByPassTemplates'''
		return ClientVpnByPassTemplatesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientQoSTemplates(self):
		'''Returns handler to access ClientQoSTemplates'''
		return ClientQoSTemplatesHandler(self._api, self._groupid, self.Id)
			
	def generate_all_configs(self):
		'''Generates all client configurations from this template'''
		return self._callMethod('/generate-all-configs')


class ClientProfileTemplatesHandler(BaseListFindHandler):
	'''Configuration of client profile templates

	Methods
	-------
		createEntry()
			Creates a new ClientProfileTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, clnttemplid):
		url = "client-mgm/{groupid}/client-templs/{clnttemplid}/profiles".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clnttemplid = clnttemplid

	def createEntry(self):
		'''Creates a new ClientProfileTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientProfileTemplate(self, self._groupid, self._clnttemplid)


class ClientProfileTemplate(LazyListEntry):
	'''Configuration of a client profile template

	Attributes [read-only]
	----------------------
		ProfileName : string
			Profile Name
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		LinkType : integer
			Communication Medium
			Enum Values: 8=LAN, 18=mobile network, 20=WiFi, 21=automatic
		UseForAMD : boolean
			Profile for automatic media detection
		SeamlessRoaming : boolean
			Seamless Roaming
		KeepTunnel : boolean
			Disconnect the logical VPN tunnel when the connection is broken
		BootUser : integer
			Default Profile after System Reboot
			Enum Values: 0=off, 1=bootuser
		UseRas : integer
			Microsoft Dial-up Networking
			Enum Values: 0=never, 2=script, 1=always
		HideProfile : boolean
			Do not include this entry in the profile settings
		DialerUser : string
			Dial-up User ID
		DialerPw : string
			Dial-up Password
		DialerPhone : string
			Dial-up Phone Number
		RasFile : string
			RAS Script File
		HttpUsername : string
			HTTP User Name
		HttpPassword : string
			HTTP Password
		HttpScript : string
			HTTP Authentication Script
		Modem : string
			Modem Type
		ComPort : string
			Com Port
		Baudrate : integer
			Baud Rate
			Enum Values: 1200=1200, 2400=2400, 4800=4800, 9600=9600, 19200=19200, 38400=38400, 57600=57600, 115200=115200
		RlsComPort : boolean
			Release Com Port
		ModemInitStr : string
			Modem Init. String
		DialPrefix : string
			Dial Prefix
		MobileConfigMode : integer
			Configuration Mode
			Enum Values: 0=manuel, 1=list, 2=SIM card
		MobileCountry : integer
			Country
		MobileProvider : integer
			Provider
		MobileApn : string
			APN
		MobilePhone : string
			Dial-up number
		MobileAuth : integer
			Authentication
			Enum Values: 0=none, 1=PAP, 2=CHAP
		MobileUsername : string
			Mobile Username
		MobilePassword : string
			Mobile Password
		MobileSimPin : string
			SIM PIN
		BiometricAuth : boolean
			Fingerprint
		EapAuthentication : boolean
			EAP Authentication
		HttpAuthentication : boolean
			HTTP Authentication
		ConnectionMode : integer
			Connection Mode
			Enum Values: 0=manually, 1=automatic, 2=variable/automatic, 3=always, 4=variable/always
		ConnectAtBoot : boolean
			Connect at Boot
		Timeout : integer
			Inactivity Timeout (sec)
		OtpToken : integer
			OTP Token
			Enum Values: 0=off, 1=NAS, 2=VPN
		SwapOtpPin : boolean
			Swap OTP password and PIN
		HideUserId : boolean
			Hide username when prompted for credentials
		TunnelTrafficMonitoring : boolean
			Enable tunnel traffic monitoring
		TunnelTrafficMonitoringAddr : string
			Alternative IP address
		PermitIpBroadcast : boolean
			Permit IP Broadcast
		QoSConfig : string or integer from ClientQoSTemplates
			Quality of Service
		PkiConfig : string or integer from ClientPkiConfigurationTemplates
			Certificate configuration
		ExchangeMode : integer
			Exchange Mode
			Enum Values: 2=main mode, 4=aggressive mode, 34=IKEv2
		VpnIpVersion : integer
			Tunnel IP Version
			Enum Values: 1=IPv4, 2=IPv6, 3=both
		IkeV2Authentication : integer
			IKEv2 Authentication
			Enum Values: 1=Certificates, 2=PSK, 3=EAP, 4=SAML
		IkePolicy : string or integer from ClientIkePolicyTemplates
			IKE Policy
		IkeV2Policy : string or integer from ClientIkev2PolicyTemplates
			IKEv2 Policy
		IkeDhGroup : integer
			IKE DH Group
			Enum Values: 0=none, 1=DHGroup1, 2=DHGroup2, 5=DHGroup5, 14=DHGroup14, 15=DHGroup15, 16=DHGroup16, 17=DHGroup17, 18=DHGroup18, 19=DHGroup19, 20=DHGroup20, 21=DHGroup21, 25=DHGroup25, 26=DHGroup26, 27=DHGroup27, 28=DHGroup28, 29=DHGroup29, 30=DHGroup306
		IkeLifeTimeDuration : integer
			Lifetime
		IpSecPolicy : string or integer from ClientIpsecPolicyTemplates
			IPsec Policy
		PFS : integer
			PFS
			Enum Values: 0=none, 1=DHGroup1, 2=DHGroup2, 5=DHGroup5, 14=DHGroup14, 15=DHGroup15, 16=DHGroup16, 17=DHGroup17, 18=DHGroup18, 19=DHGroup19, 20=DHGroup20, 21=DHGroup21, 25=DHGroup25, 26=DHGroup26, 27=DHGroup27, 28=DHGroup28, 29=DHGroup29, 30=DHGroup30
		IpSecLifeTimeType : integer
			Lifetime Type (IPsec)
			Enum Values: 0=off, 1=duration, 2=KByte, 3=Both
		IpSecLifeTimeDuration : integer
			Ip Sec Life Time Duration
		IpSecLifeTimeVolume : integer
			Volume
		UseCompression : boolean
			IPsec Compression
		IkeIdType : integer
			IKE ID Type
			Enum Values: 1=IpAddr, 2=DomainName, 3=UserId, 4=IpSubNet, 7=IpAddrRange, 9=ASN1DN, 10=ASN1GroupName, 11=FreeString, 19=X500DistingName, 20=X500GeneralName, 21=KeyId
		IkeId : string
			IKE ID
		VpnUserId : string
			VPN User ID
		VpnPassword : string
			VPN Password
		VpnPwSave : boolean
			Save VPN Password in Profile Settings
		VpnSuffix : string
			VPN Suffix
		TunnelSecret : string
			IPsec Pre-shared Key
		VpnRemIpAddr : string
			Gateway (Tunnel Endpoint)
		AuthFromCert : integer
			VPN Tunnel Authentication Data
			Enum Values: 0=config, 1=e-mail, 2=common name, 3=serial number, 4=UPN, 5=SAN e-mail, 6=subject serial number
		SamlUrl : string
			Authentication Provider URL
		SamlRealm : string
			Realm
		SplitTunnelingModeV4 : integer
			Split tunneling mode IPv4
			Enum Values: 0=split, 1=all tunnel
		SplitTunnelingNetworksV4 : array from model ClientSplitTunnelNetV4
			Split tunneling networks IPv4
		VpnTunnelRelay : boolean
			Full Local Network Enclosure Mode
		SplitTunnelingModeV6 : integer
			Split tunneling mode IPv6
			Enum Values: 0=split, 1=all tunnel
		SplitTunnelingNetworksV6 : array from model ClientSplitTunnelNetV6
			Split tunneling networks IPv6
		VpnByPassConfig : string or integer from ClientVpnByPassTemplates
			VPN bypass configuration
		UseXAUTH : boolean
			Extended Authentication (XAUTH)
		UseIkePort : integer
			UDP Encapsulation Port
		DisableDPD : integer
			Disable DPD (Dead Peer Detection)
			Enum Values: 0=on, 1=off
		DPDInterval : integer
			DPD Interval
		DPDRetries : integer
			DPD Number of retries
		AntiReplay : boolean
			Anti-replay Protection
		PathFinder : boolean
			VPN Path Finder
		UseRFC7427 : boolean
			Enable negotiating RFC7427 (digital signatures)
		RFC7427Padding : integer
			RFC7427 Padding Method
			Enum Values: 0=undefined, 1=PKCS#1, 2=PSS
		IkeV2AuthPrf : boolean
			IKEv2 RSA authentication with PRF hash
		AssignPrivateIpAddress : integer
			Assignment of private IP address
			Enum Values: 1=IKE Config Mode, 2=Local IP address, 3=DHCP over IPsec, 4=manual
		PrivateIpAddess : string with IP address
			IP address
		PrivateIpMask : string with IP address
			Subnet Mask
		DNS1 : string with IP address
			1. DNS Server
		DNS2 : string with IP address
			2. DNS Server
		MgmSrv : string with IP address
			1. Management Server
		MgmSrv2 : string with IP address
			2. Management Server
		DomainName : string
			Domain Name
		DomainInTunnel : string
			DNS domains to be resolved in the tunnel
		WebProxyType : integer
			Proxy type
			Enum Values: 0=none, 1=auto, 2=manually
		WebProxyAutoURL : string
			Proxy configuration URL
		WebProxyHttp : string
			HTTP proxy
		WebProxyHttps : string
			HTTPS proxy
		WebProxyExceptions : string
			Web Proxy exceptions
		HASupport : integer
			HA Support
			Enum Values: 0=off, 2=HA over VPN-Port
		HAServer1 : string
			Primary HA Server
		HAServer2 : string
			Secondary HA Server
		DveSecret : string
			HA Secret
		HaUseLastGateway : boolean
			Last Assigned Gateway
		CertSubject : string
			Incoming Certificate's Subject
		CertIssuer : string
			Incoming Certificate's Issuer
		CertFingerprint : string
			Issuer's Certificate Fingerprint
		CertFingerPrintHash : integer
			Fingerprint Hash
			Enum Values: 0=MD5, 1=SHA1
		ProtectLan : integer
			Stateful Inspection
			Enum Values: 0=off, 1=when connect, 2=always
		FwOnlyVpn : boolean
			Only Tunneling Permitted
		FwRasOnlyVpn : boolean
			In Combination with Microsoft's RAS Dialer only Tunneling permitted
		SrvCreateEntry : integer
			Create configuration on RADIUS server
			Enum Values: 0=off, 1=VPN, 2=NAS, 3=both
		SrvNasIpAddr : string with IP address
			NAS IP address for client
		SrvNasParam1 : string
			NAS parameter 1
		SrvNasParam2 : string
			NAS parameter 2
		SrvNasParam3 : string
			NAS parameter 3
		SrvNasParam4 : string
			NAS parameter 4
		SrvNasParam5 : string
			NAS parameter 5
		SrvNasParam6 : string
			NAS parameter 6
		SrvNasParam7 : string
			NAS parameter 7
		SrvNasParam8 : string
			NAS parameter 8
		SrvVpnIpAddr : string with IP address
			VPN IP address for client
		SrvVpnParam1 : string
			VPN parameter 1
		SrvVpnParam2 : string
			VPN parameter 2
		SrvVpnParam3 : string
			VPN parameter 3
		SrvVpnParam4 : string
			VPN parameter 4
		SrvVpnParam5 : string
			VPN parameter 5
		SrvVpnParam6 : string
			VPN parameter 6
		SrvVpnParam7 : string
			VPN parameter 7
		SrvVpnParam8 : string
			VPN parameter 8
		SrvVpnParamSplitTunneling : string
			Server Parameter Split Tunneling
		RadiusValidFrom : time
			Enable connections starting on
		RadiusValidUntil : time
			Deny connections starting on
		TwoFactAuthLang : string
			Language
		TwoFactAuthId : string
			Device number
		TimeOTPCreate : boolean
			Enable creation of time-based OTP secrets
		TimeOTPDesc : string
			Time-based OTP description
		ParameterRights : object
			Parameter rights
		RightsViewTabs : object
			Rights View Tabs and Flips
		RightDisplay : boolean
			Profile may be displayed
		RightDelete : boolean
			Profile may be deleted
		RightCopy : boolean
			Profile may be copied
		RightUpdLockedParams : boolean
			Only update locked parameters
		RightExport : boolean
			User may open the export mode
		UserParameters : object
			User parameters
	'''

	def __init__(self, getHandler, groupid, clnttemplid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"ProfileName" : "",
			"LinkType" : "LAN",
			"UseForAMD" : False,
			"SeamlessRoaming" : False,
			"KeepTunnel" : False,
			"BootUser" : "off",
			"UseRas" : "never",
			"HideProfile" : False,
			"DialerUser" : "",
			"DialerPw" : "NoPassword",
			"DialerPhone" : "",
			"RasFile" : "",
			"HttpUsername" : "",
			"HttpPassword" : "",
			"HttpScript" : "",
			"Modem" : "",
			"ComPort" : "COM1",
			"Baudrate" : "57600",
			"RlsComPort" : True,
			"ModemInitStr" : "",
			"DialPrefix" : "",
			"MobileConfigMode" : "SIM card",
			"MobileCountry" : 0,
			"MobileProvider" : 4294967295,
			"MobileApn" : "AT+cgdcont=1,\"IP\",\"\"",
			"MobilePhone" : "",
			"MobileAuth" : "none",
			"MobileUsername" : "",
			"MobilePassword" : "",
			"MobileSimPin" : "",
			"BiometricAuth" : False,
			"EapAuthentication" : False,
			"HttpAuthentication" : False,
			"ConnectionMode" : "manually",
			"ConnectAtBoot" : False,
			"Timeout" : 100,
			"OtpToken" : "off",
			"SwapOtpPin" : False,
			"HideUserId" : False,
			"TunnelTrafficMonitoring" : False,
			"TunnelTrafficMonitoringAddr" : "0.0.0.0",
			"PermitIpBroadcast" : True,
			"QoSConfig" : "0",
			"PkiConfig" : "0",
			"ExchangeMode" : "IKEv2",
			"VpnIpVersion" : "IPv4",
			"IkeV2Authentication" : "EAP",
			"IkePolicy" : "-1",
			"IkeV2Policy" : "-1",
			"IkeDhGroup" : "DHGroup14",
			"IkeLifeTimeDuration" : 86400,
			"IpSecPolicy" : "-1",
			"PFS" : "DHGroup14",
			"IpSecLifeTimeType" : "duration",
			"IpSecLifeTimeDuration" : 28800,
			"IpSecLifeTimeVolume" : 50000,
			"UseCompression" : True,
			"IkeIdType" : "UserId",
			"IkeId" : "",
			"VpnUserId" : "",
			"VpnPassword" : "",
			"VpnPwSave" : True,
			"VpnSuffix" : "",
			"TunnelSecret" : "",
			"VpnRemIpAddr" : "",
			"AuthFromCert" : "config",
			"SamlUrl" : "",
			"SamlRealm" : "",
			"SplitTunnelingModeV4" : "all tunnel",
			"SplitTunnelingNetworksV4" : [],
			"VpnTunnelRelay" : True,
			"SplitTunnelingModeV6" : "all tunnel",
			"SplitTunnelingNetworksV6" : [],
			"VpnByPassConfig" : "0",
			"UseXAUTH" : True,
			"UseIkePort" : 500,
			"DisableDPD" : "on",
			"DPDInterval" : 20,
			"DPDRetries" : 8,
			"AntiReplay" : False,
			"PathFinder" : False,
			"UseRFC7427" : True,
			"RFC7427Padding" : "PSS",
			"IkeV2AuthPrf" : False,
			"AssignPrivateIpAddress" : "IKE Config Mode",
			"PrivateIpAddess" : "0.0.0.0",
			"PrivateIpMask" : "255.255.255.0",
			"DNS1" : "0.0.0.0",
			"DNS2" : "0.0.0.0",
			"MgmSrv" : "0.0.0.0",
			"MgmSrv2" : "0.0.0.0",
			"DomainName" : "",
			"DomainInTunnel" : "",
			"WebProxyType" : "none",
			"WebProxyAutoURL" : "",
			"WebProxyHttp" : "",
			"WebProxyHttps" : "",
			"WebProxyExceptions" : "",
			"HASupport" : "off",
			"HAServer1" : "",
			"HAServer2" : "",
			"DveSecret" : "",
			"HaUseLastGateway" : True,
			"CertSubject" : "",
			"CertIssuer" : "",
			"CertFingerprint" : "",
			"CertFingerPrintHash" : "MD5",
			"ProtectLan" : "off",
			"FwOnlyVpn" : False,
			"FwRasOnlyVpn" : True,
			"SrvCreateEntry" : "off",
			"SrvNasIpAddr" : "0.0.0.0",
			"SrvNasParam1" : "",
			"SrvNasParam2" : "",
			"SrvNasParam3" : "",
			"SrvNasParam4" : "",
			"SrvNasParam5" : "",
			"SrvNasParam6" : "",
			"SrvNasParam7" : "",
			"SrvNasParam8" : "",
			"SrvVpnIpAddr" : "0.0.0.0",
			"SrvVpnParam1" : "",
			"SrvVpnParam2" : "",
			"SrvVpnParam3" : "",
			"SrvVpnParam4" : "",
			"SrvVpnParam5" : "",
			"SrvVpnParam6" : "",
			"SrvVpnParam7" : "",
			"SrvVpnParam8" : "",
			"SrvVpnParamSplitTunneling" : "",
			"RadiusValidFrom" : "",
			"RadiusValidUntil" : "",
			"TwoFactAuthLang" : "",
			"TwoFactAuthId" : "",
			"TimeOTPCreate" : False,
			"TimeOTPDesc" : "",
			"ParameterRights" : {},
			"RightsViewTabs" : {},
			"RightDisplay" : True,
			"RightDelete" : True,
			"RightCopy" : True,
			"RightUpdLockedParams" : False,
			"RightExport" : True,
			"UserParameters" : {},
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def ProfileName(self):
		return self.__getattr__("ProfileName")

	@cached_property
	def LinkType(self):
		return self.__getattr__("LinkType")

	@cached_property
	def UseForAMD(self):
		return self.__getattr__("UseForAMD")

	@cached_property
	def SeamlessRoaming(self):
		return self.__getattr__("SeamlessRoaming")

	@cached_property
	def KeepTunnel(self):
		return self.__getattr__("KeepTunnel")

	@cached_property
	def BootUser(self):
		return self.__getattr__("BootUser")

	@cached_property
	def UseRas(self):
		return self.__getattr__("UseRas")

	@cached_property
	def HideProfile(self):
		return self.__getattr__("HideProfile")

	@cached_property
	def DialerUser(self):
		return self.__getattr__("DialerUser")

	@cached_property
	def DialerPw(self):
		return self.__getattr__("DialerPw")

	@cached_property
	def DialerPhone(self):
		return self.__getattr__("DialerPhone")

	@cached_property
	def RasFile(self):
		return self.__getattr__("RasFile")

	@cached_property
	def HttpUsername(self):
		return self.__getattr__("HttpUsername")

	@cached_property
	def HttpPassword(self):
		return self.__getattr__("HttpPassword")

	@cached_property
	def HttpScript(self):
		return self.__getattr__("HttpScript")

	@cached_property
	def Modem(self):
		return self.__getattr__("Modem")

	@cached_property
	def ComPort(self):
		return self.__getattr__("ComPort")

	@cached_property
	def Baudrate(self):
		return self.__getattr__("Baudrate")

	@cached_property
	def RlsComPort(self):
		return self.__getattr__("RlsComPort")

	@cached_property
	def ModemInitStr(self):
		return self.__getattr__("ModemInitStr")

	@cached_property
	def DialPrefix(self):
		return self.__getattr__("DialPrefix")

	@cached_property
	def MobileConfigMode(self):
		return self.__getattr__("MobileConfigMode")

	@cached_property
	def MobileCountry(self):
		return self.__getattr__("MobileCountry")

	@cached_property
	def MobileProvider(self):
		return self.__getattr__("MobileProvider")

	@cached_property
	def MobileApn(self):
		return self.__getattr__("MobileApn")

	@cached_property
	def MobilePhone(self):
		return self.__getattr__("MobilePhone")

	@cached_property
	def MobileAuth(self):
		return self.__getattr__("MobileAuth")

	@cached_property
	def MobileUsername(self):
		return self.__getattr__("MobileUsername")

	@cached_property
	def MobilePassword(self):
		return self.__getattr__("MobilePassword")

	@cached_property
	def MobileSimPin(self):
		return self.__getattr__("MobileSimPin")

	@cached_property
	def BiometricAuth(self):
		return self.__getattr__("BiometricAuth")

	@cached_property
	def EapAuthentication(self):
		return self.__getattr__("EapAuthentication")

	@cached_property
	def HttpAuthentication(self):
		return self.__getattr__("HttpAuthentication")

	@cached_property
	def ConnectionMode(self):
		return self.__getattr__("ConnectionMode")

	@cached_property
	def ConnectAtBoot(self):
		return self.__getattr__("ConnectAtBoot")

	@cached_property
	def Timeout(self):
		return self.__getattr__("Timeout")

	@cached_property
	def OtpToken(self):
		return self.__getattr__("OtpToken")

	@cached_property
	def SwapOtpPin(self):
		return self.__getattr__("SwapOtpPin")

	@cached_property
	def HideUserId(self):
		return self.__getattr__("HideUserId")

	@cached_property
	def TunnelTrafficMonitoring(self):
		return self.__getattr__("TunnelTrafficMonitoring")

	@cached_property
	def TunnelTrafficMonitoringAddr(self):
		return self.__getattr__("TunnelTrafficMonitoringAddr")

	@cached_property
	def PermitIpBroadcast(self):
		return self.__getattr__("PermitIpBroadcast")

	@cached_property
	def QoSConfig(self):
		return self.__getattr__("QoSConfig")

	@cached_property
	def PkiConfig(self):
		return self.__getattr__("PkiConfig")

	@cached_property
	def ExchangeMode(self):
		return self.__getattr__("ExchangeMode")

	@cached_property
	def VpnIpVersion(self):
		return self.__getattr__("VpnIpVersion")

	@cached_property
	def IkeV2Authentication(self):
		return self.__getattr__("IkeV2Authentication")

	@cached_property
	def IkePolicy(self):
		return self.__getattr__("IkePolicy")

	@cached_property
	def IkeV2Policy(self):
		return self.__getattr__("IkeV2Policy")

	@cached_property
	def IkeDhGroup(self):
		return self.__getattr__("IkeDhGroup")

	@cached_property
	def IkeLifeTimeDuration(self):
		return self.__getattr__("IkeLifeTimeDuration")

	@cached_property
	def IpSecPolicy(self):
		return self.__getattr__("IpSecPolicy")

	@cached_property
	def PFS(self):
		return self.__getattr__("PFS")

	@cached_property
	def IpSecLifeTimeType(self):
		return self.__getattr__("IpSecLifeTimeType")

	@cached_property
	def IpSecLifeTimeDuration(self):
		return self.__getattr__("IpSecLifeTimeDuration")

	@cached_property
	def IpSecLifeTimeVolume(self):
		return self.__getattr__("IpSecLifeTimeVolume")

	@cached_property
	def UseCompression(self):
		return self.__getattr__("UseCompression")

	@cached_property
	def IkeIdType(self):
		return self.__getattr__("IkeIdType")

	@cached_property
	def IkeId(self):
		return self.__getattr__("IkeId")

	@cached_property
	def VpnUserId(self):
		return self.__getattr__("VpnUserId")

	@cached_property
	def VpnPassword(self):
		return self.__getattr__("VpnPassword")

	@cached_property
	def VpnPwSave(self):
		return self.__getattr__("VpnPwSave")

	@cached_property
	def VpnSuffix(self):
		return self.__getattr__("VpnSuffix")

	@cached_property
	def TunnelSecret(self):
		return self.__getattr__("TunnelSecret")

	@cached_property
	def VpnRemIpAddr(self):
		return self.__getattr__("VpnRemIpAddr")

	@cached_property
	def AuthFromCert(self):
		return self.__getattr__("AuthFromCert")

	@cached_property
	def SamlUrl(self):
		return self.__getattr__("SamlUrl")

	@cached_property
	def SamlRealm(self):
		return self.__getattr__("SamlRealm")

	@cached_property
	def SplitTunnelingModeV4(self):
		return self.__getattr__("SplitTunnelingModeV4")

	@cached_property
	def SplitTunnelingNetworksV4(self):
		return self.__getattr__("SplitTunnelingNetworksV4")

	@cached_property
	def VpnTunnelRelay(self):
		return self.__getattr__("VpnTunnelRelay")

	@cached_property
	def SplitTunnelingModeV6(self):
		return self.__getattr__("SplitTunnelingModeV6")

	@cached_property
	def SplitTunnelingNetworksV6(self):
		return self.__getattr__("SplitTunnelingNetworksV6")

	@cached_property
	def VpnByPassConfig(self):
		return self.__getattr__("VpnByPassConfig")

	@cached_property
	def UseXAUTH(self):
		return self.__getattr__("UseXAUTH")

	@cached_property
	def UseIkePort(self):
		return self.__getattr__("UseIkePort")

	@cached_property
	def DisableDPD(self):
		return self.__getattr__("DisableDPD")

	@cached_property
	def DPDInterval(self):
		return self.__getattr__("DPDInterval")

	@cached_property
	def DPDRetries(self):
		return self.__getattr__("DPDRetries")

	@cached_property
	def AntiReplay(self):
		return self.__getattr__("AntiReplay")

	@cached_property
	def PathFinder(self):
		return self.__getattr__("PathFinder")

	@cached_property
	def UseRFC7427(self):
		return self.__getattr__("UseRFC7427")

	@cached_property
	def RFC7427Padding(self):
		return self.__getattr__("RFC7427Padding")

	@cached_property
	def IkeV2AuthPrf(self):
		return self.__getattr__("IkeV2AuthPrf")

	@cached_property
	def AssignPrivateIpAddress(self):
		return self.__getattr__("AssignPrivateIpAddress")

	@cached_property
	def PrivateIpAddess(self):
		return self.__getattr__("PrivateIpAddess")

	@cached_property
	def PrivateIpMask(self):
		return self.__getattr__("PrivateIpMask")

	@cached_property
	def DNS1(self):
		return self.__getattr__("DNS1")

	@cached_property
	def DNS2(self):
		return self.__getattr__("DNS2")

	@cached_property
	def MgmSrv(self):
		return self.__getattr__("MgmSrv")

	@cached_property
	def MgmSrv2(self):
		return self.__getattr__("MgmSrv2")

	@cached_property
	def DomainName(self):
		return self.__getattr__("DomainName")

	@cached_property
	def DomainInTunnel(self):
		return self.__getattr__("DomainInTunnel")

	@cached_property
	def WebProxyType(self):
		return self.__getattr__("WebProxyType")

	@cached_property
	def WebProxyAutoURL(self):
		return self.__getattr__("WebProxyAutoURL")

	@cached_property
	def WebProxyHttp(self):
		return self.__getattr__("WebProxyHttp")

	@cached_property
	def WebProxyHttps(self):
		return self.__getattr__("WebProxyHttps")

	@cached_property
	def WebProxyExceptions(self):
		return self.__getattr__("WebProxyExceptions")

	@cached_property
	def HASupport(self):
		return self.__getattr__("HASupport")

	@cached_property
	def HAServer1(self):
		return self.__getattr__("HAServer1")

	@cached_property
	def HAServer2(self):
		return self.__getattr__("HAServer2")

	@cached_property
	def DveSecret(self):
		return self.__getattr__("DveSecret")

	@cached_property
	def HaUseLastGateway(self):
		return self.__getattr__("HaUseLastGateway")

	@cached_property
	def CertSubject(self):
		return self.__getattr__("CertSubject")

	@cached_property
	def CertIssuer(self):
		return self.__getattr__("CertIssuer")

	@cached_property
	def CertFingerprint(self):
		return self.__getattr__("CertFingerprint")

	@cached_property
	def CertFingerPrintHash(self):
		return self.__getattr__("CertFingerPrintHash")

	@cached_property
	def ProtectLan(self):
		return self.__getattr__("ProtectLan")

	@cached_property
	def FwOnlyVpn(self):
		return self.__getattr__("FwOnlyVpn")

	@cached_property
	def FwRasOnlyVpn(self):
		return self.__getattr__("FwRasOnlyVpn")

	@cached_property
	def SrvCreateEntry(self):
		return self.__getattr__("SrvCreateEntry")

	@cached_property
	def SrvNasIpAddr(self):
		return self.__getattr__("SrvNasIpAddr")

	@cached_property
	def SrvNasParam1(self):
		return self.__getattr__("SrvNasParam1")

	@cached_property
	def SrvNasParam2(self):
		return self.__getattr__("SrvNasParam2")

	@cached_property
	def SrvNasParam3(self):
		return self.__getattr__("SrvNasParam3")

	@cached_property
	def SrvNasParam4(self):
		return self.__getattr__("SrvNasParam4")

	@cached_property
	def SrvNasParam5(self):
		return self.__getattr__("SrvNasParam5")

	@cached_property
	def SrvNasParam6(self):
		return self.__getattr__("SrvNasParam6")

	@cached_property
	def SrvNasParam7(self):
		return self.__getattr__("SrvNasParam7")

	@cached_property
	def SrvNasParam8(self):
		return self.__getattr__("SrvNasParam8")

	@cached_property
	def SrvVpnIpAddr(self):
		return self.__getattr__("SrvVpnIpAddr")

	@cached_property
	def SrvVpnParam1(self):
		return self.__getattr__("SrvVpnParam1")

	@cached_property
	def SrvVpnParam2(self):
		return self.__getattr__("SrvVpnParam2")

	@cached_property
	def SrvVpnParam3(self):
		return self.__getattr__("SrvVpnParam3")

	@cached_property
	def SrvVpnParam4(self):
		return self.__getattr__("SrvVpnParam4")

	@cached_property
	def SrvVpnParam5(self):
		return self.__getattr__("SrvVpnParam5")

	@cached_property
	def SrvVpnParam6(self):
		return self.__getattr__("SrvVpnParam6")

	@cached_property
	def SrvVpnParam7(self):
		return self.__getattr__("SrvVpnParam7")

	@cached_property
	def SrvVpnParam8(self):
		return self.__getattr__("SrvVpnParam8")

	@cached_property
	def SrvVpnParamSplitTunneling(self):
		return self.__getattr__("SrvVpnParamSplitTunneling")

	@cached_property
	def RadiusValidFrom(self):
		return self.__getattr__("RadiusValidFrom")

	@cached_property
	def RadiusValidUntil(self):
		return self.__getattr__("RadiusValidUntil")

	@cached_property
	def TwoFactAuthLang(self):
		return self.__getattr__("TwoFactAuthLang")

	@cached_property
	def TwoFactAuthId(self):
		return self.__getattr__("TwoFactAuthId")

	@cached_property
	def TimeOTPCreate(self):
		return self.__getattr__("TimeOTPCreate")

	@cached_property
	def TimeOTPDesc(self):
		return self.__getattr__("TimeOTPDesc")

	@cached_property
	def ParameterRights(self):
		return self.__getattr__("ParameterRights")

	@cached_property
	def RightsViewTabs(self):
		return self.__getattr__("RightsViewTabs")

	@cached_property
	def RightDisplay(self):
		return self.__getattr__("RightDisplay")

	@cached_property
	def RightDelete(self):
		return self.__getattr__("RightDelete")

	@cached_property
	def RightCopy(self):
		return self.__getattr__("RightCopy")

	@cached_property
	def RightUpdLockedParams(self):
		return self.__getattr__("RightUpdLockedParams")

	@cached_property
	def RightExport(self):
		return self.__getattr__("RightExport")

	@cached_property
	def UserParameters(self):
		return self.__getattr__("UserParameters")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientIkePolicyTemplatesHandler(BaseListFindHandler):
	'''Configuration of client IKE policy templates

	Methods
	-------
		createEntry()
			Creates a new ClientIkePolicyTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, clnttemplid):
		url = "client-mgm/{groupid}/client-templs/{clnttemplid}/ikev1".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clnttemplid = clnttemplid

	def createEntry(self):
		'''Creates a new ClientIkePolicyTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientIkePolicyTemplate(self, self._groupid, self._clnttemplid)


class ClientIkePolicyTemplate(LazyListEntry):
	'''Client IKE policy template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		Proposals : array from model IKEv1Proposal
			Proposals
		RightDisplay : boolean
			Entry may be displayed
		RightModify : boolean
			Entry may be modified
		RightDelete : boolean
			Entry may be deleted
	'''

	def __init__(self, getHandler, groupid, clnttemplid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"Proposals" : [],
			"RightDisplay" : True,
			"RightModify" : True,
			"RightDelete" : True,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def Proposals(self):
		return self.__getattr__("Proposals")

	@cached_property
	def RightDisplay(self):
		return self.__getattr__("RightDisplay")

	@cached_property
	def RightModify(self):
		return self.__getattr__("RightModify")

	@cached_property
	def RightDelete(self):
		return self.__getattr__("RightDelete")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientIkev2PolicyTemplatesHandler(BaseListFindHandler):
	'''Configuration of client IKEv2 policy templates

	Methods
	-------
		createEntry()
			Creates a new ClientIkeV2PolicyTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, clnttemplid):
		url = "client-mgm/{groupid}/client-templs/{clnttemplid}/ikev2".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clnttemplid = clnttemplid

	def createEntry(self):
		'''Creates a new ClientIkeV2PolicyTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientIkeV2PolicyTemplate(self, self._groupid, self._clnttemplid)


class ClientIkeV2PolicyTemplate(LazyListEntry):
	'''Client IKEv2 policy template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		Proposals : array from model IKEv2Proposal
			Proposals
		RightDisplay : boolean
			Entry may be displayed
		RightModify : boolean
			Entry may be modified
		RightDelete : boolean
			Entry may be deleted
	'''

	def __init__(self, getHandler, groupid, clnttemplid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"Proposals" : [],
			"RightDisplay" : True,
			"RightModify" : True,
			"RightDelete" : True,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def Proposals(self):
		return self.__getattr__("Proposals")

	@cached_property
	def RightDisplay(self):
		return self.__getattr__("RightDisplay")

	@cached_property
	def RightModify(self):
		return self.__getattr__("RightModify")

	@cached_property
	def RightDelete(self):
		return self.__getattr__("RightDelete")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientIpsecPolicyTemplatesHandler(BaseListFindHandler):
	'''Configuration of client IPsec policy templates

	Methods
	-------
		createEntry()
			Creates a new ClientIpsecPolicyTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, clnttemplid):
		url = "client-mgm/{groupid}/client-templs/{clnttemplid}/ipsecs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clnttemplid = clnttemplid

	def createEntry(self):
		'''Creates a new ClientIpsecPolicyTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientIpsecPolicyTemplate(self, self._groupid, self._clnttemplid)


class ClientIpsecPolicyTemplate(LazyListEntry):
	'''Client IPsec policy template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		Proposals : array from model IPsecProposal
			Proposals
		RightDisplay : boolean
			Entry may be displayed
		RightModify : boolean
			Entry may be modified
		RightDelete : boolean
			Entry may be deleted
	'''

	def __init__(self, getHandler, groupid, clnttemplid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"Proposals" : [],
			"RightDisplay" : True,
			"RightModify" : True,
			"RightDelete" : True,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def Proposals(self):
		return self.__getattr__("Proposals")

	@cached_property
	def RightDisplay(self):
		return self.__getattr__("RightDisplay")

	@cached_property
	def RightModify(self):
		return self.__getattr__("RightModify")

	@cached_property
	def RightDelete(self):
		return self.__getattr__("RightDelete")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientWifiTemplatesHandler(BaseListFindHandler):
	'''Configuration of client Wi-Fi profile templates

	Methods
	-------
		createEntry()
			Creates a new ClientWiFiTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, clnttemplid):
		url = "client-mgm/{groupid}/client-templs/{clnttemplid}/wifis".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clnttemplid = clnttemplid

	def createEntry(self):
		'''Creates a new ClientWiFiTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientWiFiTemplate(self, self._groupid, self._clnttemplid)


class ClientWiFiTemplate(LazyListEntry):
	'''Configuration of a client Wi-Fi profile template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		SSID : string
			SSID
		PowerMode : integer
			Power Mode
			Enum Values: 0=medium, 1=high, 2=low
		ConnectionMode : integer
			Auto-Connect
			Enum Values: 0=manually, 1=automatic
		HiddenSSID : boolean
			Hidden SSID
		DisconnectByVpn : boolean
			Disconnect if VPN gets disconnected
		MeteredConnection : boolean
			Metered connection
		EncryptionType : integer
			Encryption WPA, ..
			Enum Values: 1=none, 2=WEP, 3=WPA, 4=WPA2, 5=WPA3
		EncryptionAuthType : integer
			Key Management PSK, EAP
			Enum Values: 1=Open System, 2=Shared Key, 3=EAP, 4=PSK
		EncryptionKeyFormat : integer
			Key Format
			Enum Values: 0=hex, 1=ascii
		EncryptionKey1 : string
			Key 1
		EncryptionKey2 : string
			Key 2
		EncryptionKey3 : string
			Key 3
		EncryptionKey4 : string
			Key 4
		DhcpMode : integer
			IP Address Automatically Assigned
			Enum Values: 0=manually, 1=automatic
		IpAddress : string with IP address
			IP Address
		NetworkMask : string with IP address
			Subnet Mask
		DefaultGateway : string with IP address
			Default Gateway
		DnsMode : integer
			DNS/WINS Server Address Automatically Assigned
			Enum Values: 0=manually, 1=automatic
		Dns1 : string with IP address
			Preferred DNS Server
		Dns2 : string with IP address
			Alternate DNS Server
		Wins1 : string with IP address
			Preferred WINS Server
		Wins2 : string with IP address
			Alternate WINS Server
		AuthType : integer
			Hotspot
			Enum Values: 0=none, 1=other, 2=T-Mobile
		AuthUserId : string
			User ID
		AuthPassword : string
			Password
		AuthScript : string
			Script File Name
		UserParameters : object
			User parameters
		ParameterRights : object
			Parameter rights
		RightViewTabGeneral : boolean
			View tab general
		RightViewTabEncryption : boolean
			View tab encryption
		RightViewTabIpAddrs : boolean
			View tab IP addresses
		RightViewTabAuth : boolean
			View tab authentication
		RightDisplay : boolean
			Wi-Fi Profile may be displayed
		RightCopy : boolean
			Wi-Fi Profile may be copied
		RightDelete : boolean
			Wi-Fi Profile may be deleted
		UpdLockParams : boolean
			Only update locked parameters
	'''

	def __init__(self, getHandler, groupid, clnttemplid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"SSID" : "",
			"PowerMode" : "medium",
			"ConnectionMode" : "manually",
			"HiddenSSID" : False,
			"DisconnectByVpn" : False,
			"MeteredConnection" : False,
			"EncryptionType" : "none",
			"EncryptionAuthType" : "Open System",
			"EncryptionKeyFormat" : "ascii",
			"EncryptionKey1" : "",
			"EncryptionKey2" : "",
			"EncryptionKey3" : "",
			"EncryptionKey4" : "",
			"DhcpMode" : "automatic",
			"IpAddress" : "0.0.0.0",
			"NetworkMask" : "0.0.0.0",
			"DefaultGateway" : "0.0.0.0",
			"DnsMode" : "automatic",
			"Dns1" : "0.0.0.0",
			"Dns2" : "0.0.0.0",
			"Wins1" : "0.0.0.0",
			"Wins2" : "0.0.0.0",
			"AuthType" : "none",
			"AuthUserId" : "",
			"AuthPassword" : "",
			"AuthScript" : "",
			"UserParameters" : {},
			"ParameterRights" : {},
			"RightViewTabGeneral" : True,
			"RightViewTabEncryption" : True,
			"RightViewTabIpAddrs" : True,
			"RightViewTabAuth" : True,
			"RightDisplay" : True,
			"RightCopy" : True,
			"RightDelete" : True,
			"UpdLockParams" : False,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def SSID(self):
		return self.__getattr__("SSID")

	@cached_property
	def PowerMode(self):
		return self.__getattr__("PowerMode")

	@cached_property
	def ConnectionMode(self):
		return self.__getattr__("ConnectionMode")

	@cached_property
	def HiddenSSID(self):
		return self.__getattr__("HiddenSSID")

	@cached_property
	def DisconnectByVpn(self):
		return self.__getattr__("DisconnectByVpn")

	@cached_property
	def MeteredConnection(self):
		return self.__getattr__("MeteredConnection")

	@cached_property
	def EncryptionType(self):
		return self.__getattr__("EncryptionType")

	@cached_property
	def EncryptionAuthType(self):
		return self.__getattr__("EncryptionAuthType")

	@cached_property
	def EncryptionKeyFormat(self):
		return self.__getattr__("EncryptionKeyFormat")

	@cached_property
	def EncryptionKey1(self):
		return self.__getattr__("EncryptionKey1")

	@cached_property
	def EncryptionKey2(self):
		return self.__getattr__("EncryptionKey2")

	@cached_property
	def EncryptionKey3(self):
		return self.__getattr__("EncryptionKey3")

	@cached_property
	def EncryptionKey4(self):
		return self.__getattr__("EncryptionKey4")

	@cached_property
	def DhcpMode(self):
		return self.__getattr__("DhcpMode")

	@cached_property
	def IpAddress(self):
		return self.__getattr__("IpAddress")

	@cached_property
	def NetworkMask(self):
		return self.__getattr__("NetworkMask")

	@cached_property
	def DefaultGateway(self):
		return self.__getattr__("DefaultGateway")

	@cached_property
	def DnsMode(self):
		return self.__getattr__("DnsMode")

	@cached_property
	def Dns1(self):
		return self.__getattr__("Dns1")

	@cached_property
	def Dns2(self):
		return self.__getattr__("Dns2")

	@cached_property
	def Wins1(self):
		return self.__getattr__("Wins1")

	@cached_property
	def Wins2(self):
		return self.__getattr__("Wins2")

	@cached_property
	def AuthType(self):
		return self.__getattr__("AuthType")

	@cached_property
	def AuthUserId(self):
		return self.__getattr__("AuthUserId")

	@cached_property
	def AuthPassword(self):
		return self.__getattr__("AuthPassword")

	@cached_property
	def AuthScript(self):
		return self.__getattr__("AuthScript")

	@cached_property
	def UserParameters(self):
		return self.__getattr__("UserParameters")

	@cached_property
	def ParameterRights(self):
		return self.__getattr__("ParameterRights")

	@cached_property
	def RightViewTabGeneral(self):
		return self.__getattr__("RightViewTabGeneral")

	@cached_property
	def RightViewTabEncryption(self):
		return self.__getattr__("RightViewTabEncryption")

	@cached_property
	def RightViewTabIpAddrs(self):
		return self.__getattr__("RightViewTabIpAddrs")

	@cached_property
	def RightViewTabAuth(self):
		return self.__getattr__("RightViewTabAuth")

	@cached_property
	def RightDisplay(self):
		return self.__getattr__("RightDisplay")

	@cached_property
	def RightCopy(self):
		return self.__getattr__("RightCopy")

	@cached_property
	def RightDelete(self):
		return self.__getattr__("RightDelete")

	@cached_property
	def UpdLockParams(self):
		return self.__getattr__("UpdLockParams")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientPkiConfigurationTemplatesHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Configuration of client certificate templates

	Methods
	-------
		createEntry()
			Creates a new ClientPkiConfigurationTemplate entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, clnttemplid):
		url = "client-mgm/{groupid}/client-templs/{clnttemplid}/pki-configs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clnttemplid = clnttemplid

	def createEntry(self):
		'''Creates a new ClientPkiConfigurationTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientPkiConfigurationTemplate(self, self._groupid, self._clnttemplid)


class ClientPkiConfigurationTemplate(LazyModifiableListEntry):
	'''Configuration of a client certificate template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		CertType : integer
			Certificate
			Enum Values: 0=none, 1=PC/SC, 2=PKCS#12, 3=PKCS#11, 4=Entrust, 5=CSP, 8=CSP User Store, 6=DATEV, 9=Keychain
		CertNr : integer
			Certificate number
		SmartcardReader : string
			Smartcard reader
		Pkcs12Filename : string
			PKCS#12 Filename
		CertPkcs12Select : boolean
			Enable certificate selection
		CertPkcs12Path : string
			PKCS#12 Certificate path
		Pkcs11Modul : string
			PKCS#11 library
		Pkcs11SlotIndex : integer
			Slot index
		CspProvider : string
			CSP provider
		CertSubjectMatch : string
			Subject CN
		CertIssuerMatch : string
			Issuer CN
		CertExtKeyUsage : string
			Extended Key Usage Match
		KeyChainHash : string
			Keychain Hash
		PinQuest : integer
			PIN Request at each connection
		AllowUserPinChange : boolean
			Modify PIN
		PinPolicy : integer
			PIN policy
		WarningBeforeCertExpires : boolean
			Enable warning before certificate expires
		CertExpireWarnDays : integer
			Days before certificate expiration warning
		ComputerCertType : integer
			Computer Certificate Type
			Enum Values: 0=none, 2=PKCS#12, 4=Entrust, 5=CSP
		ComputerPkcs12Filename : string
			Computer PKCS#12 Filename
		ComputerSubjectMatch : string
			Computer Subject CN
		ComputerIssuerMatch : string
			Computer Issuer CN
		ComputerExtKeyUsage : string
			Extended Key Usage
		UserParameters : object
			User parameters
		ParameterRights : object
			Parameter rights
		RightsViewTabs : object
			View tabs
		RightDisplay : boolean
			PKI configuration may be displayed
		RightCopy : boolean
			PKI configuration may be copied
		RightDelete : boolean
			PKI configuration may be deleted
	'''

	def __init__(self, getHandler, groupid, clnttemplid):
		LazyModifiableListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"CertType" : "none",
			"CertNr" : 1,
			"SmartcardReader" : "",
			"Pkcs12Filename" : "",
			"CertPkcs12Select" : False,
			"CertPkcs12Path" : "%CertDir%",
			"Pkcs11Modul" : "",
			"Pkcs11SlotIndex" : 0,
			"CspProvider" : "",
			"CertSubjectMatch" : "",
			"CertIssuerMatch" : "",
			"CertExtKeyUsage" : "",
			"KeyChainHash" : "",
			"PinQuest" : 0,
			"AllowUserPinChange" : False,
			"PinPolicy" : 6,
			"WarningBeforeCertExpires" : True,
			"CertExpireWarnDays" : 30,
			"ComputerCertType" : "none",
			"ComputerPkcs12Filename" : "",
			"ComputerSubjectMatch" : "",
			"ComputerIssuerMatch" : "",
			"ComputerExtKeyUsage" : "",
			"UserParameters" : {},
			"ParameterRights" : {},
			"RightsViewTabs" : {},
			"RightDisplay" : True,
			"RightCopy" : True,
			"RightDelete" : True,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def CertType(self):
		return self.__getattr__("CertType")

	@cached_property
	def CertNr(self):
		return self.__getattr__("CertNr")

	@cached_property
	def SmartcardReader(self):
		return self.__getattr__("SmartcardReader")

	@cached_property
	def Pkcs12Filename(self):
		return self.__getattr__("Pkcs12Filename")

	@cached_property
	def CertPkcs12Select(self):
		return self.__getattr__("CertPkcs12Select")

	@cached_property
	def CertPkcs12Path(self):
		return self.__getattr__("CertPkcs12Path")

	@cached_property
	def Pkcs11Modul(self):
		return self.__getattr__("Pkcs11Modul")

	@cached_property
	def Pkcs11SlotIndex(self):
		return self.__getattr__("Pkcs11SlotIndex")

	@cached_property
	def CspProvider(self):
		return self.__getattr__("CspProvider")

	@cached_property
	def CertSubjectMatch(self):
		return self.__getattr__("CertSubjectMatch")

	@cached_property
	def CertIssuerMatch(self):
		return self.__getattr__("CertIssuerMatch")

	@cached_property
	def CertExtKeyUsage(self):
		return self.__getattr__("CertExtKeyUsage")

	@cached_property
	def KeyChainHash(self):
		return self.__getattr__("KeyChainHash")

	@cached_property
	def PinQuest(self):
		return self.__getattr__("PinQuest")

	@cached_property
	def AllowUserPinChange(self):
		return self.__getattr__("AllowUserPinChange")

	@cached_property
	def PinPolicy(self):
		return self.__getattr__("PinPolicy")

	@cached_property
	def WarningBeforeCertExpires(self):
		return self.__getattr__("WarningBeforeCertExpires")

	@cached_property
	def CertExpireWarnDays(self):
		return self.__getattr__("CertExpireWarnDays")

	@cached_property
	def ComputerCertType(self):
		return self.__getattr__("ComputerCertType")

	@cached_property
	def ComputerPkcs12Filename(self):
		return self.__getattr__("ComputerPkcs12Filename")

	@cached_property
	def ComputerSubjectMatch(self):
		return self.__getattr__("ComputerSubjectMatch")

	@cached_property
	def ComputerIssuerMatch(self):
		return self.__getattr__("ComputerIssuerMatch")

	@cached_property
	def ComputerExtKeyUsage(self):
		return self.__getattr__("ComputerExtKeyUsage")

	@cached_property
	def UserParameters(self):
		return self.__getattr__("UserParameters")

	@cached_property
	def ParameterRights(self):
		return self.__getattr__("ParameterRights")

	@cached_property
	def RightsViewTabs(self):
		return self.__getattr__("RightsViewTabs")

	@cached_property
	def RightDisplay(self):
		return self.__getattr__("RightDisplay")

	@cached_property
	def RightCopy(self):
		return self.__getattr__("RightCopy")

	@cached_property
	def RightDelete(self):
		return self.__getattr__("RightDelete")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientVpnByPassTemplatesHandler(BaseListFindHandler):
	'''Configuration of client VPN bypass templates

	Methods
	-------
		createEntry()
			Creates a new ClientVpnByPassTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, clnttemplid):
		url = "client-mgm/{groupid}/client-templs/{clnttemplid}/vpn-bypass".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clnttemplid = clnttemplid

	def createEntry(self):
		'''Creates a new ClientVpnByPassTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientVpnByPassTemplate(self, self._groupid, self._clnttemplid)


class ClientVpnByPassTemplate(LazyListEntry):
	'''Configuration of a client VPN bypass template

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		Entries : array from model VpnByPassEntry
			Entries
		RightDisplay : boolean
			Configuration may be displayed
		RightModify : boolean
			Configuration may be modified
		RightCopy : boolean
			Configuration may be copied
		RightDelete : boolean
			Configuration may be deleted
	'''

	def __init__(self, getHandler, groupid, clnttemplid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"Entries" : [],
			"RightDisplay" : True,
			"RightModify" : True,
			"RightCopy" : True,
			"RightDelete" : True,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def Entries(self):
		return self.__getattr__("Entries")

	@cached_property
	def RightDisplay(self):
		return self.__getattr__("RightDisplay")

	@cached_property
	def RightModify(self):
		return self.__getattr__("RightModify")

	@cached_property
	def RightCopy(self):
		return self.__getattr__("RightCopy")

	@cached_property
	def RightDelete(self):
		return self.__getattr__("RightDelete")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientQoSTemplatesHandler(BaseListFindHandler):
	'''Configuration of quality of service profile

	Methods
	-------
		createEntry()
			Creates a new ClientQoSTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid, clnttemplid):
		url = "client-mgm/{groupid}/client-templs/{clnttemplid}/qos".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clnttemplid = clnttemplid

	def createEntry(self):
		'''Creates a new ClientQoSTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientQoSTemplate(self, self._groupid, self._clnttemplid)


class ClientQoSTemplate(LazyListEntry):
	'''Client quality of service profile

	Attributes [read-only]
	----------------------
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		Name : string
			Name
		MaxRate : integer
			Max Rate
		Groups : array from model QoSGroups
			Groups
		RightDisplay : boolean
			Configuration may be displayed
		RightModify : boolean
			Configuration may be modified
		RightCopy : boolean
			Configuration may be copied
		RightDelete : boolean
			Configuration may be deleted
	'''

	def __init__(self, getHandler, groupid, clnttemplid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"MaxRate" : 6400,
			"Groups" : [],
			"RightDisplay" : True,
			"RightModify" : True,
			"RightCopy" : True,
			"RightDelete" : True,
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def MaxRate(self):
		return self.__getattr__("MaxRate")

	@cached_property
	def Groups(self):
		return self.__getattr__("Groups")

	@cached_property
	def RightDisplay(self):
		return self.__getattr__("RightDisplay")

	@cached_property
	def RightModify(self):
		return self.__getattr__("RightModify")

	@cached_property
	def RightCopy(self):
		return self.__getattr__("RightCopy")

	@cached_property
	def RightDelete(self):
		return self.__getattr__("RightDelete")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class AdminCertificatesHandler(BaseListFindHandler):
	'''Configuration of administrator certificates

	Methods
	-------
		createEntry()
			Creates a new AdminCertificate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "client-mgm/{groupid}/admin-certs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new AdminCertificate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return AdminCertificate(self, self._groupid)


class AdminCertificate(LazyListEntry):
	'''List of administrator certificates

	Attributes [writable]
	---------------------
		Name : string
			Name
		FingerPrint : string
			Fingerprint (SHA2-256)
		NotAfter : string
			Not After
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"FingerPrint" : "",
			"NotAfter" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def FingerPrint(self):
		return self.__getattr__("FingerPrint")

	@cached_property
	def NotAfter(self):
		return self.__getattr__("NotAfter")


class ClientConfigurationsHandler(BaseListFindHandler, BaseListUpdateHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Management of clients

	Methods
	-------
		createEntry()
			Creates a new ClientConfiguration entry object.
		generate_all_configs()
			Generates all client configurations in a this SEM group
	
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
		url = "client-mgm/{groupid}/clients".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		
	def generate_all_configs(self):
		'''Generates all client configurations in a this SEM group'''
		return self._callFunction('/generate-all-configs')

	def createEntry(self):
		'''Creates a new ClientConfiguration entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientConfiguration(self, self._groupid)


class ClientConfiguration(LazyModifiableListEntry):
	'''Configuration of a client

	Attributes [read-only]
	----------------------
		UserType : integer
			User Type
			Enum Values: 0=Enterprise Client, 11=VS GovNet Connector Client
		ProductGroup : integer
			Product Group
			Enum Values: 2=Client for Windows, 14=Client for Linux, 21=Client for macOS, 22=Client for Android, 25=Client for iOS
		ProductType : integer
			ProductType
			Enum Values: 3=NCP Secure Enterprise Client, 2=NCP Dynamic Net Guard, 11=NCP Secure GovNet Client, 259=NCP VS GovNet Connector, 1245187=NCP Exclusive Remote Access Client, 131075=Telekom Secure Client, 131074=Telekom Dynamic Net Guard
		SoftwareVersion : string
			Software Version
		UserParameters : object
			User parameters
		SWProduct : integer
			Installed Software Product
			Enum Values: 2=Windows Client, 14=Linux Client, 21=macOS Client, 22=Android Client, 25=iOS Client
		SWVersion : string
			Version of the installed Software
		SWBuildInfo : string
			Build Information about the installed Software
		ConfigDescription : string
			Description of configuration
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info
		AuthenticationCode : string
			Authentication Code
		AuthenticationCodeValidFrom : time
			Authentication Code valid from
		AuthenticationCodeExpires : time
			Authentication Code valid to
		ConfigLastChangeTime : time
			Time of last configuration change
		ConfigCreationTime : time
			Time of last configuration to be generated
		ConfigDownloadTime : time
			Download time of last configuration
		LastUpdateClientLogin : time
			Time of last update client login
		RSUSecretConfigured : boolean
			Flag, if RSU secret configured

	Attributes [writable]
	---------------------
		Name : string
			Name
		Template : string or integer from ClientTemplates
			Template
		RsuID : string
			ID for personalized configuration (RSUID)
		SoftwareUpdateList : string or integer from SoftwareUpdateLists
			Software Update List
		FirewallTemplate : string or integer from FirewallTemplates
			Firewall Template
		ShowCBO : integer
			Enable Custom Branding Option
		UnlockUserId : string
			Unlock User ID
		UnlockPassword : string
			Unlock Password
		ShowNewCfgMsg : boolean
			Show message if user has received a new configuration
		UseLeaseLicense : boolean
			Use lease license
		DistribLicKeys : boolean
			Automatic distribution of license keys
		ModuleDialer : boolean
			Module Dialer
		ModuleWiFi : boolean
			Module Wi Fi
		ModuleEAP : boolean
			Module EAP
		ModuleFirewall : boolean
			Module Firewall
		ModuleVPN : boolean
			Module VPN
		WiFiActivate : boolean
			Wi-Fi
		WiFiDisableAdapter : boolean
			Disable Wi-Fi when LAN cable is connected
		WiFiEnableHotspot : boolean
			Enable Hotspot detection
		EapState : integer
			IEEE 802.1x authentication (EAP)
			Enum Values: 0=off, 1=all, 2=WiFi, 3=LAN
		EapId : string
			EAP identity
		EapPassword : string
			EAP password
		InstallCredProv : boolean
			Install NCP Credential Provider for connection dialog before Windows logon
		LogonShow : boolean
			Show connection dialog before Windows logon
		LogonUseVpnId : boolean
			Logon use VPN User ID
		LogonUseVpnPw : boolean
			Use VPN Password for Windows logon
		LogonUserId : string
			User ID
		LogonPassword : string
			Password
		LogonDomain : string
			Domain
		LogoffAfterDisconnect : boolean
			Disconnect after Logoff
		LogonResetPW : boolean
			Logon Reset PW
		LogonStartAppl : boolean
			External Applications or Batch Files
		LogonStartAppls : array
			Logon Start Applications
		LogonDomainWait : boolean
			Logon Domain Wait
		LogonDomainWaitTime : integer
			Logon Domain Wait Time
		LogonEAPWait : boolean
			Logon EAP Wait
		LogonVistaMax : boolean
			Logon Vista Max
		LogonShowPreSelIconMax : boolean
			Logon Show Pre Sel Icon Max
		LogonAutoDlgOpen : boolean
			Logon Auto Dlg Open
		LogonRights : boolean
			User rights
		LanUpdateMgmSrv1 : string
			Primary Management Server
		LanUpdateMgmSrv2 : string
			Secondary Management Server
		LanUpdRsuID : string
			User ID
		LanUpdAutoAuthCode : string
			Lan Upd Auto Auth Code
		MonitorAlwaysOnTop : boolean
			Monitor Always On Top
		ProxyActive : integer
			Proxy Active
		HttpProxies : array from model HttpProxy
			HTTP Proxies
		NetworkDiagnosticIPAddr : string with IP address
			Network Diagnostic IP Addr
		NetworkDiagnosticURL : string
			Network Diagnostic URL
		FreeDesc1 : string
			1. User Information
		FreeDesc2 : string
			2. User Information
		FreeDesc3 : string
			3. User Information
		FreeDesc4 : string
			4. User Information
		FreeDesc5 : string
			Free Desc5
		CustomParameters : string
			Custom Parameters

	Sub-Handlers
	------------
		clientProfiles
			Access ClientProfilesHandler
		clientWifiConfigurations
			Access ClientWifiConfigurationsHandler
		clientPkiConfigurations
			Access ClientPkiConfigurationsHandler
		clientVpnByPassProfiles
			Access ClientVpnByPassProfilesHandler
		auditLog
			Access AuditLogHandler

	Methods
	-------
		generate_config()
			Generates a client configuration
		set_auth_code(AuthenticationCode=None)
			Sets the authetication code for this client
		reset_rsu_secret()
			Resets the RSU secret of this client
	'''

	def __init__(self, getHandler, groupid):
		LazyModifiableListEntry.__init__(self, getHandler)
		self._groupid = groupid
		self._api = getHandler._api
		# Default values
		self._defaultValues = {
			"Name" : "",
			"UserType" : "Enterprise Client",
			"Template" : "0",
			"RsuID" : "",
			"SoftwareUpdateList" : "0",
			"FirewallTemplate" : "0",
			"ShowCBO" : 0,
			"UnlockUserId" : "",
			"UnlockPassword" : "",
			"ShowNewCfgMsg" : False,
			"ProductGroup" : 0,
			"ProductType" : "NCP Secure Enterprise Client",
			"SoftwareVersion" : "1210",
			"UseLeaseLicense" : False,
			"DistribLicKeys" : False,
			"ModuleDialer" : True,
			"ModuleWiFi" : True,
			"ModuleEAP" : True,
			"ModuleFirewall" : True,
			"ModuleVPN" : True,
			"WiFiActivate" : False,
			"WiFiDisableAdapter" : False,
			"WiFiEnableHotspot" : False,
			"EapState" : "off",
			"EapId" : "",
			"EapPassword" : "",
			"InstallCredProv" : False,
			"LogonShow" : False,
			"LogonUseVpnId" : False,
			"LogonUseVpnPw" : False,
			"LogonUserId" : "",
			"LogonPassword" : "",
			"LogonDomain" : "",
			"LogoffAfterDisconnect" : False,
			"LogonResetPW" : False,
			"LogonStartAppl" : False,
			"LogonStartAppls" : [],
			"LogonDomainWait" : False,
			"LogonDomainWaitTime" : 45,
			"LogonEAPWait" : False,
			"LogonVistaMax" : False,
			"LogonShowPreSelIconMax" : False,
			"LogonAutoDlgOpen" : False,
			"LogonRights" : False,
			"LanUpdateMgmSrv1" : "",
			"LanUpdateMgmSrv2" : "",
			"LanUpdRsuID" : "",
			"LanUpdAutoAuthCode" : "",
			"MonitorAlwaysOnTop" : False,
			"ProxyActive" : 0,
			"HttpProxies" : [],
			"NetworkDiagnosticIPAddr" : "0.0.0.0",
			"NetworkDiagnosticURL" : "",
			"FreeDesc1" : "",
			"FreeDesc2" : "",
			"FreeDesc3" : "",
			"FreeDesc4" : "",
			"FreeDesc5" : "",
			"CustomParameters" : "",
			"UserParameters" : {},
			"SWProduct" : 0,
			"SWVersion" : "",
			"SWBuildInfo" : "",
			"ConfigDescription" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
			"AuthenticationCode" : "",
			"AuthenticationCodeValidFrom" : "",
			"AuthenticationCodeExpires" : "",
			"ConfigLastChangeTime" : "",
			"ConfigCreationTime" : "",
			"ConfigDownloadTime" : "",
			"LastUpdateClientLogin" : "",
			"RSUSecretConfigured" : False,
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def UserType(self):
		return self.__getattr__("UserType")

	@cached_property
	def Template(self):
		return self.__getattr__("Template")

	@cached_property
	def RsuID(self):
		return self.__getattr__("RsuID")

	@cached_property
	def SoftwareUpdateList(self):
		return self.__getattr__("SoftwareUpdateList")

	@cached_property
	def FirewallTemplate(self):
		return self.__getattr__("FirewallTemplate")

	@cached_property
	def ShowCBO(self):
		return self.__getattr__("ShowCBO")

	@cached_property
	def UnlockUserId(self):
		return self.__getattr__("UnlockUserId")

	@cached_property
	def UnlockPassword(self):
		return self.__getattr__("UnlockPassword")

	@cached_property
	def ShowNewCfgMsg(self):
		return self.__getattr__("ShowNewCfgMsg")

	@cached_property
	def ProductGroup(self):
		return self.__getattr__("ProductGroup")

	@cached_property
	def ProductType(self):
		return self.__getattr__("ProductType")

	@cached_property
	def SoftwareVersion(self):
		return self.__getattr__("SoftwareVersion")

	@cached_property
	def UseLeaseLicense(self):
		return self.__getattr__("UseLeaseLicense")

	@cached_property
	def DistribLicKeys(self):
		return self.__getattr__("DistribLicKeys")

	@cached_property
	def ModuleDialer(self):
		return self.__getattr__("ModuleDialer")

	@cached_property
	def ModuleWiFi(self):
		return self.__getattr__("ModuleWiFi")

	@cached_property
	def ModuleEAP(self):
		return self.__getattr__("ModuleEAP")

	@cached_property
	def ModuleFirewall(self):
		return self.__getattr__("ModuleFirewall")

	@cached_property
	def ModuleVPN(self):
		return self.__getattr__("ModuleVPN")

	@cached_property
	def WiFiActivate(self):
		return self.__getattr__("WiFiActivate")

	@cached_property
	def WiFiDisableAdapter(self):
		return self.__getattr__("WiFiDisableAdapter")

	@cached_property
	def WiFiEnableHotspot(self):
		return self.__getattr__("WiFiEnableHotspot")

	@cached_property
	def EapState(self):
		return self.__getattr__("EapState")

	@cached_property
	def EapId(self):
		return self.__getattr__("EapId")

	@cached_property
	def EapPassword(self):
		return self.__getattr__("EapPassword")

	@cached_property
	def InstallCredProv(self):
		return self.__getattr__("InstallCredProv")

	@cached_property
	def LogonShow(self):
		return self.__getattr__("LogonShow")

	@cached_property
	def LogonUseVpnId(self):
		return self.__getattr__("LogonUseVpnId")

	@cached_property
	def LogonUseVpnPw(self):
		return self.__getattr__("LogonUseVpnPw")

	@cached_property
	def LogonUserId(self):
		return self.__getattr__("LogonUserId")

	@cached_property
	def LogonPassword(self):
		return self.__getattr__("LogonPassword")

	@cached_property
	def LogonDomain(self):
		return self.__getattr__("LogonDomain")

	@cached_property
	def LogoffAfterDisconnect(self):
		return self.__getattr__("LogoffAfterDisconnect")

	@cached_property
	def LogonResetPW(self):
		return self.__getattr__("LogonResetPW")

	@cached_property
	def LogonStartAppl(self):
		return self.__getattr__("LogonStartAppl")

	@cached_property
	def LogonStartAppls(self):
		return self.__getattr__("LogonStartAppls")

	@cached_property
	def LogonDomainWait(self):
		return self.__getattr__("LogonDomainWait")

	@cached_property
	def LogonDomainWaitTime(self):
		return self.__getattr__("LogonDomainWaitTime")

	@cached_property
	def LogonEAPWait(self):
		return self.__getattr__("LogonEAPWait")

	@cached_property
	def LogonVistaMax(self):
		return self.__getattr__("LogonVistaMax")

	@cached_property
	def LogonShowPreSelIconMax(self):
		return self.__getattr__("LogonShowPreSelIconMax")

	@cached_property
	def LogonAutoDlgOpen(self):
		return self.__getattr__("LogonAutoDlgOpen")

	@cached_property
	def LogonRights(self):
		return self.__getattr__("LogonRights")

	@cached_property
	def LanUpdateMgmSrv1(self):
		return self.__getattr__("LanUpdateMgmSrv1")

	@cached_property
	def LanUpdateMgmSrv2(self):
		return self.__getattr__("LanUpdateMgmSrv2")

	@cached_property
	def LanUpdRsuID(self):
		return self.__getattr__("LanUpdRsuID")

	@cached_property
	def LanUpdAutoAuthCode(self):
		return self.__getattr__("LanUpdAutoAuthCode")

	@cached_property
	def MonitorAlwaysOnTop(self):
		return self.__getattr__("MonitorAlwaysOnTop")

	@cached_property
	def ProxyActive(self):
		return self.__getattr__("ProxyActive")

	@cached_property
	def HttpProxies(self):
		return self.__getattr__("HttpProxies")

	@cached_property
	def NetworkDiagnosticIPAddr(self):
		return self.__getattr__("NetworkDiagnosticIPAddr")

	@cached_property
	def NetworkDiagnosticURL(self):
		return self.__getattr__("NetworkDiagnosticURL")

	@cached_property
	def FreeDesc1(self):
		return self.__getattr__("FreeDesc1")

	@cached_property
	def FreeDesc2(self):
		return self.__getattr__("FreeDesc2")

	@cached_property
	def FreeDesc3(self):
		return self.__getattr__("FreeDesc3")

	@cached_property
	def FreeDesc4(self):
		return self.__getattr__("FreeDesc4")

	@cached_property
	def FreeDesc5(self):
		return self.__getattr__("FreeDesc5")

	@cached_property
	def CustomParameters(self):
		return self.__getattr__("CustomParameters")

	@cached_property
	def UserParameters(self):
		return self.__getattr__("UserParameters")

	@cached_property
	def SWProduct(self):
		return self.__getattr__("SWProduct")

	@cached_property
	def SWVersion(self):
		return self.__getattr__("SWVersion")

	@cached_property
	def SWBuildInfo(self):
		return self.__getattr__("SWBuildInfo")

	@cached_property
	def ConfigDescription(self):
		return self.__getattr__("ConfigDescription")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")

	@cached_property
	def AuthenticationCode(self):
		return self.__getattr__("AuthenticationCode")

	@cached_property
	def AuthenticationCodeValidFrom(self):
		return self.__getattr__("AuthenticationCodeValidFrom")

	@cached_property
	def AuthenticationCodeExpires(self):
		return self.__getattr__("AuthenticationCodeExpires")

	@cached_property
	def ConfigLastChangeTime(self):
		return self.__getattr__("ConfigLastChangeTime")

	@cached_property
	def ConfigCreationTime(self):
		return self.__getattr__("ConfigCreationTime")

	@cached_property
	def ConfigDownloadTime(self):
		return self.__getattr__("ConfigDownloadTime")

	@cached_property
	def LastUpdateClientLogin(self):
		return self.__getattr__("LastUpdateClientLogin")

	@cached_property
	def RSUSecretConfigured(self):
		return self.__getattr__("RSUSecretConfigured")

	@cached_property
	def clientProfiles(self):
		'''Returns handler to access ClientProfiles'''
		return ClientProfilesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientWifiConfigurations(self):
		'''Returns handler to access ClientWifiConfigurations'''
		return ClientWifiConfigurationsHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientPkiConfigurations(self):
		'''Returns handler to access ClientPkiConfigurations'''
		return ClientPkiConfigurationsHandler(self._api, self._groupid, self.Id)

	@cached_property
	def clientVpnByPassProfiles(self):
		'''Returns handler to access ClientVpnByPassProfiles'''
		return ClientVpnByPassProfilesHandler(self._api, self._groupid, self.Id)

	@cached_property
	def auditLog(self):
		'''Returns handler to access AuditLog'''
		return AuditLogHandler(self._api, self._groupid)
			
	def generate_config(self):
		'''Generates a client configuration'''
		return self._callMethod('/generate-config')
			
	def set_auth_code(self, AuthenticationCode=None):
		'''Sets the authetication code for this client
			AuthenticationCode : string
				New authentication code
		'''
		return self._callMethod('/set-auth-code', AuthenticationCode=AuthenticationCode)
			
	def reset_rsu_secret(self):
		'''Resets the RSU secret of this client'''
		return self._callMethod('/reset-rsu-secret')


class ClientProfilesHandler(BaseListFindHandler, BaseListUpdateHandler):
	'''Configuration of client profiles

	Methods
	-------
		createEntry()
			Creates a new ClientProfile entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, clientid):
		url = "client-mgm/{groupid}/clients/{clientid}/profiles".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clientid = clientid

	def createEntry(self):
		'''Creates a new ClientProfile entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientProfile(self, self._groupid, self._clientid)


class ClientProfile(LazyModifiableListEntry):
	'''Configuration of a client profile

	Attributes [read-only]
	----------------------
		Name : string
			Name
		TimeOTPSecretUrl : string
			QR Code
		UserParameters : object
			User parameters
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		ProfileName : string
			Profile Name
		LinkType : integer
			Communication Medium
			Enum Values: 8=LAN, 18=mobile network, 20=WiFi, 21=automatic
		UseForAMD : boolean
			Profile for automatic media detection
		SeamlessRoaming : boolean
			Seamless Roaming
		KeepTunnel : boolean
			Disconnect the logical VPN tunnel when the connection is broken
		BootUser : integer
			Default Profile after System Reboot
			Enum Values: 0=off, 1=bootuser
		UseRas : integer
			Microsoft Dial-up Networking
			Enum Values: 0=never, 2=script, 1=always
		HideProfile : boolean
			Do not include this entry in the profile settings
		DialerUser : string
			Dial-up User ID
		DialerPw : string
			Dial-up Password
		DialerPhone : string
			Dial-up Phone Number
		RasFile : string
			RAS Script File
		HttpUsername : string
			HTTP User Name
		HttpPassword : string
			HTTP Password
		HttpScript : string
			HTTP Authentication Script
		Modem : string
			Modem Type
		ComPort : string
			Com Port
		Baudrate : integer
			Baud Rate
			Enum Values: 1200=1200, 2400=2400, 4800=4800, 9600=9600, 19200=19200, 38400=38400, 57600=57600, 115200=115200
		RlsComPort : boolean
			Release Com Port
		ModemInitStr : string
			Modem Init. String
		DialPrefix : string
			Dial Prefix
		MobileConfigMode : integer
			Configuration Mode
			Enum Values: 0=manuel, 1=list, 2=SIM card
		MobileCountry : integer
			Country
		MobileProvider : integer
			Provider
		MobileApn : string
			APN
		MobilePhone : string
			Dial-up number
		MobileAuth : integer
			Authentication
			Enum Values: 0=none, 1=PAP, 2=CHAP
		MobileUsername : string
			Mobile Username
		MobilePassword : string
			Mobile Password
		MobileSimPin : string
			SIM PIN
		BiometricAuth : boolean
			Fingerprint
		EapAuthentication : boolean
			EAP Authentication
		HttpAuthentication : boolean
			HTTP Authentication
		ConnectionMode : integer
			Connection Mode
			Enum Values: 0=manually, 1=automatic, 2=variable/automatic, 3=always, 4=variable/always
		ConnectAtBoot : boolean
			Connect at Boot
		Timeout : integer
			Inactivity Timeout (sec)
		OtpToken : integer
			OTP Token
			Enum Values: 0=off, 1=NAS, 2=VPN
		SwapOtpPin : boolean
			Swap OTP password and PIN
		HideUserId : boolean
			Hide username when prompted for credentials
		TunnelTrafficMonitoring : boolean
			Enable tunnel traffic monitoring
		TunnelTrafficMonitoringAddr : string
			Alternative IP address
		PermitIpBroadcast : boolean
			Permit IP Broadcast
		QoSConfig : string or integer from ClientQoSTemplates
			Quality of Service
		PkiConfig : string or integer from ClientPkiConfigurationTemplates
			Certificate configuration
		ExchangeMode : integer
			Exchange Mode
			Enum Values: 2=main mode, 4=aggressive mode, 34=IKEv2
		VpnIpVersion : integer
			Tunnel IP Version
			Enum Values: 1=IPv4, 2=IPv6, 3=both
		IkeV2Authentication : integer
			IKEv2 Authentication
			Enum Values: 1=Certificates, 2=PSK, 3=EAP, 4=SAML
		IkePolicy : string or integer from ClientIkePolicyTemplates
			IKE Policy
		IkeV2Policy : string or integer from ClientIkev2PolicyTemplates
			IKEv2 Policy
		IkeDhGroup : integer
			IKE DH Group
			Enum Values: 0=none, 1=DHGroup1, 2=DHGroup2, 5=DHGroup5, 14=DHGroup14, 15=DHGroup15, 16=DHGroup16, 17=DHGroup17, 18=DHGroup18, 19=DHGroup19, 20=DHGroup20, 21=DHGroup21, 25=DHGroup25, 26=DHGroup26, 27=DHGroup27, 28=DHGroup28, 29=DHGroup29, 30=DHGroup306
		IkeLifeTimeDuration : integer
			Lifetime
		IpSecPolicy : string or integer from ClientIpsecPolicyTemplates
			IPsec Policy
		PFS : integer
			PFS
			Enum Values: 0=none, 1=DHGroup1, 2=DHGroup2, 5=DHGroup5, 14=DHGroup14, 15=DHGroup15, 16=DHGroup16, 17=DHGroup17, 18=DHGroup18, 19=DHGroup19, 20=DHGroup20, 21=DHGroup21, 25=DHGroup25, 26=DHGroup26, 27=DHGroup27, 28=DHGroup28, 29=DHGroup29, 30=DHGroup30
		IpSecLifeTimeType : integer
			Lifetime Type (IPsec)
			Enum Values: 0=off, 1=duration, 2=KByte, 3=Both
		IpSecLifeTimeDuration : integer
			Ip Sec Life Time Duration
		IpSecLifeTimeVolume : integer
			Volume
		UseCompression : boolean
			IPsec Compression
		IkeIdType : integer
			IKE ID Type
			Enum Values: 1=IpAddr, 2=DomainName, 3=UserId, 4=IpSubNet, 7=IpAddrRange, 9=ASN1DN, 10=ASN1GroupName, 11=FreeString, 19=X500DistingName, 20=X500GeneralName, 21=KeyId
		IkeId : string
			IKE ID
		VpnUserId : string
			VPN User ID
		VpnPassword : string
			VPN Password
		VpnPwSave : boolean
			Save VPN Password in Profile Settings
		VpnSuffix : string
			VPN Suffix
		TunnelSecret : string
			IPsec Pre-shared Key
		VpnRemIpAddr : string
			Gateway (Tunnel Endpoint)
		AuthFromCert : integer
			VPN Tunnel Authentication Data
			Enum Values: 0=config, 1=e-mail, 2=common name, 3=serial number, 4=UPN, 5=SAN e-mail, 6=subject serial number
		SamlUrl : string
			Authentication Provider URL
		SamlRealm : string
			Realm
		SplitTunnelingModeV4 : integer
			Split tunneling mode IPv4
			Enum Values: 0=split, 1=all tunnel
		SplitTunnelingNetworksV4 : array from model ClientSplitTunnelNetV4
			Split tunneling networks IPv4
		VpnTunnelRelay : boolean
			Full Local Network Enclosure Mode
		SplitTunnelingModeV6 : integer
			Split tunneling mode IPv6
			Enum Values: 0=split, 1=all tunnel
		SplitTunnelingNetworksV6 : array from model ClientSplitTunnelNetV6
			Split tunneling networks IPv6
		VpnByPassConfig : string or integer from ClientVpnByPassTemplates
			VPN bypass configuration
		UseXAUTH : boolean
			Extended Authentication (XAUTH)
		UseIkePort : integer
			UDP Encapsulation Port
		DisableDPD : integer
			Disable DPD (Dead Peer Detection)
			Enum Values: 0=on, 1=off
		DPDInterval : integer
			DPD Interval
		DPDRetries : integer
			DPD Number of retries
		AntiReplay : boolean
			Anti-replay Protection
		PathFinder : boolean
			VPN Path Finder
		UseRFC7427 : boolean
			Enable negotiating RFC7427 (digital signatures)
		RFC7427Padding : integer
			RFC7427 Padding Method
			Enum Values: 0=undefined, 1=PKCS#1, 2=PSS
		IkeV2AuthPrf : boolean
			IKEv2 RSA authentication with PRF hash
		AssignPrivateIpAddress : integer
			Assignment of private IP address
			Enum Values: 1=IKE Config Mode, 2=Local IP address, 3=DHCP over IPsec, 4=manual
		PrivateIpAddess : string with IP address
			IP address
		PrivateIpMask : string with IP address
			Subnet Mask
		DNS1 : string with IP address
			1. DNS Server
		DNS2 : string with IP address
			2. DNS Server
		MgmSrv : string with IP address
			1. Management Server
		MgmSrv2 : string with IP address
			2. Management Server
		DomainName : string
			Domain Name
		DomainInTunnel : string
			DNS domains to be resolved in the tunnel
		WebProxyType : integer
			Proxy type
			Enum Values: 0=none, 1=auto, 2=manually
		WebProxyAutoURL : string
			Proxy configuration URL
		WebProxyHttp : string
			HTTP proxy
		WebProxyHttps : string
			HTTPS proxy
		WebProxyExceptions : string
			Web Proxy exceptions
		HASupport : integer
			HA Support
			Enum Values: 0=off, 2=HA over VPN-Port
		HAServer1 : string
			Primary HA Server
		HAServer2 : string
			Secondary HA Server
		DveSecret : string
			HA Secret
		HaUseLastGateway : boolean
			Last Assigned Gateway
		CertSubject : string
			Incoming Certificate's Subject
		CertIssuer : string
			Incoming Certificate's Issuer
		CertFingerprint : string
			Issuer's Certificate Fingerprint
		CertFingerPrintHash : integer
			Fingerprint Hash
			Enum Values: 0=MD5, 1=SHA1
		ProtectLan : integer
			Stateful Inspection
			Enum Values: 0=off, 1=when connect, 2=always
		FwOnlyVpn : boolean
			Only Tunneling Permitted
		FwRasOnlyVpn : boolean
			In Combination with Microsoft's RAS Dialer only Tunneling permitted
		SrvCreateEntry : integer
			Create configuration on RADIUS server
			Enum Values: 0=off, 1=VPN, 2=NAS, 3=both
		SrvNasIpAddr : string with IP address
			NAS IP address for client
		SrvNasParam1 : string
			NAS parameter 1
		SrvNasParam2 : string
			NAS parameter 2
		SrvNasParam3 : string
			NAS parameter 3
		SrvNasParam4 : string
			NAS parameter 4
		SrvNasParam5 : string
			NAS parameter 5
		SrvNasParam6 : string
			NAS parameter 6
		SrvNasParam7 : string
			NAS parameter 7
		SrvNasParam8 : string
			NAS parameter 8
		SrvVpnIpAddr : string with IP address
			VPN IP address for client
		SrvVpnParam1 : string
			VPN parameter 1
		SrvVpnParam2 : string
			VPN parameter 2
		SrvVpnParam3 : string
			VPN parameter 3
		SrvVpnParam4 : string
			VPN parameter 4
		SrvVpnParam5 : string
			VPN parameter 5
		SrvVpnParam6 : string
			VPN parameter 6
		SrvVpnParam7 : string
			VPN parameter 7
		SrvVpnParam8 : string
			VPN parameter 8
		SrvVpnParamSplitTunneling : string
			Server Parameter Split Tunneling
		RadiusValidFrom : time
			Enable connections starting on
		RadiusValidUntil : time
			Deny connections starting on
		TwoFactAuthLang : string
			Language
		TwoFactAuthId : string
			Device number
		TimeOTPSecretBase32 : string
			Time-based OTP Secret (Base32)
	'''

	def __init__(self, getHandler, groupid, clientid):
		LazyModifiableListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"ProfileName" : "",
			"LinkType" : "LAN",
			"UseForAMD" : False,
			"SeamlessRoaming" : False,
			"KeepTunnel" : False,
			"BootUser" : "off",
			"UseRas" : "never",
			"HideProfile" : False,
			"DialerUser" : "",
			"DialerPw" : "NoPassword",
			"DialerPhone" : "",
			"RasFile" : "",
			"HttpUsername" : "",
			"HttpPassword" : "",
			"HttpScript" : "",
			"Modem" : "",
			"ComPort" : "COM1",
			"Baudrate" : "57600",
			"RlsComPort" : True,
			"ModemInitStr" : "",
			"DialPrefix" : "",
			"MobileConfigMode" : "SIM card",
			"MobileCountry" : 0,
			"MobileProvider" : 4294967295,
			"MobileApn" : "AT+cgdcont=1,\"IP\",\"\"",
			"MobilePhone" : "",
			"MobileAuth" : "none",
			"MobileUsername" : "",
			"MobilePassword" : "",
			"MobileSimPin" : "",
			"BiometricAuth" : False,
			"EapAuthentication" : False,
			"HttpAuthentication" : False,
			"ConnectionMode" : "manually",
			"ConnectAtBoot" : False,
			"Timeout" : 100,
			"OtpToken" : "off",
			"SwapOtpPin" : False,
			"HideUserId" : False,
			"TunnelTrafficMonitoring" : False,
			"TunnelTrafficMonitoringAddr" : "0.0.0.0",
			"PermitIpBroadcast" : True,
			"QoSConfig" : "0",
			"PkiConfig" : "0",
			"ExchangeMode" : "IKEv2",
			"VpnIpVersion" : "IPv4",
			"IkeV2Authentication" : "EAP",
			"IkePolicy" : "-1",
			"IkeV2Policy" : "-1",
			"IkeDhGroup" : "DHGroup14",
			"IkeLifeTimeDuration" : 86400,
			"IpSecPolicy" : "-1",
			"PFS" : "DHGroup14",
			"IpSecLifeTimeType" : "duration",
			"IpSecLifeTimeDuration" : 28800,
			"IpSecLifeTimeVolume" : 50000,
			"UseCompression" : True,
			"IkeIdType" : "UserId",
			"IkeId" : "",
			"VpnUserId" : "",
			"VpnPassword" : "",
			"VpnPwSave" : True,
			"VpnSuffix" : "",
			"TunnelSecret" : "",
			"VpnRemIpAddr" : "",
			"AuthFromCert" : "config",
			"SamlUrl" : "",
			"SamlRealm" : "",
			"SplitTunnelingModeV4" : "all tunnel",
			"SplitTunnelingNetworksV4" : [],
			"VpnTunnelRelay" : True,
			"SplitTunnelingModeV6" : "all tunnel",
			"SplitTunnelingNetworksV6" : [],
			"VpnByPassConfig" : "0",
			"UseXAUTH" : True,
			"UseIkePort" : 500,
			"DisableDPD" : "on",
			"DPDInterval" : 20,
			"DPDRetries" : 8,
			"AntiReplay" : False,
			"PathFinder" : False,
			"UseRFC7427" : True,
			"RFC7427Padding" : "PSS",
			"IkeV2AuthPrf" : False,
			"AssignPrivateIpAddress" : "IKE Config Mode",
			"PrivateIpAddess" : "0.0.0.0",
			"PrivateIpMask" : "255.255.255.0",
			"DNS1" : "0.0.0.0",
			"DNS2" : "0.0.0.0",
			"MgmSrv" : "0.0.0.0",
			"MgmSrv2" : "0.0.0.0",
			"DomainName" : "",
			"DomainInTunnel" : "",
			"WebProxyType" : "none",
			"WebProxyAutoURL" : "",
			"WebProxyHttp" : "",
			"WebProxyHttps" : "",
			"WebProxyExceptions" : "",
			"HASupport" : "off",
			"HAServer1" : "",
			"HAServer2" : "",
			"DveSecret" : "",
			"HaUseLastGateway" : True,
			"CertSubject" : "",
			"CertIssuer" : "",
			"CertFingerprint" : "",
			"CertFingerPrintHash" : "MD5",
			"ProtectLan" : "off",
			"FwOnlyVpn" : False,
			"FwRasOnlyVpn" : True,
			"SrvCreateEntry" : "off",
			"SrvNasIpAddr" : "0.0.0.0",
			"SrvNasParam1" : "",
			"SrvNasParam2" : "",
			"SrvNasParam3" : "",
			"SrvNasParam4" : "",
			"SrvNasParam5" : "",
			"SrvNasParam6" : "",
			"SrvNasParam7" : "",
			"SrvNasParam8" : "",
			"SrvVpnIpAddr" : "0.0.0.0",
			"SrvVpnParam1" : "",
			"SrvVpnParam2" : "",
			"SrvVpnParam3" : "",
			"SrvVpnParam4" : "",
			"SrvVpnParam5" : "",
			"SrvVpnParam6" : "",
			"SrvVpnParam7" : "",
			"SrvVpnParam8" : "",
			"SrvVpnParamSplitTunneling" : "",
			"RadiusValidFrom" : "",
			"RadiusValidUntil" : "",
			"TwoFactAuthLang" : "",
			"TwoFactAuthId" : "",
			"TimeOTPSecretBase32" : "",
			"TimeOTPSecretUrl" : "",
			"UserParameters" : {},
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def ProfileName(self):
		return self.__getattr__("ProfileName")

	@cached_property
	def LinkType(self):
		return self.__getattr__("LinkType")

	@cached_property
	def UseForAMD(self):
		return self.__getattr__("UseForAMD")

	@cached_property
	def SeamlessRoaming(self):
		return self.__getattr__("SeamlessRoaming")

	@cached_property
	def KeepTunnel(self):
		return self.__getattr__("KeepTunnel")

	@cached_property
	def BootUser(self):
		return self.__getattr__("BootUser")

	@cached_property
	def UseRas(self):
		return self.__getattr__("UseRas")

	@cached_property
	def HideProfile(self):
		return self.__getattr__("HideProfile")

	@cached_property
	def DialerUser(self):
		return self.__getattr__("DialerUser")

	@cached_property
	def DialerPw(self):
		return self.__getattr__("DialerPw")

	@cached_property
	def DialerPhone(self):
		return self.__getattr__("DialerPhone")

	@cached_property
	def RasFile(self):
		return self.__getattr__("RasFile")

	@cached_property
	def HttpUsername(self):
		return self.__getattr__("HttpUsername")

	@cached_property
	def HttpPassword(self):
		return self.__getattr__("HttpPassword")

	@cached_property
	def HttpScript(self):
		return self.__getattr__("HttpScript")

	@cached_property
	def Modem(self):
		return self.__getattr__("Modem")

	@cached_property
	def ComPort(self):
		return self.__getattr__("ComPort")

	@cached_property
	def Baudrate(self):
		return self.__getattr__("Baudrate")

	@cached_property
	def RlsComPort(self):
		return self.__getattr__("RlsComPort")

	@cached_property
	def ModemInitStr(self):
		return self.__getattr__("ModemInitStr")

	@cached_property
	def DialPrefix(self):
		return self.__getattr__("DialPrefix")

	@cached_property
	def MobileConfigMode(self):
		return self.__getattr__("MobileConfigMode")

	@cached_property
	def MobileCountry(self):
		return self.__getattr__("MobileCountry")

	@cached_property
	def MobileProvider(self):
		return self.__getattr__("MobileProvider")

	@cached_property
	def MobileApn(self):
		return self.__getattr__("MobileApn")

	@cached_property
	def MobilePhone(self):
		return self.__getattr__("MobilePhone")

	@cached_property
	def MobileAuth(self):
		return self.__getattr__("MobileAuth")

	@cached_property
	def MobileUsername(self):
		return self.__getattr__("MobileUsername")

	@cached_property
	def MobilePassword(self):
		return self.__getattr__("MobilePassword")

	@cached_property
	def MobileSimPin(self):
		return self.__getattr__("MobileSimPin")

	@cached_property
	def BiometricAuth(self):
		return self.__getattr__("BiometricAuth")

	@cached_property
	def EapAuthentication(self):
		return self.__getattr__("EapAuthentication")

	@cached_property
	def HttpAuthentication(self):
		return self.__getattr__("HttpAuthentication")

	@cached_property
	def ConnectionMode(self):
		return self.__getattr__("ConnectionMode")

	@cached_property
	def ConnectAtBoot(self):
		return self.__getattr__("ConnectAtBoot")

	@cached_property
	def Timeout(self):
		return self.__getattr__("Timeout")

	@cached_property
	def OtpToken(self):
		return self.__getattr__("OtpToken")

	@cached_property
	def SwapOtpPin(self):
		return self.__getattr__("SwapOtpPin")

	@cached_property
	def HideUserId(self):
		return self.__getattr__("HideUserId")

	@cached_property
	def TunnelTrafficMonitoring(self):
		return self.__getattr__("TunnelTrafficMonitoring")

	@cached_property
	def TunnelTrafficMonitoringAddr(self):
		return self.__getattr__("TunnelTrafficMonitoringAddr")

	@cached_property
	def PermitIpBroadcast(self):
		return self.__getattr__("PermitIpBroadcast")

	@cached_property
	def QoSConfig(self):
		return self.__getattr__("QoSConfig")

	@cached_property
	def PkiConfig(self):
		return self.__getattr__("PkiConfig")

	@cached_property
	def ExchangeMode(self):
		return self.__getattr__("ExchangeMode")

	@cached_property
	def VpnIpVersion(self):
		return self.__getattr__("VpnIpVersion")

	@cached_property
	def IkeV2Authentication(self):
		return self.__getattr__("IkeV2Authentication")

	@cached_property
	def IkePolicy(self):
		return self.__getattr__("IkePolicy")

	@cached_property
	def IkeV2Policy(self):
		return self.__getattr__("IkeV2Policy")

	@cached_property
	def IkeDhGroup(self):
		return self.__getattr__("IkeDhGroup")

	@cached_property
	def IkeLifeTimeDuration(self):
		return self.__getattr__("IkeLifeTimeDuration")

	@cached_property
	def IpSecPolicy(self):
		return self.__getattr__("IpSecPolicy")

	@cached_property
	def PFS(self):
		return self.__getattr__("PFS")

	@cached_property
	def IpSecLifeTimeType(self):
		return self.__getattr__("IpSecLifeTimeType")

	@cached_property
	def IpSecLifeTimeDuration(self):
		return self.__getattr__("IpSecLifeTimeDuration")

	@cached_property
	def IpSecLifeTimeVolume(self):
		return self.__getattr__("IpSecLifeTimeVolume")

	@cached_property
	def UseCompression(self):
		return self.__getattr__("UseCompression")

	@cached_property
	def IkeIdType(self):
		return self.__getattr__("IkeIdType")

	@cached_property
	def IkeId(self):
		return self.__getattr__("IkeId")

	@cached_property
	def VpnUserId(self):
		return self.__getattr__("VpnUserId")

	@cached_property
	def VpnPassword(self):
		return self.__getattr__("VpnPassword")

	@cached_property
	def VpnPwSave(self):
		return self.__getattr__("VpnPwSave")

	@cached_property
	def VpnSuffix(self):
		return self.__getattr__("VpnSuffix")

	@cached_property
	def TunnelSecret(self):
		return self.__getattr__("TunnelSecret")

	@cached_property
	def VpnRemIpAddr(self):
		return self.__getattr__("VpnRemIpAddr")

	@cached_property
	def AuthFromCert(self):
		return self.__getattr__("AuthFromCert")

	@cached_property
	def SamlUrl(self):
		return self.__getattr__("SamlUrl")

	@cached_property
	def SamlRealm(self):
		return self.__getattr__("SamlRealm")

	@cached_property
	def SplitTunnelingModeV4(self):
		return self.__getattr__("SplitTunnelingModeV4")

	@cached_property
	def SplitTunnelingNetworksV4(self):
		return self.__getattr__("SplitTunnelingNetworksV4")

	@cached_property
	def VpnTunnelRelay(self):
		return self.__getattr__("VpnTunnelRelay")

	@cached_property
	def SplitTunnelingModeV6(self):
		return self.__getattr__("SplitTunnelingModeV6")

	@cached_property
	def SplitTunnelingNetworksV6(self):
		return self.__getattr__("SplitTunnelingNetworksV6")

	@cached_property
	def VpnByPassConfig(self):
		return self.__getattr__("VpnByPassConfig")

	@cached_property
	def UseXAUTH(self):
		return self.__getattr__("UseXAUTH")

	@cached_property
	def UseIkePort(self):
		return self.__getattr__("UseIkePort")

	@cached_property
	def DisableDPD(self):
		return self.__getattr__("DisableDPD")

	@cached_property
	def DPDInterval(self):
		return self.__getattr__("DPDInterval")

	@cached_property
	def DPDRetries(self):
		return self.__getattr__("DPDRetries")

	@cached_property
	def AntiReplay(self):
		return self.__getattr__("AntiReplay")

	@cached_property
	def PathFinder(self):
		return self.__getattr__("PathFinder")

	@cached_property
	def UseRFC7427(self):
		return self.__getattr__("UseRFC7427")

	@cached_property
	def RFC7427Padding(self):
		return self.__getattr__("RFC7427Padding")

	@cached_property
	def IkeV2AuthPrf(self):
		return self.__getattr__("IkeV2AuthPrf")

	@cached_property
	def AssignPrivateIpAddress(self):
		return self.__getattr__("AssignPrivateIpAddress")

	@cached_property
	def PrivateIpAddess(self):
		return self.__getattr__("PrivateIpAddess")

	@cached_property
	def PrivateIpMask(self):
		return self.__getattr__("PrivateIpMask")

	@cached_property
	def DNS1(self):
		return self.__getattr__("DNS1")

	@cached_property
	def DNS2(self):
		return self.__getattr__("DNS2")

	@cached_property
	def MgmSrv(self):
		return self.__getattr__("MgmSrv")

	@cached_property
	def MgmSrv2(self):
		return self.__getattr__("MgmSrv2")

	@cached_property
	def DomainName(self):
		return self.__getattr__("DomainName")

	@cached_property
	def DomainInTunnel(self):
		return self.__getattr__("DomainInTunnel")

	@cached_property
	def WebProxyType(self):
		return self.__getattr__("WebProxyType")

	@cached_property
	def WebProxyAutoURL(self):
		return self.__getattr__("WebProxyAutoURL")

	@cached_property
	def WebProxyHttp(self):
		return self.__getattr__("WebProxyHttp")

	@cached_property
	def WebProxyHttps(self):
		return self.__getattr__("WebProxyHttps")

	@cached_property
	def WebProxyExceptions(self):
		return self.__getattr__("WebProxyExceptions")

	@cached_property
	def HASupport(self):
		return self.__getattr__("HASupport")

	@cached_property
	def HAServer1(self):
		return self.__getattr__("HAServer1")

	@cached_property
	def HAServer2(self):
		return self.__getattr__("HAServer2")

	@cached_property
	def DveSecret(self):
		return self.__getattr__("DveSecret")

	@cached_property
	def HaUseLastGateway(self):
		return self.__getattr__("HaUseLastGateway")

	@cached_property
	def CertSubject(self):
		return self.__getattr__("CertSubject")

	@cached_property
	def CertIssuer(self):
		return self.__getattr__("CertIssuer")

	@cached_property
	def CertFingerprint(self):
		return self.__getattr__("CertFingerprint")

	@cached_property
	def CertFingerPrintHash(self):
		return self.__getattr__("CertFingerPrintHash")

	@cached_property
	def ProtectLan(self):
		return self.__getattr__("ProtectLan")

	@cached_property
	def FwOnlyVpn(self):
		return self.__getattr__("FwOnlyVpn")

	@cached_property
	def FwRasOnlyVpn(self):
		return self.__getattr__("FwRasOnlyVpn")

	@cached_property
	def SrvCreateEntry(self):
		return self.__getattr__("SrvCreateEntry")

	@cached_property
	def SrvNasIpAddr(self):
		return self.__getattr__("SrvNasIpAddr")

	@cached_property
	def SrvNasParam1(self):
		return self.__getattr__("SrvNasParam1")

	@cached_property
	def SrvNasParam2(self):
		return self.__getattr__("SrvNasParam2")

	@cached_property
	def SrvNasParam3(self):
		return self.__getattr__("SrvNasParam3")

	@cached_property
	def SrvNasParam4(self):
		return self.__getattr__("SrvNasParam4")

	@cached_property
	def SrvNasParam5(self):
		return self.__getattr__("SrvNasParam5")

	@cached_property
	def SrvNasParam6(self):
		return self.__getattr__("SrvNasParam6")

	@cached_property
	def SrvNasParam7(self):
		return self.__getattr__("SrvNasParam7")

	@cached_property
	def SrvNasParam8(self):
		return self.__getattr__("SrvNasParam8")

	@cached_property
	def SrvVpnIpAddr(self):
		return self.__getattr__("SrvVpnIpAddr")

	@cached_property
	def SrvVpnParam1(self):
		return self.__getattr__("SrvVpnParam1")

	@cached_property
	def SrvVpnParam2(self):
		return self.__getattr__("SrvVpnParam2")

	@cached_property
	def SrvVpnParam3(self):
		return self.__getattr__("SrvVpnParam3")

	@cached_property
	def SrvVpnParam4(self):
		return self.__getattr__("SrvVpnParam4")

	@cached_property
	def SrvVpnParam5(self):
		return self.__getattr__("SrvVpnParam5")

	@cached_property
	def SrvVpnParam6(self):
		return self.__getattr__("SrvVpnParam6")

	@cached_property
	def SrvVpnParam7(self):
		return self.__getattr__("SrvVpnParam7")

	@cached_property
	def SrvVpnParam8(self):
		return self.__getattr__("SrvVpnParam8")

	@cached_property
	def SrvVpnParamSplitTunneling(self):
		return self.__getattr__("SrvVpnParamSplitTunneling")

	@cached_property
	def RadiusValidFrom(self):
		return self.__getattr__("RadiusValidFrom")

	@cached_property
	def RadiusValidUntil(self):
		return self.__getattr__("RadiusValidUntil")

	@cached_property
	def TwoFactAuthLang(self):
		return self.__getattr__("TwoFactAuthLang")

	@cached_property
	def TwoFactAuthId(self):
		return self.__getattr__("TwoFactAuthId")

	@cached_property
	def TimeOTPSecretBase32(self):
		return self.__getattr__("TimeOTPSecretBase32")

	@cached_property
	def TimeOTPSecretUrl(self):
		return self.__getattr__("TimeOTPSecretUrl")

	@cached_property
	def UserParameters(self):
		return self.__getattr__("UserParameters")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientWifiConfigurationsHandler(BaseListFindHandler, BaseListUpdateHandler):
	'''Configuration of client wifi configurations

	Methods
	-------
		createEntry()
			Creates a new ClientWifiConfiguration entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, clientid):
		url = "client-mgm/{groupid}/clients/{clientid}/wifis".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clientid = clientid

	def createEntry(self):
		'''Creates a new ClientWifiConfiguration entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientWifiConfiguration(self, self._groupid, self._clientid)


class ClientWifiConfiguration(LazyModifiableListEntry):
	'''Configuration of a client Wi-Fi profiles

	Attributes [read-only]
	----------------------
		Name : string
			Name
		UserParameters : object
			User parameters
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		SSID : string
			SSID
		PowerMode : integer
			Power Mode
			Enum Values: 0=medium, 1=high, 2=low
		ConnectionMode : integer
			Auto-Connect
			Enum Values: 0=manually, 1=automatic
		HiddenSSID : boolean
			Hidden SSID
		DisconnectByVpn : boolean
			Disconnect if VPN gets disconnected
		MeteredConnection : boolean
			Metered connection
		EncryptionType : integer
			Encryption WPA, ..
			Enum Values: 1=none, 2=WEP, 3=WPA, 4=WPA2, 5=WPA3
		EncryptionAuthType : integer
			Key Management PSK, EAP
			Enum Values: 1=Open System, 2=Shared Key, 3=EAP, 4=PSK
		EncryptionKeyFormat : integer
			Key Format
			Enum Values: 0=hex, 1=ascii
		EncryptionKey1 : string
			Key 1
		EncryptionKey2 : string
			Key 2
		EncryptionKey3 : string
			Key 3
		EncryptionKey4 : string
			Key 4
		DhcpMode : integer
			IP Address Automatically Assigned
			Enum Values: 0=manually, 1=automatic
		IpAddress : string with IP address
			IP Address
		NetworkMask : string with IP address
			Subnet Mask
		DefaultGateway : string with IP address
			Default Gateway
		DnsMode : integer
			DNS/WINS Server Address Automatically Assigned
			Enum Values: 0=manually, 1=automatic
		Dns1 : string with IP address
			Preferred DNS Server
		Dns2 : string with IP address
			Alternate DNS Server
		Wins1 : string with IP address
			Preferred WINS Server
		Wins2 : string with IP address
			Alternate WINS Server
		AuthType : integer
			Hotspot
			Enum Values: 0=none, 1=other, 2=T-Mobile
		AuthUserId : string
			User ID
		AuthPassword : string
			Password
		AuthScript : string
			Script File Name
	'''

	def __init__(self, getHandler, groupid, clientid):
		LazyModifiableListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"SSID" : "",
			"PowerMode" : "medium",
			"ConnectionMode" : "manually",
			"HiddenSSID" : False,
			"DisconnectByVpn" : False,
			"MeteredConnection" : False,
			"EncryptionType" : "none",
			"EncryptionAuthType" : "Open System",
			"EncryptionKeyFormat" : "ascii",
			"EncryptionKey1" : "",
			"EncryptionKey2" : "",
			"EncryptionKey3" : "",
			"EncryptionKey4" : "",
			"DhcpMode" : "automatic",
			"IpAddress" : "0.0.0.0",
			"NetworkMask" : "0.0.0.0",
			"DefaultGateway" : "0.0.0.0",
			"DnsMode" : "automatic",
			"Dns1" : "0.0.0.0",
			"Dns2" : "0.0.0.0",
			"Wins1" : "0.0.0.0",
			"Wins2" : "0.0.0.0",
			"AuthType" : "none",
			"AuthUserId" : "",
			"AuthPassword" : "",
			"AuthScript" : "",
			"UserParameters" : {},
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def SSID(self):
		return self.__getattr__("SSID")

	@cached_property
	def PowerMode(self):
		return self.__getattr__("PowerMode")

	@cached_property
	def ConnectionMode(self):
		return self.__getattr__("ConnectionMode")

	@cached_property
	def HiddenSSID(self):
		return self.__getattr__("HiddenSSID")

	@cached_property
	def DisconnectByVpn(self):
		return self.__getattr__("DisconnectByVpn")

	@cached_property
	def MeteredConnection(self):
		return self.__getattr__("MeteredConnection")

	@cached_property
	def EncryptionType(self):
		return self.__getattr__("EncryptionType")

	@cached_property
	def EncryptionAuthType(self):
		return self.__getattr__("EncryptionAuthType")

	@cached_property
	def EncryptionKeyFormat(self):
		return self.__getattr__("EncryptionKeyFormat")

	@cached_property
	def EncryptionKey1(self):
		return self.__getattr__("EncryptionKey1")

	@cached_property
	def EncryptionKey2(self):
		return self.__getattr__("EncryptionKey2")

	@cached_property
	def EncryptionKey3(self):
		return self.__getattr__("EncryptionKey3")

	@cached_property
	def EncryptionKey4(self):
		return self.__getattr__("EncryptionKey4")

	@cached_property
	def DhcpMode(self):
		return self.__getattr__("DhcpMode")

	@cached_property
	def IpAddress(self):
		return self.__getattr__("IpAddress")

	@cached_property
	def NetworkMask(self):
		return self.__getattr__("NetworkMask")

	@cached_property
	def DefaultGateway(self):
		return self.__getattr__("DefaultGateway")

	@cached_property
	def DnsMode(self):
		return self.__getattr__("DnsMode")

	@cached_property
	def Dns1(self):
		return self.__getattr__("Dns1")

	@cached_property
	def Dns2(self):
		return self.__getattr__("Dns2")

	@cached_property
	def Wins1(self):
		return self.__getattr__("Wins1")

	@cached_property
	def Wins2(self):
		return self.__getattr__("Wins2")

	@cached_property
	def AuthType(self):
		return self.__getattr__("AuthType")

	@cached_property
	def AuthUserId(self):
		return self.__getattr__("AuthUserId")

	@cached_property
	def AuthPassword(self):
		return self.__getattr__("AuthPassword")

	@cached_property
	def AuthScript(self):
		return self.__getattr__("AuthScript")

	@cached_property
	def UserParameters(self):
		return self.__getattr__("UserParameters")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientPkiConfigurationsHandler(BaseListFindHandler, BaseListUpdateHandler):
	'''Configuration of client certificates

	Methods
	-------
		createEntry()
			Creates a new ClientPkiConfiguration entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, clientid):
		url = "client-mgm/{groupid}/clients/{clientid}/pki-configs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clientid = clientid

	def createEntry(self):
		'''Creates a new ClientPkiConfiguration entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientPkiConfiguration(self, self._groupid, self._clientid)


class ClientPkiConfiguration(LazyModifiableListEntry):
	'''Configuration of a client certificates

	Attributes [read-only]
	----------------------
		Name : string
			Name
		UserParameters : object
			User parameters
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		CertType : integer
			Certificate
			Enum Values: 0=none, 1=PC/SC, 2=PKCS#12, 3=PKCS#11, 4=Entrust, 5=CSP, 8=CSP User Store, 6=DATEV, 9=Keychain
		CertNr : integer
			Certificate number
		SmartcardReader : string
			Smartcard reader
		Pkcs12Filename : string
			PKCS#12 Filename
		CertPkcs12Select : boolean
			Enable certificate selection
		CertPkcs12Path : string
			PKCS#12 Certificate path
		Pkcs11Modul : string
			PKCS#11 library
		Pkcs11SlotIndex : integer
			Slot index
		CspProvider : string
			CSP provider
		CertSubjectMatch : string
			Subject CN
		CertIssuerMatch : string
			Issuer CN
		CertExtKeyUsage : string
			Extended Key Usage Match
		KeyChainHash : string
			Keychain Hash
		PinQuest : integer
			PIN Request at each connection
		AllowUserPinChange : boolean
			Modify PIN
		PinPolicy : integer
			PIN policy
		WarningBeforeCertExpires : boolean
			Enable warning before certificate expires
		CertExpireWarnDays : integer
			Days before certificate expiration warning
		ComputerCertType : integer
			Computer Certificate Type
			Enum Values: 0=none, 2=PKCS#12, 4=Entrust, 5=CSP
		ComputerPkcs12Filename : string
			Computer PKCS#12 Filename
		ComputerSubjectMatch : string
			Computer Subject CN
		ComputerIssuerMatch : string
			Computer Issuer CN
		ComputerExtKeyUsage : string
			Extended Key Usage
	'''

	def __init__(self, getHandler, groupid, clientid):
		LazyModifiableListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"CertType" : "none",
			"CertNr" : 1,
			"SmartcardReader" : "",
			"Pkcs12Filename" : "",
			"CertPkcs12Select" : False,
			"CertPkcs12Path" : "%CertDir%",
			"Pkcs11Modul" : "",
			"Pkcs11SlotIndex" : 0,
			"CspProvider" : "",
			"CertSubjectMatch" : "",
			"CertIssuerMatch" : "",
			"CertExtKeyUsage" : "",
			"KeyChainHash" : "",
			"PinQuest" : 0,
			"AllowUserPinChange" : False,
			"PinPolicy" : 6,
			"WarningBeforeCertExpires" : True,
			"CertExpireWarnDays" : 30,
			"ComputerCertType" : "none",
			"ComputerPkcs12Filename" : "",
			"ComputerSubjectMatch" : "",
			"ComputerIssuerMatch" : "",
			"ComputerExtKeyUsage" : "",
			"UserParameters" : {},
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def CertType(self):
		return self.__getattr__("CertType")

	@cached_property
	def CertNr(self):
		return self.__getattr__("CertNr")

	@cached_property
	def SmartcardReader(self):
		return self.__getattr__("SmartcardReader")

	@cached_property
	def Pkcs12Filename(self):
		return self.__getattr__("Pkcs12Filename")

	@cached_property
	def CertPkcs12Select(self):
		return self.__getattr__("CertPkcs12Select")

	@cached_property
	def CertPkcs12Path(self):
		return self.__getattr__("CertPkcs12Path")

	@cached_property
	def Pkcs11Modul(self):
		return self.__getattr__("Pkcs11Modul")

	@cached_property
	def Pkcs11SlotIndex(self):
		return self.__getattr__("Pkcs11SlotIndex")

	@cached_property
	def CspProvider(self):
		return self.__getattr__("CspProvider")

	@cached_property
	def CertSubjectMatch(self):
		return self.__getattr__("CertSubjectMatch")

	@cached_property
	def CertIssuerMatch(self):
		return self.__getattr__("CertIssuerMatch")

	@cached_property
	def CertExtKeyUsage(self):
		return self.__getattr__("CertExtKeyUsage")

	@cached_property
	def KeyChainHash(self):
		return self.__getattr__("KeyChainHash")

	@cached_property
	def PinQuest(self):
		return self.__getattr__("PinQuest")

	@cached_property
	def AllowUserPinChange(self):
		return self.__getattr__("AllowUserPinChange")

	@cached_property
	def PinPolicy(self):
		return self.__getattr__("PinPolicy")

	@cached_property
	def WarningBeforeCertExpires(self):
		return self.__getattr__("WarningBeforeCertExpires")

	@cached_property
	def CertExpireWarnDays(self):
		return self.__getattr__("CertExpireWarnDays")

	@cached_property
	def ComputerCertType(self):
		return self.__getattr__("ComputerCertType")

	@cached_property
	def ComputerPkcs12Filename(self):
		return self.__getattr__("ComputerPkcs12Filename")

	@cached_property
	def ComputerSubjectMatch(self):
		return self.__getattr__("ComputerSubjectMatch")

	@cached_property
	def ComputerIssuerMatch(self):
		return self.__getattr__("ComputerIssuerMatch")

	@cached_property
	def ComputerExtKeyUsage(self):
		return self.__getattr__("ComputerExtKeyUsage")

	@cached_property
	def UserParameters(self):
		return self.__getattr__("UserParameters")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")


class ClientVpnByPassProfilesHandler(BaseListFindHandler, BaseListUpdateHandler):
	'''Configuration of client VPN bypass profiles

	Methods
	-------
		createEntry()
			Creates a new ClientVpnByPassProfile entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
		update (BaseListUpdateHandler)
	'''
	
	def __init__(self, api, groupid, clientid):
		url = "client-mgm/{groupid}/clients/{clientid}/vpn-bypass".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		self._clientid = clientid

	def createEntry(self):
		'''Creates a new ClientVpnByPassProfile entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return ClientVpnByPassProfile(self, self._groupid, self._clientid)


class ClientVpnByPassProfile(LazyModifiableListEntry):
	'''Configuration of a client VPN bypass profile

	Attributes [read-only]
	----------------------
		Name : string
			Name
		Entries : array from model VpnByPassEntry
			Entries
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by
		PluginInfo : string
			Plug-in Info

	Attributes [writable]
	---------------------
		ClientEntries : array from model VpnByPassEntry
			Client entries
	'''

	def __init__(self, getHandler, groupid, clientid):
		LazyModifiableListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"Entries" : [],
			"ClientEntries" : [],
			"ModifiedOn" : "",
			"ModifiedBy" : "",
			"PluginInfo" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def Entries(self):
		return self.__getattr__("Entries")

	@cached_property
	def ClientEntries(self):
		return self.__getattr__("ClientEntries")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")

	@cached_property
	def PluginInfo(self):
		return self.__getattr__("PluginInfo")



class GetIdNameList(BaseEntry):
	'''Default model for get list operation

	Attributes [writable]
	---------------------
		Id : integer
			REST ID
		Name : string
			Name
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
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


class ClientTemplateRestrictions(BaseEntry):
	'''Client template restrictions

	Attributes [writable]
	---------------------
		OpenHotspotLogon : boolean
			Open Hotspot logon
		OpenMobileNetworkCard : boolean
			Open Mobile Network Card
		OpenConnectionInfo : boolean
			Open Connection info
		OpenAvailableCommMedia : boolean
			Open Available Communication Media
		PreconfAvailableCommMedia : boolean
			Preconfigure Available Communication Media
		OpenBudgetManagerStatistics : boolean
			Open Budget Manager Statistics
		OpenBudgetManagerHistory : boolean
			Open Budget Manager History
		OpenMenuCertificates : boolean
			Open View Certificates
		MenuExit : boolean
			Exit
		OpenProfiles : boolean
			Open Profiles
		OpenIPsec : boolean
			Open IPsec
		OpenFirewall : boolean
			Open Firewall
		ModifyFirewall : boolean
			Modify Firewall
		OpenVpnByPass : boolean
			Open VPN bypass
		OpenQoS : boolean
			Open Quality of Service
		OpenWiFi : boolean
			Open Wi-Fi
		OpenCertificates : boolean
			Open Certificates
		ModifyCertificates : boolean
			Modify Certificates
		OpenLinkOptions : boolean
			Open Link options
		ModifyLinkOptions : boolean
			Modify Link options
		PreconfLinkOptions : boolean
			Preconfigure Link options
		OpenEapOptions : boolean
			Open EAP options
		ModifyEapOptions : boolean
			Modify EAP options
		PreconfEapOptions : boolean
			Preconfigure EAP options
		OpenLogonOptions : boolean
			Open Logon options
		ModifyLogonOptions : boolean
			Modify Logon options
		PreconfLogonOptions : boolean
			Preconfigure Logon options
		OpenHotspot : boolean
			Open Hotspot Configuration
		ModifyHotspot : boolean
			Modify Hotspot Configuration
		PreconfHotspot : boolean
			Preconfigure Hotspot Configuration
		OpenSWoLAN : boolean
			Open Software Update over LAN
		ModifySWoverLAN : boolean
			Modify Software Update over LAN
		PreconfSWoLAN : boolean
			Preconfigure Software Update over LAN
		OpenProxyVPNoLAN : boolean
			Open Proxy for VPN over LAN
		PreconfProxyVPNoLAN : boolean
			Preconfigure Proxy for VPN over LAN
		RestoreLastConfiguration : boolean
			Restore Last Configuration
		ProfileBackupCreate : boolean
			Profile settings backup - Create
		ProfileBackupRestore : boolean
			Profile settings backup - Restore
		ShowProfiles : boolean
			Show Profiles
		PreconfProfiles : boolean
			Preconfigure Profiles
		ShowButtons : boolean
			Show Buttons
		PreconfButtons : boolean
			Preconfigure Buttons
		ShowStatistics : boolean
			Show Statistics
		PreconfStatistics : boolean
			Preconfigure Statistics
		ShowWiFiState : boolean
			Show Wi-Fi State
		PreconfWiFiState : boolean
			Preconfigure Wi-Fi State
		ShowAlwaysOnTop : boolean
			Show always on top 
		PreconfAlwaysOnTop : boolean
			Preconf Always on top 
		ShowAutostart : boolean
			Show Autostart
		ModifyAutostart : boolean
			Modify Autostart
		PreconfAutostart : boolean
			Preconfigure Autostart
		ShowMinWhenClosing : boolean
			Show minimize when closing
		PreconfMinWhenClosing : boolean
			Preconfigure minimize when closing
		ShowMinWhenConnected : boolean
			Show Minimize when connected
		PreconfMinWhenConnected : boolean
			Preconfigure minimize when connected
		ShowOptions : boolean
			Show Options
		ModifyOptions : boolean
			Modify Options
		PreconfOptions : boolean
			Preconfigure Options
		OpenLogbook : boolean
			Open Logbook
		OpenExtendedLogSettings : boolean
			Open Extended Log Settings
		OpenClientInfoCenter : boolean
			Open Client Info Center
		OpenNetworkDiagnostics : boolean
			Open Network diagnostics
		ModifyNetworkDiagnostics : boolean
			Modify Network diagnostics
		PreconfNetworkDiagnostics : boolean
			Preconfigure Network diagnostics
		OpenSupportAssistant : boolean
			Open Support Assistant
		PreconfSupportAssistant : boolean
			Preconfigure Support Assistant
		OpenLicensing : boolean
			Open Licensing
		OpenProfileFilterGroups : boolean
			Open Profile filter groups
		ModifyProfileFilterGroups : boolean
			Modify Profile filter groups
		PreconfProfileFilterGroups : boolean
			Preconfigure Profile filter groups
		PreconfExtendedOptions : boolean
			Preconfigure Extended Options
		PermitUserCreateProfiles : boolean
			Permit user to create new profiles
		DelAllProfiles : boolean
			Delete all profile entries
		DelAllProfileFilterGroups : boolean
			Delete all profile filter groups
		HideShowAllProfiles : boolean
			Hide option 'Show all profiles'
		UserCreateFirewallRules : boolean
			User may create new firewall rules
		DelAllFirewallRules : boolean
			Delete all firewall rules
		UserCreateFriendlyNetworks : boolean
			User may create new friendly networks
		FriendlyNetworksMayModify : boolean
			Friendly networks may be modified
		FriendlyNetworksMayDeleted : boolean
			Friendly Networks may be deleted
		DelAllFriendlyNetworks : boolean
			Delete all friendly networks
		EnableWiFi : boolean
			Enable Wi-Fi management
		DisableWiFiIsConnected : boolean
			Disable Wi-Fi when LAN cable is connected
		EnableHotspotDetection : boolean
			Enable Hotspot detection
		PermitUserNewWiFiProfiles : boolean
			Permit user to create new Wi-Fi profiles
		DisableWiFiLANisConnected : boolean
			Disable Wi-Fi when LAN cable is connected
		DelAllWiFiProfiles : boolean
			Delete all Wi-Fi profiles
		UserCreateNewVPNbypassConfigs : boolean
			User may create new VPN bypass configuration
		DelAllVPNbypassConfigs : boolean
			Delete all VPN bypass configurations
		UserCreateNewQoSconfigs : boolean
			User may create new Quality of Service configuration
		DelAllQoSconfigs : boolean
			Delete all Quality of Service configurations
		UserCreateNewCertConfigs : boolean
			User may create new certificate configurations
		DelAllCertConfigs : boolean
			Delete all certificate configurations
		UserCreateNewProxyConfigs : boolean
			User may create new proxy configurations
		ProxyConfigMayModify : boolean
			Proxy configurations may be modified
		ProxyConfigMayDeleted : boolean
			Proxy configurations may be deleted
		DeleteAllProxyConfigs : boolean
			Delete all proxy configurations
		PermitSavePIN : boolean
			Permit user to save the SIM PIN in the configuration
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"OpenHotspotLogon" : True,
			"OpenMobileNetworkCard" : True,
			"OpenConnectionInfo" : True,
			"OpenAvailableCommMedia" : True,
			"PreconfAvailableCommMedia" : True,
			"OpenBudgetManagerStatistics" : True,
			"OpenBudgetManagerHistory" : True,
			"OpenMenuCertificates" : True,
			"MenuExit" : True,
			"OpenProfiles" : True,
			"OpenIPsec" : True,
			"OpenFirewall" : True,
			"ModifyFirewall" : True,
			"OpenVpnByPass" : True,
			"OpenQoS" : True,
			"OpenWiFi" : True,
			"OpenCertificates" : True,
			"ModifyCertificates" : True,
			"OpenLinkOptions" : True,
			"ModifyLinkOptions" : True,
			"PreconfLinkOptions" : True,
			"OpenEapOptions" : True,
			"ModifyEapOptions" : True,
			"PreconfEapOptions" : True,
			"OpenLogonOptions" : True,
			"ModifyLogonOptions" : True,
			"PreconfLogonOptions" : True,
			"OpenHotspot" : True,
			"ModifyHotspot" : True,
			"PreconfHotspot" : True,
			"OpenSWoLAN" : True,
			"ModifySWoverLAN" : True,
			"PreconfSWoLAN" : True,
			"OpenProxyVPNoLAN" : True,
			"PreconfProxyVPNoLAN" : True,
			"RestoreLastConfiguration" : True,
			"ProfileBackupCreate" : True,
			"ProfileBackupRestore" : True,
			"ShowProfiles" : True,
			"PreconfProfiles" : True,
			"ShowButtons" : True,
			"PreconfButtons" : True,
			"ShowStatistics" : True,
			"PreconfStatistics" : True,
			"ShowWiFiState" : True,
			"PreconfWiFiState" : True,
			"ShowAlwaysOnTop" : True,
			"PreconfAlwaysOnTop" : True,
			"ShowAutostart" : True,
			"ModifyAutostart" : True,
			"PreconfAutostart" : True,
			"ShowMinWhenClosing" : True,
			"PreconfMinWhenClosing" : True,
			"ShowMinWhenConnected" : True,
			"PreconfMinWhenConnected" : True,
			"ShowOptions" : True,
			"ModifyOptions" : True,
			"PreconfOptions" : True,
			"OpenLogbook" : True,
			"OpenExtendedLogSettings" : True,
			"OpenClientInfoCenter" : True,
			"OpenNetworkDiagnostics" : True,
			"ModifyNetworkDiagnostics" : True,
			"PreconfNetworkDiagnostics" : True,
			"OpenSupportAssistant" : True,
			"PreconfSupportAssistant" : True,
			"OpenLicensing" : True,
			"OpenProfileFilterGroups" : True,
			"ModifyProfileFilterGroups" : True,
			"PreconfProfileFilterGroups" : True,
			"PreconfExtendedOptions" : True,
			"PermitUserCreateProfiles" : True,
			"DelAllProfiles" : True,
			"DelAllProfileFilterGroups" : True,
			"HideShowAllProfiles" : True,
			"UserCreateFirewallRules" : True,
			"DelAllFirewallRules" : True,
			"UserCreateFriendlyNetworks" : True,
			"FriendlyNetworksMayModify" : True,
			"FriendlyNetworksMayDeleted" : True,
			"DelAllFriendlyNetworks" : True,
			"EnableWiFi" : True,
			"DisableWiFiIsConnected" : True,
			"EnableHotspotDetection" : True,
			"PermitUserNewWiFiProfiles" : True,
			"DisableWiFiLANisConnected" : True,
			"DelAllWiFiProfiles" : True,
			"UserCreateNewVPNbypassConfigs" : True,
			"DelAllVPNbypassConfigs" : True,
			"UserCreateNewQoSconfigs" : True,
			"DelAllQoSconfigs" : True,
			"UserCreateNewCertConfigs" : True,
			"DelAllCertConfigs" : True,
			"UserCreateNewProxyConfigs" : True,
			"ProxyConfigMayModify" : True,
			"ProxyConfigMayDeleted" : True,
			"DeleteAllProxyConfigs" : True,
			"PermitSavePIN" : True,
		}

	@cached_property
	def OpenHotspotLogon(self):
		return self.__getattr__("OpenHotspotLogon")

	@cached_property
	def OpenMobileNetworkCard(self):
		return self.__getattr__("OpenMobileNetworkCard")

	@cached_property
	def OpenConnectionInfo(self):
		return self.__getattr__("OpenConnectionInfo")

	@cached_property
	def OpenAvailableCommMedia(self):
		return self.__getattr__("OpenAvailableCommMedia")

	@cached_property
	def PreconfAvailableCommMedia(self):
		return self.__getattr__("PreconfAvailableCommMedia")

	@cached_property
	def OpenBudgetManagerStatistics(self):
		return self.__getattr__("OpenBudgetManagerStatistics")

	@cached_property
	def OpenBudgetManagerHistory(self):
		return self.__getattr__("OpenBudgetManagerHistory")

	@cached_property
	def OpenMenuCertificates(self):
		return self.__getattr__("OpenMenuCertificates")

	@cached_property
	def MenuExit(self):
		return self.__getattr__("MenuExit")

	@cached_property
	def OpenProfiles(self):
		return self.__getattr__("OpenProfiles")

	@cached_property
	def OpenIPsec(self):
		return self.__getattr__("OpenIPsec")

	@cached_property
	def OpenFirewall(self):
		return self.__getattr__("OpenFirewall")

	@cached_property
	def ModifyFirewall(self):
		return self.__getattr__("ModifyFirewall")

	@cached_property
	def OpenVpnByPass(self):
		return self.__getattr__("OpenVpnByPass")

	@cached_property
	def OpenQoS(self):
		return self.__getattr__("OpenQoS")

	@cached_property
	def OpenWiFi(self):
		return self.__getattr__("OpenWiFi")

	@cached_property
	def OpenCertificates(self):
		return self.__getattr__("OpenCertificates")

	@cached_property
	def ModifyCertificates(self):
		return self.__getattr__("ModifyCertificates")

	@cached_property
	def OpenLinkOptions(self):
		return self.__getattr__("OpenLinkOptions")

	@cached_property
	def ModifyLinkOptions(self):
		return self.__getattr__("ModifyLinkOptions")

	@cached_property
	def PreconfLinkOptions(self):
		return self.__getattr__("PreconfLinkOptions")

	@cached_property
	def OpenEapOptions(self):
		return self.__getattr__("OpenEapOptions")

	@cached_property
	def ModifyEapOptions(self):
		return self.__getattr__("ModifyEapOptions")

	@cached_property
	def PreconfEapOptions(self):
		return self.__getattr__("PreconfEapOptions")

	@cached_property
	def OpenLogonOptions(self):
		return self.__getattr__("OpenLogonOptions")

	@cached_property
	def ModifyLogonOptions(self):
		return self.__getattr__("ModifyLogonOptions")

	@cached_property
	def PreconfLogonOptions(self):
		return self.__getattr__("PreconfLogonOptions")

	@cached_property
	def OpenHotspot(self):
		return self.__getattr__("OpenHotspot")

	@cached_property
	def ModifyHotspot(self):
		return self.__getattr__("ModifyHotspot")

	@cached_property
	def PreconfHotspot(self):
		return self.__getattr__("PreconfHotspot")

	@cached_property
	def OpenSWoLAN(self):
		return self.__getattr__("OpenSWoLAN")

	@cached_property
	def ModifySWoverLAN(self):
		return self.__getattr__("ModifySWoverLAN")

	@cached_property
	def PreconfSWoLAN(self):
		return self.__getattr__("PreconfSWoLAN")

	@cached_property
	def OpenProxyVPNoLAN(self):
		return self.__getattr__("OpenProxyVPNoLAN")

	@cached_property
	def PreconfProxyVPNoLAN(self):
		return self.__getattr__("PreconfProxyVPNoLAN")

	@cached_property
	def RestoreLastConfiguration(self):
		return self.__getattr__("RestoreLastConfiguration")

	@cached_property
	def ProfileBackupCreate(self):
		return self.__getattr__("ProfileBackupCreate")

	@cached_property
	def ProfileBackupRestore(self):
		return self.__getattr__("ProfileBackupRestore")

	@cached_property
	def ShowProfiles(self):
		return self.__getattr__("ShowProfiles")

	@cached_property
	def PreconfProfiles(self):
		return self.__getattr__("PreconfProfiles")

	@cached_property
	def ShowButtons(self):
		return self.__getattr__("ShowButtons")

	@cached_property
	def PreconfButtons(self):
		return self.__getattr__("PreconfButtons")

	@cached_property
	def ShowStatistics(self):
		return self.__getattr__("ShowStatistics")

	@cached_property
	def PreconfStatistics(self):
		return self.__getattr__("PreconfStatistics")

	@cached_property
	def ShowWiFiState(self):
		return self.__getattr__("ShowWiFiState")

	@cached_property
	def PreconfWiFiState(self):
		return self.__getattr__("PreconfWiFiState")

	@cached_property
	def ShowAlwaysOnTop(self):
		return self.__getattr__("ShowAlwaysOnTop")

	@cached_property
	def PreconfAlwaysOnTop(self):
		return self.__getattr__("PreconfAlwaysOnTop")

	@cached_property
	def ShowAutostart(self):
		return self.__getattr__("ShowAutostart")

	@cached_property
	def ModifyAutostart(self):
		return self.__getattr__("ModifyAutostart")

	@cached_property
	def PreconfAutostart(self):
		return self.__getattr__("PreconfAutostart")

	@cached_property
	def ShowMinWhenClosing(self):
		return self.__getattr__("ShowMinWhenClosing")

	@cached_property
	def PreconfMinWhenClosing(self):
		return self.__getattr__("PreconfMinWhenClosing")

	@cached_property
	def ShowMinWhenConnected(self):
		return self.__getattr__("ShowMinWhenConnected")

	@cached_property
	def PreconfMinWhenConnected(self):
		return self.__getattr__("PreconfMinWhenConnected")

	@cached_property
	def ShowOptions(self):
		return self.__getattr__("ShowOptions")

	@cached_property
	def ModifyOptions(self):
		return self.__getattr__("ModifyOptions")

	@cached_property
	def PreconfOptions(self):
		return self.__getattr__("PreconfOptions")

	@cached_property
	def OpenLogbook(self):
		return self.__getattr__("OpenLogbook")

	@cached_property
	def OpenExtendedLogSettings(self):
		return self.__getattr__("OpenExtendedLogSettings")

	@cached_property
	def OpenClientInfoCenter(self):
		return self.__getattr__("OpenClientInfoCenter")

	@cached_property
	def OpenNetworkDiagnostics(self):
		return self.__getattr__("OpenNetworkDiagnostics")

	@cached_property
	def ModifyNetworkDiagnostics(self):
		return self.__getattr__("ModifyNetworkDiagnostics")

	@cached_property
	def PreconfNetworkDiagnostics(self):
		return self.__getattr__("PreconfNetworkDiagnostics")

	@cached_property
	def OpenSupportAssistant(self):
		return self.__getattr__("OpenSupportAssistant")

	@cached_property
	def PreconfSupportAssistant(self):
		return self.__getattr__("PreconfSupportAssistant")

	@cached_property
	def OpenLicensing(self):
		return self.__getattr__("OpenLicensing")

	@cached_property
	def OpenProfileFilterGroups(self):
		return self.__getattr__("OpenProfileFilterGroups")

	@cached_property
	def ModifyProfileFilterGroups(self):
		return self.__getattr__("ModifyProfileFilterGroups")

	@cached_property
	def PreconfProfileFilterGroups(self):
		return self.__getattr__("PreconfProfileFilterGroups")

	@cached_property
	def PreconfExtendedOptions(self):
		return self.__getattr__("PreconfExtendedOptions")

	@cached_property
	def PermitUserCreateProfiles(self):
		return self.__getattr__("PermitUserCreateProfiles")

	@cached_property
	def DelAllProfiles(self):
		return self.__getattr__("DelAllProfiles")

	@cached_property
	def DelAllProfileFilterGroups(self):
		return self.__getattr__("DelAllProfileFilterGroups")

	@cached_property
	def HideShowAllProfiles(self):
		return self.__getattr__("HideShowAllProfiles")

	@cached_property
	def UserCreateFirewallRules(self):
		return self.__getattr__("UserCreateFirewallRules")

	@cached_property
	def DelAllFirewallRules(self):
		return self.__getattr__("DelAllFirewallRules")

	@cached_property
	def UserCreateFriendlyNetworks(self):
		return self.__getattr__("UserCreateFriendlyNetworks")

	@cached_property
	def FriendlyNetworksMayModify(self):
		return self.__getattr__("FriendlyNetworksMayModify")

	@cached_property
	def FriendlyNetworksMayDeleted(self):
		return self.__getattr__("FriendlyNetworksMayDeleted")

	@cached_property
	def DelAllFriendlyNetworks(self):
		return self.__getattr__("DelAllFriendlyNetworks")

	@cached_property
	def EnableWiFi(self):
		return self.__getattr__("EnableWiFi")

	@cached_property
	def DisableWiFiIsConnected(self):
		return self.__getattr__("DisableWiFiIsConnected")

	@cached_property
	def EnableHotspotDetection(self):
		return self.__getattr__("EnableHotspotDetection")

	@cached_property
	def PermitUserNewWiFiProfiles(self):
		return self.__getattr__("PermitUserNewWiFiProfiles")

	@cached_property
	def DisableWiFiLANisConnected(self):
		return self.__getattr__("DisableWiFiLANisConnected")

	@cached_property
	def DelAllWiFiProfiles(self):
		return self.__getattr__("DelAllWiFiProfiles")

	@cached_property
	def UserCreateNewVPNbypassConfigs(self):
		return self.__getattr__("UserCreateNewVPNbypassConfigs")

	@cached_property
	def DelAllVPNbypassConfigs(self):
		return self.__getattr__("DelAllVPNbypassConfigs")

	@cached_property
	def UserCreateNewQoSconfigs(self):
		return self.__getattr__("UserCreateNewQoSconfigs")

	@cached_property
	def DelAllQoSconfigs(self):
		return self.__getattr__("DelAllQoSconfigs")

	@cached_property
	def UserCreateNewCertConfigs(self):
		return self.__getattr__("UserCreateNewCertConfigs")

	@cached_property
	def DelAllCertConfigs(self):
		return self.__getattr__("DelAllCertConfigs")

	@cached_property
	def UserCreateNewProxyConfigs(self):
		return self.__getattr__("UserCreateNewProxyConfigs")

	@cached_property
	def ProxyConfigMayModify(self):
		return self.__getattr__("ProxyConfigMayModify")

	@cached_property
	def ProxyConfigMayDeleted(self):
		return self.__getattr__("ProxyConfigMayDeleted")

	@cached_property
	def DeleteAllProxyConfigs(self):
		return self.__getattr__("DeleteAllProxyConfigs")

	@cached_property
	def PermitSavePIN(self):
		return self.__getattr__("PermitSavePIN")


class HttpProxy(BaseEntry):
	'''Model for one HTTP proxy configuration entry

	Attributes [writable]
	---------------------
		Index : integer
			Index
		Flags : integer
			Flags
		Name : string
			Name
		IpAddress : string
			Proxy IP Address
		Port : string
			Port
		UserId : string
			Proxy User ID
		Password : string
			Password
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Index" : 0,
			"Flags" : 0,
			"Name" : "",
			"IpAddress" : "",
			"Port" : "",
			"UserId" : "",
			"Password" : "",
		}

	@cached_property
	def Index(self):
		return self.__getattr__("Index")

	@cached_property
	def Flags(self):
		return self.__getattr__("Flags")

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def IpAddress(self):
		return self.__getattr__("IpAddress")

	@cached_property
	def Port(self):
		return self.__getattr__("Port")

	@cached_property
	def UserId(self):
		return self.__getattr__("UserId")

	@cached_property
	def Password(self):
		return self.__getattr__("Password")


class ClientTemplateList(BaseEntry):
	'''List of client templates

	Attributes [read-only]
	----------------------
		TemplateType : integer
			Template Type
			Enum Values: 0=Enterprise template, 11=VS GovNet Connector template
		ModifiedOn : time
			Modified on

	Attributes [writable]
	---------------------
		Id : integer
			ID
		Name : string
			Name
		OsType : integer
			OS Type
			Enum Values: 2=Windows, 14=Linux, 21=macOS, 22=Android, 25=iOS
		GroupId : integer
			SEM Group ID
		GroupName : string
			SEM Group name
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Name" : "",
			"OsType" : 0,
			"TemplateType" : "Enterprise template",
			"GroupId" : 0,
			"GroupName" : "",
			"ModifiedOn" : "",
		}

	@cached_property
	def Id(self):
		return self.__getattr__("Id")

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def OsType(self):
		return self.__getattr__("OsType")

	@cached_property
	def TemplateType(self):
		return self.__getattr__("TemplateType")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def GroupName(self):
		return self.__getattr__("GroupName")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")


class ClientProfileTabLocks(BaseEntry):
	'''Client Profile Tab Locks

	Attributes [writable]
	---------------------
		ViewGrpStdConfig : boolean
			View Group Standard Configuration
		ViewFlipGeneral : boolean
			View Flip General
		ViewFlipInternetConnection : boolean
			View Flip Internet Connection
		ViewFlipVPNConn : boolean
			View Flip VPN Connection
		ViewFlipHA : boolean
			View Flip HA Configuration
		ViewGrpMobile : boolean
			View Group Mobile Network
		ViewFlipMobile : boolean
			View Flip Mobile Network
		ViewGrpModem : boolean
			View Group Modem Settings
		ViewFlipModem : boolean
			View Flip Modem Settings
		ViewGrpIPsec : boolean
			View Group IPsec
		ViewFlipIKE : boolean
			View Flip IKE
		ViewFlipIPsec : boolean
			View Flip IPsec
		ViewFlipAdvIPsec : boolean
			View Flip Advanced IPsec Settings
		ViewGrpSplitTunneling : boolean
			View Group Split Tunneling
		ViewGrpVPNBypass : boolean
			View Group VPN Bypass
		ViewGrpConnection : boolean
			View Group Connection
		ViewGrpLineMgm : boolean
			View Group Line Management
		ViewFlipDNS : boolean
			View Flip DNS / Management
		ViewGrpExtAuth : boolean
			View Group Ext. Authentication
		ViewFlipAuthOptions : boolean
			View Flip Authentication Options
		ViewFlipPreAuth : boolean
			View Flip Pre-Authentication
		ViewFlipCertCheck : boolean
			View Flip Certificate Check
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"ViewGrpStdConfig" : True,
			"ViewFlipGeneral" : True,
			"ViewFlipInternetConnection" : True,
			"ViewFlipVPNConn" : True,
			"ViewFlipHA" : True,
			"ViewGrpMobile" : True,
			"ViewFlipMobile" : True,
			"ViewGrpModem" : True,
			"ViewFlipModem" : True,
			"ViewGrpIPsec" : True,
			"ViewFlipIKE" : True,
			"ViewFlipIPsec" : True,
			"ViewFlipAdvIPsec" : True,
			"ViewGrpSplitTunneling" : True,
			"ViewGrpVPNBypass" : True,
			"ViewGrpConnection" : True,
			"ViewGrpLineMgm" : True,
			"ViewFlipDNS" : True,
			"ViewGrpExtAuth" : True,
			"ViewFlipAuthOptions" : True,
			"ViewFlipPreAuth" : True,
			"ViewFlipCertCheck" : True,
		}

	@cached_property
	def ViewGrpStdConfig(self):
		return self.__getattr__("ViewGrpStdConfig")

	@cached_property
	def ViewFlipGeneral(self):
		return self.__getattr__("ViewFlipGeneral")

	@cached_property
	def ViewFlipInternetConnection(self):
		return self.__getattr__("ViewFlipInternetConnection")

	@cached_property
	def ViewFlipVPNConn(self):
		return self.__getattr__("ViewFlipVPNConn")

	@cached_property
	def ViewFlipHA(self):
		return self.__getattr__("ViewFlipHA")

	@cached_property
	def ViewGrpMobile(self):
		return self.__getattr__("ViewGrpMobile")

	@cached_property
	def ViewFlipMobile(self):
		return self.__getattr__("ViewFlipMobile")

	@cached_property
	def ViewGrpModem(self):
		return self.__getattr__("ViewGrpModem")

	@cached_property
	def ViewFlipModem(self):
		return self.__getattr__("ViewFlipModem")

	@cached_property
	def ViewGrpIPsec(self):
		return self.__getattr__("ViewGrpIPsec")

	@cached_property
	def ViewFlipIKE(self):
		return self.__getattr__("ViewFlipIKE")

	@cached_property
	def ViewFlipIPsec(self):
		return self.__getattr__("ViewFlipIPsec")

	@cached_property
	def ViewFlipAdvIPsec(self):
		return self.__getattr__("ViewFlipAdvIPsec")

	@cached_property
	def ViewGrpSplitTunneling(self):
		return self.__getattr__("ViewGrpSplitTunneling")

	@cached_property
	def ViewGrpVPNBypass(self):
		return self.__getattr__("ViewGrpVPNBypass")

	@cached_property
	def ViewGrpConnection(self):
		return self.__getattr__("ViewGrpConnection")

	@cached_property
	def ViewGrpLineMgm(self):
		return self.__getattr__("ViewGrpLineMgm")

	@cached_property
	def ViewFlipDNS(self):
		return self.__getattr__("ViewFlipDNS")

	@cached_property
	def ViewGrpExtAuth(self):
		return self.__getattr__("ViewGrpExtAuth")

	@cached_property
	def ViewFlipAuthOptions(self):
		return self.__getattr__("ViewFlipAuthOptions")

	@cached_property
	def ViewFlipPreAuth(self):
		return self.__getattr__("ViewFlipPreAuth")

	@cached_property
	def ViewFlipCertCheck(self):
		return self.__getattr__("ViewFlipCertCheck")


class IKEv1Proposal(BaseEntry):
	'''IKEv1 Proposal

	Attributes [writable]
	---------------------
		Authentication : integer
			Authentication
			Enum Values: 1=Pre-shared key, 3=RSA signature
		Encryption : integer
			Encryption
			Enum Values: 1=DES, 3=BFISH, 5=3DES, 7=AES-CBC
		KeyLength : integer
			Key length
			Enum Values: 64=64, 128=128, 192=192, 256=256
		Hash : integer
			Hash
			Enum Values: 1=MD5, 2=SHA, 3=TIGER, 4=SHA2-256, 5=SHA2-384, 6=SHA2-512
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Authentication" : "Pre-shared key",
			"Encryption" : "AES-CBC",
			"KeyLength" : 0,
			"Hash" : "MD5",
		}

	@cached_property
	def Authentication(self):
		return self.__getattr__("Authentication")

	@cached_property
	def Encryption(self):
		return self.__getattr__("Encryption")

	@cached_property
	def KeyLength(self):
		return self.__getattr__("KeyLength")

	@cached_property
	def Hash(self):
		return self.__getattr__("Hash")


class IKEv2Proposal(BaseEntry):
	'''IKEv2 Proposal

	Attributes [writable]
	---------------------
		CryptoAlgorithm : integer
			Encryption
			Enum Values: 2=DES, 3=3DES, 7=BFISH, 12=AES-CBC, 13=AES-CTR, 20=AES-GCM
		KeyLength : integer
			Key Length
			Enum Values: 64=64, 128=128, 192=192, 256=256
		PRF : integer
			Pseudo-Random Function
			Enum Values: 1=HMAC-MD5, 2=HMAC-SHA1, 5=HMAC-SHA2-256, 6=HMAC-SHA2-384, 7=HMAC-SHA2-512
		IntegrityAlgorithm : integer
			Integrity Algorithm
			Enum Values: 1=MD5-96, 2=SHA1-96, 12=SHA2-256, 13=SHA2-384, 14=SHA2-512
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"CryptoAlgorithm" : 0,
			"KeyLength" : 0,
			"PRF" : 0,
			"IntegrityAlgorithm" : 0,
		}

	@cached_property
	def CryptoAlgorithm(self):
		return self.__getattr__("CryptoAlgorithm")

	@cached_property
	def KeyLength(self):
		return self.__getattr__("KeyLength")

	@cached_property
	def PRF(self):
		return self.__getattr__("PRF")

	@cached_property
	def IntegrityAlgorithm(self):
		return self.__getattr__("IntegrityAlgorithm")


class IPsecProposal(BaseEntry):
	'''IPsec Proposal

	Attributes [writable]
	---------------------
		Protocol : integer
			Protocol
			Enum Values: 2=AH, 3=ESP, 4=COMP
		Encryption : integer
			Encryption
			Enum Values: 11=NULL, 2=DES, 3=3DES, 7=Blowfish, 12=AES-CBC, 13=AES-CTR, 20=AES-GCM
		KeyLength : integer
			Key Length
		Authentication : integer
			Authentication
			Enum Values: 0=none, 1=MD5, 2=SHA, 5=SHA2-256, 6=SHA2-384, 7=SHA2-512
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Protocol" : "ESP",
			"Encryption" : 786560,
			"KeyLength" : 0,
			"Authentication" : "SHA",
		}

	@cached_property
	def Protocol(self):
		return self.__getattr__("Protocol")

	@cached_property
	def Encryption(self):
		return self.__getattr__("Encryption")

	@cached_property
	def KeyLength(self):
		return self.__getattr__("KeyLength")

	@cached_property
	def Authentication(self):
		return self.__getattr__("Authentication")


class VpnByPassEntry(BaseEntry):
	'''VPN bypass entry

	Attributes [writable]
	---------------------
		Name : string
			Application Name
		Path : string
			Application Path
		Domain : string
			Domain Name
		Protocol : integer
			Protocol
			Enum Values: 0=any, 1=tcp, 2=udp
		Ports : string
			Ports
		VpnApplDns1 : string with IP address
			1. DNS Server
		VpnApplDns2 : string with IP address
			2. DNS Server
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"Path" : "",
			"Domain" : "",
			"Protocol" : "any",
			"Ports" : "",
			"VpnApplDns1" : "0.0.0.0",
			"VpnApplDns2" : "0.0.0.0",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def Path(self):
		return self.__getattr__("Path")

	@cached_property
	def Domain(self):
		return self.__getattr__("Domain")

	@cached_property
	def Protocol(self):
		return self.__getattr__("Protocol")

	@cached_property
	def Ports(self):
		return self.__getattr__("Ports")

	@cached_property
	def VpnApplDns1(self):
		return self.__getattr__("VpnApplDns1")

	@cached_property
	def VpnApplDns2(self):
		return self.__getattr__("VpnApplDns2")


class QoSGroups(BaseEntry):
	'''Client quality of service group

	Attributes [writable]
	---------------------
		Name : string
			Name
		MinRate : integer
			Min Rate
		ApplicationPaths : array from str
			Application paths
		ApplicationDirs : array from str
			Application directories
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"MinRate" : 0,
			"ApplicationPaths" : [],
			"ApplicationDirs" : [],
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def MinRate(self):
		return self.__getattr__("MinRate")

	@cached_property
	def ApplicationPaths(self):
		return self.__getattr__("ApplicationPaths")

	@cached_property
	def ApplicationDirs(self):
		return self.__getattr__("ApplicationDirs")


class ClientSetAuthCode(BaseEntry):
	'''Model for setting the authentication code

	Attributes [writable]
	---------------------
		AuthenticationCode : string
			New authentication code
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"AuthenticationCode" : "",
		}

	@cached_property
	def AuthenticationCode(self):
		return self.__getattr__("AuthenticationCode")


class ClientConfigurationList(BaseEntry):
	'''List of client configurations

	Attributes [read-only]
	----------------------
		UserType : integer
			User Type
			Enum Values: 0=Enterprise Client, 11=VS GovNet Connector Client
		ModifiedOn : time
			Modified on

	Attributes [writable]
	---------------------
		Id : integer
			ID
		Name : string
			Name
		RsuID : string
			ID for personal configuration
		OsType : integer
			OS Type
			Enum Values: 2=Windows, 14=Linux, 21=macOS, 22=Android, 25=iOS
		GroupId : integer
			SEM Group ID
		GroupName : string
			SEM Group name
		LastLogin : time
			Last login
		LastDownload : time
			Last download
		ConfigLastCreationTime : time
			Configuration last creation time
		ConfigLastModifyTime : time
			Configuration last modification time
		ConfigLastDownloadTime : time
			Configuration last download time
		SWVersion : string
			Software version
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Name" : "",
			"RsuID" : "",
			"OsType" : 0,
			"UserType" : "Enterprise Client",
			"GroupId" : 0,
			"GroupName" : "",
			"LastLogin" : "",
			"LastDownload" : "",
			"ConfigLastCreationTime" : "",
			"ConfigLastModifyTime" : "",
			"ConfigLastDownloadTime" : "",
			"SWVersion" : "",
			"ModifiedOn" : "",
		}

	@cached_property
	def Id(self):
		return self.__getattr__("Id")

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def RsuID(self):
		return self.__getattr__("RsuID")

	@cached_property
	def OsType(self):
		return self.__getattr__("OsType")

	@cached_property
	def UserType(self):
		return self.__getattr__("UserType")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def GroupName(self):
		return self.__getattr__("GroupName")

	@cached_property
	def LastLogin(self):
		return self.__getattr__("LastLogin")

	@cached_property
	def LastDownload(self):
		return self.__getattr__("LastDownload")

	@cached_property
	def ConfigLastCreationTime(self):
		return self.__getattr__("ConfigLastCreationTime")

	@cached_property
	def ConfigLastModifyTime(self):
		return self.__getattr__("ConfigLastModifyTime")

	@cached_property
	def ConfigLastDownloadTime(self):
		return self.__getattr__("ConfigLastDownloadTime")

	@cached_property
	def SWVersion(self):
		return self.__getattr__("SWVersion")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

