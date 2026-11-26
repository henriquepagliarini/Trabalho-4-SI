import random

class AGCaxeiroViajante:
    def __init__(self, xy_base, vitimas, pop_size=200, generations=500, mutation_rate=0.05, elitism=True):
        self.xy_base = xy_base
        self.vitimas = vitimas
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elitism = elitism
    
    def calcular_distancia_total(self, rota):
        if not rota:
            return 0.0
        
        distancia = rota[0].distancia_para(self.xy_base)
        for i in range(len(rota) - 1):
            distancia += rota[i].distancia_para((rota[i+1].x, rota[i+1].y))
        distancia += rota[-1].distancia_para(self.xy_base)
        
        return distancia
    
    def fitness(self, rota):
        dist = self.calcular_distancia_total(rota)
        return 1.0 / (dist + 1e-6)
    
    def gerar_populacao_inicial(self):
        populacao = []
        
        for _ in range(self.pop_size):
            ind = self.vitimas.copy()
            random.shuffle(ind)
            populacao.append(ind)
            
        return populacao
    
    def crossover_ox(self, pai1, pai2):
        size = len(pai1)
        a, b = sorted(random.sample(range(size), 2))
        
        filho = [None] * size
        filho[a:b+1] = pai1[a:b+1]
        
        pos_atual = (b + 1) % size
        for item in pai2:
            if item not in filho:
                while filho[pos_atual] is not None:
                    pos_atual = (pos_atual + 1) % size
                filho[pos_atual] = item
        return filho
    
    def mutacao_swap(self, ind):
        if random.random() < self.mutation_rate:
            idx1, idx2 = random.sample(range(len(ind)), 2)
            ind[idx1], ind[idx2] = ind[idx2], ind[idx1]
        return ind
        
    def executar(self):
        if len(self.vitimas) <= 1:
            return self.vitimas, self.calcular_distancia_total(self.vitimas)
        
        populacao = self.gerar_populacao_inicial()
        
        for _ in range(self.generations):
            populacao.sort(key=lambda ind: self.fitness(ind), reverse=True)
            nova_populacao = []
            
            if self.elitism:
                nova_populacao.append(populacao[0])
            
            while len(nova_populacao) < self.pop_size:
                pai1 = max(random.sample(populacao, 5), key=self.fitness)
                pai2 = max(random.sample(populacao, 5), key=self.fitness)
                
                filho = self.crossover_ox(pai1, pai2)
                filho = self.mutacao_swap(filho)
                nova_populacao.append(filho)
                
            populacao = nova_populacao
        
        melhor_rota = max(populacao, key=self.fitness)
        melhor_distancia = self.calcular_distancia_total(melhor_rota)
        return melhor_rota, melhor_distancia