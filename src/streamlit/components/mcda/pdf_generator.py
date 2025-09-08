# CP2B PDF Report Generator
# Gerador de relatórios PDF para propriedades MCDA

import streamlit as st
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
import io
from typing import Dict, Any
import logging
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

def generate_mcda_pdf_report(property_data: Dict[str, Any]) -> bytes:
    """
    Gera relatório PDF completo da propriedade MCDA
    
    Args:
        property_data: Dados completos da propriedade
        
    Returns:
        bytes: Conteúdo do PDF gerado
    """
    try:
        # Criar buffer em memória
        buffer = io.BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo customizado para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c5530')
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2c5530')
        )
        
        # Conteúdo do PDF
        story = []
        
        # CABEÇALHO
        story.extend(create_pdf_header(property_data, title_style))
        
        # RESUMO EXECUTIVO
        story.extend(create_executive_summary(property_data, subtitle_style, styles))
        
        # ANÁLISE MCDA DETALHADA
        story.extend(create_mcda_analysis(property_data, subtitle_style, styles))
        
        # ANÁLISE DE BIOMASSA
        story.extend(create_biomass_analysis(property_data, subtitle_style, styles))
        
        # ANÁLISE DE INFRAESTRUTURA
        story.extend(create_infrastructure_analysis(property_data, subtitle_style, styles))
        
        # ANÁLISE DE RESTRIÇÕES
        story.extend(create_restrictions_analysis(property_data, subtitle_style, styles))
        
        # RECOMENDAÇÕES
        story.extend(create_recommendations(property_data, subtitle_style, styles))
        
        # RODAPÉ
        story.extend(create_pdf_footer(styles))
        
        # Gerar PDF
        doc.build(story)
        
        # Obter conteúdo do buffer
        pdf_content = buffer.getvalue()
        buffer.close()
        
        logger.info(f"✅ PDF gerado com {len(pdf_content)} bytes")
        return pdf_content
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar PDF: {str(e)}")
        raise

def create_pdf_header(property_data: Dict[str, Any], title_style) -> list:
    """Cria cabeçalho do PDF"""
    story = []
    
    # Título principal
    title = Paragraph("🌱 RELATÓRIO MCDA - ANÁLISE DE VIABILIDADE", title_style)
    story.append(title)
    
    subtitle = Paragraph("Localização Ótima para Planta de Biogás", title_style)
    story.append(subtitle)
    
    story.append(Spacer(1, 20))
    
    # Informações da propriedade em tabela
    data = [
        ['Propriedade SICAR:', property_data.get('cod_imovel', 'N/A')],
        ['Município:', property_data.get('municipio', 'N/A')],
        ['Data do Relatório:', datetime.now().strftime('%d/%m/%Y %H:%M')],
        ['Score MCDA:', f"{property_data.get('mcda_score', 0):.1f}/100"],
        ['Ranking:', f"#{property_data.get('ranking', 'N/A')}"]
    ]
    
    table = Table(data, colWidths=[4*cm, 8*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    return story

def create_executive_summary(property_data: Dict[str, Any], subtitle_style, styles) -> list:
    """Cria resumo executivo"""
    story = []
    
    story.append(Paragraph("📋 RESUMO EXECUTIVO", subtitle_style))
    
    # Gerar texto do resumo baseado nos dados
    score = property_data.get('mcda_score', 0)
    municipio = property_data.get('municipio', 'N/A')
    
    if score >= 70:
        viability = "ALTA VIABILIDADE"
        recommendation = "Recomendada para desenvolvimento de planta de biogás."
    elif score >= 50:
        viability = "VIABILIDADE MODERADA"  
        recommendation = "Viável com estudos adicionais e planejamento cuidadoso."
    else:
        viability = "BAIXA VIABILIDADE"
        recommendation = "Não recomendada devido aos desafios identificados."
    
    summary_text = f"""
    Esta análise avaliou a viabilidade de instalação de uma planta de biogás na propriedade SICAR 
    localizada em {municipio}, utilizando metodologia MCDA (Multi-Criteria Decision Analysis).
    
    <b>RESULTADO:</b> {viability} - Score MCDA de {score:.1f}/100
    
    <b>POSIÇÃO:</b> #{property_data.get('ranking', 'N/A')} entre 12.163 propriedades analisadas na RMC
    
    <b>RECOMENDAÇÃO:</b> {recommendation}
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_mcda_analysis(property_data: Dict[str, Any], subtitle_style, styles) -> list:
    """Cria análise MCDA detalhada"""
    story = []
    
    story.append(Paragraph("🔬 ANÁLISE MCDA DETALHADA", subtitle_style))
    
    # Tabela com componentes MCDA
    biomass_norm = property_data.get('biomass_norm', 0)
    infra_norm = property_data.get('infra_norm', 0)
    restriction_norm = property_data.get('restriction_norm', 0)
    
    mcda_data = [
        ['Componente', 'Score Normalizado', 'Peso', 'Contribuição', 'Avaliação'],
        ['Potencial de Biomassa', f"{biomass_norm:.1f}/100", '35%', f"{biomass_norm * 0.35:.1f}", get_component_rating(biomass_norm)],
        ['Acesso à Infraestrutura', f"{infra_norm:.1f}/100", '49%', f"{infra_norm * 0.49:.1f}", get_component_rating(infra_norm)],
        ['Baixas Restrições Ambientais', f"{restriction_norm:.1f}/100", '16%', f"{restriction_norm * 0.16:.1f}", get_component_rating(restriction_norm)],
        ['SCORE FINAL MCDA', f"{property_data.get('mcda_score', 0):.1f}/100", '100%', f"{property_data.get('mcda_score', 0):.1f}", get_final_rating(property_data.get('mcda_score', 0))]
    ]
    
    mcda_table = Table(mcda_data, colWidths=[4*cm, 2.5*cm, 1.5*cm, 2*cm, 2.5*cm])
    mcda_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5530')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e8')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(mcda_table)
    story.append(Spacer(1, 15))
    
    # Interpretação
    interpretation = generate_mcda_interpretation_pdf(property_data)
    story.append(Paragraph("<b>Interpretação:</b>", styles['Normal']))
    story.append(Paragraph(interpretation, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_biomass_analysis(property_data: Dict[str, Any], subtitle_style, styles) -> list:
    """Cria análise de biomassa"""
    story = []
    
    story.append(Paragraph("🌾 ANÁLISE DE BIOMASSA DISPONÍVEL", subtitle_style))
    
    # Tabela de biomassa por cultura (raio 10km)
    biomass_data = [
        ['Cultura', 'Hectares Disponíveis', 'Potencial Relativo'],
    ]
    
    cultures = {
        'Pastagem': 'pasture_ha_10km',
        'Cana-de-açúcar': 'sugarcane_ha_10km', 
        'Soja': 'soy_ha_10km',
        'Café': 'coffee_ha_10km',
        'Citros': 'citrus_ha_10km',
        'Outras Temporárias': 'other_temp_ha_10km'
    }
    
    total_biomass = sum(property_data.get(key, 0) for key in cultures.values())
    
    for culture_name, key in cultures.items():
        hectares = property_data.get(key, 0)
        if hectares > 0:
            percentage = (hectares / total_biomass * 100) if total_biomass > 0 else 0
            biomass_data.append([
                culture_name, 
                f"{hectares:,.0f} ha", 
                f"{percentage:.1f}%"
            ])
    
    if len(biomass_data) > 1:  # Tem dados além do cabeçalho
        biomass_table = Table(biomass_data, colWidths=[4*cm, 3*cm, 3*cm])
        biomass_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7c59')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(biomass_table)
    else:
        story.append(Paragraph("Nenhuma biomassa significativa identificada no raio de 10km.", styles['Normal']))
    
    story.append(Spacer(1, 20))
    return story

def create_infrastructure_analysis(property_data: Dict[str, Any], subtitle_style, styles) -> list:
    """Cria análise de infraestrutura"""
    story = []
    
    story.append(Paragraph("🏗️ ANÁLISE DE INFRAESTRUTURA E LOGÍSTICA", subtitle_style))
    
    # Tabela de distâncias
    infra_data = [
        ['Tipo de Infraestrutura', 'Distância (km)', 'Classificação'],
    ]
    
    infrastructures = {
        'Subestações de Energia': 'dist_subestacoes_km',
        'Rodovias Federais': 'dist_rodovias_federais_km',
        'Rodovias Estaduais': 'dist_rodovias_estaduais_km',
        'Gasodutos': 'dist_gasodutos_km',
        'Linhas de Transmissão': 'dist_linhas_transmissao_km'
    }
    
    for infra_name, key in infrastructures.items():
        distance = property_data.get(key, 0)
        if distance > 0:
            classification = classify_distance(distance)
            infra_data.append([
                infra_name,
                f"{distance:.1f} km",
                classification
            ])
    
    if len(infra_data) > 1:
        infra_table = Table(infra_data, colWidths=[5*cm, 2.5*cm, 3*cm])
        infra_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5530')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(infra_table)
    
    story.append(Spacer(1, 20))
    return story

def create_restrictions_analysis(property_data: Dict[str, Any], subtitle_style, styles) -> list:
    """Cria análise de restrições"""
    story = []
    
    story.append(Paragraph("⚠️ ANÁLISE DE RESTRIÇÕES AMBIENTAIS", subtitle_style))
    
    restriction_score = property_data.get('restriction_score', 0)
    
    if restriction_score == 0:
        status = "✅ NENHUMA RESTRIÇÃO IDENTIFICADA"
        description = "Área livre para desenvolvimento de planta de biogás."
    elif restriction_score <= 3:
        status = "ℹ️ RESTRIÇÕES BAIXAS"
        description = "Desenvolvimento viável com cuidados ambientais básicos."
    elif restriction_score <= 7:
        status = "⚠️ RESTRIÇÕES MODERADAS"
        description = "Necessário estudo detalhado de impacto ambiental."
    else:
        status = "🚫 RESTRIÇÕES ALTAS"
        description = "Desenvolvimento não recomendado devido a restrições significativas."
    
    story.append(Paragraph(f"<b>Status:</b> {status}", styles['Normal']))
    story.append(Paragraph(f"<b>Score de Restrições:</b> {restriction_score:.1f}/10", styles['Normal']))
    story.append(Paragraph(f"<b>Interpretação:</b> {description}", styles['Normal']))
    
    story.append(Spacer(1, 15))
    
    # Tipos de restrições consideradas
    restrictions_text = """
    <b>Tipos de restrições analisadas:</b>
    • Unidades de Conservação de Proteção Integral (166 áreas)
    • Unidades de Conservação de Uso Sustentável (216 áreas)  
    • Perímetros Urbanos com buffer de 1km (3.630 áreas)
    
    <b>Metodologia:</b> Score de 0-10 onde valores maiores indicam mais restrições.
    Aplicado buffer de 1km para áreas urbanas considerando aspectos de ruído e odor.
    """
    
    story.append(Paragraph(restrictions_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_recommendations(property_data: Dict[str, Any], subtitle_style, styles) -> list:
    """Cria seção de recomendações"""
    story = []
    
    story.append(Paragraph("🎯 RECOMENDAÇÕES E PRÓXIMOS PASSOS", subtitle_style))
    
    score = property_data.get('mcda_score', 0)
    
    if score >= 70:
        recommendations = """
        <b>RECOMENDAÇÃO: DESENVOLVIMENTO PRIORITÁRIO</b>
        
        Esta propriedade apresenta excelente viabilidade para instalação de planta de biogás:
        
        <b>Próximos Passos:</b>
        1. Realizar estudo de viabilidade técnico-econômica detalhado
        2. Contactar proprietários para negociação de parcerias
        3. Desenvolver projeto executivo de engenharia
        4. Iniciar processo de licenciamento ambiental
        5. Estruturar modelo de negócio e captação de recursos
        
        <b>Considerações Técnicas:</b>
        • Avaliar capacidade de processamento baseada na biomassa disponível
        • Verificar condições específicas do solo e topografia
        • Analisar logística de coleta e transporte de matéria-prima
        • Estudar possibilidades de integração com infraestrutura existente
        """
    elif score >= 50:
        recommendations = """
        <b>RECOMENDAÇÃO: DESENVOLVIMENTO COM ESTUDOS COMPLEMENTARES</b>
        
        Esta propriedade apresenta viabilidade moderada, requerendo análises adicionais:
        
        <b>Estudos Necessários:</b>
        1. Análise detalhada dos fatores limitantes identificados
        2. Avaliação de alternativas para otimização da localização
        3. Estudo de viabilidade econômica com cenários conservadores
        4. Análise de riscos operacionais e ambientais
        
        <b>Possíveis Otimizações:</b>
        • Parcerias com propriedades vizinhas para ampliar disponibilidade de biomassa
        • Investimentos em infraestrutura de acesso
        • Soluções tecnológicas para mitigar restrições identificadas
        """
    else:
        recommendations = """
        <b>RECOMENDAÇÃO: NÃO PRIORITÁRIA PARA DESENVOLVIMENTO</b>
        
        Esta propriedade apresenta desafios significativos para instalação de planta de biogás:
        
        <b>Principais Limitações:</b>
        1. Baixa disponibilidade de biomassa na região
        2. Dificuldades de acesso à infraestrutura essencial
        3. Presença de restrições ambientais significativas
        
        <b>Alternativas:</b>
        • Considerar outras propriedades com melhor score MCDA na região
        • Avaliar modelo de coleta centralizada com propriedades vizinhas
        • Aguardar desenvolvimento de infraestrutura regional
        """
    
    story.append(Paragraph(recommendations, styles['Normal']))
    story.append(Spacer(1, 20))
    
    return story

def create_pdf_footer(styles) -> list:
    """Cria rodapé do PDF"""
    story = []
    
    story.append(Spacer(1, 30))
    
    footer_text = """
    <b>Metodologia MCDA:</b> Análise Multicritério baseada em literatura científica 
    (Laasasenaho et al. 2019, Kaynak & Gümüş 2025).
    
    <b>Dados:</b> 12.163 propriedades SICAR analisadas na Região Metropolitana de Campinas.
    Processamento realizado no Google Earth Engine com validação científica.
    
    <b>Disclaimer:</b> Este relatório é uma análise preliminar baseada em dados públicos. 
    Estudos detalhados de campo são necessários antes de qualquer implementação.
    
    <b>Gerado por:</b> CP2B - Sistema de Análise Geoespacial para Biogás
    """
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_JUSTIFY
    )
    
    story.append(Paragraph(footer_text, footer_style))
    
    return story

# Funções auxiliares

def get_component_rating(score: float) -> str:
    """Retorna classificação do componente MCDA"""
    if score >= 80:
        return "Excelente"
    elif score >= 60:
        return "Bom"
    elif score >= 40:
        return "Regular"
    else:
        return "Baixo"

def get_final_rating(score: float) -> str:
    """Retorna classificação final"""
    if score >= 70:
        return "ALTA VIABILIDADE"
    elif score >= 50:
        return "VIABILIDADE MODERADA"
    else:
        return "BAIXA VIABILIDADE"

def classify_distance(distance: float) -> str:
    """Classifica distância para infraestrutura"""
    if distance < 5:
        return "Excelente (< 5km)"
    elif distance < 15:
        return "Boa (5-15km)"
    elif distance < 30:
        return "Regular (15-30km)"
    else:
        return "Distante (> 30km)"

def generate_mcda_interpretation_pdf(property_data: Dict[str, Any]) -> str:
    """Gera interpretação textual para PDF"""
    score = property_data.get('mcda_score', 0)
    biomass_norm = property_data.get('biomass_norm', 0)
    infra_norm = property_data.get('infra_norm', 0)
    restriction_norm = property_data.get('restriction_norm', 0)
    
    interpretation = f"Esta propriedade obteve score MCDA de {score:.1f}/100. "
    
    # Identificar pontos fortes
    strengths = []
    if biomass_norm >= 70:
        strengths.append("excelente disponibilidade de biomassa")
    if infra_norm >= 70:
        strengths.append("boa acessibilidade à infraestrutura") 
    if restriction_norm >= 70:
        strengths.append("poucas restrições ambientais")
    
    # Identificar pontos fracos
    weaknesses = []
    if biomass_norm < 30:
        weaknesses.append("baixa disponibilidade de biomassa")
    if infra_norm < 30:
        weaknesses.append("infraestrutura distante")
    if restriction_norm < 30:
        weaknesses.append("muitas restrições ambientais")
    
    if strengths:
        interpretation += f"<b>Pontos fortes:</b> {', '.join(strengths)}. "
    if weaknesses:
        interpretation += f"<b>Pontos de atenção:</b> {', '.join(weaknesses)}. "
    
    return interpretation

def create_pdf_download_button(pdf_content: bytes, property_data: Dict[str, Any]) -> None:
    """Cria botão de download do PDF"""
    try:
        # Criar nome do arquivo
        municipio = property_data.get('municipio', 'Propriedade').replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"Relatorio_MCDA_{municipio}_{timestamp}.pdf"
        
        # Codificar PDF em base64 para download
        b64_pdf = base64.b64encode(pdf_content).decode()
        
        # Botão de download
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" target="_blank">'
        
        st.markdown(
            f"""
            {href}
                <button style='background-color: #2c5530; color: white; padding: 12px 24px; 
                              border: none; border-radius: 6px; cursor: pointer; font-weight: bold;
                              font-size: 16px; width: 100%;'>
                    📄 BAIXAR RELATÓRIO PDF
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar botão de download: {str(e)}")
        st.error("Erro ao preparar download do PDF")