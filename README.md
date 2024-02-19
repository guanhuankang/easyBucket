# easyBucket
An easy multi-thread supported bucket database


# Installation
```sh
pip install git+https://github.com/guanhuankang/easyBucket.git
```


# Quick Try
Below is the tutorial code.

```python
from easybucket import easyBucket

## optional
easyBucket.bucket_path = "easyBucketDataBase"
easyBucket.max_fifo = 100 

def tutorial(x):
    bucket_name = "test"  ## Bucket name
    with easyBucket(bucket_name, btype="json") as bucket:
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
        bucket.flush()  ## flush mannually ## Actually, easyBucket will flush automatically
        data = bucket.content()
    print(data)
    print(easyBucket.buckets, len(easyBucket.fifo))

if __name__=="__main__":
    from threading import Thread

    # tutorial(2)
    # exit(0)

    threads = [
        Thread(target=tutorial, args=(x,))
        for x in range(1000)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    easyBucket.clean()  ## flush all data to stroage before exiting easyBucket
    print(easyBucket.buckets)  ## cache in the easyBucket

```
where "easyBucket.bucket_path" is the root location of the bucket database, and "easyBucket.max_fifo" is the max-length of the FIFO queue, which will trigger the flush and unload event when the length of FIFO exceed the max-length value.

Run tutorial.py:
```shell
python tutorial.py
```

Note that "bucket_name" is the unique identifier to retrieve the bucket.

# ToDo
[] Multi-bucket supporting

```shell
Huankang Guan, 2659814334@qq.com
```