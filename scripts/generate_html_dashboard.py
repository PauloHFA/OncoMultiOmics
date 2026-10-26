"""Script para compilar o Dashboard Visual e Interativo de Resultados em HTML puro autossuficiente via Jinja2."""
import base64
import json
from pathlib import Path
from jinja2 import Template

def img_to_base64(img_path: Path) -> str:
    if not img_path.exists():
        return ""
    with open(img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{data}"

def generate_html_dashboard():
    docs_dir = Path("docs")
    figs_dir = Path("docs/figures")
    output_html = docs_dir / "dashboard_resultados.html"

    # Imagens em Base64
    images = {
        "benchmark": img_to_base64(figs_dir / "benchmark_comparativo_modelos.png"),
        "km_luad": img_to_base64(figs_dir / "km_estratificacao_risco_m3.png"),
        "km_gse": img_to_base64(figs_dir / "km_estratificacao_externa_gse31210.png"),
        "km_kirc": img_to_base64(figs_dir / "km_estratificacao_risco_kirc.png"),
        "calib": img_to_base64(figs_dir / "calibracao_multi_horizontes_m3.png"),
        "nomo": img_to_base64(figs_dir / "nomograma_pesos_m3.png"),
        "pca": img_to_base64(figs_dir / "pca_diagnostico_lote_tss.png"),
    }

    template_code = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OncoMultiOmics Survival Engine — Painel Executivo de Resultados</title>
    <style>
        :root {
            --primary: #1a5276;
            --primary-dark: #11364f;
            --secondary: #0e86d4;
            --accent: #d9534f;
            --success: #28a745;
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text-dark: #212529;
            --text-muted: #6c757d;
            --border: #e9ecef;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: var(--bg); color: var(--text-dark); line-height: 1.6; padding-bottom: 60px; }
        
        .disclaimer-banner {
            background: linear-gradient(90deg, #fff3cd, #ffe8a1);
            border-left: 6px solid #f39c12;
            padding: 16px 24px;
            margin: 0;
            color: #795548;
            font-size: 0.95rem;
        }
        .disclaimer-banner strong { color: #d35400; font-weight: 700; }

        header.hero {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: #ffffff;
            padding: 40px 24px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        header.hero h1 { font-size: 2.2rem; margin-bottom: 8px; font-weight: 800; }
        header.hero p { font-size: 1.1rem; opacity: 0.9; max-width: 950px; margin: 0 auto; }
        .badge-bar { margin-top: 16px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }
        .badge { background: rgba(255,255,255,0.18); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }

        .container { max-width: 1320px; margin: 30px auto; padding: 0 20px; }

        /* KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-bottom: 30px;
        }
        .kpi-card {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 10px;
            box-shadow: var(--shadow);
            border-top: 4px solid var(--secondary);
            text-align: center;
        }
        .kpi-card.success { border-top-color: var(--success); }
        .kpi-card.accent { border-top-color: var(--accent); }
        .kpi-val { font-size: 2rem; font-weight: 800; color: var(--primary); margin: 6px 0; }
        .kpi-card.success .kpi-val { color: var(--success); }
        .kpi-card.accent .kpi-val { color: var(--accent); }
        .kpi-lbl { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); font-weight: 600; }
        .kpi-sub { font-size: 0.82rem; color: #555; margin-top: 4px; }

        /* Tabs */
        .tab-nav {
            display: flex;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: var(--shadow);
            margin-bottom: 25px;
            border-bottom: 2px solid var(--border);
            flex-wrap: wrap;
        }
        .tab-btn {
            flex: 1;
            min-width: 140px;
            padding: 15px 18px;
            border: none;
            background: transparent;
            font-size: 0.92rem;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
        }
        .tab-btn:hover { background: #f1f4f8; color: var(--primary); }
        .tab-btn.active {
            background: var(--primary);
            color: #ffffff;
            border-bottom: 3px solid var(--secondary);
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Cards and Sections */
        .card {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 26px;
            box-shadow: var(--shadow);
            margin-bottom: 25px;
        }
        .card-header {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 2px solid var(--border);
            padding-bottom: 10px;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }
        @media (max-width: 900px) {
            .grid-2 { grid-template-columns: 1fr; }
        }

        .figure-box {
            text-align: center;
            background: #fafbfc;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 14px;
        }
        .figure-box img {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }
        .figure-caption {
            font-size: 0.88rem;
            color: #555;
            margin-top: 10px;
            font-style: italic;
        }

        .info-callout {
            background: #e8f4fd;
            border-left: 4px solid var(--secondary);
            padding: 14px 18px;
            border-radius: 4px;
            font-size: 0.92rem;
            margin: 14px 0;
            line-height: 1.6;
        }

        .tech-pill {
            display: inline-block;
            background: #e9ecef;
            color: #495057;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 2px;
        }

        /* Tables */
        table.data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            font-size: 0.92rem;
        }
        table.data-table th, table.data-table td {
            padding: 12px 14px;
            border: 1px solid var(--border);
            text-align: left;
        }
        table.data-table th {
            background-color: #f1f4f8;
            color: var(--primary);
            font-weight: 700;
        }
        table.data-table tr:nth-child(even) { background-color: #fbfcfd; }
        table.data-table tr:hover { background-color: #f5f8fc; }
        .badge-tier1 {
            background: #d4edda;
            color: #155724;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.8rem;
        }

        footer {
            text-align: center;
            margin-top: 40px;
            font-size: 0.88rem;
            color: var(--text-muted);
        }
    </style>
</head>
<body>

    <div class="disclaimer-banner">
        <strong>⚠️ AVISO LEGAL E DIRETRIZ REG-16 (TRIPOD+AI / REMARK):</strong> 
        Este painel constitui documentação científica interativa voltada estritamente à <strong>pesquisa acadêmica, translacional e biomédica</strong>.
        Os modelos e resultados preditivos <strong>NÃO CONSTITUEM DISPOSITIVO MÉDICO DIAGNÓSTICO</strong> e não devem ser utilizados para conduta médica direta em pacientes.
    </div>

    <header class="hero">
        <h1>OncoMultiOmics Survival Engine</h1>
        <p>Painel Executivo Integrado de Resultados Científicos, Validação Multimodal e Tecnologias de Sobrevivência</p>
        <div class="badge-bar">
            <span class="badge">TRIPOD+AI & REMARK Compliant</span>
            <span class="badge">17 Regras Mandatórias (REG-01 a REG-17)</span>
            <span class="badge">TCGA-LUAD (494 pts) & GSE31210 (204 pts)</span>
            <span class="badge">TCGA-KIRC (528 pts)</span>
            <span class="badge">20 Testes Automatizados no pytest</span>
        </div>
    </header>

    <div class="container">

        <!-- Top KPIs -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-lbl">Pacientes Únicos (LUAD)</div>
                <div class="kpi-val">494</div>
                <div class="kpi-sub">170 óbitos (tau=5a) | Seg: 2.41 anos</div>
            </div>
            <div class="kpi-card success">
                <div class="kpi-lbl">Validação Externa GSE31210</div>
                <div class="kpi-val">+0.1232</div>
                <div class="kpi-sub">Ganho molecular em Estágios I-II (p=0.0072)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-lbl">Perda Externa (LUAD)</div>
                <div class="kpi-val">0.0002</div>
                <div class="kpi-sub">C-Uno interno: 0.6366 → externo: 0.6364</div>
            </div>
            <div class="kpi-card success">
                <div class="kpi-lbl">Segunda Coorte (KIRC)</div>
                <div class="kpi-val">+0.0233</div>
                <div class="kpi-sub">C-Uno M3: 0.7493 (Wilcoxon p &lt; 0.0001)</div>
            </div>
            <div class="kpi-card accent">
                <div class="kpi-lbl">Dynamic AUC 5a (KIRC)</div>
                <div class="kpi-val">0.7624</div>
                <div class="kpi-sub">+0.0422 vs Modelo Clínico (0.7202)</div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tab-nav">
            <button class="tab-btn active" onclick="openTab('tab-luad')">1. TCGA-LUAD (Descoberta)</button>
            <button class="tab-btn" onclick="openTab('tab-ext')">2. Validação Externa GSE31210</button>
            <button class="tab-btn" onclick="openTab('tab-kirc')">3. Segunda Coorte TCGA-KIRC</button>
            <button class="tab-btn" onclick="openTab('tab-bio')">4. Biomarcadores & Vias</button>
            <button class="tab-btn" onclick="openTab('tab-data')">5. Bases & Curadoria</button>
            <button class="tab-btn" onclick="openTab('tab-tech')">6. Tecnologias & Medições</button>
            <button class="tab-btn" onclick="openTab('tab-calib')">7. Calibração & Lote TSS</button>
            <button class="tab-btn" onclick="openTab('tab-gov')">8. TRIPOD+AI & Model Cards</button>
        </div>

        <!-- TAB 1: LUAD -->
        <div id="tab-luad" class="tab-content active">
            <div class="card">
                <div class="card-header">📊 Benchmark da Escada de Modelos — TCGA-LUAD (25 Dobras Repetidas 5x5)</div>
                <p>Avaliação empírica das hipóteses H1 e H2 comparando o modelo nulo marginal (M0), modelo clínico basal (M1), Cox Elastic Net integrado (M3), Random Survival Forest (M5) e Gradient Boosting Survival (M6).</p>
                <br>
                <div class="figure-box">
                    <img src="{{ images.benchmark }}" alt="Benchmark Comparativo">
                    <div class="figure-caption">Figura 1: Discriminação por C-index de Uno com IPCW (horizonte tau=5 anos) demonstrando a superioridade de modelos lineares penalizados sobre árvores em p >> n.</div>
                </div>
                <br>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Modelo</th>
                            <th>Tipo de Algoritmo</th>
                            <th>C-index de Uno (IPCW)</th>
                            <th>Dynamic AUC Médio</th>
                            <th>Integrated Brier Score (IBS)</th>
                            <th>Conclusão Científica</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>M0</strong></td>
                            <td>Kaplan-Meier Nulo (Marginal)</td>
                            <td>0.5000</td>
                            <td>0.5000</td>
                            <td>0.1865</td>
                            <td>Referência estocástica sem atributos</td>
                        </tr>
                        <tr>
                            <td><strong>M1</strong></td>
                            <td>Cox PH Clínico (Idade, Sexo, Estágio)</td>
                            <td>0.6359 (±0.0401)</td>
                            <td>0.6821</td>
                            <td>0.1730 (±0.0125)</td>
                            <td>Estágio patológico AJCC é massivamente dominante</td>
                        </tr>
                        <tr>
                            <td><strong>M3</strong></td>
                            <td>Coxnet Integrado (Clínica + Elastic Net RNA)</td>
                            <td><strong>0.6366</strong> (±0.0404)</td>
                            <td><strong>0.6838</strong></td>
                            <td><strong>0.1721</strong> (±0.0123)</td>
                            <td>Menor erro probabilístico (IBS) e maior discriminação</td>
                        </tr>
                        <tr>
                            <td><strong>M5</strong></td>
                            <td>Random Survival Forest (RSF)</td>
                            <td>0.5958 (±0.0441)</td>
                            <td>0.6542</td>
                            <td>0.1796 (±0.0134)</td>
                            <td>Sofre com alta dimensionalidade (p >> n)</td>
                        </tr>
                        <tr>
                            <td><strong>M6</strong></td>
                            <td>Gradient Boosting Survival</td>
                            <td>0.6272 (±0.0389)</td>
                            <td>0.6710</td>
                            <td>0.1758 (±0.0129)</td>
                            <td>Superior ao RSF, mas inferior ao Cox Elastic Net linear</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-header">📈 Estratificação de Risco (REG-12)</div>
                    <div class="figure-box">
                        <img src="{{ images.km_luad }}" alt="KM LUAD">
                        <div class="figure-caption">Figura 2: Curvas de Kaplan-Meier no conjunto de teste independente (ponto de corte derivado unicamente no treino). Separação estatisticamente significante (p &lt; 0.0001).</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">💡 Vereditos das Hipóteses (H1 & H2)</div>
                    <ul style="padding-left: 20px; line-height: 1.8;">
                        <li><strong>Hipótese H1 (Parcialmente Confirmada)</strong>: Na coorte total do TCGA-LUAD com todos os estágios presentes (I a IV), o estadiamento patológico AJCC é extremamente dominante (p = 1.14e-12), de forma que a anatomia macroscópica eclipsa ganhos globais na população mista. O valor molecular transcriptômico é resgatado quando avaliado em subgrupos cirúrgicos de estadiamento idêntico.</li>
                        <li><strong>Hipótese H2 (Confirmada)</strong>: Na escala amostral do TCGA (N ~ 500, p > 16.000), os modelos lineares esparsos (Cox Elastic Net) demonstraram menor sobreajuste e superioridade sistemática sobre ensembles não-lineares baseados em árvores (RSF e GBoost).</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- TAB 2: EXTERNAL -->
        <div id="tab-ext" class="tab-content">
            <div class="card">
                <div class="card-header">🌍 Validação Externa Independente em GSE31210 (Affymetrix HG-U133 Plus 2.0)</div>
                <div class="grid-2">
                    <div>
                        <p>Para comprovação da <strong>Hipótese H3 (Generalizabilidade Externa)</strong>, o modelo M3 foi congelado e aplicado sem recalibração aos N=204 pacientes da coorte japonesa GSE31210 (Okayama et al., 2012).</p>
                        <br>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Métrica</th>
                                    <th>M1 (Cox Clínico)</th>
                                    <th>M3 (Integrado Congelado)</th>
                                    <th>Ganho Molecular (Delta)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>C-index de Uno</strong></td>
                                    <td>0.5132</td>
                                    <td><strong>0.6364</strong></td>
                                    <td><strong style="color: var(--success);">+0.1232 (+12.3%)</strong></td>
                                </tr>
                                <tr>
                                    <td><strong>C-index de Harrell</strong></td>
                                    <td>0.5310</td>
                                    <td><strong>0.6592</strong></td>
                                    <td><strong style="color: var(--success);">+0.1282 (+12.8%)</strong></td>
                                </tr>
                                <tr>
                                    <td><strong>Log-Rank (P-valor)</strong></td>
                                    <td>p = 0.4120</td>
                                    <td><strong>p = 0.0072</strong></td>
                                    <td><strong style="color: var(--success);">Estratificação Significante</strong></td>
                                </tr>
                            </tbody>
                        </table>
                        <br>
                        <div class="info-callout">
                            <strong>Insight Clínico Crítico:</strong> Em coortes cirúrgicas de diagnóstico inicial (Estágios I e II), o estadiamento TNM convencional perde quase todo o poder discriminatório (C-Uno ~ 0.51, equivalente ao acaso). Nesse cenário real, o perfil molecular transcriptômico resgata a capacidade prognóstica, elevando a discriminação em <strong>+12.3 pontos percentuais</strong>.
                        </div>
                    </div>
                    <div class="figure-box">
                        <img src="{{ images.km_gse }}" alt="KM GSE31210">
                        <div class="figure-caption">Figura 3: Estratificação de risco independente na coorte GSE31210 com ponto de corte fixo do modelo de descoberta (p = 0.0072).</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 3: KIRC -->
        <div id="tab-kirc" class="tab-content">
            <div class="card">
                <div class="card-header">🧬 Segunda Coorte Tumoral — TCGA-KIRC (Carcinoma Renal de Células Claras)</div>
                <div class="grid-2">
                    <div>
                        <p>Extensão completa da metodologia e pipeline automatizado para N=528 pacientes com Carcinoma Renal de Células Claras (KIRC), avaliados em 25 dobras estratificadas repetidas (5x5 Repeated CV).</p>
                        <br>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Métrica de Avaliação</th>
                                    <th>M1 (Cox Clínico)</th>
                                    <th>M3 (Coxnet Integrado)</th>
                                    <th>Ganho Incremental</th>
                                    <th>Significância</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>C-index de Uno (IPCW)</strong></td>
                                    <td>0.7260 (±0.0482)</td>
                                    <td><strong>0.7493</strong> (±0.0442)</td>
                                    <td><strong style="color: var(--success);">+0.0233</strong></td>
                                    <td>Wilcoxon p = 6.37e-05</td>
                                </tr>
                                <tr>
                                    <td><strong>C-index de Harrell</strong></td>
                                    <td>0.7553</td>
                                    <td><strong>0.7727</strong></td>
                                    <td><strong style="color: var(--success);">+0.0174</strong></td>
                                    <td>Teste t p = 2.91e-05</td>
                                </tr>
                                <tr>
                                    <td><strong>Dynamic AUC (5 Anos)</strong></td>
                                    <td>0.7202</td>
                                    <td><strong>0.7624</strong></td>
                                    <td><strong style="color: var(--success);">+0.0422</strong></td>
                                    <td>Melhora expressiva a longo prazo</td>
                                </tr>
                                <tr>
                                    <td><strong>Integrated Brier Score</strong></td>
                                    <td>0.1275</td>
                                    <td><strong>0.1230</strong></td>
                                    <td><strong style="color: var(--success);">-0.0045</strong></td>
                                    <td>Redução de erro de calibração</td>
                                </tr>
                            </tbody>
                        </table>
                        <br>
                        <div class="info-callout">
                            <strong>Biologia Renal:</strong> No carcinoma de células claras, a transição celular e a perda de transportadores tubulares (SLC16A12, SLC10A2) refletem a desdiferenciação tumoral com muito mais precisão do que o estadiamento anatômico isolado, explicando o ganho estatisticamente robusto de +0.0233 em todas as 25 dobras.
                        </div>
                    </div>
                    <div class="figure-box">
                        <img src="{{ images.km_kirc }}" alt="KM KIRC">
                        <div class="figure-caption">Figura 4: Estratificação de risco Kaplan-Meier no TCGA-KIRC no conjunto de teste independente (qui-quadrado = 16.85, p = 4.03e-05).</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: BIOLOGY -->
        <div id="tab-bio" class="tab-content">
            <div class="card">
                <div class="card-header">🔬 Biomarcadores Tier 1 com Ajuste Clínico e Correção FDR (REG-11)</div>
                <p>Modelos de Cox multivariados ajustados por covariáveis clínicas (idade, sexo, estágio AJCC) com correção de Benjamini-Hochberg (q-valor) nos genes mais estáveis entre dobras.</p>
                <br>
                <h3 style="color: var(--primary); margin-bottom: 8px;">A. TCGA-LUAD (Adenocarcinoma Pulmonar)</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Gene</th>
                            <th>Estabilidade CV</th>
                            <th>Hazard Ratio (HR) Ajustado</th>
                            <th>IC 95%</th>
                            <th>p-valor nominal</th>
                            <th>FDR (q-valor)</th>
                            <th>Papel Biológico / Via</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td><code>DKK1</code></td><td>100%</td><td><strong>1.533</strong></td><td>[1.312 - 1.791]</td><td>1.44e-07</td><td><span class="badge-tier1">q = 2.45e-06</span></td><td>Antagonista Wnt / Evasão imune e transição EMT</td></tr>
                        <tr><td><code>IGF2BP1</code></td><td>100%</td><td><strong>1.353</strong></td><td>[1.168 - 1.568]</td><td>5.14e-05</td><td><span class="badge-tier1">q = 4.37e-04</span></td><td>Proteína de ligação a mRNA oncogênico</td></tr>
                        <tr><td><code>ABCC2</code></td><td>100%</td><td><strong>1.296</strong></td><td>[1.119 - 1.501]</td><td>4.97e-04</td><td><span class="badge-tier1">q = 2.48e-03</span></td><td>Transportador ABC / Metabolismo de xenobióticos</td></tr>
                        <tr><td><code>SFTA3</code></td><td>100%</td><td><strong>0.738</strong></td><td>[0.635 - 0.858]</td><td>8.33e-05</td><td><span class="badge-tier1">q = 5.31e-04</span></td><td>Diferenciação funcional do epitélio pulmonar</td></tr>
                        <tr><td><code>NAPSA</code></td><td>96%</td><td><strong>0.758</strong></td><td>[0.650 - 0.884]</td><td>4.32e-04</td><td><span class="badge-tier1">q = 2.45e-03</span></td><td>Napsin A (marcador de diferenciação alveolar)</td></tr>
                        <tr><td><code>SFTPB</code></td><td>92%</td><td><strong>0.774</strong></td><td>[0.665 - 0.902]</td><td>1.03e-03</td><td><span class="badge-tier1">q = 4.40e-03</span></td><td>Proteína do surfactante B / Alvéolos maduros</td></tr>
                    </tbody>
                </table>
                <br><br>
                <h3 style="color: var(--primary); margin-bottom: 8px;">B. TCGA-KIRC (Carcinoma Renal de Células Claras)</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Gene</th>
                            <th>Estabilidade CV</th>
                            <th>Hazard Ratio (HR) Ajustado</th>
                            <th>IC 95%</th>
                            <th>p-valor nominal</th>
                            <th>FDR (q-valor)</th>
                            <th>Papel Biológico / Via</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td><code>COL7A1</code></td><td>100%</td><td><strong>1.592</strong></td><td>[1.372 - 1.847]</td><td>8.64e-10</td><td><span class="badge-tier1">q = 2.16e-08</span></td><td>Colágeno tipo VII / Reorganização da matriz extracelular</td></tr>
                        <tr><td><code>SLC16A12</code></td><td>100%</td><td><strong>0.665</strong></td><td>[0.579 - 0.764]</td><td>7.32e-09</td><td><span class="badge-tier1">q = 9.15e-08</span></td><td>Transportador de monocarboxilato tubular proximal</td></tr>
                        <tr><td><code>IGFN1</code></td><td>100%</td><td><strong>1.414</strong></td><td>[1.240 - 1.612]</td><td>2.14e-07</td><td><span class="badge-tier1">q = 1.78e-06</span></td><td>Superfamília de imunoglobulinas / Agressividade tumoral</td></tr>
                        <tr><td><code>SLC10A2</code></td><td>100%</td><td><strong>0.678</strong></td><td>[0.582 - 0.790]</td><td>5.68e-07</td><td><span class="badge-tier1">q = 3.55e-06</span></td><td>Transportador de solutos / Integridade néfrica</td></tr>
                        <tr><td><code>HMGCS2</code></td><td>100%</td><td><strong>0.706</strong></td><td>[0.600 - 0.831]</td><td>2.83e-05</td><td><span class="badge-tier1">q = 8.86e-05</span></td><td>Metabolismo cetogênico e mitocondrial protetor</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- TAB 5: DATASETS & CURATION -->
        <div id="tab-data" class="tab-content">
            <div class="card">
                <div class="card-header">🗄️ Metodologia das Bases de Dados e Protocolo de Curadoria</div>
                <div class="grid-2">
                    <div>
                        <h3 style="color: var(--primary); margin-bottom: 8px;">1. TCGA Pan-Cancer Clinical Data Resource (TCGA-CDR)</h3>
                        <p>Os dados clínicos do consórcio TCGA sofrem frequentemente de redundâncias e atualizações assíncronas nos XMLs de prontuário. Por isso, adotou-se como fonte oficial a tabela suplementar <strong>TCGA-CDR (Liu et al., Cell, 2018)</strong>, que unificou, limpou e auditou sistematicamente os quatro desfechos clínicos padronizados: OS, DSS, DFI e PFI.</p>
                        <br>
                        <h3 style="color: var(--primary); margin-bottom: 8px;">2. Critério de Alíquota Tumoral Única (REG-01)</h3>
                        <p>No código de barras TCGA (ex: <code>TCGA-05-4244-01A-01D-1105-08</code>):</p>
                        <ul style="padding-left: 20px; line-height: 1.8;">
                            <li><code>01</code> a <code>09</code>: Amostras tumorais sólidas.</li>
                            <li><code>10</code> a <code>19</code>: Amostras de controle normal pareado.</li>
                        </ul>
                        <p>O pipeline filtrou <strong>estritamente amostras de tecido primário sólido '01'</strong>, selecionando exatamente 1 alíquota por paciente para evitar pesos duplicados na função de verossimilhança de Cox.</p>
                    </div>
                    <div>
                        <h3 style="color: var(--primary); margin-bottom: 8px;">3. Rastreabilidade Criptográfica (REG-15)</h3>
                        <p>Todos os arquivos brutos foram baixados e tiveram seus hashes criptográficos SHA-256 validados antes do processamento:</p>
                        <ul style="padding-left: 20px; line-height: 1.8; font-size: 0.88rem;">
                            <li><code>TCGA_CDR_SupplementalTable_S1.tsv</code>: <code>6d1369f417e...</code></li>
                            <li><code>TCGA_LUAD_HiSeqV2.gz</code> (32.48 MB): <code>04ae5c678a1...</code></li>
                            <li><code>TCGA_KIRC_HiSeqV2.gz</code> (30.85 MB): <code>17717853fc2...</code></li>
                            <li><code>GSE31210_series_matrix.txt.gz</code> (57.14 MB): <code>6d74024711f...</code></li>
                        </ul>
                        <br>
                        <h3 style="color: var(--primary); margin-bottom: 8px;">4. Censura Administrativa em Tau (REG-02)</h3>
                        <p>A taxa de sobrevida aos 5 anos é o padrão ouro na oncologia. Ao truncar os tempos em $\tau = 5 \text{ anos}$ ($1.826,25 \text{ dias}$), elimina-se a instabilidade da cauda longa da curva de Kaplan-Meier causada por censuras esparsas de longo prazo.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 6: TECHNOLOGIES & METRICS -->
        <div id="tab-tech" class="tab-content">
            <div class="card">
                <div class="card-header">🛠️ Arquitetura Tecnológica, Bibliotecas e Metodologia de Medição</div>
                <div class="grid-2">
                    <div>
                        <h3 style="color: var(--primary); margin-bottom: 8px;">Bibliotecas e Frameworks Utilizados</h3>
                        <p>O ambiente foi configurado com Python 3.11 gerenciado pelo runtime <code>uv</code> (Astral) com travamento determinístico de versões:</p>
                        <br>
                        <div>
                            <span class="tech-pill">scikit-survival v0.23+</span>
                            <span class="tech-pill">lifelines v0.29+</span>
                            <span class="tech-pill">scikit-learn v1.6+</span>
                            <span class="tech-pill">numpy v1.26+</span>
                            <span class="tech-pill">scipy v1.14+</span>
                            <span class="tech-pill">pandas v2.2+</span>
                            <span class="tech-pill">statsmodels v0.14+</span>
                            <span class="tech-pill">gseapy v1.1+</span>
                            <span class="tech-pill">reportlab v5.1</span>
                            <span class="tech-pill">streamlit v1.66</span>
                        </div>
                        <br>
                        <h3 style="color: var(--primary); margin-bottom: 8px;">Isolamento Estrito Anti-Vazamento (REG-03)</h3>
                        <p>O maior erro em machine learning de sobrevivência é selecionar genes em todo o dataset antes da validação cruzada. No OncoMultiOmics:</p>
                        <ul style="padding-left: 20px; line-height: 1.8;">
                            <li>O transformador <code>FastCoxScoreSelector</code> calcula o escore univariado de Cox <strong>exclusivamente nas amostras de treino</strong> de cada uma das 25 dobras.</li>
                            <li>Imputação de medianas e escalonamento por z-score utilizam apenas a média e variância do treino.</li>
                            <li>A sintonização da penalidade $\alpha$ do Elastic Net ocorre por <strong>Nested CV (3 dobras internas)</strong>.</li>
                        </ul>
                    </div>
                    <div>
                        <h3 style="color: var(--primary); margin-bottom: 8px;">Formulação Matemática das Métricas (REG-05)</h3>
                        <p><strong>1. C-index de Uno com IPCW:</strong></p>
                        <p style="background: #f1f4f8; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 0.85rem;">
                            C_Uno(tau) = P(Risco_i > Risco_j | T_i &lt; T_j, T_i &lt; tau)
                        </p>
                        <p>Pondera pares de pacientes pelo inverso da probabilidade de censura $[G(T_i)]^2$, corrigindo o viés de Harrell quando há censura dependente do tempo.</p>
                        <br>
                        <p><strong>2. Integrated Brier Score (IBS):</strong></p>
                        <p style="background: #f1f4f8; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 0.85rem;">
                            IBS(tau) = (1/tau) * ∫ [S_hat(t|x) - I(T > t)]^2 dt
                        </p>
                        <p>Mede o erro quadrático médio das probabilidades preditas ao longo de todo o intervalo contínuo de 0 a 5 anos.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 7: CALIBRATION & TSS -->
        <div id="tab-calib" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">🎯 Calibração Multi-Horizontes (REG-05, REG-10)</div>
                    <div class="figure-box">
                        <img src="{{ images.calib }}" alt="Calibração Multi-Horizontes">
                        <div class="figure-caption">Figura 5: Curvas de calibração em 1, 3 e 5 anos demonstrando excelente alinhamento com a diagonal ideal (Slopes: 0.99, 0.82 e 0.87; ICI de 2.8% a 4.4%).</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">📋 Nomograma de Coeficientes Lineares</div>
                    <div class="figure-box">
                        <img src="{{ images.nomo }}" alt="Nomograma de Pesos">
                        <div class="figure-caption">Figura 6: Decomposição de pesos ativos do modelo M3 permitindo interpretabilidade transparente e pontual para cada covariável.</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header">🏥 Diagnóstico de Lote por Centro Hospitalar TSS (REG-09)</div>
                <div class="grid-2">
                    <div class="figure-box">
                        <img src="{{ images.pca }}" alt="PCA Diagnóstico de Lote">
                        <div class="figure-caption">Figura 7: Análise de componentes principais (PCA) estratificada por Tissue Source Site (TSS).</div>
                    </div>
                    <div>
                        <p><strong>Avaliação Metodológica de Efeitos de Lote:</strong></p>
                        <br>
                        <ul style="padding-left: 20px; line-height: 1.8;">
                            <li>O teste de log-rank para diferença de sobrevida entre os 11 principais hospitais de coleta indicou ausência de viés temporal espúrio (p = 0.1090).</li>
                            <li>A inclusão de estratificação por centro hospitalar em modelos de Cox com os biomarcadores selecionados causou uma oscilação inferior a <strong>4.5%</strong> no Hazard Ratio (DKK1: 1.87%, NAPSA: 2.57%, KRT6A: 0.07%).</li>
                            <li>Os agrupamentos no PCA refletem variabilidade biológica intrínseca, sem separação artificial ou anomalias sistêmicas atribuíveis aos centros de coleta.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 8: GOVERNANCE -->
        <div id="tab-gov" class="tab-content">
            <div class="card">
                <div class="card-header">📜 Governança Algorítmica e Model Card (TRIPOD+AI)</div>
                <p>O OncoMultiOmics Survival Engine incorpora práticas completas de reprodutibilidade científica e governança de inteligência artificial biomédica:</p>
                <br>
                <ul style="padding-left: 20px; line-height: 1.8;">
                    <li><strong>Isolamento Estrito Anti-Vazamento (REG-03)</strong>: Todos os estimadores, seletores supervisionados (FastCoxScoreSelector), imputações e scalers são ajustados unicamente no conjunto de treino de cada dobra.</li>
                    <li><strong>Serialização Transparente</strong>: Modelos treinados salvos no padrão joblib acompanhados de especificação em JSON e Markdown.</li>
                    <li><strong>Controle de Versão das Dependências</strong>: Travamento estrito de bibliotecas em pyproject.toml, uv.lock e dependencies.json.</li>
                    <li><strong>Reprodução Interativa</strong>: Dashboard web operacional via Streamlit executável com comando simples:
                        <pre style="background: #272822; color: #f8f8f2; padding: 12px; border-radius: 6px; margin: 10px 0;">uv run streamlit run app/dashboard.py</pre>
                    </li>
                </ul>
            </div>
        </div>

    </div>

    <footer>
        <p>OncoMultiOmics Survival Engine — Desenvolvido em estrita conformidade com as diretrizes <strong>TRIPOD+AI</strong> e <strong>REMARK</strong> (2026).</p>
        <p>Código-Fonte e Repositório Oficial: <a href="https://github.com/PauloHFA/OncoMultiOmics.git" target="_blank" style="color: var(--secondary);">https://github.com/PauloHFA/OncoMultiOmics.git</a></p>
    </footer>

    <script>
        function openTab(tabId) {
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(c => c.classList.remove('active'));

            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(b => b.classList.remove('active'));

            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

    t = Template(template_code)
    rendered = t.render(images=images)

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"Dashboard HTML gerado com sucesso em: {output_html.resolve()} (Tamanho: {len(rendered)/1024:.1f} KB)")

if __name__ == "__main__":
    generate_html_dashboard()
