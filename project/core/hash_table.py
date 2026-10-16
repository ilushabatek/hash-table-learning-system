from hash_function import hash_Dan_Bernstein, hash_FNV1a, hash_polynomial


class HashTable:
   def  __init__(self, size):
      self.size = size
      self.slots = None * self.size
      self.used = 0
      self.collision = 0
      
   def hash_func_select(self, choice, key):
      if choice == 1:
         hash_polynomial(key, self.size)
      if choice == 2:
         hash_FNV1a(key, self.size)
      if choice == 3:
         hash_Dan_Bernstein(key, self.size)
   
         
         
          