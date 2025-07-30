import os
from hashlib import md5
from cryptography.fernet import Fernet

def encrypt (key, s, t = None):
  f = Fernet (key)
  with open(s, "rb") as file:
    file_data = file.read()
    encrypted_data = f.encrypt(file_data)

  with open(t or s, "wb") as file:
    file.write (encrypted_data)

def decrypt (key, s, t = None):
  f = Fernet (key)
  with open(s, "rb") as file:
    file_data = file.read()
    decrypted_data = f.decrypt(file_data)

  with open(t or s, "wb") as file:
    file.write (decrypted_data)

def get_file_hash (path):
  with open (path, 'rb') as f:
    hash = md5 (f.read ()).hexdigest()
  return hash

def get_directory_hash (base_dir, exts = ['.py']):
  hashes = []
  for path, dirs, files in os.walk (base_dir):
    for file in files:
      _, ext = os.path.splitext (file)
      if ext not in exts:
        continue
      hash = get_file_hash (os.path.join (path, file))
      hashes.append (hash)
  assert hashes
  return md5 (','.join (sorted (hashes)).encode ()).hexdigest ()
