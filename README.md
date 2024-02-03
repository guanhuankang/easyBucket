# easyBucket
An easy multi-thread supported bucket database


# Tutorial
```sh
pip install git+https://github.com/guanhuankang/easyBucket.git
BUCKET_PATH=bucket_archive BUCKET_FIFO=5 python main.py
```

```python
from threading import Thread
import time,random

from easybucket import easyBucket

if __name__=="__main__":
    def tutorial(x):
        bucket_name = "test"  ## Bucket name
        bucket = easyBucket.tick(bucket_name, btype="json")  ## Claim a bucket, btype=json OR pickle
        with bucket:  ## thread-safe
            ## Code Here
            ## bucket supports dict-like usage
            bucket["say"] = "Hello World"
            bucket["name"] = "I am easyBucket"
            bucket["array"] = ["I", "support", "array"]
            bucket["hasAddr"] = bucket.has("addr")
            bucket["dictOfdict"] = {
                "key2": {
                    "key1": "value"
                }
            }
            bucket["cnt"] = bucket.get("cnt", 0) + 1
            # bucket.flush()  ## flush mannually
            ## Actually, easyBucket will flush automatically
        easyBucket.untick(bucket)  ## Tell easyBucket that we are done with this bucket

    threads = [
        Thread(target=tutorial, args=(x,))
        for x in range(100)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    easyBucket.clean()  ## flush all data to stroage before exiting easyBucket
    print(easyBucket.buckets)  ## cache in the easyBucket

```