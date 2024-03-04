import os, copy
import threading
import pickle, json

__format__ = ["json", "pickle"]

def read(filename, btype="json"):
    mode = {"json": "r", "pickle": "rb"}[btype]
    method = {"json": json.load, "pickle": pickle.load}[btype]
    if btype=="json":
        with open(filename, mode, encoding="utf8") as f:
            data = method(f)
    else:
        with open(filename, mode) as f:
            data = method(f)
    return data

def write(data, filename, btype="json"):
    mode = {"json": "w", "pickle": "wb"}[btype]
    method = {"json": json.dump, "pickle": pickle.dump}[btype]
    if btype=="json":
        with open(filename, mode, encoding='utf8') as f:
            method(data, f, ensure_ascii=False)
    else:
        with open(filename, mode) as f:
            method(data, f)
        
class Bucket:
    def __init__(self, bucket_name, bucket_path, btype, exit_callback=lambda:None):
        self.bucket_name = bucket_name
        self.btype = btype
        
        self.__exit_callback__ = exit_callback
        self.__lock__ = threading.Lock()
        self.__locked__ = False
        self.__location__ = os.path.join(bucket_path, bucket_name+"."+btype)
        self.__content__ = self.__load__(default={})
    
    def flush(self):
        write(self.__content__, self.__location__, btype=self.btype)
    
    def has(self, key):
        assert self.__locked__
        return key in self.__content__
    
    def get(self, key, default=None):
        assert self.__locked__
        return self.__content__[key] if self.has(key) else default

    def content(self):
        assert self.__locked__
        return self.__content__

    def __load__(self, default={}):
        if not os.path.exists(self.__location__):
            os.makedirs(os.path.dirname(self.__location__), exist_ok=True)
            write(default, self.__location__, btype=self.btype)
            return copy.deepcopy(default)
        return read(self.__location__, btype=self.btype)
    
    def __getitem__(self, key):
        return self.__content__[key]
    
    def __setitem__(self, key, value):
        self.__content__[key] = value
    
    def __enter__(self):
        self.__lock__.acquire()
        self.__locked__ = True
        return self
    
    def __exit__(self, exec_type, exc, exc_tb):
        self.__content__ = copy.deepcopy(self.__content__)
        self.__exit_callback__(self)
        self.__locked__ = False
        self.__lock__.release()
    
    def __str__(self):
        return str(self.__content__)
    
class EasyBucket:
    def __init__(self):
        self.collection_lock = threading.Lock()
        self.buckets = {}
        self.fifo = []
        self.max_fifo = 1024
        self.btype = "json"
        self.bucket_path = "easybucketdatabase"

    def __call__(self, bucket_name, btype=None):
        bucket_name = bucket_name.replace("\\", "/")
        assert bucket_name.startswith("/") == False
        
        bucket_path = self.bucket_path
        btype = btype if btype else self.btype
        with self.collection_lock:
            bucket, cnt = self.buckets.get(bucket_name, (None, 0))
            if bucket==None:
                bucket = Bucket(bucket_name, bucket_path=bucket_path, btype=btype, exit_callback=self.untick)
            self.buckets[bucket_name] = (bucket, cnt + 1)
            self.fifo.append(bucket_name)
        return bucket
        
    def untick(self, bucket):
        bucket_name = bucket.bucket_name
        with self.collection_lock:
            bucket, cnt = self.buckets[bucket_name]
            self.buckets[bucket_name] = (bucket, cnt - 1)
            if len(self.fifo) > self.max_fifo:
                self.tryUnload(self.fifo.pop(0))
    
    def list(self):
        lst = os.listdir(self.bucket_path)
        buckets = []
        for x in lst:
            tmp = x.split(".")
            bucket_name = ".".join(tmp[0:-1])
            btype = tmp[-1]
            if len(bucket_name) > 0 and (btype in __format__):
                buckets.append({
                    "bucket_name": bucket_name,
                    "btype": btype,
                })
        return buckets
    
    def delete(self, bucket_name):
        ret = False
        with self.collection_lock:
            for btype in __format__:
                filename = os.path.join(self.bucket_path, bucket_name+"."+btype)
                if os.path.exists(filename) and self.tryUnload(bucket_name):
                    os.remove(filename)
                    ret = True
        return ret
    
    def tryUnload(self, bucket_name):
        bucket, cnt = self.buckets.get(bucket_name, (None, 0))
        if bucket == None:
            return True
        else:
            if cnt <= 0:
                bucket.flush()
                self.buckets.pop(bucket_name)
                return True
            else:
                return False
    
    def clean(self):
        with self.collection_lock:
            while len(self.fifo) > 0:
                self.tryUnload(self.fifo.pop(0))

easyBucket = EasyBucket()
