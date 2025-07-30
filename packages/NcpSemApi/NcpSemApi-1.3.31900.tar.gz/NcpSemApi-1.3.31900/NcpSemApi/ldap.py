try:
	from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, SUBTREE
	ldap_available = True
except ModuleNotFoundError:
	ldap_available = False
	Server = None
	Connection = None
	ALL = None
	ALL_ATTRIBUTES = None
	SUBTREE = None

	

# install python ldap3 library:
#   pip install ldap3

# https://ldap3.readthedocs.io/en/latest/searches.html

class Ldap:
	def __init__(self, host, bindDN, password):
		if not ldap_available:
			raise ModuleNotFoundError("Module named ldap3 is not installed. Try: pip install ldap3")
		self._server = Server(host, get_info=ALL)
		self._conn = Connection(self._server, bindDN, password, auto_bind=True)
		self._pageSize = 500
		self._result = []

	def search (self, baseDn, filter="(objectclass=*)", scope=SUBTREE, attributes=ALL_ATTRIBUTES):

		ret = []
		self._conn.search(baseDn, filter, attributes=attributes, 
 					  	  search_scope=scope,
					      paged_size=self._pageSize)
		for e in self._conn.entries:
			ret.append(e) 

		cookie = self._conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
		while cookie:	
			self._conn.search(baseDn, filter,  attributes=attributes, 
						search_scope=scope,
						paged_size=self._pageSize,
						paged_cookie = cookie)
			cookie = self._conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
			for e in self._conn.entries:
				ret.append(e) 

		return ret 


#ldap = Ldap ('ads.company1.com', "cn=Administrator,cn=users,dc=xxx,dc=yyy,dc=zz", "...")
#users = ldap.search ("cn=users,dc=zzz,dc=yyy,dc=zz", 
#					 filter="(objectclass=person)",
#					 attributes = ['cn', 'distinguishedName', 'memberOf', 'sAMAccountName'])
