
import urllib.parse
import urllib.request
import urllib.error
import ssl
import json
import base64
import binascii
from .base import ApiException, ApiAuthenticationException

class AuthBase:
	def __init__(self):
		pass

	# this init function is called from BaseApi
	def init(self, host, tls, ssl_verify, ssl_ca_options, callback=None):
		self._host = host
		self._tls = tls 
		self._ssl_verify = ssl_verify
		self._ssl_ca_options = ssl_ca_options
		self._callback = callback # called on every login

	def __del__(self):
		try:
			self._logout()
		except:
			#ingore all errors; and do not print them
			pass

	# derived classes may implement this method
	def getHeader(self):
		"""Returns header-fields needed for the authentication as key-value pairs in a dict. May call _login()"""
		return {}

	# derived classes may implement this method
	def _login(self):
		pass

	# derived classes may implement this method
	def _logout(self):
		pass


class AuthAccessToken(AuthBase):
	def __init__(self, token, type="Bearer"):
		AuthBase.__init__(self)
		self.setToken(token, type)
		self._oauthTokenUrlPath  = "/oauth2/token" 
		self._oauthRevokeUrlPath = "/oauth2/revoke" 

	def setToken(self, token, type):
		self._accessToken = token 
		self._tokenType = type

	def getHeader(self):
		if self._accessToken and self._tokenType:
			return {'Authorization': self._tokenType + " " + self._accessToken}
		return {}

class AuthClientCredential(AuthAccessToken):
	"""oauth2 client credentioal authentication.
		Needs a clientId and a clientSecret.
	"""

	def __init__(self, clientId, clientSecret):
		AuthAccessToken.__init__(self, "")
		self._clientId = clientId
		self._clientSecret = clientSecret

	def getHeader(self):
		if not self._accessToken:
			self._login() 
		return AuthAccessToken.getHeader(self)

	def _sendRequest(self, url, data, headers, method):
		resp = ""	# json http response as dict
		err = None	# exception
		try:
			if self._tls:
				context = ssl.create_default_context(**self._ssl_ca_options)
				if not self._ssl_verify:
					context.check_hostname = False
					context.verify_mode = ssl.CERT_NONE
			else:
				context = None
			conn = urllib.request.Request(url, data=data, headers=headers, method=method)
			res = urllib.request.urlopen(conn, context=context)
			content = res.read().decode("utf-8")
			if content:
				resp = json.loads(content)
		except urllib.error.HTTPError as e:
			if e.code == 502:
				raise ApiException ("HTTP Error 502: Server is not running")

			content = e.read().decode("utf-8")
			if content:
				resp = json.loads(content)	#when this fails, it might be an ssl error...
				e.msg = resp["error"] + ": " + resp["error_description"]
			err = e

		finally:
			if err:
				if err.code == 400:
					raise ApiAuthenticationException("HTTP Error 400: "+err.msg)
				else:
					raise err
		return resp

	def _login(self, verbose=False, show_requests=False):
		headers = {
			'Accept'		: 'application/json,UTF-8',
			'Content-Type'	: 'application/x-www-form-urlencoded',
		}
		url = self._host + self._oauthTokenUrlPath
		data = f"client_id={urllib.parse.quote(self._clientId)}"
		data += f"&client_secret={urllib.parse.quote(self._clientSecret)}"
		data +=	"&grant_type=client_credentials"
		data = bytes(data, encoding="utf-8")

		if verbose:
			print ("Login ------------")
		if verbose or show_requests:
			print ("POST " + url)
		if verbose:
			print ("\t"+ str(headers))
			print ("\t"+ str(data)) # this prints credentials

		resp = self._sendRequest(url, data, headers, "POST")
		self.setToken(resp.get("access_token"), resp.get("token_type"))

		if verbose:
			print(resp)
		if self._callback:
			self._callback()
		
	def __del__(self):
		try:
			self._logout()
		except:
			#ingore all errors; and do not print them
			pass

	def _logout(self, verbose=False):
		if not self._accessToken:
			return

		authorization_b64 = base64.b64encode("{}:{}".format(self._clientId, self._clientSecret).encode()).decode('ascii')
		headers = {
			'Accept'		: 'application/json,UTF-8',
			'Content-Type'	: 'application/x-www-form-urlencoded',
			'Authorization': "Basic " + authorization_b64 
		}
		url = self._host + self._oauthRevokeUrlPath
		data = f"token={urllib.parse.quote(self._accessToken)}"
		data += "&token_type_hint=access_token"
		data = bytes(data, encoding="utf-8")

		if verbose:
			print ("Logout -----------")
			print ("POST " + url)
			print ("\t"+ str(headers))
			print ("\t"+ str(data)) # this prints credentials
		resp = self._sendRequest(url, data, headers, "POST")
		if verbose:
			print(resp)
