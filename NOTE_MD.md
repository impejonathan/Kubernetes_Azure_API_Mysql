Excellente question ! Les **probes** sont des **vérifications automatiques** que Kubernetes effectue régulièrement sur tes pods pour s'assurer qu'ils fonctionnent correctement. Voici les différences :

---

## **1. `livenessProbe` (Probe de vivacité)**

### **Rôle :**
- Vérifie si l'application **est toujours vivante** et fonctionne correctement.
- Si la probe échoue plusieurs fois, Kubernetes considère que le conteneur est "mort" ou bloqué.

### **Action de Kubernetes :**
- **Redémarre automatiquement le pod** qui ne répond plus.

### **Cas d'usage :**
- Détecter un deadlock (l'app est figée)
- Détecter une corruption mémoire
- Détecter un crash silencieux (le process tourne mais ne répond plus)

### **Dans ton cas :**
```yaml
livenessProbe:
  httpGet:
    path: /jimpe/health    # Kubernetes appelle cette URL
    port: 8000             # Sur ce port
  initialDelaySeconds: 10  # Attend 10 secondes après le démarrage
  periodSeconds: 5         # Vérifie toutes les 5 secondes
```
**Traduction :** *"Toutes les 5 secondes, appelle `GET http://pod-ip:8000/jimpe/health`. Si ça échoue 3 fois d'affilée (valeur par défaut), redémarre le pod."*

---

## **2. `readinessProbe` (Probe de disponibilité)**

### **Rôle :**
- Vérifie si l'application **est prête à recevoir du trafic**.
- Si la probe échoue, Kubernetes retire temporairement ce pod du Service (il ne reçoit plus de requêtes).

### **Action de Kubernetes :**
- **Retire le pod du load balancing** (plus aucune requête ne lui est envoyée).
- Le pod reste en vie, mais Kubernetes attend qu'il redevienne "Ready".

### **Cas d'usage :**
- Attendre que la connexion à la base de données soit établie
- Attendre le chargement de la configuration
- Attendre qu'un cache soit initialisé

### **Dans ton cas :**
```yaml
readinessProbe:
  httpGet:
    path: /jimpe/health    # Kubernetes appelle cette URL
    port: 8000             # Sur ce port
  initialDelaySeconds: 10  # Attend 10 secondes avant la 1ère vérification
  periodSeconds: 5         # Vérifie toutes les 5 secondes
```
**Traduction :** *"Toutes les 5 secondes, appelle `GET http://pod-ip:8000/jimpe/health`. Si ça échoue, marque le pod comme 'Not Ready' et arrête de lui envoyer du trafic."*

---

## **Différence clé entre les deux**

| Probe | Question posée | Action si échec |
|-------|---------------|-----------------|
| **livenessProbe** | "Es-tu **vivant** ?" | ❌ **Redémarre le pod** |
| **readinessProbe** | "Es-tu **prêt** à traiter des requêtes ?" | ⏸️ **Retire du trafic** (sans redémarrer) |

---

## **Exemple concret avec ton API**

### **Scénario 1 : Démarrage du pod**
1. Le pod démarre.
2. Kubernetes attend **10 secondes** (`initialDelaySeconds`).
3. Kubernetes appelle `/jimpe/health` toutes les **5 secondes**.
4. Si `/jimpe/health` retourne 200 OK :
   - ✅ `readinessProbe` → Pod marqué **"Ready"** → Reçoit du trafic
   - ✅ `livenessProbe` → Pod considéré **vivant**

### **Scénario 2 : La base de données MySQL plante**
- Ton API ne peut plus répondre correctement (erreur 500 ou timeout).
- `/jimpe/health` commence à échouer ou à retourner 500.
- **readinessProbe échoue** → Pod marqué "Not Ready" → Plus de trafic vers ce pod.
- **livenessProbe échoue aussi** → Après 3 échecs (par défaut), Kubernetes redémarre le pod.

### **Scénario 3 : Déploiement rolling update**
- Tu déploies une nouvelle version de l'API.
- Kubernetes crée de nouveaux pods.
- Les nouveaux pods ne reçoivent du trafic QUE quand leur `readinessProbe` réussit.
- Les anciens pods restent actifs jusqu'à ce que les nouveaux soient "Ready".
- ➡️ **Zero downtime deployment** !

---

## **Paramètres expliqués**

```yaml
livenessProbe:
  httpGet:
    path: /jimpe/health         # URL à appeler
    port: 8000                  # Port du conteneur
  initialDelaySeconds: 10       # Délai avant la 1ère vérification (laisse le temps de démarrer)
  periodSeconds: 5              # Intervalle entre chaque vérification
  timeoutSeconds: 1             # (défaut) Temps max d'attente de réponse
  successThreshold: 1           # (défaut) Nb de succès pour considérer "OK"
  failureThreshold: 3           # (défaut) Nb d'échecs avant action (redémarrage/retrait)
```

---

## **Pourquoi `/jimpe/health` et pas `/health` ?**

Parce que tu as configuré `ROOT_PATH=/jimpe` dans ton API. FastAPI monte alors toutes ses routes sous `/jimpe`, y compris `/health` qui devient `/jimpe/health`.

Les probes appellent **directement le pod** (pas via l'Ingress), donc elles doivent utiliser le chemin tel que l'API l'expose réellement.

---

## **Résumé visuel**

```
┌─────────────────────────────────────┐
│   Kubernetes surveille ton pod     │
└─────────────────────────────────────┘
           │
           ├─► livenessProbe (toutes les 5s)
           │   └─► Échoue ? → REDÉMARRE le pod
           │
           └─► readinessProbe (toutes les 5s)
               └─► Échoue ? → RETIRE du Service
                             (pas de trafic)
```

---

**En résumé :** Les probes permettent à Kubernetes d'auto-réparer ton infrastructure et de garantir que seuls les pods sains reçoivent du trafic. C'est un des piliers de la **résilience** et de la **haute disponibilité** ! 🚀

**As-tu d'autres questions sur les probes ou sur un autre aspect de ton déploiement ?**