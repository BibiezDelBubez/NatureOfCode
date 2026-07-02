"""
Questo script usa un algoritmo genetico per risolvere risolve un "Criptaritmo" (o Alfametica) proposto nella rubrica "Il Quesito della Susy" de "La Settimana Enigmistica" (Quesito N. 1021).
Nel Quesito 1021 l'obiettivo è il seguente:

Trovare l'unica combinazione di cifre (da 0 a 9) da assegnare alle lettere in modo che la seguente somma sia esatta:
  TIGRE + 
  LEONE = 
 ------
 TAPIRO

Regole:
1. Ogni lettera corrisponde a una cifra diversa da 0 a 9. Essendoci esattamente 10 lettere uniche (T, I, G, R, E, L, O, N, A, P), cerchiamo una permutazione di 10 elementi.
2. In base alle regole classiche dei criptaritmi, le parole non possono iniziare con la cifra 0 (quindi T != 0 e L != 0).

Come funziona l'Algoritmo Genetico qui applicato:
- DNA (Cromosoma): Una specifica permutazione dei numeri da 0 a 9.
- Fitness: Quanto la somma calcolata (TIGRE + LEONE) si avvicina al risultato atteso (TAPIRO). Meno c'è differenza, più è alta la fitness.
- Crossover (Order Crossover - OX1): Incrociamo i genitori assicurandoci che nel figlio ogni numero da 0 a 9 appaia sempre una sola volta (evitando doppioni e mancanze).
- Mutazione: Scambiamo casualmente due numeri di posto per mantenere la diversità genetica ed evitare minimi locali.
- Selezione e Elitismo: Si prediligono i genitori con fitness migliore (Tournament Selection) e il campione di ogni generazione passa sempre intatto alla successiva.
"""

import random

# --- PARAMETRI DELL'ALGORITMO GENETICO ---
# POP_SIZE: Numero di individui (possibili soluzioni) per ogni generazione.
# Aumentato a 2000 per avere maggiore "diversità genetica" iniziale.
POP_SIZE = 2000 

# MUTATION_RATE: Probabilità che avvenga una mutazione in un figlio.
# Aumentato al 40% (0.4) per evitare che l'algoritmo si blocchi in un "minimo locale"
# (cioè una soluzione quasi perfetta, ma non quella giusta).
MUTATION_RATE = 0.4 

# ITERAZIONI: Quante generazioni vogliamo far scorrere prima di arrenderci.
ITERAZIONI = 500

# TOURNAMENT_SIZE: Quanti individui competono nel "Torneo" per riprodursi.
# Usiamo la "Tournament Selection" invece della "Roulette Wheel" perché
# previene che un individuo "quasi perfetto" si riproduca troppo dominando la popolazione.
TOURNAMENT_SIZE = 5

class DNA:
    def __init__(self, init_random=True):
        self.genes = [] 
        self.fitness = 0.0
        self.diff = -1
        
        # Se init_random è True, creiamo un DNA casuale (per la generazione 0)
        if init_random:
            # Creiamo i numeri da 0 a 9 e li mescoliamo.
            # Questo garantisce che all'inizio non ci siano numeri doppi!
            self.genes = list(range(10))
            random.shuffle(self.genes)
            
    def calcolafitness(self):
        # Mappiamo i numeri (i "geni") alle nostre 10 lettere:
        # Indici: 0:T, 1:I, 2:G, 3:R, 4:E, 5:L, 6:O, 7:N, 8:A, 9:P
        T, I, G, R, E, L, O, N, A, P = self.genes
        
        # Ricostruiamo i numeri completi
        tigre = T*10000 + I*1000 + G*100 + R*10 + E
        leone = L*10000 + E*1000 + O*100 + N*10 + E
        tapiro = T*100000 + A*10000 + P*1000 + I*100 + R*10 + O
        
        # Calcoliamo la distanza dalla soluzione esatta. Se è 0, abbiamo vinto.
        self.diff = abs((tigre + leone) - tapiro)
        
        # Nei criptaritmi seri le parole non possono iniziare con lo zero.
        # Assegniamo una penalità altissima se accade.
        penalty = 0
        if T == 0 or L == 0:
            penalty = 5000000
            
        # FITNESS: Vogliamo che sia alta quando diff è bassa.
        self.fitness = 1000000.0 / (1.0 + self.diff + penalty)
        return self.fitness

    def mate(self, partner):
        newDNA = DNA(init_random=False)
        newDNA.genes = [-1] * 10
        
        # --- ORDER CROSSOVER (OX1) ---
        # Dato che stiamo cercando una PERMUTAZIONE (numeri unici da 0 a 9),
        # non possiamo dividere a metà il DNA come in Hamlet.py, avremmo dei doppioni.
        
        # 1. Prendiamo un "pezzetto" casuale dal genitore 1
        start = random.randint(0, 8)
        end = random.randint(start + 1, 9)
        
        # Copiamo questo pezzetto nel figlio esattamente com'è
        for i in range(start, end + 1):
            newDNA.genes[i] = self.genes[i]
            
        # 2. Riempiamo gli spazi vuoti (-1) prendendo i numeri dal genitore 2.
        # Li prendiamo nell'ordine in cui appaiono, SALTANDO quelli che abbiamo
        # già copiato dal genitore 1 (per evitare doppioni).
        p_idx = 0
        for i in range(10):
            if newDNA.genes[i] == -1: # Se c'è uno spazio vuoto...
                # Cerchiamo il prossimo numero del genitore 2 non ancora usato
                while partner.genes[p_idx] in newDNA.genes:
                    p_idx += 1
                newDNA.genes[i] = partner.genes[p_idx] # Lo inseriamo!
        
        # --- MUTAZIONE ---
        # Con una certa probabilità, scambiamo di posto due geni casuali.
        # Questo serve per esplorare nuove combinazioni ed evitare i minimi locali.
        if random.random() < MUTATION_RATE:
            idx1 = random.randint(0, 9)
            idx2 = random.randint(0, 9)
            # Scambio veloce tipico di Python
            newDNA.genes[idx1], newDNA.genes[idx2] = newDNA.genes[idx2], newDNA.genes[idx1]
            
        return newDNA

# --- FUNZIONE DI SELEZIONE: TOURNAMENT SELECTION ---
# Invece della Roulette, scegliamo casualmente N individui e vince il migliore.
# Questo mantiene alta la pressione selettiva ma evita che il migliore in assoluto
# si accoppi col 90% della popolazione distruggendo la diversità.
def tournament_selection(popolazione):
    # Scegliamo un gruppetto a caso
    torneo = random.sample(popolazione, TOURNAMENT_SIZE)
    # Restituiamo quello con la fitness più alta nel gruppetto
    migliore = max(torneo, key=lambda dna: dna.fitness)
    return migliore

# 1. Creiamo la popolazione iniziale (Generazione 0)
popolazione = []
for _ in range(POP_SIZE):
    popolazione.append(DNA())

# 2. Ciclo generazionale
stasi_counter = 0
last_best_diff = float('inf')

for i in range(ITERAZIONI):
    
    # Calcoliamo la fitness di tutti
    for genotipo in popolazione:
        genotipo.calcolafitness()
        
    # Ordiniamo la popolazione dal migliore (diff più bassa) al peggiore
    popolazione.sort(key=lambda x: x.diff)
    
    # Il migliore in assoluto di questa generazione è il primo della lista
    best_genotipo = popolazione[0]
    best_diff = best_genotipo.diff

    # --- MECCANISMO ANTISTALLO (CATACLISMA) ---
    if best_diff == last_best_diff:
        stasi_counter += 1
    else:
        stasi_counter = 0
        last_best_diff = best_diff
        
    if stasi_counter > 30:
        # Se siamo bloccati da 30 generazioni sullo stesso risultato, sostituiamo
        # il 90% della popolazione con individui generati completamente a caso (salvando l'élite).
        # Questo reset "terremoto" ci sblocca dai minimi locali e inietta sangue fresco.
        if i % 10 != 0: # Evitiamo di stampare troppo testo
            print(f"Generazione {i:3} | !!! STALLO RILEVATO !!! Genero nuove combinazioni casuali...")
        for j in range(1, int(POP_SIZE * 0.9)):
            popolazione[j] = DNA(init_random=True)
        stasi_counter = 0
        
        # Ricalcoliamo e riordiniamo
        for genotipo in popolazione:
            genotipo.calcolafitness()
        popolazione.sort(key=lambda x: x.diff)
        best_genotipo = popolazione[0]
        best_diff = best_genotipo.diff

    # Ogni 10 generazioni stampiamo a che punto siamo
    if i % 10 == 0:
        T, I, G, R, E, L, O, N, A, P = best_genotipo.genes
        print(f"Generazione {i:3} | Migliore diff: {best_diff:6} | TIGRE+LEONE={T}{I}{G}{R}{E}+{L}{E}{O}{N}{E} TAPIRO={T}{A}{P}{I}{R}{O}")
        
    # SE ABBIAMO TROVATO LA SOLUZIONE (Differenza 0)
    if best_diff == 0:
        print("\n*** SOLUZIONE TROVATA! ***")
        T, I, G, R, E, L, O, N, A, P = best_genotipo.genes
        print(f"Lettere: T={T}, I={I}, G={G}, R={R}, E={E}, L={L}, O={O}, N={N}, A={A}, P={P}")
        print(f"  {T}{I}{G}{R}{E} +")
        print(f"  {L}{E}{O}{N}{E} =")
        print(f" {T}{A}{P}{I}{R}{O}")
        break

    nuova_popolazione = []
    
    # --- ELITISMO ---
    # Per non "perdere" accidentalmente il miglior individuo (a causa di crossover o mutazioni),
    # copiamo il migliore in assoluto direttamente nella nuova generazione senza toccarlo.
    nuova_popolazione.append(best_genotipo)
    
    # Creiamo il resto dei figli per rimpiazzare la vecchia popolazione
    for _ in range(POP_SIZE - 1): # -1 perché uno spazio è per l'élite
        # Selezioniamo due genitori col Torneo
        genitore1 = tournament_selection(popolazione)
        genitore2 = tournament_selection(popolazione)
        
        # Facciamo nascere il figlio e lo aggiungiamo
        figlio = genitore1.mate(genitore2)
        nuova_popolazione.append(figlio)
        
    # La nuova generazione prende il posto della vecchia
    popolazione = nuova_popolazione
