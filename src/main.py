import os
import pandas as pd

def carregar_base(env_config_path):
    with open(env_config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("BASE"):
                _, coordenadas = line.split(maxsplit=1)
                x, y = [int(v.strip()) for v in coordenadas.split(",")]
                return x, y
    raise ValueError(f"'BASE' não encontrada em {env_config_path}")

def carregar_vitimas(map_csv_path, coordenadas_base):
    base_x, base_y = coordenadas_base
    df = pd.read_csv(map_csv_path, encoding="utf-8")
    vitimas_df = df[df["id"] != -1].copy()
    
    vitimas = {}
    for _, row in vitimas_df.iterrows():
        v_id = int(row["id"])
        x_rel = int(row["x_rel"])
        y_rel = int(row["y_rel"])
        
        vitimas[v_id] = {
            "id": v_id,
            "x_rel": x_rel,
            "y_rel": y_rel,
            "x": base_x + x_rel,
            "y": base_y + y_rel,
            "idade": int(row["idade"]),
            "tri": int(row["tri"]),
            "sobr": float(row["sobr"])
        }
    return vitimas

def carregar_clusters(clusters_dir):
    clusters = {}
    
    for nome_file in sorted(os.listdir(clusters_dir)):
        path = os.path.join(clusters_dir, nome_file)
        if os.path.isfile(path) and nome_file.startswith("cluster") and nome_file.endswith(".txt"):
            ids = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    linha = line.strip()
                    if linha:
                        ids.append(int(linha))
            clusters[nome_file] = ids
    return clusters

def contar_menores_12(clusters, vitimas):
    resumo = {}
    
    for nome_file, ids in clusters.items():
        total_validos = 0
        menores_12 = 0
        nao_encontrados = 0
        
        for v_id in ids:
            if v_id in vitimas:
                total_validos += 1
                if vitimas[v_id]["idade"] < 12:
                    menores_12 += 1
            else:
                nao_encontrados += 1

        porcentagem = (menores_12 / total_validos * 100.0) if total_validos > 0 else 0.0
        resumo[nome_file] = {
            "menores_12": menores_12,
            "total": total_validos,
            "porcentagem": porcentagem,
            "nao_encontrados": nao_encontrados
        }
    return resumo
    
if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(base_dir)
    
    grid_str = "75x75"
    vict_str = "410v"
    
    base_path = os.path.join(base_dir, "datasets", "env", f"{grid_str}_{vict_str}", "env_config.txt")
    coordenadas_base = carregar_base(base_path)
    
    vitimas_path = os.path.join(base_dir, "datasets", "map_tri_sobr.csv")
    vitimas = carregar_vitimas(vitimas_path, coordenadas_base)
    
    clusters_dir = os.path.join(base_dir, "datasets", "clusters")
    clusters = carregar_clusters(clusters_dir)
    
    print(f"Base: {coordenadas_base} / Vitimas carregadas: {len(vitimas)}")
    for nome, ids in clusters.items():
        print(f"{nome}: {len(ids)} vitimas")
        
    print("\n--- Vítimas com idade < 12 por arquivo ---")
    resumo_idade = contar_menores_12(clusters, vitimas)
    for nome, info in resumo_idade.items():
        extra = (
            f" (sem dados no mapa: {info['nao_encontrados']})"
            if info["nao_encontrados"] > 0
            else ""
        )
        print(
            f"{nome}: {info['menores_12']}/{info['total']}"
            f" ({info['porcentagem']:.1f}%){extra}"
        )