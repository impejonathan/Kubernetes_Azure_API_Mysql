# 🏢 Application de Gestion des Clients - Kubernetes sur Azure AKS

## 📋 Table des matières
- [Description](#-description)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Structure du projet](#-structure-du-projet)
- [Déploiement](#-déploiement)
- [Tests et vérifications](#-tests-et-vérifications)
- [Accès à l'application](#-accès-à-lapplication)
- [Commandes utiles](#-commandes-utiles)
- [Dépannage](#-dépannage)

---

## 📝 Description

Application cloud-native de gestion des clients déployée sur **Azure Kubernetes Service (AKS)** avec :
- **Backend** : API REST FastAPI (Python)
- **Frontend** : Interface web Streamlit
- **Base de données** : MySQL avec stockage persistant Azure Disk
- **Orchestration** : Kubernetes
- **Exposition** : Application Gateway + LoadBalancer

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌──────────────┐
│ App Gateway   │         │ LoadBalancer │
│ 4.251.145.205 │         │ 4.251.155.176│
└───────┬───────┘         └──────┬───────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────▼─────────────┐
        │   Namespace: jimpe       │
        │                          │
        │  ┌──────────────────┐   │
        │  │ Streamlit x2     │   │
        │  │ (Frontend)       │   │
        │  │ Port: 8501       │   │
        │  └────────┬─────────┘   │
        │           │              │
        │           ▼              │
        │  ┌──────────────────┐   │
        │  │ FastAPI x2       │   │
        │  │ (Backend API)    │   │
        │  │ Port: 8000       │   │
        │  └────────┬─────────┘   │
        │           │              │
        │           ▼              │
        │  ┌──────────────────┐   │
        │  │ MySQL x1         │   │
        │  │ Port: 3306       │   │
        │  │ + Azure Disk 5Gi │   │
        │  └──────────────────┘   │
        │                          │
        └──────────────────────────┘
```

### Composants

| Composant | Type | Replicas | Accès | Port |
|-----------|------|----------|-------|------|
| **Streamlit** | Frontend | 2 | Public | 8501 |
| **FastAPI** | Backend API | 2 | Interne uniquement | 8000 |
| **MySQL** | Base de données | 1 | Interne uniquement | 3306 |

---

## ✅ Prérequis

- Azure CLI installé
- kubectl installé
- Docker installé (pour build/push des images)
- Accès à un cluster AKS
- Accès à Docker Hub ou Azure Container Registry

---

## 📂 Structure du projet

```
.
├── Namespace.yaml
├── Secret-MySQL.yaml
├── PVC-MySQL.yaml
├── Service-MySQL.yaml
├── Deployment-MySQL.yaml
├── Service-API.yaml
├── Deployment-API.yaml
├── Ingress.yaml
├── Service-Streamlit.yaml
├── Deployment-Streamlit.yaml
├── Service-Streamlit-LoadBalancer.yaml  # (Optionnel - backup)
├── streamlit/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

---

## 🚀 Déploiement

### **Étape 0 : Connexion à Azure et AKS**

```powershell
# Connexion à Azure
az login

# Récupération des credentials du cluster AKS
az aks get-credentials --resource-group RG_PROMO --name cluster_promo

# Vérification de la connexion
kubectl cluster-info
kubectl get nodes
```

---
## ATTENTION **jimpe** C'EST LE NOM DE MON NAME SPACE A VOUS DE LE MODIFIER
### **Étape 1 : Déploiement de la base de données MySQL**  

**Ordre d'exécution :**

```powershell
# 1. Créer le namespace
kubectl apply -f Namespace.yaml

# 2. Créer les secrets MySQL
kubectl apply -f Secret-MySQL.yaml

# 3. Créer le volume persistant
kubectl apply -f PVC-MySQL.yaml

# 4. Déployer MySQL
kubectl apply -f Deployment-MySQL.yaml

# 5. Créer le service MySQL
kubectl apply -f Service-MySQL.yaml

# Vérifier le déploiement
kubectl get pods -n jimpe
kubectl get pvc -n jimpe
```

**Attendre que le pod MySQL soit `Running` et `Ready 1/1`**

---

### **Étape 2 : Déploiement de l'API FastAPI**

```powershell
# 1. Déployer l'API
kubectl apply -f Deployment-API.yaml

# 2. Créer le service API
kubectl apply -f Service-API.yaml

# 3. Créer l'Ingress pour exposer l'API
kubectl apply -f Ingress.yaml

# Vérifier le déploiement
kubectl get pods -n jimpe
kubectl get svc -n jimpe
kubectl get ingress -n jimpe
```

**Attendre que les pods API soient `Running` et `Ready 1/1` (2-3 minutes)**

---

### **🧪 Test de l'API (avant Streamlit)**

Une fois l'Ingress configuré, récupérer l'adresse IP publique :

```powershell
kubectl get ingress -n jimpe
```

**Tester les endpoints dans un navigateur ou avec curl :**

```bash
# Health check
http://4.251.145.205/jimpe/health

# Liste des clients (devrait retourner Alice, Bruno, Claire)
http://4.251.145.205/jimpe/clients

# Documentation Swagger
http://4.251.145.205/jimpe/docs
```

✅ **Si l'API répond correctement, passer à l'étape suivante.**

---

### **Étape 3 : Déploiement de Streamlit**

```powershell
# 1. Déployer Streamlit
kubectl apply -f Deployment-Streamlit.yaml

# 2. Créer le service Streamlit (ClusterIP)
kubectl apply -f Service-Streamlit.yaml

# 3. (Optionnel) Créer le LoadBalancer pour exposition publique
kubectl apply -f Service-Streamlit-LoadBalancer.yaml

# Vérifier le déploiement
kubectl get pods -n jimpe
kubectl get svc -n jimpe
```

**Attendre que les pods Streamlit soient `Running` et `Ready 1/1` (2-3 minutes)**

---

## 🧪 Tests et vérifications

### **1. Vérifier l'état des pods**

```powershell
# Voir tous les pods du namespace
kubectl get pods -n jimpe

# Vérifier qu'ils sont tous Running avec 0 restarts
# Exemple de sortie attendue :
# NAME                                   READY   STATUS    RESTARTS   AGE
# api-deployment-6d58d676cd-5nrkg        1/1     Running   0          18h
# api-deployment-6d58d676cd-rtrd8        1/1     Running   0          18h
# mysql-deployment-df8df758-zp467        1/1     Running   0          19h
# streamlit-deployment-9d8588877-7spvk   1/1     Running   0          45s
# streamlit-deployment-9d8588877-j9vn8   1/1     Running   0          62s
```

---

### **2. Vérifier les services**

```powershell
kubectl get svc -n jimpe

# Sortie attendue :
# NAME               TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)
# api-service        ClusterIP      10.0.x.x        <none>          8000/TCP
# mysql-service      ClusterIP      10.0.x.x        <none>          3306/TCP
# streamlit-service  ClusterIP      10.0.x.x        <none>          8501/TCP
# streamlit-lb       LoadBalancer   10.0.x.x        4.251.155.176   80:xxxxx/TCP
```

---

### **3. Vérifier les logs**

```powershell
# Logs de l'API
kubectl logs -n jimpe deployment/api-deployment --tail=50

# Logs de Streamlit
kubectl logs -n jimpe deployment/streamlit-deployment --tail=50

# Logs de MySQL
kubectl logs -n jimpe deployment/mysql-deployment --tail=50

# Suivre les logs en temps réel
kubectl logs -n jimpe deployment/streamlit-deployment -f
```

---

### **4. Tester en local avec port-forward**

**Test de l'API :**

```powershell
kubectl port-forward -n jimpe svc/api-service 8000:8000
```

Accéder à : `http://localhost:8000/jimpe/clients`

**Test de Streamlit :**

```powershell
kubectl port-forward -n jimpe svc/streamlit-service 8501:8501
```

Accéder à : `http://localhost:8501/jimpe`

*(Ctrl+C pour arrêter le port-forward)*

---

### **5. Vérifier l'Ingress**

```powershell
kubectl get ingress -n jimpe
kubectl describe ingress api-ingress -n jimpe
kubectl describe ingress streamlit-ingress -n jimpe
```

---

### **6. Diagnostiquer un pod qui crashe**

```powershell
# Voir les événements récents
kubectl get events -n jimpe --sort-by='.lastTimestamp'

# Décrire un pod spécifique
kubectl describe pod -n jimpe <nom-du-pod>

# Voir les logs d'un pod qui redémarre
kubectl logs -n jimpe <nom-du-pod> --previous
```

---

## 🌐 Accès à l'application

### **Option 1 : Via Application Gateway (Ingress)**

#### **API FastAPI**
- Health check : `http://4.251.145.205/jimpe/health`
- Liste clients : `http://4.251.145.205/jimpe/clients`
- Documentation Swagger : `http://4.251.145.205/jimpe/docs`

#### **Streamlit (si configuré avec Ingress)**
- Interface web : `http://4.251.145.205/jimpe`

---

### **Option 2 : Via LoadBalancer direct**

```powershell
# Récupérer l'IP externe du LoadBalancer
kubectl get svc -n jimpe streamlit-lb
```

**Accès Streamlit :**
- Interface web : `http://4.251.155.176/jimpe`

> **Note :** Cette option est recommandée si Application Gateway pose problème.

---

## 🛠️ Commandes utiles

### **Gestion des pods**

```powershell
# Voir tous les pods du namespace
kubectl get pods -n jimpe

# Voir les pods en temps réel (watch)
kubectl get pods -n jimpe -w

# Redémarrer un deployment
kubectl rollout restart deployment/streamlit-deployment -n jimpe
kubectl rollout restart deployment/api-deployment -n jimpe

# Voir l'état d'un rollout
kubectl rollout status deployment/streamlit-deployment -n jimpe

# Scaler un deployment
kubectl scale deployment/streamlit-deployment -n jimpe --replicas=3
kubectl scale deployment/api-deployment -n jimpe --replicas=3
```

---

### **Gestion des services**

```powershell
# Lister tous les services
kubectl get svc -n jimpe

# Détails d'un service
kubectl describe svc streamlit-service -n jimpe

# Voir les endpoints (IPs des pods)
kubectl get endpoints -n jimpe streamlit-service
```

---

### **Accès aux conteneurs**

```powershell
# Se connecter à un pod
kubectl exec -it -n jimpe <nom-du-pod> -- /bin/bash

# Se connecter à MySQL
kubectl exec -it -n jimpe deployment/mysql-deployment -- mysql -u root -p
# Mot de passe : rootpass

# Exécuter une commande dans un pod
kubectl exec -n jimpe <nom-du-pod> -- ls -la /app
```

---

### **Gestion des secrets**

```powershell
# Voir les secrets
kubectl get secrets -n jimpe

# Décoder un secret
kubectl get secret mysql-secret -n jimpe -o jsonpath='{.data.MYSQL_PASSWORD}' | base64 -d
```

---

### **Monitoring**

```powershell
# Voir les métriques des pods (CPU/RAM)
kubectl top pods -n jimpe

# Voir les métriques des nodes
kubectl top nodes

# Voir les événements récents
kubectl get events -n jimpe --sort-by='.lastTimestamp'
```

---

### **Nettoyage**

```powershell
# Supprimer un deployment
kubectl delete deployment streamlit-deployment -n jimpe

# Supprimer tout le namespace (ATTENTION : supprime TOUT)
kubectl delete namespace jimpe

# Supprimer des ressources spécifiques
kubectl delete -f Deployment-Streamlit.yaml -n jimpe
kubectl delete -f Service-Streamlit-LoadBalancer.yaml -n jimpe
```

---

## 🐛 Dépannage

### **Problème 1 : Pod en CrashLoopBackOff**

```powershell
# Voir les logs du pod
kubectl logs -n jimpe <nom-du-pod>

# Voir les logs du conteneur précédent (avant crash)
kubectl logs -n jimpe <nom-du-pod> --previous

# Décrire le pod pour voir les événements
kubectl describe pod -n jimpe <nom-du-pod>
```

**Causes fréquentes :**
- Health probes qui échouent
- Variables d'environnement manquantes
- Image Docker incorrecte

---

### **Problème 2 : Service inaccessible (502 Bad Gateway)**

```powershell
# Vérifier que les pods sont Ready
kubectl get pods -n jimpe

# Vérifier les endpoints du service
kubectl get endpoints -n jimpe <nom-service>

# Tester en port-forward
kubectl port-forward -n jimpe svc/<nom-service> <port>:<port>

# Vérifier les logs AGIC (Application Gateway Ingress Controller)
kubectl get pods -n kube-system | Select-String "ingress"
kubectl logs -n kube-system <pod-agic> --tail=100
```

**Solution de contournement :**
Utiliser le LoadBalancer à la place de l'Ingress :

```powershell
kubectl apply -f Service-Streamlit-LoadBalancer.yaml -n jimpe
kubectl get svc -n jimpe streamlit-lb
```

---

### **Problème 3 : Image Docker non mise à jour**

```powershell
# Forcer un nouveau pull de l'image
kubectl rollout restart deployment/<nom-deployment> -n jimpe

# Ou modifier l'imagePullPolicy dans le Deployment
imagePullPolicy: Always
```

Si l'image ne change pas, utiliser un nouveau tag :

```powershell
# Build avec un nouveau tag
docker build -t impejonathan/brief-streamlit:v2 .
docker push impejonathan/brief-streamlit:v2

# Modifier le Deployment
image: impejonathan/brief-streamlit:v2
```

---

### **Problème 4 : Base de données MySQL vide**

```powershell
# Se connecter à MySQL
kubectl exec -it -n jimpe deployment/mysql-deployment -- mysql -u root -p

# Vérifier les données
USE clients;
SHOW TABLES;
SELECT * FROM client;
```

Si la table est vide, vérifier que l'image MySQL contient bien le script `init.sql`.

---

### **Problème 5 : PVC en Pending**

```powershell
kubectl get pvc -n jimpe
kubectl describe pvc mysql-pvc -n jimpe
```

**Causes :**
- StorageClass non disponible
- Quota de stockage dépassé

**Solution :**

```powershell
# Vérifier les StorageClass disponibles
kubectl get storageclass

# Modifier le PVC pour utiliser une StorageClass existante
storageClassName: managed-csi  # ou default
```

---

## 📊 Endpoints disponibles

### **API FastAPI**

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/jimpe/health` | Health check |
| GET | `/jimpe/clients` | Liste tous les clients |
| GET | `/jimpe/clients/{id}` | Récupère un client par ID |
| POST | `/jimpe/clients` | Crée un nouveau client |
| DELETE | `/jimpe/clients/{id}` | Supprime un client |
| GET | `/jimpe/docs` | Documentation Swagger |

---

### **Streamlit**

| Page | Description |
|------|-------------|
| 🏠 Accueil | Statistiques et santé de l'API |
| 📋 Liste des Clients | Affiche tous les clients |
| ➕ Ajouter un Client | Formulaire de création |
| 🔍 Rechercher un Client | Recherche par ID |
| 🗑️ Supprimer un Client | Suppression par ID |

---

## 🔐 Sécurité

- ✅ API et MySQL accessibles **uniquement en interne** (ClusterIP)
- ✅ Secrets Kubernetes pour les credentials MySQL
- ✅ Communication inter-services via DNS Kubernetes
- ✅ Stockage persistant avec Azure Disk

---

## 📈 Production Recommendations

### **1. HTTPS / SSL**

Configurer un certificat SSL sur l'Application Gateway ou utiliser cert-manager :

```powershell
# Installer cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

---

### **2. Resource Limits**

Ajouter dans les Deployments :

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

---

### **3. Backup MySQL**

Configurer des sauvegardes régulières du PVC ou migrer vers Azure Database for MySQL.

---

### **4. Monitoring**

Mettre en place Azure Monitor, Prometheus ou Grafana :

```powershell
kubectl top pods -n jimpe
kubectl top nodes
```

---

### **5. ConfigMaps**

Externaliser la configuration :

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: jimpe
data:
  API_URL: "http://api-service.jimpe.svc.cluster.local:8000/jimpe"
```

---

## 👥 Auteurs

- **Nom** : [Impe jonathan]
- **Projet** : Brief Kubernetes - Gestion des Clients
- **Date** : Novembre 2025

---

## 📄 Licence

Ce projet est à usage éducatif.

---

## 🎯 Résumé des commandes de déploiement

```powershell
# Connexion
az login
az aks get-credentials --resource-group RG_PROMO --name cluster_promo

# Déploiement complet (dans l'ordre)
kubectl apply -f Namespace.yaml
kubectl apply -f Secret-MySQL.yaml
kubectl apply -f PVC-MySQL.yaml
kubectl apply -f Deployment-MySQL.yaml
kubectl apply -f Service-MySQL.yaml
kubectl apply -f Deployment-API.yaml
kubectl apply -f Service-API.yaml
kubectl apply -f Ingress.yaml
kubectl apply -f Deployment-Streamlit.yaml
kubectl apply -f Service-Streamlit.yaml
kubectl apply -f Service-Streamlit-LoadBalancer.yaml

# Vérification
kubectl get all -n jimpe
kubectl get ingress -n jimpe
kubectl get pvc -n jimpe

# Récupérer les IPs publiques
kubectl get ingress -n jimpe
kubectl get svc -n jimpe streamlit-lb
```

---

**🎉 Application déployée avec succès ! 🚀**