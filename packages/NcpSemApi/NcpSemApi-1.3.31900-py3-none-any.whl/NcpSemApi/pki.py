
#---------------------------------------------------------------
# This file is generated! Dont make any changes in this file.
#---------------------------------------------------------------
from .base import *
from .cached_property import cached_property



class CertificateRequestsHandler(BaseListFindHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Management of certificate requests

	Methods
	-------
		createEntry()
			Creates a new CertificateRequest entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "pki-mgm/{groupid}/requests".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new CertificateRequest entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return CertificateRequest(self, self._groupid)


class CertificateRequest(LazyListEntry):
	'''Parameters of certificate request

	Attributes [read-only]
	----------------------
		HasPrivateKey : boolean
			Has private key
		RequestId : string
			Request ID
		CertUsage : integer
			Certificate usage
			Enum Values: 0=VPN Certificate, 1=Computer Certificate

	Attributes [writable]
	---------------------
		Name : string
			Name
		CertificateTemplate : string or integer from {Controller}
			Certificate Template
		CommonName : string
			Common Name
		GivenName : string
			Given name
		SurName : string
			Surname
		EMail : string
			E-Mail
		Title : string
			Title
		OrganizationalUnit1 : string
			1. Organizational Unit
		OrganizationalUnit2 : string
			2. Organizational Unit
		OrganizationalUnit3 : string
			3. Organizational Unit
		Organization : string
			Organization
		Location : string
			Location
		StateProvince : string
			State / Province
		Country : string
			Country
		ChallengePassword : string
			Challenge password
		Username : string
			Username
		UseKeyUsage : boolean
			Use key usage
		KeyUsage : integer
			Key usage
		UseExtKeyUsage : boolean
			Use extented key usage
		ExtKeyUsage : string
			Extented key usage
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"CertificateTemplate" : "",
			"CommonName" : "",
			"GivenName" : "",
			"SurName" : "",
			"EMail" : "",
			"Title" : "",
			"OrganizationalUnit1" : "",
			"OrganizationalUnit2" : "",
			"OrganizationalUnit3" : "",
			"Organization" : "",
			"Location" : "",
			"StateProvince" : "",
			"Country" : "",
			"ChallengePassword" : "",
			"Username" : "",
			"UseKeyUsage" : False,
			"KeyUsage" : 0,
			"UseExtKeyUsage" : False,
			"ExtKeyUsage" : "",
			"HasPrivateKey" : False,
			"RequestId" : "",
			"CertUsage" : 0,
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def CertificateTemplate(self):
		return self.__getattr__("CertificateTemplate")

	@cached_property
	def CommonName(self):
		return self.__getattr__("CommonName")

	@cached_property
	def GivenName(self):
		return self.__getattr__("GivenName")

	@cached_property
	def SurName(self):
		return self.__getattr__("SurName")

	@cached_property
	def EMail(self):
		return self.__getattr__("EMail")

	@cached_property
	def Title(self):
		return self.__getattr__("Title")

	@cached_property
	def OrganizationalUnit1(self):
		return self.__getattr__("OrganizationalUnit1")

	@cached_property
	def OrganizationalUnit2(self):
		return self.__getattr__("OrganizationalUnit2")

	@cached_property
	def OrganizationalUnit3(self):
		return self.__getattr__("OrganizationalUnit3")

	@cached_property
	def Organization(self):
		return self.__getattr__("Organization")

	@cached_property
	def Location(self):
		return self.__getattr__("Location")

	@cached_property
	def StateProvince(self):
		return self.__getattr__("StateProvince")

	@cached_property
	def Country(self):
		return self.__getattr__("Country")

	@cached_property
	def ChallengePassword(self):
		return self.__getattr__("ChallengePassword")

	@cached_property
	def Username(self):
		return self.__getattr__("Username")

	@cached_property
	def UseKeyUsage(self):
		return self.__getattr__("UseKeyUsage")

	@cached_property
	def KeyUsage(self):
		return self.__getattr__("KeyUsage")

	@cached_property
	def UseExtKeyUsage(self):
		return self.__getattr__("UseExtKeyUsage")

	@cached_property
	def ExtKeyUsage(self):
		return self.__getattr__("ExtKeyUsage")

	@cached_property
	def HasPrivateKey(self):
		return self.__getattr__("HasPrivateKey")

	@cached_property
	def RequestId(self):
		return self.__getattr__("RequestId")

	@cached_property
	def CertUsage(self):
		return self.__getattr__("CertUsage")


class IssuedCertificatesHandler(BaseListFindHandler):
	'''Management of issued certificates

	Methods
	-------
		createEntry()
			Creates a new IssuedCertificate entry object.
		create(CertificateRequest, PkiProfile, PIN=None)
			Create a new certificates
		import_pkcs12(PKCS12, PIN, VpnUserName, Authcode=None, OsMask=None, ServerCertificateName=None, SavePIN=None)
			Import a PKCS#12 file
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "pki-mgm/{groupid}/issued-certs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid
		
	def create(self, CertificateRequest, PkiProfile, PIN=None):
		'''Create a new certificates
			CertificateRequest : integer
				REST ID of certificate request
			PkiProfile : integer
				REST ID of PKI profile
			PIN : string
				PIN
		'''
		return self._callFunction('/create', CertificateRequest=CertificateRequest, PkiProfile=PkiProfile, PIN=PIN)
		
	def import_pkcs12(self, PKCS12, PIN, VpnUserName, Authcode=None, OsMask=None, ServerCertificateName=None, SavePIN=None):
		'''Import a PKCS#12 file
			PKCS12 : string
				PKCS#12 Content
			PIN : string
				PIN
			VpnUserName : string
				User ID
			Authcode : string
				Authentication code
			OsMask : string
				OS Mask
			ServerCertificateName : string
				Server Certificate Name
			SavePIN : boolean
				Save PIN
		'''
		return self._callFunction('/import-pkcs12', PKCS12=PKCS12, PIN=PIN, VpnUserName=VpnUserName, Authcode=Authcode, OsMask=OsMask, ServerCertificateName=ServerCertificateName, SavePIN=SavePIN)

	def createEntry(self):
		'''Creates a new IssuedCertificate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return IssuedCertificate(self, self._groupid)


class IssuedCertificate(LazyListEntry):
	'''Parameters of issued certificates

	Attributes [read-only]
	----------------------
		CommonName : string
			Common Name
		Certificate : cert
			Certificate
		CertUsage : integer
			Certificate usage
			Enum Values: 0=VPN Certificate, 1=Computer Certificate
		DownloadTime : time
			Download Time
		UserID : string
			User ID
		AuthenticationCode : string
			Authentication Code
		AuthCodeOsWindows : boolean
			Authentication Code for Windows
		AuthCodeOsLinux : boolean
			Authentication Code for Linux
		AuthCodeOsMac : boolean
			Authentication Code for Mac
		AuthCodeOsAndroid : boolean
			Authentication Code for Android
		AuthCodeOsIOS : boolean
			Authentication Code for iOS
		AuthCodeValidFrom : time
			Authentication valid from
		AuthCodeValidTo : time
			Authentication valid to
		AuthCodeNumErrors : integer
			Authentication number of errors
		GroupId : integer
			Group ID
		ConfiguredIn : string
			Configured in
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by

	Methods
	-------
		renew(PkiProfile)
			Renew a certificates
		revoke(RevokeReason)
			Revoke a certificates
		set_auth_code(AuthenticationCode=None, AuthCodeOsWindows=None, AuthCodeOsLinux=None, AuthCodeOsMac=None, AuthCodeOsAndroid=None, AuthCodeOsIOS=None)
			Set/resets the authenication code of a certificate
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"CommonName" : "",
			"Certificate" : {},
			"CertUsage" : 0,
			"DownloadTime" : "",
			"UserID" : "",
			"AuthenticationCode" : "",
			"AuthCodeOsWindows" : False,
			"AuthCodeOsLinux" : False,
			"AuthCodeOsMac" : False,
			"AuthCodeOsAndroid" : False,
			"AuthCodeOsIOS" : False,
			"AuthCodeValidFrom" : "",
			"AuthCodeValidTo" : "",
			"AuthCodeNumErrors" : 0,
			"GroupId" : 0,
			"ConfiguredIn" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}

	@cached_property
	def CommonName(self):
		return self.__getattr__("CommonName")

	@cached_property
	def Certificate(self):
		return self.__getattr__("Certificate")

	@cached_property
	def CertUsage(self):
		return self.__getattr__("CertUsage")

	@cached_property
	def DownloadTime(self):
		return self.__getattr__("DownloadTime")

	@cached_property
	def UserID(self):
		return self.__getattr__("UserID")

	@cached_property
	def AuthenticationCode(self):
		return self.__getattr__("AuthenticationCode")

	@cached_property
	def AuthCodeOsWindows(self):
		return self.__getattr__("AuthCodeOsWindows")

	@cached_property
	def AuthCodeOsLinux(self):
		return self.__getattr__("AuthCodeOsLinux")

	@cached_property
	def AuthCodeOsMac(self):
		return self.__getattr__("AuthCodeOsMac")

	@cached_property
	def AuthCodeOsAndroid(self):
		return self.__getattr__("AuthCodeOsAndroid")

	@cached_property
	def AuthCodeOsIOS(self):
		return self.__getattr__("AuthCodeOsIOS")

	@cached_property
	def AuthCodeValidFrom(self):
		return self.__getattr__("AuthCodeValidFrom")

	@cached_property
	def AuthCodeValidTo(self):
		return self.__getattr__("AuthCodeValidTo")

	@cached_property
	def AuthCodeNumErrors(self):
		return self.__getattr__("AuthCodeNumErrors")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")
			
	def renew(self, PkiProfile):
		'''Renew a certificates
			PkiProfile : integer
				REST ID of PKI profile
		'''
		return self._callMethod('/renew', PkiProfile=PkiProfile)
			
	def revoke(self, RevokeReason):
		'''Revoke a certificates
			RevokeReason : integer
				Revoke reason
		'''
		return self._callMethod('/revoke', RevokeReason=RevokeReason)
			
	def set_auth_code(self, AuthenticationCode=None, AuthCodeOsWindows=None, AuthCodeOsLinux=None, AuthCodeOsMac=None, AuthCodeOsAndroid=None, AuthCodeOsIOS=None):
		'''Set/resets the authenication code of a certificate
			AuthenticationCode : string
				Authentication Code
			AuthCodeOsWindows : boolean
				Authentication Code enabled for Windows
			AuthCodeOsLinux : boolean
				Authentication Code enabled for Linux
			AuthCodeOsMac : boolean
				Authentication Code enabled for Mac
			AuthCodeOsAndroid : boolean
				Authentication Code enabled for Android
			AuthCodeOsIOS : boolean
				Authentication Code enabled for iOS
		'''
		return self._callMethod('/set-auth-code', AuthenticationCode=AuthenticationCode, AuthCodeOsWindows=AuthCodeOsWindows, AuthCodeOsLinux=AuthCodeOsLinux, AuthCodeOsMac=AuthCodeOsMac, AuthCodeOsAndroid=AuthCodeOsAndroid, AuthCodeOsIOS=AuthCodeOsIOS)


class CACertificatesHandler(BaseListFindHandler):
	'''Management of CA certificates

	Methods
	-------
		createEntry()
			Creates a new CACertificate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "pki-mgm/{groupid}/ca-certs".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new CACertificate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return CACertificate(self, self._groupid)


class CACertificate(LazyListEntry):
	'''Parameters of CA certificates

	Attributes [read-only]
	----------------------
		CommonName : string
			Common Name
		Certificate : cert
			Certificate
		NotAfter : string
			Not After
		GroupId : integer
			Group ID
		ConfiguredIn : string
			Configured in
		ModifiedOn : time
			Modified on
		ModifiedBy : string
			Modified by

	Attributes [writable]
	---------------------
		InheritedToSubgroups : boolean
			Entry inherited to subgroups
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"CommonName" : "",
			"Certificate" : {},
			"NotAfter" : "",
			"InheritedToSubgroups" : False,
			"GroupId" : 0,
			"ConfiguredIn" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}

	@cached_property
	def CommonName(self):
		return self.__getattr__("CommonName")

	@cached_property
	def Certificate(self):
		return self.__getattr__("Certificate")

	@cached_property
	def NotAfter(self):
		return self.__getattr__("NotAfter")

	@cached_property
	def InheritedToSubgroups(self):
		return self.__getattr__("InheritedToSubgroups")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")


class CertificateTemplatesHandler(BaseListFindHandler):
	'''Management of certificate templates

	Methods
	-------
		createEntry()
			Creates a new CertificateTemplate entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "pki-mgm/{groupid}/templates".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new CertificateTemplate entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return CertificateTemplate(self, self._groupid)


class CertificateTemplate(LazyListEntry):
	'''Parameters of certificate request

	Attributes [read-only]
	----------------------
		GroupId : integer
			Group ID
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
		OrganizationalUnit1 : string
			1. Organizational Unit
		OrganizationalUnit2 : string
			2. Organizational Unit
		OrganizationalUnit3 : string
			3. Organizational Unit
		Organization : string
			Organization
		Location : string
			Location
		StateProvince : string
			State / Province
		Country : string
			Country
		ChallengePassword : string
			Challenge password
		UseKeyUsage : boolean
			Use key usage
		KeyUsage : integer
			Key usage
		UseExtKeyUsage : boolean
			Use extented key usage
		ExtKeyUsage : string
			Extented key usage
		WindownCertificateTemplateName : string
			Windows certificate server template name
		InheritedToSubgroups : boolean
			Entry inherited to subgroups
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"OrganizationalUnit1" : "",
			"OrganizationalUnit2" : "",
			"OrganizationalUnit3" : "",
			"Organization" : "",
			"Location" : "",
			"StateProvince" : "",
			"Country" : "",
			"ChallengePassword" : "",
			"UseKeyUsage" : False,
			"KeyUsage" : 0,
			"UseExtKeyUsage" : False,
			"ExtKeyUsage" : "",
			"WindownCertificateTemplateName" : "",
			"InheritedToSubgroups" : False,
			"GroupId" : 0,
			"ConfiguredIn" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def OrganizationalUnit1(self):
		return self.__getattr__("OrganizationalUnit1")

	@cached_property
	def OrganizationalUnit2(self):
		return self.__getattr__("OrganizationalUnit2")

	@cached_property
	def OrganizationalUnit3(self):
		return self.__getattr__("OrganizationalUnit3")

	@cached_property
	def Organization(self):
		return self.__getattr__("Organization")

	@cached_property
	def Location(self):
		return self.__getattr__("Location")

	@cached_property
	def StateProvince(self):
		return self.__getattr__("StateProvince")

	@cached_property
	def Country(self):
		return self.__getattr__("Country")

	@cached_property
	def ChallengePassword(self):
		return self.__getattr__("ChallengePassword")

	@cached_property
	def UseKeyUsage(self):
		return self.__getattr__("UseKeyUsage")

	@cached_property
	def KeyUsage(self):
		return self.__getattr__("KeyUsage")

	@cached_property
	def UseExtKeyUsage(self):
		return self.__getattr__("UseExtKeyUsage")

	@cached_property
	def ExtKeyUsage(self):
		return self.__getattr__("ExtKeyUsage")

	@cached_property
	def WindownCertificateTemplateName(self):
		return self.__getattr__("WindownCertificateTemplateName")

	@cached_property
	def InheritedToSubgroups(self):
		return self.__getattr__("InheritedToSubgroups")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")


class PkiProfilesHandler(BaseListFindHandler):
	'''Management of PKI profiles

	Methods
	-------
		createEntry()
			Creates a new PkiProfile entry object.
	
	Inherited Methods
	-----------------
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "pki-mgm/{groupid}/profiles".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new PkiProfile entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return PkiProfile(self, self._groupid)


class PkiProfile(LazyListEntry):
	'''Model PkiProfile

	Attributes [read-only]
	----------------------
		GroupId : integer
			Group ID
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
		InheritedToSubgroups : boolean
			Entry inherited to subgroups
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"InheritedToSubgroups" : False,
			"GroupId" : 0,
			"ConfiguredIn" : "",
			"ModifiedOn" : "",
			"ModifiedBy" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def InheritedToSubgroups(self):
		return self.__getattr__("InheritedToSubgroups")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")

	@cached_property
	def ModifiedOn(self):
		return self.__getattr__("ModifiedOn")

	@cached_property
	def ModifiedBy(self):
		return self.__getattr__("ModifiedBy")



class GetIdNameGroupList(BaseEntry):
	'''Model GetIdNameGroupList

	Attributes [read-only]
	----------------------
		Id : integer
			REST ID of the entry
		GroupId : integer
			Group ID of the entry
		ConfiguredIn : string
			Group name of the entry

	Attributes [writable]
	---------------------
		Name : string
			Name of the entry
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Name" : "",
			"GroupId" : 0,
			"ConfiguredIn" : "",
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


class CACertificateList(BaseEntry):
	'''Parameters of a CA certificate list

	Attributes [read-only]
	----------------------
		CommonName : string
			Common Name
		NotAfter : string
			Not After
		GroupId : integer
			Group ID
		ConfiguredIn : string
			Configured in

	Attributes [writable]
	---------------------
		Id : integer
			Id
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"CommonName" : "",
			"NotAfter" : "",
			"GroupId" : 0,
			"ConfiguredIn" : "",
		}

	@cached_property
	def Id(self):
		return self.__getattr__("Id")

	@cached_property
	def CommonName(self):
		return self.__getattr__("CommonName")

	@cached_property
	def NotAfter(self):
		return self.__getattr__("NotAfter")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")


class ImportPkcs12(BaseEntry):
	'''Parameters for importing a PKCS#12 file

	Attributes [writable]
	---------------------
		PKCS12 : string
			PKCS#12 Content
		PIN : string
			PIN
		VpnUserName : string
			User ID
		Authcode : string
			Authentication code
		OsMask : string
			OS Mask
		ServerCertificateName : string
			Server Certificate Name
		SavePIN : boolean
			Save PIN
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"PKCS12" : "",
			"PIN" : "",
			"VpnUserName" : "",
			"Authcode" : "",
			"OsMask" : "",
			"ServerCertificateName" : "",
			"SavePIN" : False,
		}

	@cached_property
	def PKCS12(self):
		return self.__getattr__("PKCS12")

	@cached_property
	def PIN(self):
		return self.__getattr__("PIN")

	@cached_property
	def VpnUserName(self):
		return self.__getattr__("VpnUserName")

	@cached_property
	def Authcode(self):
		return self.__getattr__("Authcode")

	@cached_property
	def OsMask(self):
		return self.__getattr__("OsMask")

	@cached_property
	def ServerCertificateName(self):
		return self.__getattr__("ServerCertificateName")

	@cached_property
	def SavePIN(self):
		return self.__getattr__("SavePIN")


class CreateCertificateResponse(BaseEntry):
	'''Parameters for creating a certificate

	Attributes [writable]
	---------------------
		NewCertId : integer
			REST ID of the created certificate
		ProtocolLog : array from {ParamType}
			Protocol log
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"NewCertId" : 0,
			"ProtocolLog" : [],
		}

	@cached_property
	def NewCertId(self):
		return self.__getattr__("NewCertId")

	@cached_property
	def ProtocolLog(self):
		return self.__getattr__("ProtocolLog")


class RevokeCertificateRequest(BaseEntry):
	'''Parameters for revoke a certificate

	Attributes [writable]
	---------------------
		RevokeReason : integer
			Revoke reason
			Enum Values: 0=unspecified, 1=keyCompromise, 2=cACompromise, 3=affiliationChanged, 4=superseded, 5=cessationOfOperation, 6=certificateHold, 8=removeFromCRL, 9=privilegeWithdrawn, 10=aACompromise
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"RevokeReason" : 0,
		}

	@cached_property
	def RevokeReason(self):
		return self.__getattr__("RevokeReason")


class PkiProfileList(BaseEntry):
	'''Model PkiProfileList

	Attributes [read-only]
	----------------------
		GroupId : integer
			Group ID
		ConfiguredIn : string
			Configured in

	Attributes [writable]
	---------------------
		Id : integer
			Id
		Name : string
			Name
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"Name" : "",
			"GroupId" : 0,
			"ConfiguredIn" : "",
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


class IssuedCertificateList(BaseEntry):
	'''Parameters of a issued certificate list

	Attributes [read-only]
	----------------------
		Id : integer
			Id
		CommonName : string
			Common Name
		GroupName : string
			Group Name
		DownloadTime : time
			Download Time
		GroupId : integer
			Group ID
		ConfiguredIn : string
			Configured in
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"CommonName" : "",
			"GroupName" : "",
			"DownloadTime" : "",
			"GroupId" : 0,
			"ConfiguredIn" : "",
		}

	@cached_property
	def Id(self):
		return self.__getattr__("Id")

	@cached_property
	def CommonName(self):
		return self.__getattr__("CommonName")

	@cached_property
	def GroupName(self):
		return self.__getattr__("GroupName")

	@cached_property
	def DownloadTime(self):
		return self.__getattr__("DownloadTime")

	@cached_property
	def GroupId(self):
		return self.__getattr__("GroupId")

	@cached_property
	def ConfiguredIn(self):
		return self.__getattr__("ConfiguredIn")


class CertificateSetAuthCode(BaseEntry):
	'''Parameters for setting the authentication code

	Attributes [writable]
	---------------------
		AuthenticationCode : string
			Authentication Code
		AuthCodeOsWindows : boolean
			Authentication Code enabled for Windows
		AuthCodeOsLinux : boolean
			Authentication Code enabled for Linux
		AuthCodeOsMac : boolean
			Authentication Code enabled for Mac
		AuthCodeOsAndroid : boolean
			Authentication Code enabled for Android
		AuthCodeOsIOS : boolean
			Authentication Code enabled for iOS
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"AuthenticationCode" : "",
			"AuthCodeOsWindows" : False,
			"AuthCodeOsLinux" : False,
			"AuthCodeOsMac" : False,
			"AuthCodeOsAndroid" : False,
			"AuthCodeOsIOS" : False,
		}

	@cached_property
	def AuthenticationCode(self):
		return self.__getattr__("AuthenticationCode")

	@cached_property
	def AuthCodeOsWindows(self):
		return self.__getattr__("AuthCodeOsWindows")

	@cached_property
	def AuthCodeOsLinux(self):
		return self.__getattr__("AuthCodeOsLinux")

	@cached_property
	def AuthCodeOsMac(self):
		return self.__getattr__("AuthCodeOsMac")

	@cached_property
	def AuthCodeOsAndroid(self):
		return self.__getattr__("AuthCodeOsAndroid")

	@cached_property
	def AuthCodeOsIOS(self):
		return self.__getattr__("AuthCodeOsIOS")


class CreateCertificateRequest(BaseEntry):
	'''POST Parameters for creating a certificate

	Attributes [writable]
	---------------------
		CertificateRequest : integer
			REST ID of certificate request
		PkiProfile : integer
			REST ID of PKI profile
		PIN : string
			PIN
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"CertificateRequest" : 0,
			"PkiProfile" : 0,
			"PIN" : "",
		}

	@cached_property
	def CertificateRequest(self):
		return self.__getattr__("CertificateRequest")

	@cached_property
	def PkiProfile(self):
		return self.__getattr__("PkiProfile")

	@cached_property
	def PIN(self):
		return self.__getattr__("PIN")


class CertificateRequestAdd(BaseEntry):
	'''Parameters for adding a certificate request

	Attributes [writable]
	---------------------
		Name : string
			Name
		CertificateTemplate : string or integer from {Controller}
			Certificate Template
		CommonName : string
			Common Name
		GivenName : string
			Given name
		SurName : string
			Surname
		EMail : string
			E-Mail
		Title : string
			Title
		OrganizationalUnit1 : string
			1. Organizational Unit
		OrganizationalUnit2 : string
			2. Organizational Unit
		OrganizationalUnit3 : string
			3. Organizational Unit
		Organization : string
			Organization
		Location : string
			Location
		StateProvince : string
			State / Province
		Country : string
			Country
		ChallengePassword : string
			Challenge password
		AuthenticationCode : string
			Authentication code
		Username : string
			Username
		UseKeyUsage : boolean
			Use key usage
		KeyUsage : integer
			Key usage
		UseExtKeyUsage : boolean
			Use extented key usage
		ExtKeyUsage : string
			Extented key usage
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Name" : "",
			"CertificateTemplate" : "",
			"CommonName" : "",
			"GivenName" : "",
			"SurName" : "",
			"EMail" : "",
			"Title" : "",
			"OrganizationalUnit1" : "",
			"OrganizationalUnit2" : "",
			"OrganizationalUnit3" : "",
			"Organization" : "",
			"Location" : "",
			"StateProvince" : "",
			"Country" : "",
			"ChallengePassword" : "",
			"AuthenticationCode" : "",
			"Username" : "",
			"UseKeyUsage" : False,
			"KeyUsage" : 0,
			"UseExtKeyUsage" : False,
			"ExtKeyUsage" : "",
		}

	@cached_property
	def Name(self):
		return self.__getattr__("Name")

	@cached_property
	def CertificateTemplate(self):
		return self.__getattr__("CertificateTemplate")

	@cached_property
	def CommonName(self):
		return self.__getattr__("CommonName")

	@cached_property
	def GivenName(self):
		return self.__getattr__("GivenName")

	@cached_property
	def SurName(self):
		return self.__getattr__("SurName")

	@cached_property
	def EMail(self):
		return self.__getattr__("EMail")

	@cached_property
	def Title(self):
		return self.__getattr__("Title")

	@cached_property
	def OrganizationalUnit1(self):
		return self.__getattr__("OrganizationalUnit1")

	@cached_property
	def OrganizationalUnit2(self):
		return self.__getattr__("OrganizationalUnit2")

	@cached_property
	def OrganizationalUnit3(self):
		return self.__getattr__("OrganizationalUnit3")

	@cached_property
	def Organization(self):
		return self.__getattr__("Organization")

	@cached_property
	def Location(self):
		return self.__getattr__("Location")

	@cached_property
	def StateProvince(self):
		return self.__getattr__("StateProvince")

	@cached_property
	def Country(self):
		return self.__getattr__("Country")

	@cached_property
	def ChallengePassword(self):
		return self.__getattr__("ChallengePassword")

	@cached_property
	def AuthenticationCode(self):
		return self.__getattr__("AuthenticationCode")

	@cached_property
	def Username(self):
		return self.__getattr__("Username")

	@cached_property
	def UseKeyUsage(self):
		return self.__getattr__("UseKeyUsage")

	@cached_property
	def KeyUsage(self):
		return self.__getattr__("KeyUsage")

	@cached_property
	def UseExtKeyUsage(self):
		return self.__getattr__("UseExtKeyUsage")

	@cached_property
	def ExtKeyUsage(self):
		return self.__getattr__("ExtKeyUsage")


class RenewCertificateRequest(BaseEntry):
	'''Parameters for renew a certificate

	Attributes [writable]
	---------------------
		PkiProfile : integer
			REST ID of PKI profile
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"PkiProfile" : 0,
		}

	@cached_property
	def PkiProfile(self):
		return self.__getattr__("PkiProfile")


class Certificate(BaseEntry):
	'''Object with certificate content

	Attributes [read-only]
	----------------------
		Subject : string
			Subject of the certificate
		Issuer : string
			Issuer of the certificate
		SerNr : string
			Serial number of the certificate
		NotBefore : string
			NotBefore time stamp of the certificate
		NotAfter : string
			NotAfter time stamp of the certificate
		FingerPrintSHA1 : string
			SHA1 finger print of the certificate
		FingerPrintSHA256 : string
			SHA-256 finger print of the certificate

	Attributes [writable]
	---------------------
		DER : string
			Base64 encoded certificate
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"DER" : "",
			"Subject" : "",
			"Issuer" : "",
			"SerNr" : "",
			"NotBefore" : "",
			"NotAfter" : "",
			"FingerPrintSHA1" : "",
			"FingerPrintSHA256" : "",
		}

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

