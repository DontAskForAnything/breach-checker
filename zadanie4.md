➜  breach-checker git:(main) ✗ docker build -t breach-checker-backend:v1 ./backend

[+] Building 7.8s (10/10) FINISHED                                                                                                                                                                                    
 => [internal] load .dockerignore                                                                                                                                                                                0.0s
 => => transferring context: 115B                                                                                                                                                                                0.0s
 => [internal] load build definition from Dockerfile                                                                                                                                                             0.0s
 => => transferring dockerfile: 237B                                                                                                                                                                             0.0s
 => [internal] load metadata for docker.io/library/python:3.12-slim                                                                                                                                              7.7s
 => [1/5] FROM docker.io/library/python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b                                                                                        0.0s
 => [internal] load build context                                                                                                                                                                                0.0s
 => => transferring context: 1.31kB                                                                                                                                                                              0.0s
 => CACHED [2/5] WORKDIR /app                                                                                                                                                                                    0.0s
 => CACHED [3/5] COPY requirements.txt .                                                                                                                                                                         0.0s
 => CACHED [4/5] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                                              0.0s
 => [5/5] COPY app.py .                                                                                                                                                                                          0.0s
 => exporting to image                                                                                                                                                                                           0.0s
 => => exporting layers                                                                                                                                                                                          0.0s
 => => writing image sha256:7d518e3cde70df6ca89a2e555cf668dfc43c4911962e36e051b92c3a4bf6c386                                                                                                                     0.0s
 => => naming to docker.io/library/breach-checker-backend:v1                                                                                                                                                     0.0s
➜  breach-checker git:(main) ✗ docker rm -f backend

backend
➜  breach-checker git:(main) ✗ docker run -d --name backend --network breach-net -p 5000:5000 -v ./data/leaked-sha1.txt:/app/data/leaked-sha1.txt:ro breach-checker-backend:v1

b29c6e11ae729667e130e5ace1f3407f38925102610a4e9282481e8deeb027e5
➜  breach-checker git:(main) ✗ curl http://localhost:5000/health
{"status":"ok"}
➜  breach-checker git:(main) ✗ docker logs backend
Wczytano 89 hashy z /app/data/leaked-sha1.txt
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.26.0.2:5000
Press CTRL+C to quit
172.26.0.1 - - [13/Nov/2026 12:45:17] "GET /health HTTP/1.1" 200 -
➜  breach-checker git:(main) ✗ 


2.
➜  breach-checker git:(main) ✗ mkdir healthcheck-probe
➜  breach-checker git:(main) ✗ docker build -t healthcheck-probe ./healthcheck-probe

[+] Building 2.2s (6/6) FINISHED                                                                
 => [internal] load .dockerignore                                                          0.0s
 => => transferring context: 2B                                                            0.0s
 => [internal] load build definition from Dockerfile                                       0.0s
 => => transferring dockerfile: 236B                                                       0.0s
 => [internal] load metadata for docker.io/library/alpine:latest                           0.0s
 => [1/2] FROM docker.io/library/alpine                                                    0.0s
 => [2/2] RUN apk add --no-cache curl                                                      2.1s
 => exporting to image                                                                     0.0s
 => => exporting layers                                                                    0.0s
 => => writing image sha256:9fb174462223fbc43762842f0440d16dca86946209a6f2ea898e607015f79  0.0s
 => => naming to docker.io/library/healthcheck-probe                                       0.0s
➜  breach-checker git:(main) ✗ docker run --rm --network breach-net healthcheck-probe

backend: OK
➜  breach-checker git:(main) ✗ docker run --rm healthcheck-probe

backend: UNREACHABLE
➜  breach-checker git:(main) ✗ docker stop backend

backend
➜  breach-checker git:(main) ✗ docker run --rm --network breach-net healthcheck-probe

backend: UNREACHABLE
➜  breach-checker git:(main) ✗ docker start backend
backend
➜  breach-checker git:(main) ✗ docker run --rm --network breach-net healthcheck-probe

backend: OK
➜  breach-checker git:(main) ✗ 

Dlaczego bez --network nazwa "backend" nie działa, choć kontener jest uruchomiony?
Kontener uruchomiony bez flagi --network trafia do domyślnej sieci bridge, która nie posiada wbudowanego serwera DNS Dockera, więc nie potrafi przetłumaczyć nazwy "backend" na adres IP. Ponadto domyślna sieć jest całkowicie odizolowana od sieci breach-net, w której faktycznie znajduje się nasz serwer.


3. 
➜  wirtualizacja docker exec backend sh -c "echo notatka > /tmp/notatka.txt"

➜  wirtualizacja 
➜  wirtualizacja 
➜  wirtualizacja cd breach-checker                
➜  breach-checker git:(main) ✗ docker exec backend sh -c "echo notatka > /tmp/notatka.txt"

➜  breach-checker git:(main) ✗ docker restart backend

backend
➜  breach-checker git:(main) ✗ docker exec backend cat /tmp/notatka.txt

notatka
➜  breach-checker git:(main) ✗ docker rm -f backend

backend
➜  breach-checker git:(main) ✗ docker run -d --name backend --network breach-net -p 5000:5000 -v $(pwd)/data/leaked-sha1.txt:/app/data/leaked-sha1.txt:ro breach-checker-backend:v1

34adaff44520d82bac98d0939c77c900f70eb1dc3f40078f7112c45f8256a6d8
➜  breach-checker git:(main) ✗ docker exec backend cat /tmp/notatka.txt
cat: /tmp/notatka.txt: No such file or directory
➜  breach-checker git:(main) ✗ docker run --rm -v breach-dane:/dane alpine sh -c "date >> /dane/historia.txt"

➜  breach-checker git:(main) ✗ docker run --rm -v breach-dane:/dane alpine sh -c "date >> /dane/historia.txt; cat /dane/historia.txt"

Fri Nov 13 12:50:21 UTC 2026
Fri Nov 13 12:50:27 UTC 2026
➜  breach-checker git:(main) ✗ docker volume ls

DRIVER    VOLUME NAME
local     breach-dane
➜  breach-checker git:(main) ✗ docker volume rm breach-dane

breach-dane
➜  breach-checker git:(main) ✗ 



Plik w /tmp przetrwał restart, ponieważ znajdował się w warstwie zapisywalnej kontenera, której docker restart nie resetuje. Został jednak bezpowrotnie utracony przy docker rm, ponieważ to polecenie usuwa całą warstwę zapisywalną. Plik historia.txt przetrwał, ponieważ znajdował się na wolumenie (volume), czyli w niezależnym magazynie zarządzanym przez Dockera, którego cykl życia nie jest powiązany z usuwaniem kontenerów. Lista wycieków również przetrwałaby docker rm, ponieważ korzysta z mechanizmu bind mount – to plik leżący bezpiecznie na fizycznym dysku naszego komputera (hosta), a kontener ma do niego jedynie podgląd.


Dodatkowe 

➜  wirtualizacja docker network create --subnet 172.30.0.0/24 breach-net-ip
181caf58709e993ebb120920f345f4d92b7343e5fb5806d3e1f264c8ce9d5eb1
➜  wirtualizacja docker run -d --name backend-ip --network breach-net-ip --ip 172.30.0.10 -v ./data/leaked-sha1.txt:/app/data/leaked-sha1.txt:ro breach-checker-backend:v1

b93b437ba5b505b67377c4103bcf5d3acab79a3cbc1f79da0117257de5ab75cf
➜  wirtualizacja docker network inspect breach-net-ip

[
    {
        "Name": "breach-net-ip",
        "Id": "181caf58709e993ebb120920f345f4d92b7343e5fb5806d3e1f264c8ce9d5eb1",
        "Created": "2026-11-13T12:59:55.025845088Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": {},
            "Config": [
                {
                    "Subnet": "172.30.0.0/24"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "b93b437ba5b505b67377c4103bcf5d3acab79a3cbc1f79da0117257de5ab75cf": {
                "Name": "backend-ip",
                "EndpointID": "3048586af155c61e05abb75e3a13253ef9b26c53b82eb08cf246fc55efd23c30",
                "MacAddress": "02:42:ac:1e:00:0a",
                "IPv4Address": "172.30.0.10/24",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {}
    }
]
➜  wirtualizacja docker run --rm --network breach-net-ip alpine ping -c 2 backend-ip

PING backend-ip (172.30.0.10): 56 data bytes
64 bytes from 172.30.0.10: seq=0 ttl=64 time=0.842 ms
64 bytes from 172.30.0.10: seq=1 ttl=64 time=0.357 ms

--- backend-ip ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.357/0.599/0.842 ms
➜  wirtualizacja docker run -d --name backend-alias --network breach-net-ip --network-alias api -v ./data/leaked-sha1.txt:/app/data/leaked-sha1.txt:ro breach-checker-backend:v1

7d4676a0920603aabd87f849a3f7d806e385014cc677ebfabb2d9064b348d7a9
➜  wirtualizacja docker run --rm --network breach-net-ip alpine ping -c 2 api

PING api (172.30.0.2): 56 data bytes
64 bytes from 172.30.0.2: seq=0 ttl=64 time=0.449 ms
64 bytes from 172.30.0.2: seq=1 ttl=64 time=0.431 ms

--- api ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.431/0.440/0.449 ms
➜  wirtualizacja 


Pytanie: W jakim scenariuszu stały adres IP może być potrzebny mimo DNS?
Odpowiedź: Stały adres IP przydaje się, gdy musimy zintegrować kontenery ze "starszymi" systemami (legacy), które nie obsługują nazw domenowych (wymagają wpisania IP na sztywno). Jest też konieczny przy bardzo rygorystycznych regułach firewalla, które filtrują ruch wyłącznie na podstawie adresów IP.

Pytanie: Do czego przydaje się alias - co się stanie, gdy ten sam alias nadasz dwóm kontenerom?
Odpowiedź: Alias pozwala ukryć kilka kontenerów pod jedną wspólną nazwą (np. "api" lub "db"). Jeśli nadasz ten sam alias kilku kontenerom, wbudowany DNS Dockera zastosuje mechanizm Round-Robin. Będzie zwracał na zmianę adresy IP tych kontenerów, co daje darmowy i prosty Load Balancing (rozłożenie ruchu równomiernie na wiele kopii tej samej usługi).

