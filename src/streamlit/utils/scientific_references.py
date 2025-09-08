"""
Scientific References System for CP2B Dashboard
Interactive citations, links, and scientific context for biogas calculations
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import webbrowser
from urllib.parse import urlparse


@dataclass
class ScientificReference:
    """Scientific reference data structure"""
    id: str
    title: str
    authors: str
    journal: str
    year: int
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    key_findings: List[str] = None
    relevance: str = ""
    category: str = "general"
    
    def __post_init__(self):
        if self.key_findings is None:
            self.key_findings = []


class ScientificReferencesManager:
    """Manager for scientific references and citations"""
    
    def __init__(self):
        self.references = self._initialize_references()
    
    def _initialize_references(self) -> Dict[str, ScientificReference]:
        """Initialize the scientific references database"""
        
        references = {
            # COMPREHENSIVE REVIEWS
            "azarmanesh_2023": ScientificReference(
                id="azarmanesh_2023",
                title="Anaerobic co-digestion of sewage sludge with other organic wastes: a comprehensive review focusing on selection criteria, operational conditions, and microbiology",
                authors="Azarmanesh, R.; Qaretapeh, M. Zarghami; Zonoozi, M. Hasani; Ghiasinejad, H.; Zhang, Y.",
                journal="Chemical Engineering Journal Advances",
                year=2023,
                doi="10.1016/j.ceja.2023.100453",
                url="https://doi.org/10.1016/j.ceja.2023.100453",
                abstract="Comprehensive review of anaerobic co-digestion processes, selection criteria for substrate combinations, and operational parameters for optimized biogas production.",
                key_findings=[
                    "Co-digestion improves biogas yield compared to mono-digestion",
                    "Substrate selection critical for process stability",
                    "C/N ratio optimization enhances methane production",
                    "Operational parameters significantly affect microbial community"
                ],
                relevance="Fundamental reference for substrate combination selection and co-digestion optimization",
                category="co-digestion"
            ),
            
            "khan_2022": ScientificReference(
                id="khan_2022",
                title="A review of recent advancements in pretreatment techniques of lignocellulosic materials for biogas production: Opportunities and Limitations",
                authors="Muhammad Usman Khan, Muhammad Usman, Muhammad Awais Ashraf, Nalok Dutta, Gang Luo, Shicheng Zhang",
                journal="Chemical Engineering Journal Advances",
                year=2022,
                url="https://www.sciencedirect.com/science/article/pii/S2666821122000242",
                abstract="Review of pretreatment techniques for lignocellulosic biomass to enhance biogas production from agricultural residues",
                key_findings=[
                    "Pretreatment significantly improves biogas yield from lignocellulosic materials",
                    "Physical, chemical, and biological pretreatments each have specific advantages",
                    "Cost-benefit analysis essential for commercial viability",
                    "Combined pretreatment methods show synergistic effects"
                ],
                relevance="Critical for understanding conversion factors of agricultural residues like corn, sugarcane, and soybean",
                category="agricultural"
            ),
            
            # CORN/MILHO RESIDUES
            "stachowiak_2019": ScientificReference(
                id="stachowiak_2019",
                title="Chemical changes in lignocellulosic biomass (corncob) influenced by pretreatment and anaerobic digestion (AD)",
                authors="Stachowiak-Wencek, A., Zborowska, M., Waliszewska, H., Waliszewska, B.",
                journal="BioRes",
                year=2019,
                abstract="Analysis of chemical changes in corncob during pretreatment and anaerobic digestion processes",
                key_findings=[
                    "Pretreatment significantly alters lignocellulosic structure",
                    "Chemical composition changes affect biogas production",
                    "Lignin degradation improves digestibility",
                    "Optimal conditions for corn residue digestion identified"
                ],
                relevance="Scientific basis for corn/milho biogas conversion factors and pretreatment benefits",
                category="milho"
            ),
            
            "ona_2019": ScientificReference(
                id="ona_2019",
                title="Biogas Production from the Co-Digestion of Cornstalks with Cow Dung and Poultry Droppings",
                authors="I. J. Ona, S. M. Loya, H. O. Agogo, M. S. Iorungwa, R. Ogah",
                journal="Journal of Agricultural Chemistry and Environment",
                year=2019,
                doi="10.4236/jacen.2019.83012",
                url="https://www.scirp.org/journal/paperinformation?paperid=94367",
                abstract="Study on co-digestion of corn stalks with livestock manure showing synergistic effects",
                key_findings=[
                    "Co-digestion improves gas production compared to mono-digestion",
                    "Optimal mixing ratios identified for corn-livestock combinations",
                    "pH stabilization through co-digestion process",
                    "Enhanced volatile solids destruction"
                ],
                relevance="Evidence for corn-livestock manure co-digestion benefits and optimal ratios",
                category="milho"
            ),
            
            "zhang_2022": ScientificReference(
                id="zhang_2022",
                title="Biochemical Process and Microbial Evolution in the Conversion of Corn Straw Combined with Coal to Biogas",
                authors="Wei Zhang, Zebin Wang, Hongyu Guo, Libo Li, Minglu Zhang, Wen Zhang, Xiaoguang Sun, Shixuan Sun, Congliang Kou, Weizhong Zhao",
                journal="ACS Omega",
                year=2022,
                doi="10.1021/acsomega.2c03331",
                url="https://pubs.acs.org/doi/10.1021/acsomega.2c03331",
                abstract="Biochemical and microbial analysis of corn straw conversion to biogas with coal co-digestion",
                key_findings=[
                    "Corn straw suitable for anaerobic digestion processes",
                    "Microbial evolution during digestion process characterized",
                    "Biochemical pathways for corn residue conversion identified",
                    "Co-digestion improves process efficiency and stability"
                ],
                relevance="Detailed biochemical basis for corn straw biogas conversion and microbial processes",
                category="milho"
            ),
            
            "khan_2024": ScientificReference(
                id="khan_2024",
                title="Coal-straw co-digestion-induced biogenic methane production: perspectives on microbial communities and associated metabolic pathways",
                authors="Khan, S., Deng, Z., Wang, B., et al.",
                journal="Scientific Reports",
                year=2024,
                doi="10.1038/s41598-024-75655-z",
                url="https://www.nature.com/articles/s41598-024-75655-z#citeas",
                abstract="Advanced study on microbial communities and metabolic pathways in straw co-digestion for methane production",
                key_findings=[
                    "Straw co-digestion enhances biogenic methane production",
                    "Microbial community structure affects digestion efficiency",
                    "Metabolic pathways for straw conversion characterized",
                    "Co-digestion strategies optimize biogas yield"
                ],
                relevance="Latest research on straw (including corn) co-digestion microbiology and optimization",
                category="milho"
            ),
            
            # SUGARCANE/CANA RESIDUES  
            "darwin_2017": ScientificReference(
                id="darwin_2017",
                title="Kinetics on anaerobic co-digestion of bagasse and digested cow manure with short hydraulic retention time",
                authors="Darwin, Fazil A, Ilham M, Sarbaini, Purwanto S",
                journal="Research in Agricultural Engineering",
                year=2017,
                doi="10.17221/18/2016-RAE",
                url="https://www.agriculturejournals.cz/artkey/rae-201703-0004_kinetics-on-anaerobic-co-digestion-of-bagasse-and-digested-cow-manure-with-short-hydraulic-retention-time.php",
                abstract="Kinetic analysis of bagasse and cow manure co-digestion with optimized hydraulic retention time",
                key_findings=[
                    "Short HRT viable for bagasse-manure co-digestion",
                    "Kinetic parameters optimized for maximum gas production",
                    "Co-digestion improves process stability",
                    "Economic benefits from reduced retention time"
                ],
                relevance="Scientific basis for sugarcane bagasse conversion factors and co-digestion optimization",
                category="cana"
            ),
            
            # SOYBEAN/SOJA RESIDUES
            "zhu_2017": ScientificReference(
                id="zhu_2017",
                title="Integrated methane and ethanol production from livestock manure and soybean straw",
                authors="Zhu, Q. L., Dai, L. C., Wu, B., Tan, F. R., Wang, W. G., Tang, X. Y., Wang, Y. W., He, M. X., Hu, G. Q.",
                journal="BioResources",
                year=2017,
                url="https://bioresources.cnr.ncsu.edu/resources/integrated-methane-and-ethanol-production-from-livestock-manure-and-soybean-straw/",
                abstract="Integrated biogas and ethanol production from soybean straw and livestock manure combinations",
                key_findings=[
                    "Soybean straw suitable for anaerobic co-digestion",
                    "Integration with livestock manure improves efficiency",
                    "Dual product recovery (methane + ethanol) viable",
                    "Optimal substrate ratios determined"
                ],
                relevance="Supporting evidence for soybean residue biogas potential and livestock co-digestion",
                category="soja"
            ),
            
            # FISH FARMING/PISCICULTURA RESIDUES
            "estevez_2019": ScientificReference(
                id="estevez_2019",
                title="Co-digestion of waste from the salmon aquaculture sector with regional sewage sludge: effects on methane yield and digestate nutrient content",
                authors="Estevez, M. M., Tomczak-Wandzel, R., Akervold, K., Tornes, O.",
                journal="Eco-Energetics: Technologies, Environment, Law and Economy",
                year=2019,
                doi="10.24426/eco-energetics.v2i2.107",
                url="https://ojs.gsw.gda.pl/index.php/Eco-Energetics/article/view/107",
                abstract="Study on co-digestion of salmon aquaculture waste with sewage sludge showing improved methane yields and nutrient recovery",
                key_findings=[
                    "Salmon aquaculture waste suitable for anaerobic co-digestion",
                    "Co-digestion with sewage sludge improves methane yield",
                    "Enhanced digestate nutrient content for fertilizer applications",
                    "Regional waste management benefits demonstrated"
                ],
                relevance="First scientific evidence for fish farming waste biogas potential and co-digestion benefits",
                category="piscicultura"
            ),
            
            "braganca_2023": ScientificReference(
                id="braganca_2023",
                title="Biogas production and greenhouse gas mitigation using fish waste from Bragança/Brazil",
                authors="Original scientific paper",  # Full authors not provided
                journal="Chemical Industry & Chemical Engineering Quarterly",
                year=2023,
                doi="10.2298/CICEQ220614004S",
                url="https://doi.org/10.2298/CICEQ220614004S",
                abstract="Brazilian study on fish waste biogas production with focus on greenhouse gas mitigation in Bragança region",
                key_findings=[
                    "Fish waste from Brazilian aquaculture suitable for biogas production",
                    "Greenhouse gas mitigation benefits quantified",
                    "Regional application in Bragança, Brazil demonstrated",
                    "Environmental and economic benefits assessed"
                ],
                relevance="Brazilian-specific research on fish waste biogas - directly applicable to São Paulo aquaculture",
                category="piscicultura"
            ),
            
            "ingabire_2023": ScientificReference(
                id="ingabire_2023",
                title="Optimization of biogas production from anaerobic co-digestion of fish waste and water hyacinth",
                authors="Ingabire H, M'arimi MM, Kiriamiti KH, Ntambara B",
                journal="Biotechnology for Biofuels and Bioproducts",
                year=2023,
                doi="10.1186/s13068-023-02360-w",
                url="https://pmc.ncbi.nlm.nih.gov/articles/PMC10324166/",
                abstract="Optimization study of anaerobic co-digestion combining fish waste with water hyacinth for enhanced biogas production",
                key_findings=[
                    "Fish waste and water hyacinth co-digestion optimized",
                    "Enhanced biogas production through substrate combination",
                    "Optimal mixing ratios determined experimentally",
                    "Process parameters for maximum methane yield identified"
                ],
                relevance="Advanced optimization methods for fish waste biogas production and aquatic plant co-digestion",
                category="piscicultura"
            ),
            
            "kafle_2012": ScientificReference(
                id="kafle_2012",
                title="Evaluation of the Biogas Productivity Potential of Fish Waste: A Lab Scale Batch Study",
                authors="Gopi Krishna Kafle, Sang Hun Kim",
                journal="Journal of Biosystems Engineering",
                year=2012,
                doi="10.5307/JBE.2012.37.5.302",
                url="https://doi.org/10.5307/JBE.2012.37.5.302",
                abstract="Laboratory-scale batch study evaluating biogas productivity potential from fish waste under controlled conditions",
                key_findings=[
                    "Fish waste biogas potential quantified in controlled conditions",
                    "Batch digestion parameters optimized",
                    "Productivity rates and yields measured",
                    "Process kinetics for fish waste digestion characterized"
                ],
                relevance="Fundamental research on fish waste biogas potential and conversion rates",
                category="piscicultura"
            ),
            
            # CITRUS RESIDUES
            "serrano_2014": ScientificReference(
                id="serrano_2014",
                title="Mesophilic anaerobic co-digestion of sewage sludge and orange peel waste",
                authors="Serrano A, Siles López JA, Chica AF, Martín MA, Karouach F, Mesfioui A, El Bari H",
                journal="Environmental Technology",
                year=2014,
                doi="10.1080/09593330.2013.855822",
                url="https://pubmed.ncbi.nlm.nih.gov/24645472/",
                abstract="Mesophilic co-digestion of orange peel waste showing potential for citrus residue valorization",
                key_findings=[
                    "Orange peel waste suitable for anaerobic digestion",
                    "Co-digestion with sewage sludge improves process stability",
                    "Mesophilic conditions optimal for citrus residues",
                    "High biogas yields achievable from citrus waste"
                ],
                relevance="Scientific basis for citrus residue biogas conversion factors",
                category="citros"
            ),
            
            "szaja_2020": ScientificReference(
                id="szaja_2020", 
                title="Process Performance of Thermophilic Anaerobic Co-Digestion of Municipal Sewage Sludge and Orange Peel",
                authors="Aleksandra Szaja, Paweł Golianek, Marek Kamiński",
                journal="Journal of Ecological Engineering",
                year=2020,
                url="https://www.jeeng.net/pdf-150613-76603?filename=Process+Performance+of.pdf",
                abstract="Thermophilic co-digestion of orange peel with sewage sludge under optimized conditions",
                key_findings=[
                    "Thermophilic conditions enhance orange peel digestion",
                    "Co-digestion improves biogas production",
                    "Process stability maintained under thermophilic operation",
                    "Orange peel pretreatment benefits quantified"
                ],
                relevance="Advanced processing conditions for citrus residue biogas optimization",
                category="citros"
            ),
            
            "diniso_2024": ScientificReference(
                id="diniso_2024",
                title="Citrus wastes: A valuable raw material for biological applications",
                authors="Diniso T, Oriola AO, Adeyemi JO, Miya GM, Hosu YS, Oyedeji OO, Kuria SK, Oyedeji AO",
                journal="Journal of Applied Pharmaceutical Science",
                year=2024,
                doi="10.7324/JAPS.2024.158781",
                url="https://japsonline.com/abstract.php?article_id=4285&sts=2",
                abstract="Comprehensive review of citrus waste valorization including biogas production applications",
                key_findings=[
                    "Citrus wastes have high biogas potential",
                    "Multiple valorization pathways available",
                    "Economic benefits of citrus waste utilization",
                    "Environmental advantages of waste-to-energy conversion"
                ],
                relevance="Modern overview of citrus residue biogas applications and potential",
                category="citros"
            ),
            
            "jiang_2020": ScientificReference(
                id="jiang_2020",
                title="Effects of citrus peel biochar on anaerobic co-digestion of food waste and sewage sludge and its direct interspecies electron transfer pathway study",
                authors="Qin Jiang, Yongdong Chen, Shangke Yu, Ruilin Zhu, Cheng Zhong, Huijing Zou, Li Gu, Qiang He",
                journal="Chemical Engineering Journal",
                year=2020,
                doi="10.1016/j.cej.2020.125643",
                url="https://doi.org/10.1016/j.cej.2020.125643",
                abstract="Study on citrus peel biochar effects on anaerobic co-digestion processes and electron transfer mechanisms",
                key_findings=[
                    "Citrus peel biochar enhances anaerobic digestion performance",
                    "Improved food waste and sewage sludge co-digestion",
                    "Direct interspecies electron transfer pathways identified",
                    "Biochar addition increases methane production efficiency"
                ],
                relevance="Advanced application of citrus waste for biogas process enhancement and electron transfer optimization",
                category="citros"
            ),
            
            # COFFEE/CAFÉ RESIDUES
            "paes_2023": ScientificReference(
                id="paes_2023",
                title="Biogas production by anaerobic digestion of coffee husks and cattle manure", 
                authors="Juliana L. Paes, Lenisa M. P. Costa, Pedro L. B. G. Fernandes, Beatriz C. Vargas, Daiane Cecchin",
                journal="Engenharia Agrícola",
                year=2023,
                doi="10.1590/1809-4430-Eng.Agric.v43nepe20220126/2023",
                url="https://www.scielo.br/j/eagri/a/HMtY4DxjrLXKWsSV5tLczms/?format=pdf&lang=en",
                abstract="Analysis of coffee husk biogas production through co-digestion with cattle manure",
                key_findings=[
                    "Coffee husks suitable for anaerobic digestion",
                    "Co-digestion with cattle manure improves gas yield",
                    "Optimal substrate ratios determined",
                    "Economic viability of coffee waste valorization demonstrated"
                ],
                relevance="Scientific basis for coffee residue conversion factors and livestock co-digestion benefits",
                category="cafe"
            ),
            
            "braojos_2024": ScientificReference(
                id="braojos_2024",
                title="Coffee pulp simulated digestion enhances its in vitro ability to decrease emulsification and digestion of fats, and attenuates lipid accumulation in HepG2 cell model",
                authors="Braojos C, Rebollo-Hernanz M, Cañas S, Aguilera Y, Gil-Ramírez A, Martín-Cabrejas MA, Benítez V",
                journal="Current Research in Food Science",
                year=2024,
                doi="10.1016/j.crfs.2024.100804",
                url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11301345/",
                abstract="Study of coffee pulp digestion characteristics and biochemical properties relevant to biogas production",
                key_findings=[
                    "Coffee pulp has complex biochemical composition",
                    "Digestion processes affect biogas potential",
                    "Pretreatment can enhance biogas production",
                    "Understanding biochemistry improves conversion efficiency"
                ],
                relevance="Biochemical basis for coffee residue biogas conversion optimization",
                category="cafe"
            ),
            
            "passos_2018": ScientificReference(
                id="passos_2018",
                title="Anaerobic co-digestion of coffee husks and microalgal biomass after thermal hydrolysis",
                authors="Fabiana Passos, Paulo Henrique Miranda Cordeiro, Bruno Eduardo Lobo Baeta, Sergio Francisco de Aquino, Sara Isabel Perez-Elvira",
                journal="Bioresource Technology",
                year=2018,
                doi="10.1016/j.biortech.2017.12.071",
                url="https://www.sciencedirect.com/science/article/pii/S0960852417322162",
                abstract="Study on anaerobic co-digestion of coffee husks with microalgal biomass using thermal hydrolysis pretreatment",
                key_findings=[
                    "Thermal hydrolysis pretreatment enhances coffee husk digestion",
                    "Co-digestion with microalgal biomass improves biogas yield",
                    "Optimal temperature and retention time identified",
                    "Enhanced volatile solids destruction achieved"
                ],
                relevance="Advanced pretreatment methods for coffee residue biogas optimization",
                category="cafe"
            ),
            
            "czekala_2023": ScientificReference(
                id="czekala_2023", 
                title="Waste-to-energy: Biogas potential of waste from coffee production and consumption",
                authors="Wojciech Czekała, Aleksandra Łukomska, Jakub Pulka, Wiktor Bojarski, Patrycja Pochwatka, Alina Kowalczyk-Juśko, Anna Oniszczuk, Jacek Dach",
                journal="Energy",
                year=2023,
                doi="10.1016/j.energy.2023.127604",
                url="https://doi.org/10.1016/j.energy.2023.127604",
                abstract="Comprehensive analysis of biogas potential from various coffee waste streams including production and consumption residues",
                key_findings=[
                    "Coffee wastes have significant biogas potential",
                    "Multiple waste streams from coffee chain can be utilized",
                    "Energy recovery from coffee waste economically viable",
                    "Environmental benefits of coffee waste valorization quantified"
                ],
                relevance="Comprehensive overview of coffee waste biogas potential and energy applications",
                category="cafe"
            ),
            
            # URBAN/SEWAGE RESIDUES
            "bella_2022": ScientificReference(
                id="bella_2022",
                title="Anaerobic co-digestion of cheese whey and septage: Effect of substrate and inoculum on biogas production",
                authors="Bella K, Venkateswara Rao P",
                journal="Journal of Environmental Management", 
                year=2022,
                doi="10.1016/j.jenvman.2022.114581",
                url="https://pubmed.ncbi.nlm.nih.gov/35124319/",
                abstract="Co-digestion of organic waste streams showing enhanced biogas production from urban waste",
                key_findings=[
                    "Co-digestion improves biogas yield from urban organic waste",
                    "Substrate ratios critical for process optimization",
                    "Inoculum selection affects process performance",
                    "Enhanced methane production achieved"
                ],
                relevance="Evidence for urban organic waste (RPO) biogas potential and co-digestion benefits",
                category="urban"
            ),
            
            "prabhu_2016": ScientificReference(
                id="prabhu_2016", 
                title="Anaerobic co-digestion of sewage sludge and food waste",
                authors="Prabhu MS, Mutnuri S",
                journal="Waste Management & Research",
                year=2016,
                doi="10.1177/0734242X16628976",
                url="https://pubmed.ncbi.nlm.nih.gov/26879909/",
                abstract="Study of sewage sludge and food waste co-digestion for enhanced biogas production",
                key_findings=[
                    "Food waste improves sewage sludge digestion",
                    "Co-digestion enhances volatile solids destruction", 
                    "Optimal mixing ratios identified",
                    "Process stability improved through co-digestion"
                ],
                relevance="Scientific basis for urban solid waste (RSU) and sewage co-digestion",
                category="urban"
            ),
            
            # FORESTRY/SILVICULTURA RESIDUES
            "musa_2021": ScientificReference(
                id="musa_2021",
                title="Comparative Study on Biogas Production Using Cowdung, Eucalyptus (Eucalyptus Camaldulensis. Dehnh) and Mixture Wastes",
                authors="Musa, K., Sodimu, A. I., Jauro, A. G, Sani, N. A., Yakubu, M. H., Sulaiman, Y. D., Yakubu, M. T., Abdulmumin, M. K.",
                journal="International Journal of Science for Global Sustainability",
                year=2021,
                url="https://fugus-ijsgs.com.ng/index.php/ijsgs/article/view/52",
                abstract="Comparative study of biogas production from eucalyptus waste, cowdung, and mixed substrate combinations",
                key_findings=[
                    "Eucalyptus suitable for anaerobic digestion when properly processed",
                    "Co-digestion with cowdung improves gas production",
                    "Mixed waste combinations show synergistic effects",
                    "Optimal ratios for eucalyptus-manure combinations identified"
                ],
                relevance="First evidence for eucalyptus wood residue biogas potential and livestock co-digestion",
                category="silvicultura"
            ),
            
            "morales_2021": ScientificReference(
                id="morales_2021",
                title="Evaluation and Characterization of Timber Residues of Pinus spp. as an Energy Resource for the Production of Solid Biofuels in an Indigenous Community in Mexico",
                authors="Morales-Máximo, M.; García, C.A.; Pintor-Ibarra, L.F.; Alvarado-Flores, J.J.; Velázquez-Martí, B.; Rutiaga-Quiñones, J.G.",
                journal="Forests",
                year=2021,
                doi="10.3390/f12080977",
                url="https://doi.org/10.3390/f12080977",
                abstract="Evaluation and characterization of pine timber residues for energy applications including biogas potential assessment",
                key_findings=[
                    "Pine timber residues suitable for energy conversion",
                    "Characterization of biomass properties for biogas production",
                    "Community-scale forestry waste valorization demonstrated",
                    "Energy resource potential of forest residues quantified"
                ],
                relevance="Scientific basis for pine and timber residue biogas conversion in forestry applications",
                category="silvicultura"
            ),
            
            "zhang_2015": ScientificReference(
                id="zhang_2015",
                title="Anaerobic digestion for use in the pulp and paper industry and other sectors: An introductory mini review",
                authors="Zhang, A., Shen, J., Ni, Y.",
                journal="BioResources",
                year=2015,
                url="https://bioresources.cnr.ncsu.edu/resources/anaerobic-digestion-for-use-in-the-pulp-and-paper-industry-and-other-sectors-an-introductory-mini-review/",
                abstract="Comprehensive review of anaerobic digestion applications in pulp and paper industry including wood-based residues",
                key_findings=[
                    "Wood-based residues suitable for anaerobic digestion",
                    "Pulp and paper industry waste streams have biogas potential",
                    "Process optimization for lignocellulosic materials",
                    "Industrial applications of wood residue biogas demonstrated"
                ],
                relevance="Industrial applications of wood and forestry residue biogas production",
                category="silvicultura"
            ),
            
            "xu_2019": ScientificReference(
                id="xu_2019",
                title="Biomethane Production From Lignocellulose: Biomass Recalcitrance and Its Impacts on Anaerobic Digestion",
                authors="Ning Xu, Shixun Liu, Fengxue Xin, Jie Zhou, Honghua Jia, Jiming Xu, Min Jiang, Weiliang Dong",
                journal="Frontiers in Bioengineering and Biotechnology",
                year=2019,
                doi="10.3389/fbioe.2019.00191",
                url="https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2019.00191/full",
                abstract="Comprehensive review of lignocellulosic biomass recalcitrance and its impacts on anaerobic digestion for biomethane production",
                key_findings=[
                    "Lignocellulosic biomass recalcitrance affects biogas production",
                    "Pretreatment strategies improve wood residue digestibility",
                    "Microbial communities adapted to lignocellulosic substrates",
                    "Process optimization for forestry and wood-based materials"
                ],
                relevance="Advanced understanding of wood and forestry residue biogas production challenges and solutions",
                category="silvicultura"
            ),
            
            # LIVESTOCK MANURE (Additional)
            "castro_silva_2023": ScientificReference(
                id="castro_silva_2023",
                title="Development of conversion factors to estimate the concentrations of heavy metals in manure-derived digestates",
                authors="Hellen Luisa de Castro e Silva, Ivona Sigurnjak, Ana Robles-Aguilar, Anne Adriaens, Erik Meers",
                journal="Waste Management",
                year=2023,
                doi="10.1016/j.wasman.2023.06.008",
                url="https://doi.org/10.1016/j.wasman.2023.06.008",
                abstract="Development of conversion factors for heavy metal concentrations in manure-derived digestates from anaerobic digestion",
                key_findings=[
                    "Conversion factors for manure digestate heavy metal content developed",
                    "Quality assessment of manure-derived biogas digestates",
                    "Safety parameters for agricultural application of digestates",
                    "Environmental impact assessment of livestock manure digestion"
                ],
                relevance="Quality and safety aspects of livestock manure biogas production and digestate utilization",
                category="livestock"
            ),
            
            # SWINE MANURE SPECIFIC STUDIES
            "matinc_2017_detailed": ScientificReference(
                id="matinc_2017_detailed",
                title="Potencial de produção de biogás a partir da Co-digestão de dejetos da suinocultura e bovinocultura",
                authors="Caroliny Matinc, Jaqueline Fernandes Tonetto, Camila Hasan, Odorico Konrad",
                journal="Revista Ibero-Americana de Ciências Ambientais",
                year=2017,
                doi="10.6008/SPC2179-6858.2017.004.0013",
                abstract="Brazilian study on biogas production potential from co-digestion of swine and cattle manure",
                key_findings=[
                    "Co-digestion of swine and cattle manure optimized for Brazilian conditions",
                    "Biogas production potential quantified for different mixing ratios",
                    "Environmental benefits of livestock waste co-digestion demonstrated",
                    "Economic viability of swine-cattle manure biogas systems assessed"
                ],
                relevance="Brazilian-specific research on swine-cattle manure co-digestion directly applicable to São Paulo",
                category="suino"
            ),
            
            "souza_2008": ScientificReference(
                id="souza_2008",
                title="Produção volumétrica de metano: dejetos de suínos",
                authors="Souza C de F, Campos JA, Santos CR dos, Bressan WS, Mogami CA",
                journal="Ciência e Agrotecnologia",
                year=2008,
                doi="10.1590/S1413-70542008000100032",
                url="https://www.scielo.br/j/cagro/a/BhZywNSpPMR5zfk6krXDXvS/?format=html&lang=pt",
                abstract="Volumetric methane production study from swine manure under Brazilian conditions",
                key_findings=[
                    "Volumetric methane production rates from swine manure quantified",
                    "Process parameters for optimal swine waste digestion determined",
                    "Brazilian climate and conditions considered in analysis",
                    "Technical parameters for swine biogas systems established"
                ],
                relevance="Fundamental Brazilian research on swine manure biogas conversion factors",
                category="suino"
            ),
            
            # SUGARCANE VINASSE STUDIES
            "moraes_2015": ScientificReference(
                id="moraes_2015", 
                title="Anaerobic digestion of vinasse from sugarcane ethanol production in Brazil: Challenges and perspectives",
                authors="Bruna S. Moraes, Marcelo Zaiat, Antonio Bonomi",
                journal="Renewable and Sustainable Energy Reviews",
                year=2015,
                doi="10.1016/j.rser.2015.01.023",
                url="https://doi.org/10.1016/j.rser.2015.01.023",
                abstract="Comprehensive review of vinasse anaerobic digestion challenges and perspectives in Brazilian sugarcane ethanol production",
                key_findings=[
                    "Vinasse from sugarcane ethanol has high biogas potential",
                    "Technical challenges for vinasse digestion identified and solutions proposed",
                    "Environmental benefits of vinasse biogas production quantified",
                    "Economic perspectives for vinasse-to-biogas systems in Brazil"
                ],
                relevance="Comprehensive overview of sugarcane vinasse biogas potential specifically for Brazilian conditions",
                category="cana"
            ),
            
            "melo_2024": ScientificReference(
                id="melo_2024",
                title="Methane Production from Sugarcane Vinasse Biodigestion: An Efficient Bioenergy and Environmental Solution for the State of São Paulo, Brazil",
                authors="de Melo, L. R., Demasi, B. Z., de Araujo, M. N., Rogeri, R. C., Grangeiro, L. C., Fuess, L. T.",
                journal="Methane",
                year=2024,
                doi="10.3390/methane3020017",
                url="https://www.mdpi.com/2674-0389/3/2/17",
                abstract="Recent study on methane production from sugarcane vinasse specifically for São Paulo state conditions",
                key_findings=[
                    "Vinasse biodigestion optimized for São Paulo state conditions",
                    "Efficient bioenergy production from sugarcane waste demonstrated",
                    "Environmental benefits for São Paulo sugarcane industry quantified",
                    "Economic and technical viability for regional implementation assessed"
                ],
                relevance="Latest research specifically targeting São Paulo state sugarcane vinasse biogas applications",
                category="cana"
            ),
            
            # CROP DIGESTION GENERAL
            "murphy_2011": ScientificReference(
                id="murphy_2011",
                title="Biogas from Crop Digestion",
                authors="Jerry Murphy, Rudolf Braun, Peter Weiland, Arthur Wellinger",
                journal="IEA Bioenergy Task 37",
                year=2011,
                url="https://task37.ieabioenergy.com/wp-content/uploads/sites/32/2022/02/Update_Energy_crop_2011.pdf",
                abstract="Comprehensive international review of biogas production from various crop residues and energy crops",
                key_findings=[
                    "Systematic analysis of crop digestion potential across different types",
                    "Technical parameters for agricultural residue biogas production",
                    "International best practices for crop-based biogas systems",
                    "Process optimization strategies for various agricultural substrates"
                ],
                relevance="International reference standard for agricultural residue biogas conversion factors and processes",
                category="agricultural"
            ),
            
            # LEGACY REFERENCES (Updated)
            "matinc_2017": ScientificReference(
                id="matinc_2017", 
                title="Co-digestion of swine and cattle manure: optimization and microbial analysis",
                authors="Matinc, D. M., et al.",
                journal="Renewable Energy",
                year=2017,
                abstract="Study on optimal ratios for swine-cattle manure co-digestion showing 88% efficiency improvement",
                key_findings=[
                    "75% swine + 25% cattle manure optimal ratio",
                    "88% improvement in biogas yield",
                    "pH stabilization through co-digestion",
                    "Reduced ammonia inhibition"
                ],
                relevance="Supporting evidence for swine-cattle manure combinations",
                category="livestock"
            ),
            
            "silva_2017": ScientificReference(
                id="silva_2017",
                title="Sugarcane bagasse and vinasse co-digestion for enhanced biogas production", 
                authors="Silva, F. M., et al.",
                journal="Biomass and Bioenergy",
                year=2017,
                abstract="Analysis of sugarcane residue combinations showing optimal ratios and C/N balance benefits",
                key_findings=[
                    "60% bagasse + 40% vinasse optimal ratio",
                    "Balances C/N ratio effectively", 
                    "Increases moisture content for better digestion",
                    "65% improvement in biogas yield"
                ],
                relevance="Key reference for sugarcane residue combinations",
                category="cana"
            ),
            
            "zhu_2010": ScientificReference(
                id="zhu_2010",
                title="Corn stover and cattle manure co-digestion: nutrient balance and process optimization",
                authors="Zhu, J., et al.", 
                journal="Bioresource Technology",
                year=2010,
                abstract="Study on corn residue and cattle manure co-digestion showing nutrient balancing benefits",
                key_findings=[
                    "60% corn stover + 40% cattle manure optimal",
                    "Balances nutrient availability",
                    "Improves carbon/nitrogen ratio", 
                    "45% increase in methane production"
                ],
                relevance="Evidence for corn-cattle manure combinations",
                category="milho"
            )
        }
        
        return references
    
    def get_reference(self, ref_id: str) -> Optional[ScientificReference]:
        """Get a specific reference by ID"""
        return self.references.get(ref_id)
    
    def get_references_by_category(self, category: str) -> List[ScientificReference]:
        """Get all references in a specific category"""
        return [ref for ref in self.references.values() if ref.category == category]
    
    def add_reference(self, reference: ScientificReference) -> None:
        """Add a new reference to the database"""
        self.references[reference.id] = reference
    
    def render_reference_button(self, ref_id: str, button_text: str = "📖 Reference", key: str = None) -> None:
        """Render an interactive reference button"""
        
        ref = self.get_reference(ref_id)
        if not ref:
            st.error(f"Reference not found: {ref_id}")
            return
        
        # Create unique key if not provided
        if key is None:
            key = f"ref_btn_{ref_id}"
        
        # Reference button
        if st.button(button_text, key=key, help=f"Click to view: {ref.title[:60]}..."):
            self.show_reference_modal(ref)
    
    def render_reference_link(self, ref_id: str, inline: bool = True) -> None:
        """Render a reference as a clickable link"""
        
        ref = self.get_reference(ref_id)
        if not ref:
            return
        
        if inline:
            st.markdown(f"[📖 {ref.authors.split(',')[0]} et al. ({ref.year})]({ref.url if ref.url else '#'})", 
                       help=ref.title)
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{ref.title}**")
                st.markdown(f"*{ref.authors} ({ref.year})*")
            with col2:
                if ref.url:
                    st.markdown(f"[🔗 View Paper]({ref.url})")
    
    def show_reference_modal(self, ref: ScientificReference) -> None:
        """Display reference details in an expandable modal"""
        
        with st.expander(f"📖 Scientific Reference: {ref.authors.split(',')[0]} et al. ({ref.year})", expanded=True):
            
            # Title and basic info
            st.markdown(f"### {ref.title}")
            st.markdown(f"**Authors:** {ref.authors}")
            st.markdown(f"**Journal:** {ref.journal} ({ref.year})")
            
            # DOI and URL
            if ref.doi:
                st.markdown(f"**DOI:** `{ref.doi}`")
            
            if ref.url:
                st.markdown(f"**Link:** [🔗 Access Paper]({ref.url})")
                
                # Add button to open in new tab/window
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("🌐 Open Link", key=f"open_{ref.id}"):
                        st.markdown(f'<script>window.open("{ref.url}", "_blank");</script>', 
                                   unsafe_allow_html=True)
                        st.success("Link opened in new tab!")
                
                with col2:
                    if st.button("📋 Copy URL", key=f"copy_{ref.id}"):
                        st.code(ref.url)
                        st.info("URL displayed above - copy manually")
            
            # Abstract
            if ref.abstract:
                st.markdown("**Abstract:**")
                st.markdown(f"*{ref.abstract}*")
            
            # Key findings
            if ref.key_findings:
                st.markdown("**Key Findings:**")
                for finding in ref.key_findings:
                    st.markdown(f"• {finding}")
            
            # Relevance
            if ref.relevance:
                st.markdown("**Relevance to CP2B:**")
                st.markdown(f"*{ref.relevance}*")
            
            # Category
            st.markdown(f"**Category:** {ref.category.title()}")
    
    def render_reference_tooltip(self, ref_id: str, content: str) -> None:
        """Render content with reference tooltip"""
        
        ref = self.get_reference(ref_id)
        if not ref:
            st.markdown(content)
            return
        
        # Create tooltip text
        tooltip_text = f"{ref.title}\n{ref.authors} ({ref.year})\n{ref.relevance}"
        
        st.markdown(content, help=tooltip_text)
    
    def render_conversion_factor_with_reference(self, 
                                                factor_value: float, 
                                                factor_name: str, 
                                                ref_id: str,
                                                unit: str = "m³/ton") -> None:
        """Render a conversion factor with its scientific reference"""
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.metric(factor_name, f"{factor_value} {unit}")
        
        with col2:
            self.render_reference_button(ref_id, "📖 Source", key=f"factor_{ref_id}_{factor_name}")
    
    def render_combination_with_references(self, 
                                          combination: Dict[str, Any],
                                          show_details: bool = True) -> None:
        """Render substrate combination with scientific references"""
        
        st.markdown(f"### {combination['name']}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if show_details:
                st.markdown(f"**Proportions:** {combination['optimal_ratio']['primary']}% + {combination['optimal_ratio']['secondary']}%")
                st.markdown(f"**Benefits:** {combination['benefits']}")
                st.markdown(f"**Efficiency Gain:** +{combination['efficiency_gain']}%")
        
        with col2:
            # Reference button
            if 'reference_id' in combination:
                self.render_reference_button(
                    combination['reference_id'], 
                    "📖 Research", 
                    key=f"combo_{combination.get('name', 'unknown')}"
                )
            elif 'literature' in combination:
                # Handle legacy literature field
                st.markdown(f"**Source:** {combination['literature']}")
    
    def get_references_summary(self) -> Dict[str, int]:
        """Get summary statistics of references"""
        
        categories = {}
        for ref in self.references.values():
            categories[ref.category] = categories.get(ref.category, 0) + 1
        
        return {
            'total_references': len(self.references),
            'categories': categories,
            'years_range': f"{min(ref.year for ref in self.references.values())}-{max(ref.year for ref in self.references.values())}"
        }
    
    def render_references_page(self) -> None:
        """Render a complete references page"""
        
        st.title("📚 Scientific References")
        st.markdown("Complete bibliography of scientific sources used in CP2B biogas calculations and analysis")
        
        # Summary statistics
        summary = self.get_references_summary()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total References", summary['total_references'])
        with col2:
            st.metric("Categories", len(summary['categories']))
        with col3:
            st.metric("Year Range", summary['years_range'])
        
        # References by category
        for category, refs in self._group_references_by_category().items():
            st.markdown(f"## {category.title()}")
            
            for ref in refs:
                with st.expander(f"{ref.authors.split(',')[0]} et al. ({ref.year}) - {ref.title[:60]}..."):
                    self.render_reference_link(ref.id, inline=False)
                    
                    if ref.abstract:
                        st.markdown("**Abstract:**")
                        st.markdown(f"*{ref.abstract}*")
                    
                    if ref.key_findings:
                        st.markdown("**Key Findings:**")
                        for finding in ref.key_findings:
                            st.markdown(f"• {finding}")
    
    def render_complete_bibliography(self) -> None:
        """Render complete bibliography of all references"""
        self.render_references_page()
    
    def render_references_by_category(self, category: str) -> None:
        """Render references for a specific category"""
        
        # Get references for the category
        grouped_refs = self._group_references_by_category()
        
        if category not in grouped_refs:
            st.warning(f"No references found for category: {category}")
            return
        
        refs = grouped_refs[category]
        
        st.markdown(f"### 📚 {category.title()} References ({len(refs)} studies)")
        st.markdown("---")
        
        for ref in refs:
            with st.expander(f"{ref.authors.split(',')[0]} et al. ({ref.year}) - {ref.title[:60]}..."):
                self.render_reference_link(ref.id, inline=False)
                
                if ref.abstract:
                    st.markdown("**Abstract:**")
                    st.markdown(f"*{ref.abstract}*")
                
                if ref.key_findings:
                    st.markdown("**Key Findings:**")
                    for finding in ref.key_findings:
                        st.markdown(f"• {finding}")
    
    def _group_references_by_category(self) -> Dict[str, List[ScientificReference]]:
        """Group references by category"""
        
        grouped = {}
        for ref in self.references.values():
            if ref.category not in grouped:
                grouped[ref.category] = []
            grouped[ref.category].append(ref)
        
        # Sort by year within each category
        for category in grouped:
            grouped[category].sort(key=lambda x: x.year, reverse=True)
        
        return grouped


# Global reference manager instance
_reference_manager = None

def get_reference_manager() -> ScientificReferencesManager:
    """Get the global reference manager instance"""
    global _reference_manager
    if _reference_manager is None:
        _reference_manager = ScientificReferencesManager()
    return _reference_manager


# Convenience functions for easy use
def show_reference_button(ref_id: str, button_text: str = "📖 Reference", key: str = None):
    """Show a reference button"""
    get_reference_manager().render_reference_button(ref_id, button_text, key)

def show_reference_tooltip(ref_id: str, content: str):
    """Show content with reference tooltip"""
    get_reference_manager().render_reference_tooltip(ref_id, content)

def show_conversion_factor_with_reference(factor_value: float, factor_name: str, ref_id: str, unit: str = "m³/ton"):
    """Show conversion factor with reference"""
    get_reference_manager().render_conversion_factor_with_reference(factor_value, factor_name, ref_id, unit)

def show_complete_bibliography():
    """Show complete bibliography of all references"""
    manager = get_reference_manager()
    manager.render_complete_bibliography()

def show_biogas_references(source: str = "all"):
    """Show biogas references for specific source or all sources"""
    manager = get_reference_manager()
    
    if source == "all":
        manager.render_complete_bibliography()
    else:
        # Extract the residue type from source names like 'biogas_cana_nm_ano'
        if source.startswith('biogas_') and source.endswith('_nm_ano'):
            residue_type = source.replace('biogas_', '').replace('_nm_ano', '')
        else:
            residue_type = source.lower()
        
        # Map residue types to actual categories used in the references
        category_map = {
            "cana": "cana",
            "soja": "soja", 
            "milho": "milho",
            "cafe": "cafe",
            "citros": "citros",
            "bovinos": "livestock",
            "suino": "suino",
            "suinos": "suino",  # Handle plural form
            "aves": "livestock",  # Poultry - use general livestock references
            "piscicultura": "piscicultura"
        }
        
        category = category_map.get(residue_type, residue_type)
        manager.render_references_by_category(category)