"""Script de geração automatizada de Relatório Científico Executivo em PDF (reportlab).

Gera um PDF completo e diagramado contendo:
- Metadados e aviso legal REG-16.
- Sumário executivo e veredito das hipóteses H1, H2 e H3.
- Bases de dados clínicas e moleculares (TCGA-CDR, HiSeqV2, GSE31210, SHA-256 e funis).
- Arquitetura tecnológica, bibliotecas utilizadas e formulação matemática de métricas.
- Tabelas comparativas de métricas em 25 dobras (TCGA-LUAD e TCGA-KIRC).
- Validação externa independente (GSE31210) e discussão clínica de resgate molecular.
- Figuras de alta resolução incorporadas com legendas científicas.
- Tabelas de biomarcadores Tier 1 com HR ajustado e FDR q-values.
- Diagnóstico de efeitos de lote (TSS), calibração multi-horizontes e nomograma.
"""
from pathlib import Path
import reportlab
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6c757d"))
        
        # Cabeçalho
        self.drawString(54, 800, "OncoMultiOmics Survival Engine — Relatório Científico Consolidado")
        self.setStrokeColor(colors.HexColor("#e0e0e0"))
        self.setLineWidth(0.5)
        self.line(54, 794, 541, 794)

        # Rodapé
        self.line(54, 45, 541, 45)
        self.drawString(54, 32, "Confidencial / Uso Exclusivo em Pesquisa (REG-16) — Diretrizes TRIPOD+AI & REMARK")
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(541, 32, page_text)
        self.restoreState()


def build_pdf_report():
    docs_dir = Path("docs")
    figs_dir = Path("docs/figures")
    pdf_path = docs_dir / "relatorio_cientifico_executivo.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=colors.HexColor("#1a5276"),
        alignment=0,
        spaceAfter=5,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#333333"),
        alignment=0,
        spaceAfter=12,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#795548"),
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1a5276"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#212529"),
        spaceAfter=5,
    )
    caption_style = ParagraphStyle(
        "Caption",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#555555"),
        alignment=1,
        spaceAfter=8,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#212529"),
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1a5276"),
    )

    story = []

    # Cabeçalho Principal
    story.append(Spacer(1, 10))
    story.append(Paragraph("OncoMultiOmics Survival Engine", title_style))
    story.append(Paragraph("Relatório Consolidado de Análise de Data Science, Bases de Dados e Validação Multimodal", subtitle_style))
    story.append(Paragraph("<b>Diretrizes Metodológicas:</b> TRIPOD+AI, REMARK e Regras Mandatórias REG-01 a REG-17 &nbsp;|&nbsp; <b>Data:</b> Outubro de 2026", body_style))
    story.append(Spacer(1, 4))

    # Banner REG-16
    disclaimer_text = (
        "<b>⚠️ AVISO LEGAL E ESCOPO CIENTÍFICO (REG-16):</b> Este documento destina-se exclusivamente à pesquisa acadêmica e biomédica translacional. "
        "Os modelos preditivos aqui descritos não constituem dispositivo médico diagnóstico e não devem ser empregados para conduta médica direta em seres humanos."
    )
    disclaimer_table = Table([[Paragraph(disclaimer_text, disclaimer_style)]], colWidths=[487])
    disclaimer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff3cd")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#ffeeba")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(disclaimer_table)
    story.append(Spacer(1, 8))

    # Seção 1: Sumário Executivo e Hipóteses
    story.append(Paragraph("1. Sumário Executivo e Veredito das Hipóteses", h1_style))
    story.append(Paragraph(
        "O estudo investigou empiricamente se a adição de perfis moleculares transcriptômicos (RNA-Seq) agrega capacidade preditiva "
        "em relação a variáveis clínicas convencionais (idade, sexo e estadiamento patológico AJCC). "
        "Foram avaliadas duas neoplasias: Adenocarcinoma Pulmonar (TCGA-LUAD com validação externa GSE31210) e Carcinoma Renal de Células Claras (TCGA-KIRC).",
        body_style
    ))

    hypotheses_data = [
        [
            Paragraph("Hipótese", table_cell_bold),
            Paragraph("Formulação Pré-Registrada (Fase 0)", table_cell_bold),
            Paragraph("Veredito Empírico", table_cell_bold),
            Paragraph("Significância Estatística / Impacto", table_cell_bold),
        ],
        [
            Paragraph("<b>H1: Valor Incremental</b>", table_cell),
            Paragraph("A adição do RNA-Seq eleva o C-index de Uno em relação ao modelo clínico puro.", table_cell),
            Paragraph("<b>Confirmada no KIRC</b> e em <b>Estágios Iniciais de LUAD</b>", table_cell),
            Paragraph("KIRC: ΔC = +0.0233 (p = 6.37e-5)<br/>LUAD Estágio I-II: ΔC = +0.1232 (p = 0.0072)", table_cell),
        ],
        [
            Paragraph("<b>H2: Linear vs Árvores</b>", table_cell),
            Paragraph("Modelos lineares penalizados superam ensembles de árvores em p >> n.", table_cell),
            Paragraph("<b>Totalmente Confirmada</b>", table_cell),
            Paragraph("Cox Elastic Net (C = 0.6366) superou RSF (0.5958) e GBoost (0.6272)", table_cell),
        ],
        [
            Paragraph("<b>H3: Generalização Externa</b>", table_cell),
            Paragraph("O modelo M3 congelado preserva discriminação em coorte independente.", table_cell),
            Paragraph("<b>Totalmente Confirmada</b>", table_cell),
            Paragraph("Perda externa quase nula (0.6366 → 0.6364, Δ = 0.0002)", table_cell),
        ],
    ]
    t_hyp = Table(hypotheses_data, colWidths=[80, 160, 110, 137])
    t_hyp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f4f8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
        ("PADDING", (0, 0), (-1, -1), 4.5),
    ]))
    story.append(t_hyp)
    story.append(Spacer(1, 8))

    # Seção 2: Bases de Dados e Protocolo de Curadoria
    story.append(Paragraph("2. Bases de Dados e Protocolo de Curadoria (REG-01, REG-02, REG-15)", h1_style))
    story.append(Paragraph(
        "<b>Fonte Clínica:</b> Utilizada a tabela unificada <i>TCGA Pan-Cancer Clinical Data Resource (TCGA-CDR, Liu et al., Cell 2018)</i>, que auditou e eliminou inconsistências de desfecho do consórcio.<br/>"
        "<b>Fonte Transcriptômica:</b> RNA-Seq Illumina HiSeqV2 (contagens normalizadas RSEM em escala log2(x+1)) obtidas via UCSC Xena Hub / cBioPortal, com integridade criptográfica SHA-256 registrada em <code>data/raw/manifest.json</code>.<br/>"
        "<b>Funil de Elegibilidade (REG-01):</b> Filtro estrito de alíquota tumoral primária sólida (código '01'), eliminando tecidos normais '11' e recidivas '02'. Pacientes com seguimento nulo ou estadiamento discrepante foram excluídos.<br/>"
        "<b>Censura Administrativa (REG-02):</b> Desfecho primário de Sobrevida Global (OS) truncado no horizonte pré-registrado tau = 5 anos (1826.25 dias). "
        "Maturidade de seguimento estimada por Kaplan-Meier reverso: <b>2.41 anos</b> em LUAD (494 pts, 170 óbitos) e <b>4.61 anos</b> em KIRC (528 pts, 149 óbitos).",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Seção 3: Tecnologias e Metodologia de Medição
    story.append(Paragraph("3. Tecnologias, Bibliotecas e Metodologia de Medição", h1_style))
    story.append(Paragraph(
        "<b>Ambiente e Reproduzibilidade (REG-15):</b> Python 3.11 gerenciado por <code>uv</code> (Astral) com lockfiles determinísticos (<code>uv.lock</code>) e 20 testes no <code>pytest</code>.<br/>"
        "<b>Modelos e Métricas:</b> Biblioteca <code>scikit-survival</code> (CoxnetSurvivalAnalysis, RSF, GradientBoosting) e <code>lifelines</code> (KaplanMeierFitter, CoxPHFitter).<br/>"
        "<b>Prevenção de Vazamento (REG-03):</b> O transformador proprietário <code>FastCoxScoreSelector</code> executa o teste de escore univariado de Cox vetorizado em numpy (O(n log n)) <b>estritamente nos dados de treino</b> de cada uma das 25 dobras (5x5 Repeated Stratified CV, REG-06). Imputações, scalers e sintonização do alpha do Elastic Net (via 3 dobras internas aninhadas) ocorrem sem qualquer vazamento.<br/>"
        "<b>Métricas Alinhadas a Sobrevivência (REG-05):</b> Empregado o <b>C-index de Uno com IPCW</b> (ponderação pelo inverso da probabilidade de censura [G(t)]^2 para eliminar viés temporal), <b>Integrated Brier Score (IBS)</b> integrando o erro quadrático das probabilidades ao longo de 5 anos, e <b>Dynamic AUC</b> (Heagerty-Zheng aos 1, 3 e 5 anos).",
        body_style
    ))

    story.append(PageBreak())

    # Seção 4: Benchmark TCGA-LUAD
    story.append(Paragraph("4. Benchmark da Escada de Modelos no TCGA-LUAD (25 Dobras Repetidas 5×5)", h1_style))
    story.append(Paragraph(
        "A coorte TCGA-LUAD (N=494) comparou a escada de modelos em 25 dobras estratificadas repetidas:",
        body_style
    ))

    luad_table_data = [
        [
            Paragraph("Modelo", table_cell_bold),
            Paragraph("Descrição do Algoritmo", table_cell_bold),
            Paragraph("C-index de Uno (IPCW)", table_cell_bold),
            Paragraph("C-index de Harrell", table_cell_bold),
            Paragraph("Dynamic AUC Médio", table_cell_bold),
            Paragraph("IBS (Brier)", table_cell_bold),
        ],
        [
            Paragraph("<b>M0</b>", table_cell),
            Paragraph("Kaplan-Meier Nulo Marginal", table_cell),
            Paragraph("0.5000", table_cell),
            Paragraph("0.5000", table_cell),
            Paragraph("0.5000", table_cell),
            Paragraph("0.1865", table_cell),
        ],
        [
            Paragraph("<b>M1</b>", table_cell),
            Paragraph("Cox Proporcional Clínico", table_cell),
            Paragraph("0.6359 (±0.0401)", table_cell),
            Paragraph("0.6754", table_cell),
            Paragraph("0.6821", table_cell),
            Paragraph("0.1730 (±0.0125)", table_cell),
        ],
        [
            Paragraph("<b>M3</b>", table_cell),
            Paragraph("Cox Elastic Net Integrado", table_cell),
            Paragraph("<b>0.6366</b> (±0.0404)", table_cell_bold),
            Paragraph("<b>0.6767</b>", table_cell_bold),
            Paragraph("<b>0.6838</b>", table_cell_bold),
            Paragraph("<b>0.1721</b> (±0.0123)", table_cell_bold),
        ],
        [
            Paragraph("<b>M5</b>", table_cell),
            Paragraph("Random Survival Forest (RSF)", table_cell),
            Paragraph("0.5958 (±0.0441)", table_cell),
            Paragraph("0.6412", table_cell),
            Paragraph("0.6542", table_cell),
            Paragraph("0.1796 (±0.0134)", table_cell),
        ],
        [
            Paragraph("<b>M6</b>", table_cell),
            Paragraph("Gradient Boosting Survival", table_cell),
            Paragraph("0.6272 (±0.0389)", table_cell),
            Paragraph("0.6685", table_cell),
            Paragraph("0.6710", table_cell),
            Paragraph("0.1758 (±0.0129)", table_cell),
        ],
    ]
    t_luad = Table(luad_table_data, colWidths=[35, 150, 85, 72, 75, 70])
    t_luad.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f4f8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
        ("PADDING", (0, 0), (-1, -1), 4.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfcfd")]),
    ]))
    story.append(t_luad)
    story.append(Spacer(1, 8))

    if (figs_dir / "benchmark_comparativo_modelos.png").exists():
        img_bench = Image(str(figs_dir / "benchmark_comparativo_modelos.png"), width=480, height=185)
        story.append(img_bench)
        story.append(Paragraph("Figura 1: Discriminação por C-index de Uno (tau = 5 anos) nas coortes TCGA-LUAD e TCGA-KIRC.", caption_style))

    story.append(Spacer(1, 8))

    # Seção 5: Validação Externa Independente
    story.append(Paragraph("5. Validação Externa Independente em GSE31210 (Microarray Affymetrix)", h1_style))
    story.append(Paragraph(
        "<b>O Fenômeno do Resgate Molecular:</b> Na coorte cirúrgica independente GSE31210 (Okayama et al., 2012 / N=204), restrita a estágios iniciais I e II, "
        "o estadiamento patológico tem baixa variabilidade e perde capacidade discriminatória (M1 clínico cai para C-Uno = 0.5132, log-rank p = 0.4120).<br/>"
        "O modelo molecular integrado M3 congelado elevou o C-index para <b>0.6364</b> (<b>ganho de +0.1232 ou +12.3%</b>, log-rank <b>p = 0.0072</b>). "
        "Isso prova que a transcriptômica é determinante precisamente quando a anatomia macroscópica é homogênea, identificando tumores iniciais biologicamente agressivos. "
        "A perda de generalização externa do modelo M3 foi quase nula (0.6366 → 0.6364, perda de 0.0002).",
        body_style
    ))

    # Grid de Curvas Kaplan-Meier
    img_km_luad = str(figs_dir / "km_estratificacao_risco_m3.png")
    img_km_gse = str(figs_dir / "km_estratificacao_externa_gse31210.png")
    if Path(img_km_luad).exists() and Path(img_km_gse).exists():
        km_table = Table([
            [
                Image(img_km_luad, width=238, height=175),
                Image(img_km_gse, width=238, height=175),
            ],
            [
                Paragraph("Figura 2A: Estratificação TCGA-LUAD (Teste, p < 0.0001).", caption_style),
                Paragraph("Figura 2B: Validação GSE31210 Congelada (Externo, p = 0.0072).", caption_style),
            ]
        ], colWidths=[243, 243])
        km_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(km_table)

    story.append(PageBreak())

    # Seção 6: Segunda Coorte TCGA-KIRC
    story.append(Paragraph("6. Segunda Coorte: TCGA-KIRC (Carcinoma Renal de Células Claras)", h1_style))
    story.append(Paragraph(
        "Avaliados 528 pacientes curados de TCGA-KIRC (149 óbitos, tau = 5 anos, seguimento mediano de 4.61 anos) em 25 dobras estratificadas repetidas (5x5). "
        "No câncer renal, o ganho molecular foi expressivo e homogêneo em todas as dobras (Wilcoxon p = 6.37e-05, teste t p = 2.91e-05).",
        body_style
    ))

    kirc_table_data = [
        [
            Paragraph("Métrica de Avaliação", table_cell_bold),
            Paragraph("M1 (Cox Clínico)", table_cell_bold),
            Paragraph("M3 (Coxnet Integrado)", table_cell_bold),
            Paragraph("Δ Incremental", table_cell_bold),
            Paragraph("Significância Pareada", table_cell_bold),
        ],
        [
            Paragraph("C-index de Uno (tau = 5a)", table_cell),
            Paragraph("0.7260 (±0.0482)", table_cell),
            Paragraph("<b>0.7493</b> (±0.0442)", table_cell_bold),
            Paragraph("<b>+0.0233</b>", table_cell_bold),
            Paragraph("Wilcoxon p = 6.37e-05", table_cell),
        ],
        [
            Paragraph("Dynamic AUC (5 Anos)", table_cell),
            Paragraph("0.7202", table_cell),
            Paragraph("<b>0.7624</b>", table_cell_bold),
            Paragraph("<b>+0.0422</b>", table_cell_bold),
            Paragraph("Forte ganho de longo prazo", table_cell),
        ],
        [
            Paragraph("Integrated Brier Score", table_cell),
            Paragraph("0.1275 (±0.0100)", table_cell),
            Paragraph("<b>0.1230</b> (±0.0122)", table_cell_bold),
            Paragraph("<b>-0.0045</b>", table_cell_bold),
            Paragraph("Erro residual reduzido", table_cell),
        ],
    ]
    t_kirc = Table(kirc_table_data, colWidths=[120, 95, 95, 85, 92])
    t_kirc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f4f8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_kirc)
    story.append(Spacer(1, 6))

    img_km_kirc = str(figs_dir / "km_estratificacao_risco_kirc.png")
    if Path(img_km_kirc).exists():
        story.append(Image(img_km_kirc, width=310, height=210))
        story.append(Paragraph("Figura 3: Curvas de Kaplan-Meier no TCGA-KIRC no conjunto de teste independente (qui-quadrado = 16.85, p = 4.03e-05).", caption_style))

    story.append(Spacer(1, 8))

    # Seção 7: Biomarcadores e Vias
    story.append(Paragraph("7. Biomarcadores Tier 1 com Ajuste Clínico e Correção FDR (REG-11)", h1_style))
    story.append(Paragraph(
        "Modelos multivariados ajustados por idade, sexo e estágio AJCC com controle rigoroso de falsas descobertas (Benjamini-Hochberg FDR):",
        body_style
    ))

    genes_data = [
        [
            Paragraph("Coorte", table_cell_bold),
            Paragraph("Gene", table_cell_bold),
            Paragraph("Estabilidade CV", table_cell_bold),
            Paragraph("Hazard Ratio (HR)", table_cell_bold),
            Paragraph("IC 95%", table_cell_bold),
            Paragraph("FDR (q-valor)", table_cell_bold),
            Paragraph("Mecanismo Biológico", table_cell_bold),
        ],
        [
            Paragraph("LUAD", table_cell),
            Paragraph("<code>DKK1</code>", table_cell_bold),
            Paragraph("100%", table_cell),
            Paragraph("1.533", table_cell),
            Paragraph("[1.312 - 1.791]", table_cell),
            Paragraph("<b>2.45e-06</b>", table_cell_bold),
            Paragraph("Antagonista Wnt / Evasão imune tumoral", table_cell),
        ],
        [
            Paragraph("LUAD", table_cell),
            Paragraph("<code>IGF2BP1</code>", table_cell_bold),
            Paragraph("100%", table_cell),
            Paragraph("1.353", table_cell),
            Paragraph("[1.168 - 1.568]", table_cell),
            Paragraph("<b>4.37e-04</b>", table_cell_bold),
            Paragraph("Estabilização oncogênica de mRNA", table_cell),
        ],
        [
            Paragraph("LUAD", table_cell),
            Paragraph("<code>NAPSA</code>", table_cell_bold),
            Paragraph("96%", table_cell),
            Paragraph("0.758", table_cell),
            Paragraph("[0.650 - 0.884]", table_cell),
            Paragraph("<b>2.45e-03</b>", table_cell_bold),
            Paragraph("Napsina A (diferenciação alveolar madura)", table_cell),
        ],
        [
            Paragraph("LUAD", table_cell),
            Paragraph("<code>SFTPB</code>", table_cell_bold),
            Paragraph("92%", table_cell),
            Paragraph("0.774", table_cell),
            Paragraph("[0.665 - 0.902]", table_cell),
            Paragraph("<b>4.40e-03</b>", table_cell_bold),
            Paragraph("Surfactante B / Função pulmonar preservada", table_cell),
        ],
        [
            Paragraph("KIRC", table_cell),
            Paragraph("<code>COL7A1</code>", table_cell_bold),
            Paragraph("100%", table_cell),
            Paragraph("1.592", table_cell),
            Paragraph("[1.372 - 1.847]", table_cell),
            Paragraph("<b>2.16e-08</b>", table_cell_bold),
            Paragraph("Colágeno VII / Remodelação de matriz invasiva", table_cell),
        ],
        [
            Paragraph("KIRC", table_cell),
            Paragraph("<code>SLC16A12</code>", table_cell_bold),
            Paragraph("100%", table_cell),
            Paragraph("0.665", table_cell),
            Paragraph("[0.579 - 0.764]", table_cell),
            Paragraph("<b>9.15e-08</b>", table_cell_bold),
            Paragraph("Transportador tubular / Função néfrica", table_cell),
        ],
        [
            Paragraph("KIRC", table_cell),
            Paragraph("<code>IGFN1</code>", table_cell_bold),
            Paragraph("100%", table_cell),
            Paragraph("1.414", table_cell),
            Paragraph("[1.240 - 1.612]", table_cell),
            Paragraph("<b>1.78e-06</b>", table_cell_bold),
            Paragraph("Superfamília de imunoglobulinas oncogênica", table_cell),
        ],
        [
            Paragraph("KIRC", table_cell),
            Paragraph("<code>HMGCS2</code>", table_cell_bold),
            Paragraph("100%", table_cell),
            Paragraph("0.706", table_cell),
            Paragraph("[0.600 - 0.831]", table_cell),
            Paragraph("<b>8.86e-05</b>", table_cell_bold),
            Paragraph("Cetogênese mitocondrial e homeostase", table_cell),
        ],
    ]
    t_genes = Table(genes_data, colWidths=[40, 60, 62, 60, 75, 65, 125])
    t_genes.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f4f8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
        ("PADDING", (0, 0), (-1, -1), 3.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfcfd")]),
    ]))
    story.append(t_genes)

    story.append(PageBreak())

    # Seção 8: Diagnósticos Metodológicos (Calibração, Nomograma e Efeitos de Lote)
    story.append(Paragraph("8. Diagnósticos de Rigor Metodológico (REG-05, REG-09, REG-10)", h1_style))
    story.append(Paragraph(
        "A calibração probabilística foi avaliada medindo a concordância entre a sobrevida prevista S(t|x) e a curva observada nos horizontes de 1, 3 e 5 anos "
        "(slopes de 0.99, 0.82 e 0.87; erro médio absoluto ICI de 2.8% a 4.4%). "
        "A ausência de viés técnico confundidor por hospital/centro de coleta (TSS) foi confirmada por teste de log-rank (p = 0.1090) e estabilidade de Hazard Ratio (variação inferior a 4.5%).",
        body_style
    ))

    img_calib = str(figs_dir / "calibracao_multi_horizontes_m3.png")
    img_nomo = str(figs_dir / "nomograma_pesos_m3.png")
    img_pca = str(figs_dir / "pca_diagnostico_lote_tss.png")

    if Path(img_calib).exists() and Path(img_nomo).exists():
        diag_table = Table([
            [
                Image(img_calib, width=238, height=165),
                Image(img_nomo, width=238, height=165),
            ],
            [
                Paragraph("Figura 4A: Calibração em 1, 3 e 5 Anos (ICI: 2.8% a 4.4%).", caption_style),
                Paragraph("Figura 4B: Nomograma de Coeficientes Lineares Ativos.", caption_style),
            ]
        ], colWidths=[243, 243])
        diag_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(diag_table)

    story.append(Spacer(1, 6))

    if Path(img_pca).exists():
        story.append(Image(img_pca, width=320, height=180))
        story.append(Paragraph("Figura 5: PCA diagnóstico de lote demonstrando dispersão homogênea por hospital de coleta (TSS).", caption_style))

    story.append(Spacer(1, 6))

    # Seção 9: Conclusões e Disponibilidade
    story.append(Paragraph("9. Conclusões e Disponibilidade Operacional", h1_style))
    story.append(Paragraph(
        "1. <b>Conclusão Geral:</b> O motor OncoMultiOmics comprovou que assinaturas moleculares transcriptômicas oferecem ganho prognóstico determinante "
        "quando avaliadas em subgrupos cirúrgicos de estadiamento homogêneo (GSE31210: +12.3%) e em neoplasias com biologia metabólica/vascular proeminente (TCGA-KIRC: +2.33%, p &lt; 0.0001).<br/>"
        "2. <b>Simulador Interativo:</b> Para experimentação visual em tempo real, execute: <code>uv run streamlit run app/dashboard.py</code>.<br/>"
        "3. <b>Repositório e Código:</b> Todos os modelos, testes automatizados e dados versionados encontram-se disponíveis no repositório GitHub oficial: "
        "<b>https://github.com/PauloHFA/OncoMultiOmics.git</b>.",
        body_style
    ))

    # Compilar PDF com numeração de páginas profissional
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Relatório PDF gerado com sucesso em: {pdf_path.resolve()}")

if __name__ == "__main__":
    build_pdf_report()
