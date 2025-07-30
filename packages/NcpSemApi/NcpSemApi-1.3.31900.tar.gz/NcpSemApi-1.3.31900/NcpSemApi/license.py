
#---------------------------------------------------------------
# This file is generated! Dont make any changes in this file.
#---------------------------------------------------------------
from .base import *
from .cached_property import cached_property



class LicenseOverviewHandler(BaseListHandler):
	'''Overview of licenses

	Methods
	-------
		createEntry()
			Creates a new LicenseOverview entry object.
	
	Inherited Methods
	-----------------
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "license-mgm/{groupid}/overview".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new LicenseOverview entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return LicenseOverview(self, self._groupid)
	

class LicenseOverview(ListEntry):
	'''Parameters of license overview

	Attributes [read-only]
	----------------------
		Product : string
			Product
		Version : string
			Version
		Tunnel : integer
			Tunnel
		Total : integer
			Total
		Assigned : integer
			Assigned
		Free : integer
			Free
	'''

	def __init__(self, getHandler, groupid):
		ListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Product" : "",
			"Version" : "",
			"Tunnel" : 0,
			"Total" : 0,
			"Assigned" : 0,
			"Free" : 0,
		}

	@cached_property
	def Product(self):
		return self.__getattr__("Product")

	@cached_property
	def Version(self):
		return self.__getattr__("Version")

	@cached_property
	def Tunnel(self):
		return self.__getattr__("Tunnel")

	@cached_property
	def Total(self):
		return self.__getattr__("Total")

	@cached_property
	def Assigned(self):
		return self.__getattr__("Assigned")

	@cached_property
	def Free(self):
		return self.__getattr__("Free")


class LicenseDetailsHandler(BaseListInsertHandler, BaseListDeleteHandler):
	'''Management of licenses

	Methods
	-------
		createEntry()
			Creates a new LicenseDetail entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "license-mgm/{groupid}/license-details".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def createEntry(self):
		'''Creates a new LicenseDetail entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return LicenseDetail(self, self._groupid)


class LicenseDetail(ListEntry):
	'''Parameters of license

	Attributes [read-only]
	----------------------
		Id : integer
			Id
		SerNr : string
			Serial Number
		Product : string
			Product
		Version : string
			Version
		Tunnel : integer
			Tunnel
		User : string
			User / Gateway
		Inherited : boolean
			Inherited
		DeviceID : string
			Device ID
		Subscription : string
			Subscription

	Methods
	-------
		unbind()
			Unbind license from device
	'''

	def __init__(self, getHandler, groupid):
		ListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"SerNr" : "",
			"Product" : "",
			"Version" : "",
			"Tunnel" : 0,
			"User" : "",
			"Inherited" : False,
			"DeviceID" : "",
			"Subscription" : "",
		}

	@cached_property
	def Id(self):
		return self.__getattr__("Id")

	@cached_property
	def SerNr(self):
		return self.__getattr__("SerNr")

	@cached_property
	def Product(self):
		return self.__getattr__("Product")

	@cached_property
	def Version(self):
		return self.__getattr__("Version")

	@cached_property
	def Tunnel(self):
		return self.__getattr__("Tunnel")

	@cached_property
	def User(self):
		return self.__getattr__("User")

	@cached_property
	def Inherited(self):
		return self.__getattr__("Inherited")

	@cached_property
	def DeviceID(self):
		return self.__getattr__("DeviceID")

	@cached_property
	def Subscription(self):
		return self.__getattr__("Subscription")
			
	def unbind(self):
		'''Unbind license from device'''
		return self._callMethod('/unbind')


class SubscriptionsHandler(BaseListFindHandler, BaseListInsertHandler, BaseListDeleteHandler):
	'''Management of subscriptions

	Methods
	-------
		createEntry()
			Creates a new Subscription entry object.
	
	Inherited Methods
	-----------------
		delete (BaseListDeleteHandler)
		find (BaseListFindHandler)
		get (BaseListGetHandler)
		insert (BasListInsertHandler)
		list (BaseListHandler)
	'''
	
	def __init__(self, api, groupid):
		url = "license-mgm/{groupid}/subscriptions".format(**vars())
		BaseHandler.__init__(self, api, url)
		self._groupid = groupid

	def find(self, searchValue, searchKey="SerialNumber", throw=False, options={}):
		return BaseListFindHandler.find(self, searchValue, searchKey=searchKey, throw=throw, options=options)

	def createEntry(self):
		'''Creates a new Subscription entry object.
			Call createEntry to get an empty object for insert() or update().
			createEntry is called by get()'''
		return Subscription(self, self._groupid)


class Subscription(LazyListEntry):
	'''Parameters of a subscription

	Attributes [read-only]
	----------------------
		Id : integer
			Id
		SubscriptionSerNr : string
			SubscriptionSerNr
		State : integer
			State
			Enum Values: 0=notValid, 1=valid, 3=notVerified, 4=deactivated, 101=expired
		ExpireDate : string
			Expire Date
		NextCheckTime : time
			Next check time
		ReplicationVersion : integer
			Replication version
		EMail : string
			E-Mail
		RefreshInProgress : boolean
			Refresh in progress
		ImportState : integer
			ImportState
			Enum Values: 0=init, 1=connect, 2=import, 3=verify, 4=confirm, 5=finished
		ImportedLicenses : integer
			Number of imported licenses
		ImportNumberOfLicenses : integer
			Number of licenses to import

	Methods
	-------
		licences()
			Get the number of licenses and products in this subscription
		reconnect()
			Reconnect a subscription to the NCP activation server
	'''

	def __init__(self, getHandler, groupid):
		LazyListEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Id" : 0,
			"SubscriptionSerNr" : "",
			"State" : 0,
			"ExpireDate" : "",
			"NextCheckTime" : "",
			"ReplicationVersion" : 0,
			"EMail" : "",
			"RefreshInProgress" : False,
			"ImportState" : 0,
			"ImportedLicenses" : 0,
			"ImportNumberOfLicenses" : 0,
		}

	@cached_property
	def Id(self):
		return self.__getattr__("Id")

	@cached_property
	def SubscriptionSerNr(self):
		return self.__getattr__("SubscriptionSerNr")

	@cached_property
	def State(self):
		return self.__getattr__("State")

	@cached_property
	def ExpireDate(self):
		return self.__getattr__("ExpireDate")

	@cached_property
	def NextCheckTime(self):
		return self.__getattr__("NextCheckTime")

	@cached_property
	def ReplicationVersion(self):
		return self.__getattr__("ReplicationVersion")

	@cached_property
	def EMail(self):
		return self.__getattr__("EMail")

	@cached_property
	def RefreshInProgress(self):
		return self.__getattr__("RefreshInProgress")

	@cached_property
	def ImportState(self):
		return self.__getattr__("ImportState")

	@cached_property
	def ImportedLicenses(self):
		return self.__getattr__("ImportedLicenses")

	@cached_property
	def ImportNumberOfLicenses(self):
		return self.__getattr__("ImportNumberOfLicenses")
			
	def licences(self):
		'''Get the number of licenses and products in this subscription'''
		return self._callMethodGet('/licences')
			
	def reconnect(self):
		'''Reconnect a subscription to the NCP activation server'''
		return self._callMethod('/reconnect')



class AddSubscription(BaseEntry):
	'''Model AddSubscription

	Attributes [writable]
	---------------------
		SubscriptionSerNr : string
			SubscriptionSerNr
		DownloadKey : string
			Download Key
		EMail : string
			EMail
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"SubscriptionSerNr" : "",
			"DownloadKey" : "",
			"EMail" : "",
		}

	@cached_property
	def SubscriptionSerNr(self):
		return self.__getattr__("SubscriptionSerNr")

	@cached_property
	def DownloadKey(self):
		return self.__getattr__("DownloadKey")

	@cached_property
	def EMail(self):
		return self.__getattr__("EMail")


class SubscriptionLicensesOverview(BaseEntry):
	'''Model SubscriptionLicensesOverview

	Attributes [read-only]
	----------------------
		Products : array from model {Model}
			List of subscrition product info entries
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"Products" : [],
		}

	@cached_property
	def Products(self):
		return self.__getattr__("Products")


class LicenseInsert(BaseEntry):
	'''Parameters of insert a license

	Attributes [writable]
	---------------------
		SerNr : string
			Serial Number
		ActivationKey : string
			Activation Key
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"SerNr" : "",
			"ActivationKey" : "",
		}

	@cached_property
	def SerNr(self):
		return self.__getattr__("SerNr")

	@cached_property
	def ActivationKey(self):
		return self.__getattr__("ActivationKey")


class SubscriptionProductInfo(BaseEntry):
	'''Model SubscriptionProductInfo

	Attributes [read-only]
	----------------------
		ProductName : string
			Product Name
		NbrOfLicenses : string
			Number of licenses
		Tunnels : string
			Tunnels
	'''

	def __init__(self, getHandler):
		BaseEntry.__init__(self, getHandler)
		# Default values
		self._defaultValues = {
			"ProductName" : "",
			"NbrOfLicenses" : "",
			"Tunnels" : "",
		}

	@cached_property
	def ProductName(self):
		return self.__getattr__("ProductName")

	@cached_property
	def NbrOfLicenses(self):
		return self.__getattr__("NbrOfLicenses")

	@cached_property
	def Tunnels(self):
		return self.__getattr__("Tunnels")

