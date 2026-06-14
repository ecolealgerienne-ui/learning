# Arguments Client — Architecte IA Environnements Réglementés

Document vivant. Enrichi à chaque session avec les slides clés du cours.
À relire avant chaque rendez-vous commercial.

---

## 1. Pourquoi l'Observabilité LLM n'est PAS du monitoring classique

> **Slide cours :** "Traditional vs LLM Observability"

### Le problème avec le monitoring traditionnel

Votre équipe a déjà Datadog, Prometheus, Grafana. Elle pense que c'est suffisant.

**Ce que le monitoring classique voit :**
```
Requête → [???] → Réponse
```
- Latence : ✅
- Erreur HTTP : ✅
- Ce que le modèle a reçu et dit : ❌
- Pourquoi la réponse était mauvaise : ❌
- Combien ça a coûté exactement : ❌

**C'est une boîte noire.** Datadog ne sait pas ce qu'il y a dans le prompt.

### Ce que l'Observabilité LLM apporte en plus

| Capacité | Monitoring classique | Observabilité LLM |
|----------|---------------------|-------------------|
| Full trace visibility | ❌ | ✅ Prompt + réponse + métadonnées |
| Token flows tracked | ❌ | ✅ Input/output tokens par appel |
| Prompt effectiveness | ❌ | ✅ Quel prompt donne les meilleurs résultats |
| Cost attribution | ❌ | ✅ Coût par équipe, par feature, par user |

### Pitch client (DSI / architecte)

> "Votre Datadog vous dit que l'appel a pris 2 secondes et a réussi.
> Langfuse vous dit ce que vous avez envoyé au modèle, ce qu'il a répondu,
> combien ça a coûté, et si la réponse était de qualité.
> C'est la différence entre surveiller un camion et savoir ce qu'il transporte."

### Argument conformité (ACPR / audit)

> "En cas d'audit, votre auditeur ne veut pas voir des codes HTTP 200.
> Il veut savoir exactement quelle décision votre IA a prise, sur quelle base,
> et avec quelles données. Seule l'observabilité LLM vous donne ça."

---

## 2. ROI Framework — Coût réel de l'absence d'observabilité

> **Slide cours :** "ROI Framework — Real cost comparison"

| Catégorie | Sans observabilité | Avec observabilité |
|-----------|-------------------|-------------------|
| Dépense LLM mensuelle | 35 000€+ | 15 000€ |
| Retries inutiles | 5 000€+ | ~0€ |
| Temps de debug/semaine | 20h+ | 2h |
| Réponse incident | Plusieurs jours | Jour même |

### Pitch ROI (30 secondes)

> "L'infrastructure que je déploie se rembourse en moins d'un mois.
> Sur le coût LLM seul, vous passez de 35 000€ à 15 000€/mois
> grâce au routing intelligent et au caching sémantique.
> Vos développeurs récupèrent 18h de debug par semaine.
> Et en cas d'incident, vous répondez le jour même — pas après trois jours
> d'investigation à l'aveugle."

### Décomposition pour un CFO

- **Routing intelligent** : tâches simples → Claude Haiku (10x moins cher que Sonnet)
- **Caching sémantique** : questions similaires → réponse depuis Redis, coût zéro
- **Budget guardrails** : impossible de dépasser le budget alloué par équipe
- **Debug rapide** : 18h développeur économisées × tarif JH = économie mensuelle réelle

---

## 3. Matrice de Risques — Sans Observabilité

> **Slide cours :** "Risk Matrix — Without observability"

| Risque | Impact | Probabilité | Traduction bancaire |
|--------|--------|-------------|---------------------|
| **Token spike** | Élevé (10 000€+) | Très élevé | Boucle infinie sur batch nocturne = facture catastrophique au matin |
| **Silent failures** | Moyen | Élevé | Le LLM répond HTTP 200 mais hallucine — personne ne le sait |
| **Performance degradation** | Moyen | Élevé | Latence qui dérive progressivement, invisible sans monitoring |
| **Compliance violation** | Critique | Moyen | PII envoyé à l'API externe sans détection — violation RGPD immédiate |

### Pitch risque (RSSI / Conformité)

> "Sans observabilité, une violation RGPD sur vos appels LLM peut passer
> inaperçue des semaines. Avec Langfuse, chaque appel est tracé,
> chaque donnée sensible est détectée avant envoi.
> C'est votre première ligne de défense face à l'ACPR."

### Pitch risque (DSI / Budget)

> "Le token spike, c'est le cauchemar de tout DSI :
> une erreur de code la nuit, et vous vous réveillez avec 10 000€
> de facture Anthropic en plus.
> Les budget guardrails que je configure coupent automatiquement avant que ça arrive."

---

## 📋 TEMPLATE — Ajouter un nouvel argument

```
## N. [Titre du concept]

> **Slide cours :** "[Titre du slide]"

### Le problème
[Ce que le client vit sans la solution]

### Ce que ça apporte
[Tableau ou liste des bénéfices concrets]

### Pitch client (DSI / architecte)
> "[Citation prête à l'emploi — 2-3 phrases max]"

### Argument conformité / budget / risque
> "[Citation adaptée à l'interlocuteur]"
```

---

_Dernière mise à jour : 2026-06-14_
_Source : Cours Udemy "LLM Observability & Cost Management" — Paulo Dichone_
