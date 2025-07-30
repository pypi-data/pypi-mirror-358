from Crypto import Random
from Crypto.Cipher import AES as AESCipher
import base64
import math
from hashlib import md5
from hmac import new as hmac
from hashlib import sha1 as _default_hash
import pickle as pickle
from urllib.parse import quote_plus, unquote_plus

def trans (key):
  return md5 (key.encode ()).hexdigest ().encode ()

class AES:
  BLCOK_SIZE = 16

  @classmethod
  def encrypt (cls, message, passphrase):
    passphrase = trans (passphrase)
    IV = Random.new ().read (cls.BLCOK_SIZE)
    aes = AESCipher.new (passphrase, AESCipher.MODE_CFB, IV)
    return base64.b64encode (IV + aes.encrypt (message))

  @classmethod
  def decrypt (cls, encrypted, passphrase):
    passphrase = trans (passphrase)
    encrypted = base64.b64decode (encrypted)
    IV = encrypted [:cls.BLCOK_SIZE]
    aes = AESCipher.new (passphrase, AESCipher.MODE_CFB, IV)
    return aes.decrypt (encrypted [cls.BLCOK_SIZE:])


class Text:
  def __init__ (self, passphrase):
    self.passphrase = passphrase.decode ()

  def serialize (self, t)  :
    return AES.encrypt (t.encode (), self.passphrase)

  def deserialize (self, t)  :
    return AES.decrypt (t, self.passphrase)


class Dict:
  hash_method = _default_hash
  serialization_method = pickle
  quote_base64 = True

  def __init__ (self, secret_key):
    self.secret_key = secret_key

  def quote (self, value):
    value = self.serialization_method.dumps (value, 1)
    value = base64.b64encode (value)
    value = b''.join (value.splitlines()).strip ()
    return value

  def unquote (self, value):
    value = value.ljust ((math.ceil (len (value) / 4)) * 4, b'=')
    value = base64.b64decode (value)
    value = self.serialization_method.loads (value)
    return value

  def serialize (self, d):
    result = []
    mac = hmac (self.secret_key, None, self.hash_method)
    for key, value in sorted (d.items(), key = lambda x: x[0]):
      assert isinstance (key, str)
      result.append (key.encode () + b"=" + self.quote (value))
      mac.update (b'|' + result[-1])
    return (base64.b64encode (mac.digest ()).strip () + b"?" + b'&'.join (result))

  def deserialize (self, string):
    base64_hash, data = string.split (b'?', 1)
    d = {}
    mac = hmac (self.secret_key, None, self.hash_method)
    for item in data.split(b'&'):
      mac.update (b'|' + item)
      if not b'=' in item:
        raise ValueError ('invalid data')
      key, value = item.split(b'=', 1)
      key = key.decode ()
      d [key] = value

    client_hash = base64.b64decode (base64_hash)
    if d and client_hash != mac.digest ():
      raise ValueError ('invalid signature')
    for key, value in sorted (d.items(), key = lambda x: x[0]):
      d [key] = self.unquote (value)
    return d
