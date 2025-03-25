# Anthropic CrewAI Dev Assistant

Un assistant de développement intelligent utilisant CrewAI et l'API Anthropic Claude, avec une interface graphique et une intégration GitHub pour automatiser les workflows de développement.

## Fonctionnalités

- **Équipe d'agents IA spécialisés** configurables selon le langage et le type de projet
- **Interface graphique conviviale** pour visualiser les erreurs et suivre les workflows
- **Intégration avec GitHub** pour déclencher des workflows automatisés
- **Gestion de contexte optimisée** pour les grands projets
- **Détection et affichage des erreurs** avec des explications claires

## Structure des agents

L'assistant repose sur une équipe de 4 agents spécialisés :

1. **Analyste des besoins** - Comprend et formalise les besoins du projet
2. **Architecte Logiciel** - Conçoit une architecture robuste et extensible 
3. **Développeur** - Transforme les spécifications en code de qualité
4. **Reviewer** - Identifie les problèmes potentiels et propose des améliorations

## Installation

### Prérequis

- Python 3.10 ou supérieur
- Compte GitHub
- Clé API Anthropic Claude

### Installation des dépendances

```bash
# Cloner le dépôt
git clone https://github.com/robinixbox/anthropic-crewai-dev-assistant.git
cd anthropic-crewai-dev-assistant

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration

1. Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```
ANTHROPIC_API_KEY=votre_clé_api_anthropic
GITHUB_ACCESS_TOKEN=votre_token_github
```

2. Configurez l'application en modifiant le fichier `config.yaml` selon vos besoins.

## Utilisation

### Lancer l'application

```bash
python src/app.py
```

### Interface graphique

L'interface graphique s'ouvrira automatiquement dans votre navigateur par défaut. Elle vous permettra de :

- Configurer les agents IA selon vos besoins
- Lancer des analyses de code
- Visualiser les erreurs et les suggestions d'amélioration
- Intégrer votre dépôt GitHub pour des workflows automatisés

### Déclencher un workflow GitHub

Pour déclencher un workflow d'analyse automatique sur GitHub :

1. Créez une issue avec le label `ai-review` sur votre dépôt
2. L'assistant analysera votre code et créera une PR avec les améliorations suggérées

## Architecture du projet

```
anthropic-crewai-dev-assistant/
├── .github/                    # Configuration des workflows GitHub
│   └── workflows/
│       └── ai_review.yml       # Workflow pour l'analyse automatique
├── src/
│   ├── agents/                 # Définition des agents IA
│   │   ├── __init__.py
│   │   ├── analyst.py
│   │   ├── architect.py
│   │   ├── developer.py
│   │   └── reviewer.py
│   ├── tools/                  # Outils utilisés par les agents
│   │   ├── __init__.py
│   │   ├── github_tool.py
│   │   └── code_analysis_tool.py
│   ├── ui/                     # Interface graphique
│   │   ├── __init__.py
│   │   ├── app.py              # Application Streamlit
│   │   └── components/         # Composants de l'interface
│   ├── workflows/              # Définition des workflows
│   │   ├── __init__.py
│   │   └── github_workflows.py # Intégration avec GitHub
│   ├── config.py               # Gestion de la configuration
│   ├── main.py                 # Point d'entrée principal
│   └── app.py                  # Lanceur de l'application
├── config/
│   ├── agents.yaml             # Configuration des agents
│   └── tasks.yaml              # Définition des tâches
├── .env                        # Variables d'environnement
├── requirements.txt            # Dépendances du projet
└── README.md                   # Ce fichier
```

## Comment contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
