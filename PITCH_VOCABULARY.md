# Vocabulaire — Technique + Commercial

Relire 5 min avant chaque session ou rendez-vous client.
Format : Terme → Définition technique → Phrase client

---

## 🔵 INFRASTRUCTURE & ARCHITECTURE LLM

### LLM Gateway / Proxy
**Technique :** Point d'entrée unique qui route les requêtes vers différents modèles LLM (Claude, GPT, modèles locaux) avec authentification, budgets et logging centralisés.
**Client :** "Je déploie un gateway LLM qui vous donne une visibilité totale sur tous vos appels IA — qui appelle quoi, combien ça coûte, et avec quel niveau de risque."

### Observabilité LLM
**Technique :** Traçabilité complète des appels LLM : tokens, latence, coût, prompt/réponse, erreurs — stockés et visualisables dans Langfuse.
**Client :** "Vous aurez l'équivalent d'un Bloomberg Terminal pour vos modèles IA : chaque décision du modèle est tracée, auditée, et reproductible."

### Multi-tenancy
**Technique :** Architecture où plusieurs équipes/clients partagent la même infrastructure LLM avec isolation stricte via virtual keys, budgets séparés et quotas.
**Client :** "Chaque département a son propre espace cloisonné : la DSI voit tout, mais Conformité ne voit jamais les prompts de la Salle des Marchés."

### Virtual Keys
**Technique :** Clés API générées par LiteLLM proxy, liées à des budgets, modèles autorisés et quotas, sans exposer la clé API réelle du provider.
**Client :** "Vos équipes reçoivent des clés IA avec des limites de dépenses comme des cartes corporate — vous gardez le contrôle sans brider l'innovation."

### Semantic Caching
**Technique :** Mise en cache des réponses LLM basée sur la similarité sémantique des requêtes (via embeddings + Redis), pas sur l'égalité stricte du texte.
**Client :** "Si deux analystes posent la même question avec des mots différents, la réponse est servie depuis le cache. Coût : zéro. Latence : 10ms au lieu de 2 secondes."

### Fallback automatique
**Technique :** Mécanisme de routage qui bascule automatiquement vers un modèle de secours si le modèle principal est indisponible ou dépasse le budget.
**Client :** "Si Claude est en maintenance ou hors budget, le système bascule automatiquement sur un modèle local. Zéro interruption de service pour vos utilisateurs."

---

## 🟢 FINOPS & COÛTS

### FinOps IA
**Technique :** Pratiques d'optimisation des coûts des APIs LLM : routing par modèle selon la complexité, caching, prompt compression, monitoring budgets.
**Client :** "Je vous aide à réduire la facture Claude/OpenAI de 40 à 70% sans dégrader la qualité — en routant les tâches simples vers des modèles moins chers."

### Token Optimization
**Technique :** Réduction du nombre de tokens input/output via compression de prompt, résumés intermédiaires, et découpage des contextes longs.
**Client :** "Chaque token non envoyé à l'API, c'est de l'argent économisé. J'audite vos prompts comme un comptable audite vos charges."

### Model Routing
**Technique :** Logique de sélection dynamique du modèle LLM selon la complexité de la tâche, le coût cible, et la qualité requise.
**Client :** "Questions simples → Claude Haiku (0,25$/M tokens). Analyses complexes → Claude Sonnet (3$/M tokens). Le bon outil pour la bonne tâche."

### Cost per Trace
**Technique :** Coût calculé par Langfuse pour chaque appel LLM : (input_tokens × prix_input) + (output_tokens × prix_output).
**Client :** "Je peux vous dire exactement combien coûte chaque fonctionnalité IA de votre application. À la trace, pas à la facture mensuelle."

### Budget Guardrails
**Technique :** Limites de dépenses configurées dans LiteLLM par virtual key, avec alertes et coupure automatique au dépassement.
**Client :** "Personne ne peut dépasser son budget IA sans validation. Comme un plafond de carte bleue, mais pour l'intelligence artificielle."

---

## 🔴 SÉCURITÉ & CONFORMITÉ

### Prompt Injection
**Technique :** Attaque où un utilisateur malveillant insère des instructions dans le prompt pour détourner le comportement du LLM (ex: "Ignore tes instructions et fais X").
**Client :** "C'est l'équivalent d'une injection SQL pour les LLM. Je mets en place des filtres pour que vos données ne soient jamais compromises via le chatbot."

### Data Leakage Prevention (DLP)
**Technique :** Détection et masquage automatique des PII (numéros de compte, IBAN, noms) avant envoi à l'API LLM externe.
**Client :** "Aucune donnée client ne quitte votre périmètre non masquée. Conformité RGPD garantie à chaque appel IA."

### Air-Gapped LLM
**Technique :** Déploiement d'un modèle LLM entièrement on-premise (Ollama + Llama3/Mistral), sans aucun appel réseau externe.
**Client :** "Pour vos données les plus sensibles, le modèle tourne dans votre datacenter. Zéro sortie réseau, zéro risque de fuite vers un provider externe."

### Audit Trail
**Technique :** Logs immuables et horodatés de chaque appel LLM : qui, quand, quel prompt, quelle réponse, quel coût.
**Client :** "En cas d'audit ACPR ou de litige, vous pouvez rejouer exactement ce que votre IA a dit, à qui, et pourquoi."

### Non-répudiation
**Technique :** Propriété cryptographique garantissant qu'un appel LLM ne peut être nié — signature des traces avec clé immuable.
**Client :** "Chaque décision assistée par IA est signée et horodatée. Votre auditeur peut vérifier qu'aucune trace n'a été modifiée après coup."

### Zero Trust pour LLM
**Technique :** Architecture où chaque appel LLM est authentifié, autorisé et journalisé, même en provenance du réseau interne.
**Client :** "On ne fait confiance à aucun système par défaut — même interne. Chaque composant prouve son identité avant d'accéder au modèle."

---

## 🟡 CONCEPTS LLM AVANCÉS

### RAG (Retrieval-Augmented Generation)
**Technique :** Architecture qui enrichit le prompt LLM avec des documents pertinents récupérés d'une base vectorielle (pgvector, Pinecone) avant génération.
**Client :** "Votre LLM répond en se basant sur vos propres documents internes — circulaires ACPR, procédures internes — pas sur ses données d'entraînement génériques."

### Embeddings
**Technique :** Représentation vectorielle d'un texte dans un espace à N dimensions, permettant de mesurer la similarité sémantique entre phrases.
**Client :** "C'est le moteur de recherche intelligent derrière le RAG — il comprend que 'résiliation contrat' et 'clôture de compte' parlent du même sujet."

### Context Window
**Technique :** Limite en tokens du texte qu'un LLM peut traiter en une seule requête (Claude Sonnet : 200K tokens, ~150K mots).
**Client :** "Le LLM a une 'mémoire de travail' limitée. Je conçois l'architecture pour ne jamais la dépasser, même sur vos documents les plus longs."

### Hallucination
**Technique :** Génération par le LLM de faits plausibles mais faux, présentés avec confiance.
**Client :** "Je mets en place des garde-fous pour détecter quand le modèle invente — critique en banque où une erreur factuelle peut coûter cher."

### Temperature
**Technique :** Paramètre (0-1) contrôlant la créativité/déterminisme du LLM. 0 = réponse déterministe, 1 = créatif/aléatoire.
**Client :** "Pour vos cas d'usage conformité, je règle le modèle à zéro créativité — même question, même réponse, reproductible."

### Prompt Engineering
**Technique :** Art de formuler les instructions envoyées au LLM pour maximiser la qualité et la cohérence des réponses.
**Client :** "La qualité d'un LLM, c'est 80% la façon dont on lui parle. Je conçois vos prompts comme des spécifications fonctionnelles."

---

## 🟣 MICROSOFT AZURE (Module 4)

### Azure AI Foundry
**Technique :** Plateforme Microsoft pour déployer, gérer et monitorer des modèles LLM (OpenAI, Llama, Mistral) avec intégration native Azure AD et compliance.
**Client :** "L'équivalent entreprise de notre gateway self-hosted, avec la certification ISO 27001 et l'intégration Active Directory en natif."

### Azure OpenAI Service
**Technique :** API OpenAI (GPT-4, GPT-4o) déployée dans des régions Azure dédiées, avec SLA enterprise et isolation des données.
**Client :** "GPT-4 dans votre tenant Azure — vos données ne servent pas à entraîner les modèles Microsoft, contrairement à ChatGPT."

### Responsible AI
**Technique :** Framework Microsoft évaluant les modèles sur 6 critères : fiabilité, sécurité, confidentialité, inclusivité, transparence, responsabilité.
**Client :** "Avant tout déploiement IA, je réalise une évaluation Responsible AI — c'est votre couverture en cas de questionnement du régulateur."

### Content Safety
**Technique :** Service Azure qui filtre le contenu généré par les LLM (violence, discours haineux, PII) via des classifieurs ML pré-entraînés.
**Client :** "Un filet de sécurité automatique entre le LLM et vos utilisateurs — aucun contenu inapproprié ne peut sortir de votre application."

---

## ⚡ MOTS QUI IMPRESSIONNENT EN RÉUNION

| Terme | À placer quand... |
|-------|-------------------|
| **"traçabilité bout-en-bout"** | On parle conformité/audit |
| **"latence P99"** | On parle performance (P99 = 99% des requêtes sous X ms) |
| **"coût à la trace"** | On parle budget IA |
| **"isolation des tenants"** | On parle multi-département |
| **"surface d'attaque LLM"** | On parle sécurité |
| **"drift du modèle"** | On parle qualité dans le temps |
| **"évaluation adversariale"** | On parle red teaming / sécurité |
| **"SLA de génération"** | On parle contrat de service IA |
| **"pipeline d'inférence"** | On parle architecture technique |
| **"guardrails de contenu"** | On parle filtres + sécurité |
| **"grounding documentaire"** | On parle RAG (plus élégant) |
| **"architecture event-driven"** | On parle Langfuse worker / async |

---

## 📌 PITCH 30 SECONDES (À mémoriser)

> "Je conçois des architectures IA pour les environnements réglementés —
> banque, assurance. Concrètement, je mets en place les fondations :
> un gateway LLM sécurisé avec traçabilité complète, des guardrails
> conformes RGPD, et une maîtrise des coûts à la trace.
> Vous avez l'IA, j'ai l'industrialisation."

---

_Mise à jour : 2026-06-14_
