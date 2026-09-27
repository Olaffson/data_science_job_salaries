# Estimation des salaires en science des données

Ce projet prédit le salaire annuel (en USD) d'un poste en science des données à partir de ses caractéristiques : niveau d'expérience, type de contrat, intitulé, pays, télétravail et taille de l'entreprise.

Il comprend :
- un pipeline de données (téléchargement Kaggle, nettoyage, base SQLite) ;
- l'entraînement d'un modèle XGBoost suivi avec MLflow ;
- une **API FastAPI** protégée par jeton JWT, qui sert le modèle ;
- une **interface Streamlit** qui interroge l'API ;
- une infrastructure Azure (PostgreSQL) décrite avec Terraform ;
- une CI/CD GitHub Actions (tests, entraînement, publication de l'image Docker de l'API).

## Jeu de données

Source : [Latest Data Science Job Salaries 2024](https://www.kaggle.com/datasets/saurabhbadole/latest-data-science-job-salaries-2024) (Kaggle), salaires de 2020 à 2024.

| Colonne | Description |
|---|---|
| `work_year` | Année à laquelle le salaire a été versé |
| `experience_level` | Niveau d'expérience : `EN` débutant, `MI` intermédiaire, `SE` confirmé, `EX` direction |
| `employment_type` | Type de contrat : `FT` temps plein, `PT` temps partiel, `CT` contrat, `FL` freelance |
| `job_title` | Intitulé du poste |
| `salary` | Salaire brut annuel, dans la devise d'origine |
| `salary_currency` | Devise du salaire (code ISO 4217) |
| `salary_in_usd` | Salaire converti en dollars américains (**variable à prédire**) |
| `employee_residence` | Pays de résidence de l'employé (code ISO 3166) |
| `remote_ratio` | Part de télétravail : `0`, `50` ou `100` (%) |
| `company_location` | Pays du siège de l'entreprise (code ISO 3166) |
| `company_size` | Taille de l'entreprise : `S` petite, `M` moyenne, `L` grande |

Le nettoyage (`analyse/analyse.ipynb`) passe les textes en minuscules sans espaces, supprime les doublons et les valeurs manquantes, et retire `work_year`, `salary` et `salary_currency`. L'API applique le même nettoyage aux données reçues.

## Structure du dépôt

```
├── 01.sh                  # Environnement local + données (bronze.csv → silver.csv → silver.db)
├── 02.sh / 03.sh          # Création / suppression des ressources Azure (Terraform)
├── run_app.sh             # Lance l'API et l'interface Streamlit
├── Dockerfile             # Image de l'API
├── requirements.txt       # Dépendances de l'application (inclut api/requirements.txt)
├── analyse/analyse.ipynb  # Nettoyage des données
├── api/
│   ├── api.py             # API FastAPI (/token, /predict)
│   ├── best_xgboost_model.pkl
│   ├── requirements.txt   # Dépendances de l'image Docker
│   └── test/              # Tests pytest
├── app/app.py             # Interface Streamlit
├── data/bronze.csv        # Données brutes
├── database_building/     # Scripts de base de données (SQLite locale, PostgreSQL Azure)
├── model/
│   ├── train_model.ipynb  # Entraînement (GridSearchCV + MLflow)
│   ├── best_model.ipynb   # Export du meilleur modèle vers api/best_xgboost_model.pkl
│   └── requirements.txt   # Dépendances des notebooks
└── terraform/main.tf      # Infrastructure Azure
```

## Installation

Prérequis : Python 3.10 et, pour télécharger les données, un jeton API Kaggle (`kaggle.json` dans `~/.kaggle/` ou `~/Téléchargements/`). Le fichier `data/bronze.csv` étant déjà dans le dépôt, le jeton n'est nécessaire que si vous le supprimez.

```bash
./01.sh
```

Ce script :
1. crée l'environnement virtuel `venv/` et installe les dépendances ;
2. télécharge le jeu de données dans `data/bronze.csv`, s'il n'est pas déjà présent ;
3. exécute `analyse/analyse.ipynb`, qui produit `data/silver.csv` ;
4. crée la base SQLite `database_building/sqlite/silver.db` utilisée par l'interface.

## Lancer l'application

L'API a besoin de deux variables d'environnement, que l'on peut aussi placer dans un fichier `.env` à la racine (ignoré par Git) :

```bash
SECRET_KEY=<clé aléatoire, ex : openssl rand -hex 32>
ADMIN_PASSWORD=<mot de passe de l'utilisateur admin>
```

```bash
./run_app.sh
```

- API : http://localhost:8000 (documentation interactive sur `/docs`)
- Interface Streamlit : http://localhost:8501 (identifiant `admin`, mot de passe `ADMIN_PASSWORD`)

L'interface appelle l'API à l'adresse `http://localhost:8000`, modifiable avec la variable `API_URL`.

### Utiliser l'API directement

```bash
# Obtenir un jeton (valable 60 minutes, modifiable avec ACCESS_TOKEN_EXPIRE_MINUTES)
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=admin&password=$ADMIN_PASSWORD" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Demander une prédiction
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"experience_level": "SE", "employment_type": "FT", "job_title": "Data Engineer",
       "employee_residence": "GB", "remote_ratio": "0", "company_location": "GB", "company_size": "M"}'
# {"prediction": 107383.33}
```

### Avec Docker

L'image est publiée par la CD sur GitHub Container Registry à chaque mise à jour de `main` :

```bash
docker run -p 8000:8000 -e SECRET_KEY=... -e ADMIN_PASSWORD=... \
  ghcr.io/olaffson/data_science_job_salaries/my-fastapi-app:latest
```

Pour la construire localement : `docker build -t my-fastapi-app .`

## Entraîner le modèle

```bash
source venv/bin/activate
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 127.0.0.1 --port 5000 &
jupyter nbconvert --to notebook --execute model/train_model.ipynb   # GridSearchCV, résultats enregistrés dans MLflow
jupyter nbconvert --to notebook --execute model/best_model.ipynb    # exporte le meilleur run vers api/best_xgboost_model.pkl
```

Le modèle est un pipeline scikit-learn (encodage one-hot + `XGBRegressor`). Son R² sur le jeu de test est d'environ **0,3** : les caractéristiques disponibles n'expliquent qu'une partie des écarts de salaire, les prédictions sont donc à prendre comme des ordres de grandeur.

Les versions de scikit-learn et de xgboost doivent être identiques entre l'entraînement (`model/requirements.txt`) et l'API (`api/requirements.txt`), sinon le modèle exporté peut ne pas se charger.

## Tests et qualité

```bash
python -m pytest api/
pycodestyle --ignore=E501,E712 api
bandit -r api/ --exclude api/test
```

Les tests utilisent leurs propres valeurs de `SECRET_KEY` et `ADMIN_PASSWORD` si elles ne sont pas définies.

## Infrastructure Azure (optionnelle)

`terraform/main.tf` crée un groupe de ressources, un serveur **PostgreSQL Flexible Server**, une base de données et une règle de pare-feu limitée à votre adresse IP. Le mot de passe n'est jamais écrit dans le code :

```bash
export TF_VAR_db_admin_password='<mot de passe fort>'
export TF_VAR_client_ip=$(curl -s ifconfig.me)
./02.sh                                  # création des ressources

export DB_ADMIN_PASSWORD="$TF_VAR_db_admin_password"
./database_building/create_table.sh      # création de la table jobs
./database_building/import_tables.sh     # import de data/silver.csv

./03.sh                                  # suppression des ressources
```

Les scripts de base de données nécessitent le client `psql`. Le fichier d'état Terraform (`*.tfstate`) contient des secrets : il est ignoré par Git et ne doit pas être committé.

## CI/CD

| Workflow | Déclencheur | Rôle |
|---|---|---|
| `CI` (`ci.yml`) | Push sur toute branche, pull request | Tests pytest avec couverture, pycodestyle, bandit |
| `MODEL` (`main.yml`) | Push sur toute branche | Exécute les notebooks d'analyse et d'entraînement avec un serveur MLflow |
| `CD` (`cd.yml`) | CI réussie sur `main` | Construit et publie l'image Docker de l'API sur `ghcr.io` |

## Licence

MIT, voir [LICENSE](LICENSE).
