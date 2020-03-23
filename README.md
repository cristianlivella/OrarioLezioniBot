# OrarioLezioniBot
Questo bot recupera automaticamente da un *iCal* di *Google Calendar* l'orario delle lezioni della settimana, genera un immagine e la imposta come immagine del gruppo WhatsApp.

Quando mancano 5 minuti all'inizio di una lezione invia un messaggio di promemoria, con il link della call (di Google Meet, oppure qualsiasi altro link trovato nella descrizione dell'evento), se presente.

Risponde ai comandi ***lezioni oggi*** e ***lezioni domani***, inviando rispettivamente l'elenco delle lezioni del giorno corrente e del giorno successivo.

Il bot è ancora in fase di sviluppo, pertanto potrebbe non funzionare correttamente. L'immagine del gruppo attualmente è semplicemente composta dalla rappresentazione JSON delle lezioni della settimana.

Oltre alle dipendenze contenute in *requirements.txt* è necessario anche [**Simple-Yet-Hackable-WhatsApp-api**](https://github.com/VISWESWARAN1998/Simple-Yet-Hackable-WhatsApp-api) e le relative dipendenze.
