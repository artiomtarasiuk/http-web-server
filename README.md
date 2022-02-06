# Project

HTTP web server.

## Setup

 - Setup python 3.8 venv
 - Install poetry `pip install poetry==1.1.12`
 - Run `poetry install --no-root` to install dependencies

## Usage

```shell
python httpd.py --host localhost --port 8080 --workers 5 --document-root .
```

# Testing

```shell
python httptest.py
```

# Load testing

With 10 workers

```shell
ab -n 50000 -c 100 -r localhost:8080/httptest/wikipedia_russia.html
```

```
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        CustomWebServer
Server Hostname:        localhost
Server Port:            8080

Document Path:          /httptest/wikipedia_russia.html
Document Length:        954824 bytes

Concurrency Level:      100
Time taken for tests:   33.961 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      47748500000 bytes
HTML transferred:       47741200000 bytes
Requests per second:    1472.30 [#/sec] (mean)
Time per request:       67.921 [ms] (mean)
Time per request:       0.679 [ms] (mean, across all concurrent requests)
Transfer rate:          1373045.63 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0   33 310.4      0    7307
Processing:     1   24  70.3     21    5764
Waiting:        0    4  69.9      1    5762
Total:          1   57 326.5     22    7725

Percentage of the requests served within a certain time (ms)
  50%     22
  66%     27
  75%     30
  80%     31
  90%     35
  95%     44
  98%   1024
  99%   1063
 100%   7725 (longest request)
```