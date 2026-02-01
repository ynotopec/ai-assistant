# ai-assistant

Assistant IA adaptatif qui apprend de chaque interaction, crée et utilise des outils lorsque nécessaire, et propose des améliorations validées par un juge indépendant.

## Fonctionnalités

- Apprentissage continu via un journal d'interactions.
- Création automatique d'outils pour répondre à des tâches spécifiques.
- Améliorations proposées et validées par un juge selon le bien commun.
- Ajustement de prudence pour réduire les erreurs et augmenter la fiabilité.

## Utilisation

```bash
python main.py
```

Pour activer un LLM (API OpenAI compatible) :

```bash
export OPENAI_API_KEY="votre-cle"
export OPENAI_MODEL="gpt-4o-mini"
export OPENAI_BASE_URL="https://api.openai.com"
python main.py
```

Exemple d'outil automatique:

```text
> outil:résumé
```

## Architecture

- `AdaptiveAssistant` orchestre les interactions, l'apprentissage et les améliorations.
- `ImprovementJudge` valide les propositions d'amélioration.
- `PerformanceTuner` ajuste le niveau de prudence.
- `SimpleTool` fournit un mécanisme simple d'outils dynamiques.
