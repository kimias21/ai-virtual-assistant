# Kubernetes deployment

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml

# Secret: copy 02-secret.yaml.example -> 02-secret.yaml, fill in HF_API_TOKEN, then:
kubectl apply -f k8s/02-secret.yaml
# (or create it imperatively, see comment inside 02-secret.yaml.example)

# Edit 10-backend-deployment.yaml and 11-frontend-deployment.yaml to point
# `image:` at your GHCR images (built automatically by .github/workflows/ci-cd.yml)
kubectl apply -f k8s/10-backend-deployment.yaml
kubectl apply -f k8s/11-frontend-deployment.yaml

# Optional, requires an ingress controller:
kubectl apply -f k8s/20-ingress.yaml
```

Check status:

```bash
kubectl -n ai-virtual-assistant get pods,svc,ingress
```
