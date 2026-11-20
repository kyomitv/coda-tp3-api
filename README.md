# Starter - Cloud Migration Challenge

Lancer le monolithe :

```bash
docker compose up -d --build
./smoke_test.sh
```

Avant toute modification, observez son comportement lorsque le conteneur est supprimé puis recréé.

Le projet se déroule ensuite en deux temps :

1. rendre l'application **Cloud-ready localement** (état externalisé, replicas, configuration runtime) ;
2. démarrer le **AWS Academy Learner Lab** dès le début du TP pour vérifier l'accès, tout en terminant le refactor local ; le déploiement AWS commence lorsque la base Cloud-ready est stable.

Le starter utilise un petit classifieur Iris pré-entraîné sans scikit-learn au runtime afin que les images Docker restent légères sur les petites VM du laboratoire.
# coda-tp3-api
