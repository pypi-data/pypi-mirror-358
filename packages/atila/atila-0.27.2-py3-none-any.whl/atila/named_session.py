from . import mbox, session

class NamedSession:
	def __init__ (self, wclass, cookie, request, secret_key, timeout = 1200):
		self.__wclass = wclass
		self.__cookie = cookie
		self.__obj = None
		self.__request = request
		self.__secret_key = secret_key
		self.__timeout = timeout
		self.__name = None
		# mount root default
		self.mount () # mount root

	def mount (self, name = None, session_timeout = None, secret_key = None, path = "/", domain = None, secure = False, http_only = False, same_site = None, extend = True):
		if self.__obj and name == self.__name:
			return
		self.__name = name

		if self.__obj:
			self.__obj.commit ()

		secret_key, session_timeout = self.__get_config (secret_key, session_timeout)
		if not secret_key:
			raise AssertionError ("Secret key is not configured")

		if not name:
			if not (path is None or path == "/"):
				raise AssertionError ("No-Named session path should be None or '/'")
			name = ""
			path = "/"

		if self.__wclass == "session":
			obj = self.__get_session (name, secret_key, session_timeout, extend)
		else:
			obj = self.__get_notices (name, secret_key)

		obj.config (path, domain, secure, http_only, same_site)
		self.__obj = obj

	def exists (self, name = None):
		if name is None:
			name = ""
		return name in self.__dataset

	def __getattr__ (self, attr):
		return getattr (self.__obj, attr)

	def __contains__ (self, k):
		return k in self.__obj

	def __getitem__ (self, k):
		return self.__obj [k]

	def __setitem__ (self, k, v):
		self.__obj [k] = v

	def __iter__ (self):
		return self.__obj.__iter__ ()

	def __delitem__ (self, k):
		del self.__obj [k]

	def __get_config (self, secret_key, session_timeout):
		return (
		 secret_key and secret_key.encode ("utf8") or self.__secret_key,
		 session_timeout and session_timeout or self.__timeout
		)

	def __get_session (self, name, secret_key, session_timeout, extend):
		return session.Session (name, self.__cookie, self.__request, secret_key, session_timeout, extend)

	def __get_notices (self, name, secret_key):
		return mbox.MessageBox (name, self.__cookie, self.__request, secret_key)

