class Alocador:
    @staticmethod
    def peso_gravidade(tri):
        pesos = {
            2: 10,
            1: 5,
            0: 2,
            3: 0
        }
        return pesos.get(tri, 0)
    
    @classmethod
    def atribuir_vitimas(cls, clusters, agentes):
        todas_criancas = []
        todos_adultos = []
        
        for cluster in clusters.values():
            todas_criancas.extend(cluster.criancas)
            todos_adultos.extend(cluster.adultos)
            
        todas_criancas.sort(key=lambda v: (cls.peso_gravidade(v.tri), v.sobr), reverse=True)
        todos_adultos.sort(key=lambda v: (cls.peso_gravidade(v.tri), v.sobr), reverse=True)
        
        agentes_criancas = [a for a in agentes if not a.apenas_adultos]
        agentes_adultos = [a for a in agentes if a.apenas_adultos]
        
        for idx, crianca in enumerate(todas_criancas):
            agente_destino = agentes_criancas[idx % len(agentes_criancas)]
            agente_destino.adicionar_vitima(crianca)
        
        todos_agentes = agentes_criancas + agentes_adultos
        
        for adulto in todos_adultos:
            agente_com_menor_carga = min(todos_agentes, key=lambda a: len(a.vitimas_atribuidas))
            agente_com_menor_carga.adicionar_vitima(adulto)
        
        cls._imprimir_resumo(agentes, len(todas_criancas), len(todos_adultos))
    
    @staticmethod
    def _imprimir_resumo(agentes, n_criancas, n_adultos):
        print("\n" + "="*67)
        print(f"ATRIBUIÇÃO FINAL | Total: {n_criancas + n_adultos} (Crianças: {n_criancas}, Adultos: {n_adultos})")
        print("="*67)
        for a in agentes:
            criancas = sum(1 for v in a.vitimas_atribuidas if v.idade < 12)
            adultos = sum(1 for v in a.vitimas_atribuidas if v.idade >= 12)
            vermelho = sum(1 for v in a.vitimas_atribuidas if v.tri == 2)
            amarelo = sum(1 for v in a.vitimas_atribuidas if v.tri == 1)
            verde = sum(1 for v in a.vitimas_atribuidas if v.tri == 0)
            preto = sum(1 for v in a.vitimas_atribuidas if v.tri == 3)
            
            print(f"Agente {a.id} (Apenas Adultos={a.apenas_adultos}): Total={len(a.vitimas_atribuidas):<3} | Crianças={criancas:<2} | Adultos={adultos:<3} | Vermelho={vermelho:<2} Amarelo={amarelo:<2} Verde={verde:<2} Preto={preto:<2}")
        print("="*50 + "\n")