# devops-exam-app

Simple Flask + JS app for DevOps diploma. Shows hostname, pod/node IPs, and AWS EC2 metadata so you can see load balancing across Kubernetes nodes.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q
python -m app.main
```

Open http://127.0.0.1:8080

## Docker

```bash
docker build -t sergejpovzaniuk/devops-exam-app:latest .
docker run --rm -p 8080:8080 sergejpovzaniuk/devops-exam-app:latest
```

## Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
curl http://<node-ip>:30080/api/info
```

## CI/CD

Jenkins Multibranch Pipeline (folder `devops-exam-app`):

- any branch: test → build → push Docker Hub
- `main`: also deploy to kubeadm cluster
