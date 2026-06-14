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

## 4. Ce que vous mesurez concrètement avec Langfuse

> **Slide cours :** "What You'll Measure"

### Les 5 dimensions de mesure

| Dimension | Ce qu'on mesure | Valeur bancaire |
|-----------|----------------|-----------------|
| **Token usage** | Ratio input/output par appel | Identifier les prompts qui "gonflent" inutilement la facture |
| **Latency** | Décomposition par étape (pas juste le total) | Savoir si le problème vient du réseau, du modèle, ou du RAG |
| **Cost** | Par requête, par feature, par utilisateur | Chargeback par département — chaque équipe voit sa consommation |
| **Quality** | Pertinence des réponses, taux d'hallucination | Détecter quand le modèle dégrade sans que personne s'en plaigne |
| **Errors** | Par type, par modèle, par prompt | Identifier quel prompt génère le plus d'erreurs |

### Pourquoi la décomposition par étape (latency per step) est clé

Sans Langfuse, vous voyez : **"L'appel a pris 4 secondes."**

Avec Langfuse, vous voyez :
```
Récupération contexte (RAG)  : 2,1s  ← problème ici
Appel Claude API             : 1,6s
Formatage réponse            : 0,3s
─────────────────────────────────────
Total                        : 4,0s
```

**Vous savez où agir.** Sans ça, vous optimisez à l'aveugle.

### Pitch client (CTO / Architecte)

> "Langfuse vous donne une vue chirurgicale sur chaque appel LLM :
> combien de tokens, à quelle étape ça ralentit, combien ça coûte,
> et si la réponse était de qualité. C'est le premier outil
> dont vos développeurs ont besoin avant de mettre un LLM en production."

### Argument FinOps (CFO / DSI)

> "Le coût par feature vous permet de savoir exactement combien coûte
> votre chatbot conformité vs votre assistant crédit.
> Vous pouvez refacturer chaque département à l'euro près —
> exactement comme vous le faites déjà avec le cloud."

### Argument qualité (Conformité / Métier)

> "Le taux d'hallucination, c'est la métrique que votre comité des risques
> attend. Je mets en place les évaluations automatiques qui mesurent
> si le modèle invente des réponses — et vous alertent quand ça dépasse un seuil."

---

## 5. ROI Calculator — La formule qui convainc un CFO

> **Slide cours :** "ROI Calculator"

### Décomposition du coût évitable (base : 20 000€/mois de LLM)

| Poste de coût | Montant mensuel | Explication |
|---------------|----------------|-------------|
| Gaspillage tokens (30%) | 6 000€ | Prompts mal optimisés, contextes inutiles |
| Temps de debug (10h/sem × 100€/h) | 4 000€ | Développeurs qui cherchent à l'aveugle |
| Coût incidents (amorti) | 5 000€ | Token spike, downtime, violations |
| **Total coût évitable** | **15 000€/mois** | |

### Investissement pour éviter ça

- **Plateforme :** 500 à 2 000€/mois (Langfuse self-hosted = ~50€/mois infra)
- **Setup :** 8 heures one-time ← c'est votre prestation

### ROI : 7 à 30x dès le premier mois

**Résultats réels mesurés :**
- **47%** de réduction des coûts tokens → via optimisation des prompts
- **80%** de temps de debug en moins → via tracing complet
- **0€** de surprises incontrôlées → via budget guardrails

### La formule (à écrire sur un tableau blanc en réunion)

```
Économies = (Gaspillage tokens) + (Temps debug × TJM) + (Incidents évités × Coût)
```

### Pitch CFO / DAF (chiffres adaptés contexte bancaire)

> "Votre équipe dépense 15 000€/mois en coûts évitables sur vos LLM.
> Mon intervention coûte 8 heures de setup et 50€/mois d'infra.
> Le ROI est entre 7 et 30x dès le premier mois.
> C'est l'investissement IA le plus rentable que vous ferez cette année."

### Comment personnaliser la formule en rendez-vous

Posez ces 3 questions au client :
1. "Quel est votre budget LLM mensuel actuel ?" → X€
2. "Combien d'heures vos devs passent à débugger des appels IA par semaine ?" → Yh
3. "Avez-vous déjà eu un incident de surcoût ou de conformité IA ?" → Z€

Puis calculez devant eux :
```
Économies = (X × 30%) + (Y × 4 semaines × TJM/8h) + (Z amorti)
```

**Ils voient leur propre chiffre. C'est imparable.**

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
