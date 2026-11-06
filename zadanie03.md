# Zadanie 3 - Michal J

## 1. Etykiety i pochodzenie warstw

docker inspect:

```
{"autor":"Michal J","data":"2026-11-06","maintainer":"Michal J"}
```

docker history:

```
IMAGE          CREATED                  CREATED BY                                      SIZE      COMMENT
982df5f4605c   Less than a second ago   EXPOSE map[80/tcp:{}]                           0B        buildkit.dockerfile.v0
<missing>      Less than a second ago   RUN /bin/sh -c htmlhint /usr/share/nginx/htm…   0B        buildkit.dockerfile.v0
<missing>      51 minutes ago           COPY . /usr/share/nginx/html # buildkit         1.51kB    buildkit.dockerfile.v0
<missing>      51 minutes ago           RUN /bin/sh -c apk add --no-cache nodejs npm…   85.7MB    buildkit.dockerfile.v0
<missing>      51 minutes ago           LABEL autor=Michal J data=2026-11-06            0B        buildkit.dockerfile.v0
<missing>      51 minutes ago           LABEL maintainer=Michal J                       0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              RUN /bin/sh -c set -x     && apkArch="$(cat …   49.3MB    buildkit.dockerfile.v0
<missing>      2 weeks ago              ENV ACME_VERSION=0.4.1                          0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              ENV NJS_RELEASE=1                               0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              ENV NJS_VERSION=1.0.2                           0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              CMD ["nginx" "-g" "daemon off;"]                0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              STOPSIGNAL SIGQUIT                              0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              EXPOSE map[80/tcp:{}]                           0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              ENTRYPOINT ["/docker-entrypoint.sh"]            0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              COPY 30-tune-worker-processes.sh /docker-ent…   4.62kB    buildkit.dockerfile.v0
<missing>      2 weeks ago              COPY 20-envsubst-on-templates.sh /docker-ent…   3.03kB    buildkit.dockerfile.v0
<missing>      2 weeks ago              COPY 15-local-resolvers.envsh /docker-entryp…   389B      buildkit.dockerfile.v0
<missing>      2 weeks ago              COPY 10-listen-on-ipv6-by-default.sh /docker…   2.14kB    buildkit.dockerfile.v0
<missing>      2 weeks ago              COPY docker-entrypoint.sh / # buildkit          1.62kB    buildkit.dockerfile.v0
<missing>      2 weeks ago              RUN /bin/sh -c set -x     && addgroup -g 101…   4.66MB    buildkit.dockerfile.v0
<missing>      2 weeks ago              ENV DYNPKG_RELEASE=1                            0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              ENV PKG_RELEASE=1                               0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              ENV NGINX_VERSION=1.31.8                        0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              LABEL maintainer=NGINX Docker Maintainers <d…   0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              CMD ["/bin/sh"]                                 0B        buildkit.dockerfile.v0
<missing>      2 weeks ago              ADD alpine-minirootfs-3.24.3-aarch64.tar.gz …   8.66MB    buildkit.dockerfile.v0
```

Warstwy z kolumną CREATED równą "2 weeks ago" pochodzą z obrazu bazowego nginx:alpine.
Z mojego Dockerfile pochodzą dwa wpisy LABEL, RUN apk, COPY, RUN htmlhint i EXPOSE.

Rozmiar 0B mają wpisy, które nie zmieniają systemu plików: metadane (LABEL, ENV, CMD,
EXPOSE, ENTRYPOINT, STOPSIGNAL) oraz RUN htmlhint, który tylko sprawdza plik.

Etykiety są dziedziczone z obrazu bazowego, ale ten sam klucz w moim Dockerfile
nadpisuje wartość. Dlatego inspect pokazuje tylko moje maintainer, a history oba wpisy.

## 2. RUN działa raz

build.txt z kontenera 1:

```
Fri Nov  6 12:54:54 UTC 2026
```

build.txt z kontenera 2:

```
Fri Nov  6 12:54:54 UTC 2026
```

docker ps:

```
CONTAINER ID   IMAGE                        COMMAND                  CREATED          STATUS          PORTS                  NAMES
0095404ffaa1   michal-frontend:v2           "/docker-entrypoint.…"   7 seconds ago    Up 6 seconds    0.0.0.0:8082->80/tcp   frontend2
791c18fa77cc   michal-frontend:v2           "/docker-entrypoint.…"   57 seconds ago   Up 56 seconds   0.0.0.0:8081->80/tcp   frontend1
ca2a81ed0230   breach-checker-frontend:v1   "/docker-entrypoint.…"   5 minutes ago    Up 5 minutes    0.0.0.0:8080->80/tcp   frontend
```

Polecenie date wykonało się raz, podczas docker build, a wynik został zapisany w warstwie
obrazu. Oba kontenery powstały z tego samego obrazu, więc mają ten sam plik build.txt.

## 3. Nadpisanie CMD

```
root   /usr/share/nginx/html;
```

Nginx serwuje pliki z katalogu /usr/share/nginx/html, dlatego właśnie tam kopiujemy pliki strony.

## 4. Diagnoza błędnego COPY

ls /usr/share/nginx:

```
html
index.html
script.js
style.css
```

ls /usr/share/nginx/html:

```
50x.html
build.txt
index.html
```

Pliki strony trafiły do /usr/share/nginx, a nginx serwuje /usr/share/nginx/html, gdzie został
domyślny index.html z obrazu bazowego. Htmlhint sprawdził właśnie ten domyślny plik, a nie
moją stronę. Plik był poprawny, więc build przeszedł.

## 5. Usunięcie tagu a usunięcie obrazu

docker rmi breach-checker-frontend:latest:

```
Untagged: breach-checker-frontend:latest
```

docker images (fragment), v2 nadal jest:

```
REPOSITORY                       TAG               IMAGE ID       CREATED          SIZE
breach-checker-frontend          v1                250f270443bc   28 minutes ago   62.7MB
breach-checker-frontend          v2                9b9d3833409a   39 minutes ago   62.7MB
```

docker rmi breach-checker-frontend:v2:

```
Untagged: breach-checker-frontend:v2
Deleted: sha256:9b9d3833409a4be70d2868925991b829f3b8f4017166ce2374d5cb65b0e0bd44
```

Po usunięciu latest obraz v2 nadal istnieje, bo to dwie etykiety tego samego obrazu.
Docker rmi usuwa obraz z dysku dopiero wtedy, gdy usuwany jest jego ostatni tag. Wcześniej
zdejmuje tylko etykietę (Untagged). Warstwy współdzielone z innymi obrazami zostają na dysku.
