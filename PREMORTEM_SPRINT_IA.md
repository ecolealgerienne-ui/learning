# Pré-Mortem — Sprint IA 30 Jours
## Industrialisation LLM en Environnement Réglementé

**Méthode :** Gary Klein — Pre-Mortem Analysis  
**Date d'analyse :** 2026-06-16  
**Équipe fictive :** Architecte d'entreprise · CTO · RSSI · Directeur de programme · Représentant métier  
**Hypothèse :** Nous sommes à J+30. Le projet est un échec majeur.

---

## REGISTRE DES RISQUES

| ID | Cause d'échec | Catégorie | P (1-5) | I (1-5) | Score | Signaux faibles | Actions préventives |
|----|--------------|-----------|---------|---------|-------|-----------------|---------------------|
| R01 | Le client pensait acheter "un chatbot IA" — pas une infrastructure | Vision | 5 | 5 | 25 | Questions sur "l'interface utilisateur" dès le kick-off | Brief écrit signé avant démarrage, avec définition explicite de ce que N'est PAS le sprint |
| R02 | Le DSI sponsor quitte son poste en semaine 2 | Gouvernance | 3 | 5 | 15 | Rumeurs de réorganisation, sponsor peu disponible | Identifier un co-sponsor dès le contrat. Clause de continuité |
| R03 | Aucune VM disponible pendant 3 semaines (processus d'achat interne) | Organisation | 4 | 5 | 20 | Délais habituels de provision infrastructure client > 3 semaines | Checklist infrastructure signée J-10 avant démarrage. Bloquer sur prérequis |
| R04 | Les données LLM passent par un proxy non validé par la SSI | Réglementaire/Sécu | 4 | 5 | 20 | Absence de la SSI dans les parties prenantes initiales | Inclure RSSI client dans le kick-off. Clause contractuelle de validation sécurité |
| R05 | Le budget "30 jours" explose car le périmètre s'élargit (scope creep) | Planning/Budget | 5 | 4 | 20 | Demandes informelles "et si on ajoutait…" dès semaine 1 | Contrat à périmètre fixe avec avenants signés. Log des demandes hors-scope |
| R06 | Les API LLM externes sont bloquées par le firewall client | Technologie | 4 | 4 | 16 | Politique de filtrage sortant stricte, DSI prudent | Test de connectivité obligatoire avant J1. Prérequis réseau dans le contrat |
| R07 | La qualité des prompts existants est catastrophique — le ROI estimé est faux | Vision/Données | 4 | 4 | 16 | Pas d'audit prompt avant signature, ROI estimé à l'aveugle | Audit gratuit de 2h OBLIGATOIRE avant signature pour valider les hypothèses ROI |
| R08 | L'équipe IT client n'a aucune compétence Docker — impossible de reprendre en main | Organisation | 4 | 4 | 16 | Profils purement développeurs sans culture DevOps | Assessment compétences équipe client en phase de découverte |
| R09 | Résistance passive de l'équipe IT interne ("on gère déjà les LLM nous-mêmes") | Adoption | 4 | 4 | 16 | Peu d'enthousiasme en kick-off, questions défensives | Sponsor positionne le sprint comme mission habilitante, pas concurrente |
| R10 | Langfuse self-hosted nécessite PostgreSQL 15+ — le client est sur Oracle 12 | Technologie | 3 | 4 | 12 | Aucun inventaire stack technique fait en amont | Grille de prérequis techniques envoyée et validée avant démarrage |
| R11 | Les logs LLM contiennent des données clients → blocage RGPD | Réglementaire | 3 | 5 | 15 | Aucune analyse RGPD des flux avant démarrage | Cartographie des flux de données (PII/non-PII) en semaine 1 |
| R12 | Le client attend −70% de coûts dès semaine 3 — impossible sans volume suffisant | Vision | 4 | 4 | 16 | Chiffres marketing repris comme contractuels | Clause explicite : économies mesurées sur volume réel du client |
| R13 | Amar est seul — une urgence personnelle arrête le projet 10 jours | Organisation | 3 | 5 | 15 | Aucun back-up, aucune documentation intermédiaire | Runbook à jour hebdomadaire. Sous-traitant de secours identifié |
| R14 | Le client change de provider LLM en semaine 2 (Azure → OpenAI direct) | Dépendance externe | 3 | 4 | 12 | Décision commerciale non partagée avec l'équipe technique | Clause de stabilité des choix techniques sur la durée du sprint |
| R15 | Aucun cas d'usage LLM réel en production — le sprint n'a rien à optimiser | Vision | 2 | 5 | 10 | Client "en projet" plutôt qu'en production | Critère d'éligibilité au sprint : minimum 1 LLM en prod ou en pilote actif |
| R16 | Les virtual keys LiteLLM ne s'intègrent pas avec le SSO Keycloak existant | Technologie | 3 | 3 | 9 | Stack IAM existante non auditée | Audit IAM client en phase découverte |
| R17 | Le comité des risques bloque la mise en production après le sprint | Gouvernance | 3 | 4 | 12 | Pas de représentant Risk/Compliance dans les parties prenantes | Inclure Risk/Compliance dès le kick-off. Livrables conformes dès J1 |
| R18 | Le Redis cache ne réduit pas les coûts — les requêtes LLM sont toutes uniques | Technologie/Vision | 3 | 4 | 12 | Aucune analyse de répétabilité des requêtes avant démarrage | Analyse statistique des logs existants avant de promettre un cache hit rate |
| R19 | Mauvaise estimation du volume réel → le ROI est 5x inférieur aux projections | Budget | 4 | 4 | 16 | Volume communiqué par le client non vérifié | Accès aux logs de production pour valider les volumes avant signature |
| R20 | Le client ne paie pas la dernière tranche après la livraison | Commercial | 3 | 4 | 12 | Sponsor changé, nouveau DSI remet en question le contrat | Paiement progressif (33% avant, 33% semaine 2, 33% livraison) |
| R21 | La documentation livrée est inexploitable sans Amar — dépendance totale | Organisation | 3 | 4 | 12 | Aucun standard de documentation défini au contrat | Templates runbook standardisés. Formation équipe client en semaine 4 |
| R22 | Estimation DORA/RGPD sous-évaluée — l'audit réglementaire prend 2 semaines de plus | Réglementaire | 3 | 3 | 9 | Client en environnement DORA sans l'avoir mentionné | Questionnaire réglementaire obligatoire en phase discovery |
| R23 | Le client utilise le sprint comme preuve de concept non payée puis internalise | Commercial | 2 | 4 | 8 | Comportement de "test" visible dès le kick-off | Clause de non-concurrence sur les livrables. Propriété intellectuelle clarifiée |
| R24 | Conflits entre l'équipe data et l'équipe IT sur qui gère le LLM gateway | Gouvernance | 3 | 3 | 9 | Absence d'un RACI clair dès le départ | RACI signé en semaine 1 |
| R25 | Dérive de planning : semaine 4 "polish" utilisée pour finir semaine 1 | Planning | 4 | 3 | 12 | Prérequis infrastructure non livrés à temps | Planning conditionnel avec jalons de go/no-go à J7 et J14 |

---

## TOP 10 DES RISQUES CRITIQUES

| Rang | ID | Cause | Score | Pourquoi c'est le plus dangereux |
|------|----|-------|-------|----------------------------------|
| 1 | R01 | Malentendu sur le périmètre du sprint | 25 | Tue le projet avant qu'il démarre. Le client attend un produit, pas une infra. |
| 2 | R03 | Infrastructure client non disponible | 20 | Bloque tout. Aucune ligne de code déployable sans VM. |
| 3 | R04 | Blocage SSI/RSSI sur le proxy LLM | 20 | En banque, un RSSI peut stopper un projet le lendemain d'un kick-off. |
| 4 | R05 | Scope creep non contrôlé | 20 | 30 jours = 0 marge. Chaque demande hors-périmètre décale la livraison. |
| 5 | R07 | ROI estimé sur des hypothèses fausses | 16 | Si les prompts existants sont déjà optimaux ou le volume insuffisant, le −70% n'existe pas. |
| 6 | R08 | Équipe client sans compétences Docker | 16 | La stack est livrée mais personne ne peut la maintenir. Échec différé. |
| 7 | R09 | Résistance IT interne | 16 | Sabotage passif. L'infra est déployée mais jamais utilisée. |
| 8 | R12 | Attentes ROI irréalistes dès semaine 3 | 16 | Client déçu à mi-parcours. Rupture de confiance. |
| 9 | R19 | Volume réel LLM 5x inférieur aux projections | 16 | Toutes les économies calculées sont fausses. |
| 10 | R13 | Amar seul — risque de disponibilité | 15 | Un consultant solo sans back-up est un SPOF projet. |

---

## MATRICE PROBABILITÉ × IMPACT

```
Impact →        1         2         3         4         5
                Mineur    Limité    Modéré    Majeur    Critique
              ┌─────────┬─────────┬─────────┬─────────┬─────────┐
P=5 Très      │         │         │   R05   │  R01    │  R01    │
    probable  │         │         │   R25   │  R07    │  R03    │
              ├─────────┼─────────┼─────────┼─────────┼─────────┤
P=4 Probable  │         │         │   R08   │  R06    │         │
              │         │         │   R09   │  R12    │         │
              │         │         │         │  R19    │         │
              ├─────────┼─────────┼─────────┼─────────┼─────────┤
P=3 Possible  │         │         │  R16    │  R10    │  R02    │
              │         │         │  R21    │  R14    │  R04    │
              │         │         │  R22    │  R17    │  R11    │
              │         │         │  R24    │  R18    │  R13    │
              │         │         │         │  R20    │         │
              ├─────────┼─────────┼─────────┼─────────┼─────────┤
P=2 Peu       │         │         │         │  R23    │  R15    │
    probable  │         │         │         │         │         │
              ├─────────┼─────────┼─────────┼─────────┼─────────┤
P=1 Rare      │         │         │         │         │         │
              └─────────┴─────────┴─────────┴─────────┴─────────┘

🔴 Zone critique (Score ≥ 16) : R01, R03, R04, R05, R07, R08, R09, R12, R19
🟠 Zone surveillance (Score 10-15) : R02, R06, R10, R11, R13, R14, R17, R18, R20, R25
🟡 Zone acceptable (Score < 10) : R15, R16, R21, R22, R23, R24
```

---

## HYPOTHÈSES IMPLICITES LES PLUS DANGEREUSES

| # | Hypothèse implicite | Réalité possible | Conséquence si fausse |
|---|---------------------|------------------|-----------------------|
| H1 | "Le client a déjà des LLM en production" | Le client est en PoC avec 200 appels/mois | ROI inexistant, sprint sans valeur mesurable |
| H2 | "Le client peut déployer Docker sur ses serveurs" | Environnement Cloud managé (Azure PaaS), Docker interdit | Stack incompatible, livrable inutilisable |
| H3 | "Le sponsor DSI a le pouvoir d'approuver l'architecture" | Le RSSI a un droit de veto non documenté | Blocage en semaine 3 sur le proxy LLM |
| H4 | "30 jours suffisent si tout se passe bien" | Les prérequis prennent 2 semaines | Livraison à J+45 au mieux |
| H5 | "Le −70% de coûts est reproductible chez ce client" | Leur mix de requêtes est 90% unique (pas cacheable) | Promesse non tenue, contentieux |
| H6 | "L'équipe IT client reprendra la main après la formation" | Turnover — la personne formée part 2 semaines après | Stack orpheline, dépendance permanente |
| H7 | "Les données envoyées au LLM sont non-sensibles" | Les prompts contiennent des noms de clients | Incident RGPD, notification CNIL |

---

## PLAN D'ACTIONS PRIORISÉ

### Avant signature du contrat (Phase Discovery)

```
✅ CHECK #1 — Audit gratuit de 2h OBLIGATOIRE
   → Accéder aux logs LLM existants (volume, types de requêtes, répétabilité)
   → Si volume < 50K appels/mois : ROI faible, adapter les promesses
   → Si aucun LLM en prod : proposer un pilote avant le sprint

✅ CHECK #2 — Questionnaire prérequis (à remplir par le client avant signature)
   → Infrastructure disponible : VM Linux, Docker, ports ouverts ?
   → Connectivité sortante : API Mistral/Anthropic accessibles ?
   → Stack IAM : Keycloak ? LDAP ? SSO requis ?
   → Réglementaire : périmètre DORA ? ACPR ? DPO impliqué ?

✅ CHECK #3 — Identifier toutes les parties prenantes avec pouvoir de blocage
   → Sponsor DSI (décision budget)
   → RSSI (veto sécurité)
   → DPO (validation RGPD)
   → Équipe IT (reprise en main)
   → Risk/Compliance (mise en production)
```

### Contrat (clauses non négociables)

```
📄 Périmètre fixe avec log des demandes hors-scope
📄 Paiement en 3 tranches : J0 / J14 / J30
📄 Prérequis techniques = conditions suspensives
📄 ROI conditionnel au volume réel (pas garanti en absolu)
📄 Disponibilité client : un point de contact technique 4h/semaine minimum
```

### Semaine 1 — Sécuriser les fondations

```
J1  → Test de connectivité réseau (API LLM accessibles ?)
J1  → RACI signé (qui décide quoi)
J2  → Cartographie des flux de données (PII ?)
J3  → Validation RSSI sur l'architecture proposée
J5  → Go/No-Go : infrastructure disponible ? Sinon : clause de suspension
```

### Semaine 4 — Sécuriser la sortie

```
J25 → Formation équipe client (pas J30 — trop tard)
J27 → Runbook validé par l'équipe client (ils doivent pouvoir refaire sans toi)
J28 → Mesure des KPIs réels vs prévus — rapport écrit
J30 → Rétrospective + accord sur le suivi mensuel optionnel
```

---

## INDICATEURS D'ALERTE PRÉCOCE

| Signal | Seuil d'alerte | Action immédiate |
|--------|---------------|------------------|
| Infrastructure pas prête à J5 | VM non provisionnée 5 jours après démarrage | Activer clause de suspension, replanning |
| RSSI pas impliqué à J3 | Aucun contact SSI après kick-off | Escalade sponsor : bloquer le déploiement jusqu'à validation |
| Demandes hors-scope > 2 | Plus de 2 demandes nouvelles en semaine 1 | Présenter le log hors-scope au sponsor, avenant ou refus |
| Point de contact client absent | Moins de 2h de disponibilité client/semaine | Mettre le projet en pause formelle |
| Volume LLM réel < 10K appels/mois | Après accès aux logs réels | Recalculer le ROI, renégocier les objectifs |
| Cache hit rate < 10% à J21 | Après 3 semaines de cache actif | Revoir la stratégie caching, alerter le client |
| Sponsor changé | Nouveau DSI ou réorganisation | Réunion de resynchronisation immédiate avec nouveau sponsor |

---

## RÉSUMÉ EXÉCUTIF — COMITÉ DE PILOTAGE

### Scénario d'échec le plus probable (probabilité ~40%)

> Le client signe sur la base d'un ROI de −70% estimé sans données réelles.
> L'infrastructure prend 2 semaines à être disponible.
> La SSI n'est impliquée qu'en semaine 3 et bloque le proxy LLM.
> Le sprint se termine à J+45 au lieu de J+30.
> Le −70% n'est pas atteint car le volume réel est 5x inférieur aux projections.
> Le client est déçu. Amar est épuisé.

### Scénario silencieux (probabilité ~25%)

> Tout est livré en temps et en heure. La stack fonctionne.
> Mais l'équipe IT client n'a pas les compétences Docker pour la maintenir.
> La personne formée part 3 semaines après.
> La stack meurt en silence en 2 mois.
> Le client ne renouvelle pas.

### Les 3 décisions qui changent tout

| Décision | Risques éliminés |
|----------|-----------------|
| Audit obligatoire avant signature (accès aux logs réels) | R01, R07, R12, R15, R18, R19 |
| Checklist prérequis techniques signée à J-10 | R03, R06, R10 |
| RSSI + DPO dans le kick-off J1 | R04, R11, R17 |

**Ces 3 décisions coûtent 4 heures de travail et éliminent 12 risques sur 25.**

### Verdict

> Ce sprint est un produit à fort potentiel avec un ROI réel mesurable —
> **à condition que les hypothèses soient validées avant de commencer**.
> Le principal ennemi n'est pas technique. C'est la précipitation commerciale :
> signer vite, démarrer sans prérequis, promettre des chiffres sans données.
>
> Un sprint mal cadré est pire que pas de sprint :
> il crée de la défiance client et détruit la réputation.

---

*Document confidentiel — Usage interne*
*Méthode : Gary Klein Pre-Mortem*
*Mise à jour : 2026-06-16*
