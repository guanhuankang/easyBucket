from easybucket import easyBucket

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
    import os
    import time,random

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
