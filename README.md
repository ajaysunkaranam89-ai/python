# Python Flask Kubernetes Example

Complete example for deploying a Python Flask web application to Kubernetes/Kind.

## 1. Build Docker image

```powershell
docker build -t python-k8s-app:1.0 .
```

## 2. If using Kind, load the image

```powershell
kind load docker-image python-k8s-app:1.0
```

## 3. Apply Kubernetes resources in order

```powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/service-nodeport.yaml
kubectl apply -f k8s/ingress.yaml
```

## 4. Verify

```powershell
kubectl get all -n python-app
kubectl get pvc -n python-app
kubectl get ingress -n python-app
```

## 5. Access the app

**Option A — NodePort (no Ingress/hosts-file setup needed)**

```powershell
kubectl get nodes -o wide
```

Open, using any node's IP:

http://<node-ip>:30500

(On Kind/Minikube, use `minikube ip` or `kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}'` for `<node-ip>`.)

**Option B — port-forward**

```powershell
kubectl port-forward svc/python-app-service 8080:80 -n python-app
```

Open:

http://localhost:8080

**Option C — Ingress**

Add `python.local` to your hosts file pointing at the ingress controller's IP, then open http://python.local

Health (any option above, path `/health`):

http://localhost:8080/health

## 6. Useful commands

```powershell
kubectl get pods -n python-app
kubectl logs deployment/python-app -n python-app
kubectl describe deployment python-app -n python-app
kubectl scale deployment python-app --replicas=5 -n python-app
```

## Resource dependency

Namespace -> ConfigMap/Secret/PVC -> Deployment -> Service -> Ingress
