# Supplier KPI (ISO 9001) — Manuale Utente

**Modulo:** Supplier KPI (ISO 9001)
**Destinatari:** Responsabile Acquisti, Responsabile Qualità, Consulente ISO 9001

---

## Indice

1. [Scopo del modulo](#1-scopo-del-modulo)
2. [Dove si trovano i report](#2-dove-si-trovano-i-report)
3. [Report Ritardi ricezione fornitori](#3-report-ritardi-ricezione-fornitori)
   - 3.1 Cosa mostra
   - 3.2 Come si calcola il ritardo
   - 3.3 Come si usa la vista elenco
   - 3.4 Come si usa la vista grafico
   - 3.5 Classificazione QC dei fornitori
4. [Report Non conformità fornitori](#4-report-non-conformità-fornitori)
   - 4.1 Cosa mostra
   - 4.2 Criteri di inclusione
   - 4.3 Come si usa
5. [Configurazione delle causali di magazzino](#5-configurazione-delle-causali-di-magazzino)
   - 5.1 Causali preconfigurate all'installazione
   - 5.2 Come aggiungere o modificare una causale
6. [Limiti e avvertenze per l'audit ISO 9001](#6-limiti-e-avvertenze-per-laudit-iso-9001)
7. [Domande frequenti](#7-domande-frequenti)

---

## 1. Scopo del modulo

Il modulo **Supplier KPI** mette a disposizione due indicatori di prestazione (KPI) sui fornitori, concepiti per supportare il sistema di gestione della qualità secondo la norma ISO 9001:

- **KPI ritardi di consegna:** misura, riga per riga, quanti giorni intercorrono tra la data di consegna concordata nell'ordine di acquisto e la data del documento di trasporto (DDT) con cui la merce è effettivamente arrivata. La media per fornitore e per anno costituisce l'indicatore di puntualità.

- **KPI non conformità:** conta il numero di operazioni di magazzino completate che, per la loro natura (causale utilizzata), indicano un problema di qualità: resi, riparazioni, sostituzioni in garanzia. Il conteggio è raggruppato per fornitore e per anno.

Entrambi i report sono accessibili direttamente dal menu **Acquisti**, senza necessità di esportare dati o elaborare fogli di calcolo.

---

## 2. Dove si trovano i report

Dalla barra di menu principale, seguire il percorso:

**Acquisti ▸ Reporting**

In questa sezione compaiono due voci:

| Voce di menu | Contenuto |
|---|---|
| **Ritardi ricezione fornitori** | KPI puntualità consegne, giorni di ritardo per riga ricevuta |
| **Non conformità fornitori** | Conteggio resi, riparazioni e altri movimenti NC per fornitore |

> **Nota:** Le due voci sono visibili solo agli utenti che dispongono dei permessi di accesso al modulo Acquisti e al modulo Magazzino. Se le voci non compaiono, contattare l'amministratore del sistema.

---

## 3. Report Ritardi ricezione fornitori

### 3.1 Cosa mostra

All'apertura, l'elenco è raggruppato per **Anno** e, all'interno di ciascun anno, per **Fornitore**. Per ogni gruppo viene mostrata la media dei giorni di ritardo (colonna **Ritardo (gg)**) e il conteggio delle righe ricevute in ritardo (colonna **In ritardo**).

Espandendo un gruppo si vedono le singole righe, ciascuna corrispondente a una riga di ordine di acquisto ricevuta. Le colonne disponibili sono:

| Colonna | Significato |
|---|---|
| **Anno** | Anno solare della ricezione |
| **Fornitore** | Ragione sociale del fornitore |
| **Classificazione QC** | Classe qualità assegnata al fornitore in anagrafica (paragrafo 3.5) |
| **Ordine** | Riferimento dell'ordine di acquisto |
| **Picking** | Riferimento del documento di ricezione merce in magazzino |
| **Prodotto** | Articolo ricevuto |
| **Data prevista** | Data di consegna concordata sulla riga dell'ordine |
| **Data DDT in** | Data del documento di trasporto del fornitore, registrata alla ricezione |
| **Ritardo (gg)** | Differenza in giorni tra Data DDT in e Data prevista |
| **In ritardo** | Indica se la consegna è avvenuta dopo la data prevista (1 = sì, 0 = no) |

### 3.2 Come si calcola il ritardo

Il calcolo è automatico e avviene al momento della visualizzazione del report, sulla base dei dati già presenti nel sistema:

```
Ritardo (gg) = Data DDT in  –  Data prevista sulla riga d'ordine
```

- Un valore **positivo** (es. +3) significa che la merce è arrivata **3 giorni dopo** la data concordata.
- Un valore **negativo** (es. -2) significa che la merce è arrivata **2 giorni prima** della data concordata (consegna in anticipo).
- Il valore **0** significa consegna puntuale.

La **media** visualizzata a livello di gruppo (fornitore/anno) è la media aritmetica dei giorni di ritardo di tutte le righe del gruppo: valori negativi (anticipi) e positivi (ritardi) si compensano tra loro.

**Condizioni affinché una riga compaia nel report:**

1. La ricezione merce deve essere in stato **Completato** (picking chiuso).
2. Alla ricezione deve essere stata registrata la **Data DDT in** (data del documento di trasporto del fornitore). Le ricezioni prive di questa data non compaiono nel report.
3. La riga di magazzino deve essere collegata a una riga di ordine di acquisto. I movimenti di entrata non originati da un ordine (es. rettifiche di inventario) sono esclusi.
4. Conta solo la **fornitura originaria**: i rientri di merce da riparazione, sostituzione o reso (causali contrassegnate come "Non Conformità", oppure documenti generati dalla procedura di reso) restano collegati all'ordine ma **non** compaiono nel report ritardi, anche se ricevuti molto tempo dopo. Esempio: un ordine consegnato a luglio 2023 la cui merce rientra da riparazione a ottobre 2024 mostra come ricezione solo quella di luglio 2023.

### 3.3 Come si usa la vista elenco

**Ricerca per fornitore o anno:** nella barra di ricerca in alto, digitare il nome del fornitore oppure l'anno (es. "2024") per filtrare i risultati.

**Filtro "In ritardo":** fare clic sul pulsante **Filtri** e selezionare **In ritardo** per visualizzare solo le righe in cui la consegna è avvenuta dopo la data concordata. Questo filtro è utile per isolare i casi problematici da presentare all'audit.

**Filtro "Solo fornitori classificati QC":** all'apertura del report questo filtro è **attivo di default**: vengono mostrati solo i fornitori a cui è stata assegnata una classificazione QC in anagrafica (paragrafo 3.5). Per vedere i ritardi di **tutti** i fornitori, rimuovere il filtro dalla barra di ricerca con un clic sulla relativa etichetta.

**Modifica del raggruppamento:** fare clic su **Raggruppa per** per modificare i criteri di raggruppamento. Le opzioni disponibili sono **Anno**, **Fornitore** e **Classificazione QC**. Si possono combinare più criteri (es. prima per Anno, poi per Fornitore) oppure usarne uno solo.

**Esportazione:** per esportare i dati in foglio di calcolo, selezionare le righe desiderate (oppure tutte con la casella in testa alla colonna) e utilizzare il pulsante **Esporta** nella barra degli strumenti.

### 3.4 Come si usa la vista grafico

Fare clic sull'icona del **grafico a barre** in alto a destra (accanto all'icona dell'elenco) per passare alla vista grafico. Il grafico mostra, per ciascun fornitore, la somma dei giorni di ritardo sul periodo visualizzato. Questa vista è particolarmente utile per il riesame della direzione (Management Review ISO 9001).

### 3.5 Classificazione QC dei fornitori

Nell'anagrafica del fornitore (menu **Acquisti ▸ Fornitori**, oppure **Vendite ▸ Rubrica indirizzi ▸ Clienti e fornitori**) è disponibile il nuovo campo **Classificazione QC fornitore**, visibile solo quando la casella **Fornitore** è spuntata. I valori possibili sono:

| Valore | Significato suggerito |
|---|---|
| **QC Importante** | Fornitore critico per la qualità del prodotto/servizio |
| **QC Primario** | Fornitore principale, monitorato regolarmente |
| **QC Secondario** | Fornitore secondario o occasionale |

Il significato operativo delle tre classi è definito dal sistema di gestione qualità aziendale; il modulo si limita a registrare la classe e a usarla nel report.

**Effetto sul report ritardi:** il report **Ritardi ricezione fornitori** mostra di default solo i fornitori che hanno una classificazione QC assegnata (qualsiasi delle tre classi). I fornitori senza classificazione restano visibili rimuovendo il filtro **Solo fornitori classificati QC** dalla barra di ricerca.

**Come assegnare la classe a un fornitore:**

1. Aprire la scheda del fornitore dall'anagrafica.
2. Nella sezione dove compare la casella **Fornitore**, selezionare il valore desiderato nel campo **Classificazione QC fornitore**.
3. Salvare la scheda con il pulsante **Salva**.

> **Nota:** la classificazione non ha effetti su ordini, prezzi o flussi operativi: è un attributo puramente informativo usato dal report qualità.

---

## 4. Report Non conformità fornitori

### 4.1 Cosa mostra

All'apertura, l'elenco è raggruppato per **Anno** e **Fornitore**. Per ogni gruppo viene mostrato il conteggio delle non conformità (colonna **# NC**).

Le colonne disponibili nell'elenco dettagliato sono:

| Colonna | Significato |
|---|---|
| **Anno** | Anno solare dell'operazione |
| **Fornitore** | Ragione sociale del fornitore |
| **Causale** | Giornale di magazzino utilizzato per l'operazione |
| **Picking** | Riferimento del documento di magazzino |
| **Data** | Data dell'operazione (data DDT se disponibile, altrimenti data di chiusura) |
| **Tipo** | Direzione del movimento: **Sending Goods** = merce in uscita (reso a fornitore), **Getting Goods** = merce in entrata |

> **Filtro di default:** all'apertura, il report mostra di default solo i movimenti in **uscita** (resi al fornitore, tipo "Sending Goods"). Per vedere anche i movimenti in entrata, rimuovere il filtro attivo nella barra di ricerca.

### 4.2 Criteri di inclusione

Un'operazione di magazzino completata compare nel report delle non conformità se rispetta tutte le seguenti condizioni:

1. L'operazione è in stato **Completato**.
2. La causale (giornale di magazzino) associata all'operazione ha la casella **Non Conformità** spuntata.
3. Se la causale ha anche la casella **NC solo se note RMA/Reso** spuntata, l'operazione compare solo se nel campo **Note** del documento di magazzino è presente la parola **RMA** (anche come prefisso: es. "RMA123" è incluso) oppure la parola **Reso** (intesa come parola intera: "Normale" o "resoconto" non vengono riconosciuti).

Il controllo sulle note è necessario per causali generiche come "Return" o "Reso a Fornitore", che possono essere utilizzate sia per movimenti di qualità sia per movimenti ordinari: la presenza della parola chiave nelle note distingue i casi di non conformità dai movimenti ordinari.

### 4.3 Come si usa

Le funzionalità di ricerca, filtro, raggruppamento ed esportazione sono analoghe a quelle del report ritardi (paragrafo 3.3). Le opzioni di raggruppamento disponibili sono **Anno**, **Fornitore** e **Causale**.

---

## 5. Configurazione delle causali di magazzino

### 5.1 Causali preconfigurate all'installazione

Al momento dell'installazione del modulo, il sistema individua automaticamente le causali di magazzino con nomi corrispondenti a quelli standard e imposta i relativi indicatori. La configurazione iniziale è la seguente:

**Causali marcate come Non Conformità (senza verifica delle note):**

| Nome causale italiano | Nome causale inglese |
|---|---|
| C/Riparazione | C/Repair |
| C/riparazione in garanzia | C/repair under warranty |
| C/sostituzione in garanzia | C/replacement under warranty |
| Reso per Sostituzione | Made for Replacement |

**Causali marcate come Non Conformità con verifica obbligatoria delle note (parola "RMA" o "Reso"):**

| Nome causale italiano | Nome causale inglese |
|---|---|
| Reso | Return |
| Reso a Fornitore | Return to Vendor |

> **Importante:** la configurazione iniziale viene eseguita solo alla prima installazione. Gli aggiornamenti successivi del modulo non sovrascrivono le impostazioni manuali eventualmente apportate dall'utente.

### 5.2 Come aggiungere o modificare una causale

Per configurare una causale non compresa nell'elenco predefinito, oppure per modificare una causale esistente:

1. Aprire il menu **Magazzino ▸ Configurazione ▸ Giornali** (o **Causali di magazzino**, a seconda della traduzione installata).
2. Selezionare la causale da modificare nell'elenco.
3. Nella scheda della causale sono presenti due nuove caselle di spunta:
   - **Non Conformità** — se spuntata, tutte le operazioni completate con questa causale vengono conteggiate come non conformità nel report.
   - **NC solo se note RMA/Reso** — visibile solo se la casella **Non Conformità** è spuntata. Se attivata, un'operazione viene conteggiata come NC solo se le note del documento di magazzino contengono la parola "RMA" o "Reso" (come specificato al paragrafo 4.2).
4. Salvare la scheda con il pulsante **Salva**.

> **Nota:** rinominare una causale non influisce sul report. Il sistema fa riferimento alle caselle di spunta, non al nome della causale. Se si rinomina una causale già configurata, il comportamento nel report rimane invariato.

---

## 6. Limiti e avvertenze per l'audit ISO 9001

I seguenti aspetti devono essere tenuti presenti in sede di audit o riesame della direzione:

**Report ritardi:**

- Le righe di ricezione merce non collegate a un ordine di acquisto (es. carichi manuali, rettifiche di inventario) sono escluse dal calcolo. Sulla base dello storico, questo riguarda circa il 3% dei movimenti in entrata. Per un'analisi completa, verificare separatamente i movimenti senza ordine collegato.
- Le ricezioni prive di **Data DDT in** sono escluse. È responsabilità dell'operatore di magazzino compilare questo campo al momento del ricevimento della merce. Un campo vuoto rende la riga invisibile al report, con possibile sottostima dei ritardi.

**Report non conformità:**

- Il riconoscimento delle non conformità basato sulle note del documento (per le causali con "NC solo se note RMA/Reso" attivo) si basa su testo libero inserito dall'operatore. La precisione dipende dalla correttezza e uniformità dei dati storici immessi. Operazioni classificabili come non conformità ma prive delle parole chiave nelle note non compaiono nel report.
- Il report riflette esclusivamente le operazioni già registrate e completate nel sistema. Non rileva non conformità gestite al di fuori di OpenERP.

---

## 7. Domande frequenti

**D: Nel report ritardi compare un valore negativo per un fornitore. È un errore?**

R: No. Un valore negativo indica che la merce è stata consegnata in anticipo rispetto alla data concordata. Ad esempio, -3 significa che la consegna è avvenuta 3 giorni prima della data prevista. Nella media per fornitore, le consegne anticipate compensano parzialmente i ritardi.

---

**D: Ho ricevuto merce da un fornitore ma il picking non compare nel report ritardi. Perché?**

R: Le cause più comuni sono:
- La **Data DDT in** non è stata compilata sulla ricezione. Aprire il documento di ricezione in Magazzino e verificare che il campo sia valorizzato.
- Il picking non è collegato a un ordine di acquisto. In questo caso, il sistema non dispone di una data prevista con cui confrontare la data di arrivo.
- Il picking non è in stato **Completato**. Le ricezioni ancora aperte o annullate non compaiono nel report.

---

**D: Un reso a fornitore non compare nel report non conformità. Perché?**

R: Verificare i seguenti punti:
- La causale associata al picking ha la casella **Non Conformità** spuntata (paragrafo 5.2)?
- Se la causale ha anche la casella **NC solo se note RMA/Reso** attiva, le note del documento di magazzino contengono la parola "RMA" o "Reso" scritta correttamente?
- Il picking è in stato **Completato**?

---

**D: Posso usare il report non conformità per tutte le NC, non solo quelle sui fornitori?**

R: Il modulo è progettato specificamente per le non conformità legate ai fornitori (resi, riparazioni, sostituzioni). Per la gestione completa delle non conformità interne, fare riferimento agli eventuali moduli di gestione qualità presenti nel sistema.

---

**D: Ho aperto il report ritardi e non vedo nessun dato (o vedo pochi fornitori). Perché?**

R: All'apertura il report applica il filtro **Solo fornitori classificati QC**: se nessun fornitore ha ancora la **Classificazione QC fornitore** compilata in anagrafica, l'elenco risulta vuoto. Rimuovere il filtro dalla barra di ricerca per vedere tutti i fornitori, oppure assegnare la classificazione ai fornitori da monitorare (paragrafo 3.5).

---

**D: Posso modificare il calcolo del ritardo per escludere i giorni festivi?**

R: No. Il calcolo attuale si basa sui giorni di calendario (differenza tra le due date), senza considerare il calendario lavorativo aziendale. Se si desidera un calcolo basato sui giorni lavorativi, è necessario richiedere una personalizzazione al fornitore del software.

---

**D: Aggiornare il modulo sovrascrive le causali che ho configurato manualmente?**

R: No. La configurazione iniziale delle causali viene eseguita solo alla prima installazione. I successivi aggiornamenti del modulo non modificano le impostazioni esistenti.

---

**D: Come si ottiene il PDF di questo manuale per allegarlo al dossier di audit?**

R: Il manuale può essere convertito in PDF con lo strumento di generazione documentazione. Contattare l'amministratore del sistema o il fornitore del software per richiedere il file PDF formattato.

---

*Versione modulo: 1.0*
*Aggiornato il: 2026-06-11*
