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

```This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
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
Time taken for tests:   154.282 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      47748500000 bytes
HTML transferred:       47741200000 bytes
Requests per second:    324.08 [#/sec] (mean)
Time per request:       308.565 [ms] (mean)
Time per request:       3.086 [ms] (mean, across all concurrent requests)
Transfer rate:          302234.24 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0  128 544.2      0   31518
Processing:    15  178  81.6    178    3469
Waiting:       12  169  79.5    168    3463
Total:         15  307 558.1    186   31642

Percentage of the requests served within a certain time (ms)
  50%    186
  66%    224
  75%    248
  80%    266
  90%    354
  95%   1229
  98%   1341
  99%   3195
 100%  31642 (longest request)
```