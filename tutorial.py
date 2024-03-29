from easybucket import easyBucket

## optional
easyBucket.bucket_path = "easyBucketDataBase"
easyBucket.max_fifo = 100 
easyBucket.btype = "json"

def tutorial(x):
    bucket_name = "testcases/test"+str(x%5)  ## Bucket name
    with easyBucket(bucket_name) as bucket:
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
    print("metainfo:", easyBucket.list(), len(easyBucket.fifo))

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

    print(easyBucket.delete("test1"), easyBucket.list())
    easyBucket.clean()  ## flush all data to stroage before exiting easyBucket
    print(easyBucket.buckets)  ## cache in the easyBucket