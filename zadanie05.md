# Zadanie 5 – Docker Compose

Skrót testowy (hasło `Kot-w-Kapeluszu-2026`, nie ma go w próbce):
`bc45408273d7e1914b741c3407b0b559764f7876`

## 1. Healthcheck backendu

Zmiany w `docker-compose.yml`:

```yaml
  frontend:
    depends_on:
      backend:
        condition: service_healthy

  backend:
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
      interval: 5s
      timeout: 3s
      retries: 5
```

```
$ docker compose down
$ docker compose up -d --build
 Container breach-checker-db-1  Starting
 Container breach-checker-db-1  Started
 Container breach-checker-db-1  Waiting
 Container breach-checker-db-1  Healthy
 Container breach-checker-backend-1  Starting
 Container breach-checker-backend-1  Started
 Container breach-checker-backend-1  Waiting
 Container breach-checker-backend-1  Healthy
 Container breach-checker-frontend-1  Starting
 Container breach-checker-frontend-1  Started
```

```
$ docker compose ps
NAME                        IMAGE                     COMMAND                  SERVICE             CREATED             STATUS                    PORTS
breach-checker-backend-1    breach-checker-backend    "python app.py"          backend             12 seconds ago      Up 5 seconds (healthy)    5000/tcp
breach-checker-db-1         postgres:16-alpine        "docker-entrypoint.s…"   db                  12 seconds ago      Up 11 seconds (healthy)   5432/tcp
breach-checker-frontend-1   breach-checker-frontend   "/docker-entrypoint.…"   frontend            12 seconds ago      Up Less than a second     0.0.0.0:8080->80/tcp
```

Frontend startuje dopiero wtedy, gdy backend ma status `healthy`, czyli gdy jego endpoint `/health` naprawdę odpowiada. Sam start kontenera już nie wystarcza.

## 2. Trwałość bazy

**Po INSERT:**

```
$ docker compose exec db psql -U breach -d breachdb -c "INSERT INTO leaked_hashes VALUES ('bc45408273d7e1914b741c3407b0b559764f7876');"
INSERT 0 1
$ curl -X POST http://localhost:8080/api/check -H "Content-Type: application/json" -d '{"hash":"bc45408273d7e1914b741c3407b0b559764f7876"}'
{"found":true}
```

**Po `down` + `up`:**

```
$ docker compose down
 Container breach-checker-frontend-1  Removed
 Container breach-checker-backend-1  Removed
 Container breach-checker-db-1  Removed
 Network breach-checker_default  Removed
$ docker compose up -d
$ curl -X POST http://localhost:8080/api/check -H "Content-Type: application/json" -d '{"hash":"bc45408273d7e1914b741c3407b0b559764f7876"}'
{"found":true}
```

**Po `down -v` + `up`:**

```
$ docker compose down -v
 Container breach-checker-frontend-1  Removed
 Container breach-checker-backend-1  Removed
 Container breach-checker-db-1  Removed
 Network breach-checker_default  Removed
 Volume breach-checker_pgdata  Removed
$ docker compose up -d
 Volume "breach-checker_pgdata"  Created
$ curl -X POST http://localhost:8080/api/check -H "Content-Type: application/json" -d '{"hash":"bc45408273d7e1914b741c3407b0b559764f7876"}'
{"found":false}
```

**Wnioski:**
`docker compose down` usuwa tylko kontenery i sieć. Dane bazy leżą w wolumenie nazwanym `pgdata`, który zostaje, a nowy kontener `db` podpina ten sam wolumen, więc dopisany skrót nadal jest w bazie. `docker compose down -v` usuwa także wolumen, czyli całą bazę. Po `down -v` katalog danych jest pusty, więc przy starcie obraz `postgres` znowu wykonuje skrypty z `/docker-entrypoint-initdb.d/`: `init.sql` tworzy tabelę od nowa i ładuje 89 skrótów z pliku `data/leaked-sha1.txt`, którego nasz `INSERT` nie zmienił.

## 3. Skalowanie

```
$ docker compose up -d --scale backend=3 --no-recreate
$ docker compose ps
NAME                        IMAGE                     COMMAND                  SERVICE             CREATED             STATUS                    PORTS
breach-checker-backend-1    breach-checker-backend    "python app.py"          backend             19 seconds ago      Up 12 seconds (healthy)   5000/tcp
breach-checker-backend-2    breach-checker-backend    "python app.py"          backend             7 seconds ago       Up 5 seconds (healthy)    5000/tcp
breach-checker-backend-3    breach-checker-backend    "python app.py"          backend             7 seconds ago       Up 5 seconds (healthy)    5000/tcp
breach-checker-db-1         postgres:16-alpine        "docker-entrypoint.s…"   db                  19 seconds ago      Up 18 seconds (healthy)   5432/tcp
breach-checker-frontend-1   breach-checker-frontend   "/docker-entrypoint.…"   frontend            19 seconds ago      Up 6 seconds              0.0.0.0:8080->80/tcp
```

```
$ docker compose exec frontend nslookup backend
Server:         127.0.0.11
Address:        127.0.0.11:53

Non-authoritative answer:
Name:   backend
Address: 172.29.0.3
Name:   backend
Address: 172.29.0.6
Name:   backend
Address: 172.29.0.5
```

**Przed restartem frontendu** (20 zapytań, wszystkie obsłużył `backend-1`):

```
$ for i in $(seq 20); do curl -s -X POST http://localhost:8080/api/check -H "Content-Type: application/json" -d '{"hash":"bc45408273d7e1914b741c3407b0b559764f7876"}'; done
$ docker compose logs backend | grep "POST /check"
breach-checker-backend-1  | 172.29.0.4 - - [19/Nov/2026 07:33:52] "POST /check HTTP/1.1" 200 -
breach-checker-backend-1  | 172.29.0.4 - - [19/Nov/2026 07:33:52] "POST /check HTTP/1.1" 200 -
breach-checker-backend-1  | 172.29.0.4 - - [19/Nov/2026 07:33:52] "POST /check HTTP/1.1" 200 -
breach-checker-backend-1  | 172.29.0.4 - - [19/Nov/2026 07:33:52] "POST /check HTTP/1.1" 200 -
breach-checker-backend-1  | 172.29.0.4 - - [19/Nov/2026 07:33:52] "POST /check HTTP/1.1" 200 -
```

**Po `docker compose restart frontend`** (20 zapytań: `backend-1` – 5, `backend-2` – 9, `backend-3` – 6):

```
$ docker compose restart frontend
 Container breach-checker-frontend-1  Restarting
 Container breach-checker-frontend-1  Started
$ for i in $(seq 20); do curl -s -X POST http://localhost:8080/api/check -H "Content-Type: application/json" -d '{"hash":"bc45408273d7e1914b741c3407b0b559764f7876"}'; done
$ docker compose logs backend | grep "POST /check"
breach-checker-backend-2  | 172.29.0.4 - - [19/Nov/2026 07:33:54] "POST /check HTTP/1.1" 200 -
breach-checker-backend-2  | 172.29.0.4 - - [19/Nov/2026 07:33:54] "POST /check HTTP/1.1" 200 -
...
breach-checker-backend-3  | 172.29.0.4 - - [19/Nov/2026 07:33:54] "POST /check HTTP/1.1" 200 -
breach-checker-backend-3  | 172.29.0.4 - - [19/Nov/2026 07:33:54] "POST /check HTTP/1.1" 200 -
...
breach-checker-backend-1  | 172.29.0.4 - - [19/Nov/2026 07:33:54] "POST /check HTTP/1.1" 200 -
breach-checker-backend-1  | 172.29.0.4 - - [19/Nov/2026 07:33:55] "POST /check HTTP/1.1" 200 -
```

```
$ docker compose up -d --scale backend=1
```

**Wnioski:**
nginx tłumaczy nazwę `backend` na adresy tylko raz, przy swoim starcie. Wystartował, gdy była jedna replika, więc znał jeden adres IP i cały ruch szedł tam. Nowe repliki były już w DNS Dockera (widać to w `nslookup`), ale nginx o nie nie pytał. Po restarcie dostał z DNS 3 adresy i rozkłada zapytania między nie po kolei (round-robin).

Uwaga: bez `--no-recreate` moja wersja Compose przy `--scale` sama odtwarzała frontend (`frontend-1 Recreate`), bo frontend zależy od backendu. Wtedy nginx od razu znał wszystkie 3 adresy i ruch był rozłożony już przed ręcznym restartem.

Z `ports: "5000:5000"` skalowanie by nie przeszło: port 5000 na hoście może zająć tylko jeden kontener, więc druga i trzecia replika dostałyby błąd `port is already allocated`.
