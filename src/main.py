import os
import pandas as pd

from modelos import Vitima, Cluster, Agente
from alocador import Alocador

def carregar_dados(base_dir):
    grid_str = "75x75"
    vict_str = "410v"
    
    env_path = os.path.join(base_dir, "datasets", "env", f"{grid_str}_{vict_str}", "env_config.txt")
    coordenadas_base = (0, 0)

    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for linha in f:
                if linha.startswith("BASE"):
                    _, coordenadas = linha.split(maxsplit=1)
                    coordenadas_base = tuple(int(v.strip()) for v in coordenadas.split(","))
    
    vitimas_csv = os.path.join(base_dir, "datasets", "map_tri_sobr.csv")
    df = pd.read_csv(vitimas_csv)
    df_v = df[df["id"] != -1]
    
    vitimas = {}
    for _, r in df_v.iterrows():
        v = Vitima(r["id"], r["x_rel"], r["y_rel"], coordenadas_base, r["idade"], r["tri"], r["sobr"])
        vitimas[v.id] = v
    
    clusters_dir = os.path.join(base_dir, "datasets", "clusters")
    clusters = {}
    for nome_arquivo in sorted(os.listdir(clusters_dir)):
        if nome_arquivo.startswith("cluster") and nome_arquivo.endswith(".txt"):
            with open(os.path.join(clusters_dir, nome_arquivo), "r", encoding="utf-8") as f:
                ids = [int(linha.strip()) for linha in f if linha.strip()]
            clusters[nome_arquivo] = Cluster(nome_arquivo, ids, vitimas)
    
    return coordenadas_base, vitimas, clusters

def gerar_resumo_menores_12(clusters):
    resumo = {}
    
    lista_clusters = clusters.values() if isinstance(clusters, dict) else clusters

    for cluster in lista_clusters:
        total = len(cluster.vitimas)
        menores = len(cluster.criancas)
        porcentagem = (menores / total * 100.0) if total > 0 else 0.0
        
        resumo[cluster.nome] = {
            "menores_12": menores,
            "total": total,
            "porcentagem": porcentagem
        }
        print(f"{cluster.nome}: {menores}/{total} ({porcentagem:.1f}%)")
        
    return resumo

def main(base_dir, coordenadas_base, vitimas, clusters):
    agentes = [
        Agente(1),
        Agente(2),
        Agente(3, apenas_adultos=True),
        Agente(4, apenas_adultos=True),
        Agente(5, apenas_adultos=True),
    ]

    Alocador.atribuir_vitimas(clusters, agentes)
    
if __name__ == '__main__':
    src_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(src_dir)
    coordenadas_base, vitimas, clusters = carregar_dados(base_dir)
    
    print(f"Base: {coordenadas_base} / Vitimas carregadas: {len(vitimas)}")
    for nome_cluster, cluster in clusters.items():
        print(f"{nome_cluster}: {len(cluster.vitimas)} vitimas")
        
    print("\n--- Vítimas com idade < 12 por arquivo ---")
    resumo = gerar_resumo_menores_12(clusters)
    
    main(base_dir, coordenadas_base, vitimas, clusters)