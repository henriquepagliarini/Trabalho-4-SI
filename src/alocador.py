import os
import numpy as np
from algoritmo_genetico import AGCaxeiroViajante


class Alocador:

    @classmethod
    def atribuir_e_sequenciar_vitimas(cls, saida_dir, xy_base, clusters, agentes):
        os.makedirs(saida_dir, exist_ok=True)

        print("\n" + "=" * 75)
        print("=== INICIANDO PROCESSAMENTO DO ALOCADOR (DEBUG) ===")
        print("=" * 75)

        # 1. Separar os agentes por capacidade de atendimento
        agentes_gerais = [a for a in agentes if not a.apenas_adultos]  # Agentes 1 e 2
        agentes_adultos = [a for a in agentes if a.apenas_adultos]    # Agentes 3, 4 e 5

        print(f"[DEBUG] Agentes Gerais (Todas idades): {[a.id for a in agentes_gerais]}")
        print(f"[DEBUG] Agentes Restritos (Apenas Adultos): {[a.id for a in agentes_adultos]}")

        # 2. Função auxiliar para calcular a porcentagem de crianças do cluster
        def pct_criancas(item_cluster):
            _, cluster_obj = item_cluster
            total = len(cluster_obj.vitimas)
            return (len(cluster_obj.criancas) / total) if total > 0 else 0.0

        # 3. Ordenar todos os clusters por % de crianças em ordem decrescente (do maior % para o menor)
        clusters_ordenados_desc = sorted(clusters.items(), key=pct_criancas, reverse=True)

        print("\n--- CLUSTERS ORDENADOS POR PORCENTAGEM DE CRIANÇAS (DECRESCENTE) ---")
        for nome_arq, c_obj in clusters_ordenados_desc:
            tot = len(c_obj.vitimas)
            cri = len(c_obj.criancas)
            pct = pct_criancas((nome_arq, c_obj)) * 100
            print(f" -> {nome_arq}: {cri}/{tot} crianças ({pct:.1f}%)")

        trajetoria_agentes = {a.id: [] for a in agentes}
        criancas_sobrantes = []

        # 4. Agentes 1 e 2 recebem os clusters com MAIOR % de crianças
        num_clusters_gerais = min(len(agentes_gerais), len(clusters_ordenados_desc))
        clusters_para_gerais = clusters_ordenados_desc[:num_clusters_gerais]

        # Os clusters restantes (com MENOS crianças) vão para os Agentes 3, 4 e 5
        clusters_para_adultos = clusters_ordenados_desc[num_clusters_gerais:]
        # Ordenamos os clusters de adultos do menor % para o maior % de crianças
        clusters_para_adultos_asc = sorted(clusters_para_adultos, key=pct_criancas)

        print("\n--- FASE 1: ATRIBUIÇÃO DOS CLUSTERS COM MAIS CRIANÇAS (AGENTES 1 E 2) ---")
        for idx, (nome_arquivo, cluster) in enumerate(clusters_para_gerais):
            agente = agentes_gerais[idx % len(agentes_gerais)]
            tot = len(cluster.vitimas)
            cri = len(cluster.criancas)
            pct = pct_criancas((nome_arquivo, cluster)) * 100
            print(f"[ATRIBUIÇÃO GERAL] [{nome_arquivo}] ({cri}/{tot} crianças - {pct:.1f}%) -> 100% ao Agente {agente.id}")

            ag = AGCaxeiroViajante(xy_base, cluster.vitimas, pop_size=100, generations=250)
            rota_ord, dist = ag.executar()

            trajetoria_agentes[agente.id].extend(rota_ord)
            cls._salvar_arquivo_cluster(saida_dir, nome_arquivo, rota_ord)
            print(f"       └─ AG executado. Distância estimada: {dist:.2f}")

        print("\n--- FASE 1: ATRIBUIÇÃO DOS CLUSTERS COM MENOS CRIANÇAS (AGENTES 3, 4 E 5) ---")
        for nome_arquivo, cluster in clusters_para_adultos_asc:
            # Seleciona o agente restrito a adultos com a menor carga atual de trabalho
            agente = min(agentes_adultos, key=lambda a: len(trajetoria_agentes[a.id]))
            tot = len(cluster.vitimas)
            adu = len(cluster.adultos)
            cri = len(cluster.criancas)
            pct = pct_criancas((nome_arquivo, cluster)) * 100
            print(f"[ATRIBUIÇÃO ADULTOS] [{nome_arquivo}] ({adu} adultos, {cri} crianças - {pct:.1f}%) -> Adultos ao Agente {agente.id}")

            adultos_ord = []
            if cluster.adultos:
                ag_adultos = AGCaxeiroViajante(xy_base, cluster.adultos, pop_size=100, generations=250)
                adultos_ord, dist_a = ag_adultos.executar()
                trajetoria_agentes[agente.id].extend(adultos_ord)
                print(f"       ├─ AG Adultos executado para Agente {agente.id} (Distância: {dist_a:.2f})")

            criancas_ord = []
            if cluster.criancas:
                ag_criancas = AGCaxeiroViajante(xy_base, cluster.criancas, pop_size=100, generations=250)
                criancas_ord, dist_c = ag_criancas.executar()
                criancas_sobrantes.append((nome_arquivo, criancas_ord))
                print(f"       └─ AG Crianças executado para ordenação final do ficheiro (Distância est.: {dist_c:.2f})")

            # Grava no ficheiro original: ADULTOS no início, CRIANÇAS no final
            conteudo_final_cluster = adultos_ord + criancas_ord
            cls._salvar_arquivo_cluster(saida_dir, nome_arquivo, conteudo_final_cluster)
            print(f"       └─ Ficheiro {nome_arquivo} salvo com {len(conteudo_final_cluster)} IDs na ordem de resgate.")

        print("\n--- FASE 2: REDISTRIBUIÇÃO DAS CRIANÇAS REMANESCENTES (AGENTES 1 E 2) ---")
        for nome_arquivo, criancas_list in criancas_sobrantes:
            if criancas_list:
                agente_socorrista = min(agentes_gerais, key=lambda a: len(trajetoria_agentes[a.id]))
                trajetoria_agentes[agente_socorrista.id].extend(criancas_list)
                print(
                    f"[REDISTRIBUIÇÃO] {len(criancas_list)} crianças de [{nome_arquivo}] "
                    f"repassadas ao Agente {agente_socorrista.id} (Nova Carga: {len(trajetoria_agentes[agente_socorrista.id])} v)"
                )

        # Atualiza a lista final de vítimas de cada agente para gerar as métricas da Tabela do Relatório
        for a in agentes:
            a.vitimas_atribuidas = trajetoria_agentes[a.id]

        cls._imprimir_resumo(agentes)

    @staticmethod
    def _salvar_arquivo_cluster(saida_dir, nome_arquivo, lista_vitimas):
        path_txt = os.path.join(saida_dir, nome_arquivo)
        with open(path_txt, "w", encoding="utf-8") as f:
            for v in lista_vitimas:
                f.write(f"{v.id}\n")

    @staticmethod
    def _imprimir_resumo(agentes):
        print("\n" + "=" * 75)
        print("=== RESUMO FINAL DA ATRIBUIÇÃO (DEBUG) ===")
        print("=" * 75)
        for a in agentes:
            criancas = sum(1 for v in a.vitimas_atribuidas if v.idade < 12)
            adultos = sum(1 for v in a.vitimas_atribuidas if v.idade >= 12)
            vermelho = sum(1 for v in a.vitimas_atribuidas if v.tri == 2)
            amarelo = sum(1 for v in a.vitimas_atribuidas if v.tri == 1)
            verde = sum(1 for v in a.vitimas_atribuidas if v.tri == 0)
            preto = sum(1 for v in a.vitimas_atribuidas if v.tri == 3)

            print(
                f"Agente {a.id} (Apenas Adultos={a.apenas_adultos:<5}): "
                f"Total={len(a.vitimas_atribuidas):<3} | Crianças={criancas:<2} | Adultos={adultos:<3} | "
                f"VM={vermelho:<2} AM={amarelo:<2} VD={verde:<2} PR={preto:<2}"
            )
        print("=" * 75 + "\n")