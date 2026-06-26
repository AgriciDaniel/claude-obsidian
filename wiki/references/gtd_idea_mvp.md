
## The flowchart, restated as rules

Every incoming item answers these questions in order:

1. **¿Puedo hacer algo concreto con esto?** (Is there a concrete action?)
   - **NO** → 2a
   - **YES** → 2b
2a. **¿Me sirve guardar la info para el futuro?**
   - **NO** → discard, nothing filed.
   - **YES** → **¿Quizás lo quiero hacer en algún momento?**
     - if it's a *possible future action* → bucket **someday/maybe**
     - if it's *pure reference, no action expected* → bucket **reference**
2b. **¿Lo puedo hacer en 2 minutos?**
   - **YES** → do it now. Nothing is filed.
   - **NO** → **¿Se puede delegar?**
     - **YES** → bucket **waiting** (delegated, waiting on someone else)
     - **NO** → **¿Lo tengo que hacer hoy?**
       - **YES** → bucket **today**
       - **NO** → **¿Se le puede poner fecha?** → bucket **backlog**, with or without a `due:` date
	   
	   
	   
Five terminal buckets: `today`, `backlog` (dated), `waiting` (delegated), `someday` (maybe/incubate), `reference` (pure info, no action).
