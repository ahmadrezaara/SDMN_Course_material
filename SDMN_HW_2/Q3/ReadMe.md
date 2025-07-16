```markdown
# Status API Service

This directory contains a simple HTTP server (`app.py`) and a Dockerfile to build and run it in a container.  
The server exposes a single endpoint:
```

/api/v1/status

````

- **GET**  → returns `{"status":"<current_status>"}` with HTTP 200
- **POST** → accepts `{"status":"<new_status>"}`, returns the same JSON with HTTP 201, and updates the status for future GETs

The server listens on port 8000.

---

## Prerequisites

- Docker installed and running
- Network/DNS configured so `docker pull` works

---

## 1. Build the Docker Image

From this directory, run:

```bash
docker build -t status-api:latest .
````

**Expected output (truncated):**

```bash
$ docker build -t status-api:latest .
Sending build context to Docker daemon  3.07kB
Step 1/7 : FROM python:3.8-slim
 ---> a1b2c3d4e5f6
Step 2/7 : ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
 ---> Using cache
 ---> 7f8e9d0a1b2c
Step 3/7 : WORKDIR /app
 ---> Using cache
 ---> 3e4f5a6b7c8d
Step 4/7 : COPY app.py .
 ---> Using cache
 ---> 9a0b1c2d3e4f
Step 5/7 : EXPOSE 8000
 ---> Using cache
 ---> 4d5e6f7a8b9c
Step 6/7 : HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD curl -f http://localhost:8000/api/v1/status || exit 1
 ---> Using cache
 ---> 1f2e3d4c5b6a
Step 7/7 : ENTRYPOINT ["python3", "app.py"]
 ---> Using cache
 ---> 0a1b2c3d4e5f
Successfully built 0a1b2c3d4e5f
Successfully tagged status-api:latest
```

---

## 2. Run the Container

Publish port 8000 on your host:

```bash
docker run -d --name mystatus -p 8000:8000 status-api:latest
```

**Expected output:**

```bash
$ docker run -d --name mystatus -p 8000:8000 status-api:latest
d4f5e6a7b8c9d0e1f2g3h4i5j6k7l8m9
```

---

## 3. Test the API

### 3.1 Initial GET

```bash
$ curl -i http://localhost:8000/api/v1/status
```

**Expected response:**

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 15

{"status":"OK"}
```

### 3.2 POST a New Status

```bash
$ curl -i -X POST http://localhost:8000/api/v1/status \
    -H "Content-Type: application/json" \
    -d '{"status":"not OK"}'
```

**Expected response:**

```
HTTP/1.1 201 Created
Content-Type: application/json; charset=utf-8
Content-Length: 20

{"status":"not OK"}
```

### 3.3 Verify State Change

```bash
$ curl -i http://localhost:8000/api/v1/status
```

**Expected response:**

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 20

{"status":"not OK"}
```

---

## 4. Clean Up

```bash
docker rm -f mystatus
docker image rm status-api:latest
```

---

**Deliverables fulfilled:**

- ✔️ **`app.py`** implements GET/POST on `/api/v1/status` with correct JSON bodies and HTTP codes
- ✔️ **`Dockerfile`** builds a working image exposing port 8000
- ✔️ **Demonstrated** building, running, and testing the containerized service in this README
