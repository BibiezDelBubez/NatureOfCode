import random

POP_SIZE=50000
TARGET_PHRASE="Viva la e po bon"
PHRASE_LENGTH=len(TARGET_PHRASE)
MUTATION_RATE=0.01
ITERAZIONI = 100

class DNA:
    def __init__(self):
        self.genes = [] #creo una lista vuota di geni
        self.fitness =0.0
        for pos_gene in range(0,PHRASE_LENGTH):
            self.genes.append(chr(random.randint(32,127)))
    def calcolafitness(self):
        self.fitness = 0.0
        self.score=0
        target= list(TARGET_PHRASE)
        for pos in range(PHRASE_LENGTH):
           # print (self.genes[pos] + " " + target[pos])
            if self.genes[pos]==target[pos]:
                self.score +=1
            self.fitness=self.score/PHRASE_LENGTH
        return self.fitness
    def mate (self, partner):
        newDNA = DNA()
        self.midpoint = random.randrange(PHRASE_LENGTH)
        for pos_lettera in range(PHRASE_LENGTH):
            if pos_lettera < self.midpoint:
                newDNA.genes[pos_lettera]=self.genes[pos_lettera]
            else:
                newDNA.genes[pos_lettera]=partner.genes[pos_lettera]
        
        #mutazione
        for pos_lettera in range(PHRASE_LENGTH):
            if random.random() < MUTATION_RATE:
                newDNA.genes[pos_lettera]=chr(random.randint(32,127))
        return newDNA


#creo una popolazione di DNA

popolazione=[]

for numero in range (POP_SIZE):
    genotipo=DNA()
    popolazione.append(genotipo)


for i in range(ITERAZIONI):

    matingpool=[]

    for genotipo in popolazione:
        for contatore in range(int(genotipo.calcolafitness()*100)):
            matingpool.append(genotipo)
        
    #print(len(matingpool))


    for elemento in range(len(popolazione)):
        genotipoM= matingpool[random.randrange(len(matingpool))]
        genotipoF= matingpool[random.randrange(len(matingpool))]
        
        popolazione[elemento]= genotipoF.mate(genotipoM)

    bestfitness=0

    for genotipo in popolazione:
        if int(genotipo.calcolafitness()*100)> bestfitness:
            bestfitness= int( genotipo.calcolafitness()*100)
            print("".join(genotipo.genes))


