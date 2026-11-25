import math

class Vitima:
    def __init__(self, v_id, x_rel, y_rel, coordenadas_base, idade, tri, sobr):
        self.id = int(v_id)
        self.x_rel = int(x_rel)
        self.y_rel = int(y_rel)
        self.x = coordenadas_base[0] + self.x_rel
        self.y = coordenadas_base[1] + self.y_rel
        self.idade = int(idade)
        self.tri = int(tri)
        self.sobr = float(sobr)
        
    def distancia_para(self, outra_coordenada):
        x, y, = outra_coordenada
        return math.hypot(self.x - x, self.y - y)
    
class Cluster:
    def __init__(self, nome, id_vitimas, dataset_vitimas):
        self.nome = nome
        self.vitimas = [dataset_vitimas[v_id] for v_id in id_vitimas if v_id in dataset_vitimas]
    
    @property
    def criancas(self):
        return [v for v in self.vitimas if v.idade < 12]

    @property
    def adultos(self):
        return [v for v in self.vitimas if v.idade >= 12]
    
class Agente:
    def __init__(self, id_agente, apenas_adultos=False):
        self.id = id_agente
        self.apenas_adultos = apenas_adultos
        self.vitimas_atribuidas = []
        self.rota_otimizada = []
        
    def adicionar_vitima(self, vitima):
        if self.apenas_adultos and vitima.idade < 12:
            raise ValueError(f"Agente {self.id} não pode socorrer vítimas menores que 12 anos.")
        self.vitimas_atribuidas.append(vitima)