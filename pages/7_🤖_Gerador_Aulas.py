import streamlit as st
import utils
import os

# Tenta importar a biblioteca da IA, se não tiver, avisa
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

st.set_page_config(page_title="Gerador de Aulas IA", layout="wide")
utils.aplicar_estilo()

st.title("🤖 Gerador de Aulas com Inteligência Artificial")
st.markdown("Crie roteiros de aula completos, criativos e alinhados à BNCC utilizando o poder do Google Gemini.")

# Inicializa o estado da sessão para persistir o texto gerado
if 'texto_gerado' not in st.session_state:
    st.session_state.texto_gerado = ""

if not HAS_GENAI:
    st.error("A biblioteca `google-generativeai` não está instalada. O administrador do sistema precisa atualizar o `requirements.txt`.")
    st.stop()

# --- SIDEBAR: CONFIGURAÇÃO ---
with st.sidebar:
    st.header("🧠 Configuração da IA")
    
    # Carrega perfil para verificar se já existe chave salva
    perfil = utils.carregar_perfil_professor()
    api_key_salva = perfil.get("api_key", "")

    # Fallback para secrets/env se não tiver no perfil
    if not api_key_salva:
        api_key_salva = os.environ.get("GOOGLE_API_KEY", "")
        try:
            if "GOOGLE_API_KEY" in st.secrets:
                api_key_salva = st.secrets["GOOGLE_API_KEY"]
        except:
            pass
        
    api_key = st.text_input("Chave de API (Google Gemini)", value=api_key_salva, type="password", help="Crie sua chave em: https://aistudio.google.com/")
    
    if st.button("💾 Salvar Chave"):
        perfil["api_key"] = api_key
        utils.salvar_perfil_professor(perfil)
        
        # Persiste no banco de dados
        nome_prof = perfil.get("professor", st.session_state.get("professor", ""))
        if nome_prof:
            utils.salvar_professor_config_db(
                nome_prof, 
                perfil.get("email", ""), 
                perfil.get("municipio", st.session_state.get("municipio", "")), 
                perfil
            )
        st.success("Chave salva no perfil!")
        st.rerun()
    
    st.info("Esta funcionalidade requer uma chave de API válida do Google.")
    
    st.divider()
    st.markdown("### Dicas de Prompt")
    st.caption("Quanto mais detalhes você fornecer nos objetivos, melhor será o resultado.")
    
    st.divider()
    st.header("📚 Material de Apoio (PDF)")
    st.caption("Selecione um PDF da pasta 'pdf' do Drive para usar como base.")
    
    pdfs_disponiveis = utils.listar_pdfs_referencia()
    opcoes_pdf = ["Nenhum"] + [p['name'] for p in pdfs_disponiveis]
    
    pdf_selecionado_nome = st.selectbox("Usar conteúdo do arquivo:", options=opcoes_pdf)
    
    conteudo_pdf_extra = ""
    if pdf_selecionado_nome != "Nenhum":
        # Encontra o ID/Caminho do arquivo selecionado
        arquivo_alvo = next((p for p in pdfs_disponiveis if p['name'] == pdf_selecionado_nome), None)
        if arquivo_alvo:
            with st.spinner(f"Lendo '{pdf_selecionado_nome}'..."):
                conteudo_pdf_extra = utils.extrair_texto_pdf_referencia(arquivo_alvo['id'])
            if conteudo_pdf_extra:
                st.success(f"PDF carregado! ({len(conteudo_pdf_extra)} caracteres)")
            else:
                st.warning("Não foi possível extrair texto deste PDF.")

# --- CARREGAMENTO DE DADOS ---
curriculo = utils.carregar_curriculo_db()
comps_basico = list(curriculo.get("BASICO", {}).keys())
comps_aprofundamento = list(curriculo.get("APROFUNDAMENTO", {}).keys())
comps_ept = list(curriculo.get("EPT", {}).keys())
turmas_disponiveis = utils.listar_turmas_db()

# --- FORMULÁRIO PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    turma_sel = st.selectbox("Turma (Opcional)", [""] + turmas_disponiveis, help="Selecione a turma para aparecer no cabeçalho do plano.")
    
    publico = st.selectbox("Público Alvo", [
        "Ensino Fundamental I (1º ao 5º ano)",
        "Ensino Fundamental II (6º ao 9º ano)",
        "Ensino Médio (1ª a 3ª série)",
        "Ensino Técnico / Profissionalizante",
        "EJA (Educação de Jovens e Adultos)"
    ], index=2)
    
    # Lógica de Sugestão de Componentes
    lista_sugestoes = []
    if "Médio" in publico:
        # Garante IA e remove Computação (se existir) para o Médio
        sugestoes_medio = set(comps_basico + comps_aprofundamento)
        sugestoes_medio.add("Inteligência Artificial")
        sugestoes_medio.discard("Computação")
        lista_sugestoes = sorted(list(sugestoes_medio))
    elif "Técnico" in publico:
        lista_sugestoes = sorted(comps_ept)
    elif "Fundamental" in publico:
        lista_sugestoes = ["Arte", "Ciências", "Computação", "Educação Física", "Ensino Religioso", "Geografia", "História", "Inglês", "Inteligência Artificial", "Língua Portuguesa", "Matemática"]
    
    opcoes_comp = ["📝 Digitar Manualmente..."] + lista_sugestoes
    sel_comp = st.selectbox("Componente Curricular", options=opcoes_comp)
    
    if sel_comp == "📝 Digitar Manualmente...":
        componente = st.text_input("Digite o Componente", placeholder="Ex: Robótica")
    else:
        componente = sel_comp

with col2:
    duracao = st.selectbox("Duração Estimada", [
        "1 Aula (50 min)",
        "2 Aulas (100 min)",
        "3 Aulas (150 min)",
        "Bloco Semanal (4-5 aulas)"
    ])
    
    tema = st.text_input("Tema da Aula / Assunto", placeholder="Ex: Revolução Industrial, Leis de Newton...")

st.write("### Detalhes Pedagógicos")
col3, col4 = st.columns(2)

with col3:
    metodologia = st.selectbox("Estratégia / Metodologia", [
        "Aula Expositiva Dialogada (Tradicional)",
        "Aprendizagem Baseada em Projetos (PBL)",
        "Sala de Aula Invertida (Flipped Classroom)",
        "Gamificação (Uso de elementos de jogos)",
        "Rotação por Estações",
        "Estudo de Caso",
        "Peer Instruction (Instrução pelos Pares)"
    ])

with col4:
    recursos = st.multiselect("Recursos Disponíveis", [
        "Projetor / Datashow",
        "Laboratório de Informática",
        "Celulares dos Alunos (BYOD)",
        "Quadro Branco e Marcadores",
        "Materiais de Papelaria (Cartolinas, etc)",
        "Laboratório de Ciências",
        "Acesso à Internet"
    ], default=["Quadro Branco e Marcadores", "Projetor / Datashow"])

objetivos_especificos = st.text_area("Objetivos Específicos ou Observações (Opcional)", height=100, placeholder="Ex: Focar na habilidade EF09HI02 da BNCC. Incluir uma atividade prática em grupo.")

# --- GERAÇÃO ---
st.divider()

if st.button("✨ Gerar Plano de Aula", type="primary"):
    if not api_key:
        st.warning("⚠️ Por favor, insira sua Chave de API no menu lateral para continuar.")
    elif not tema or not componente:
        st.warning("⚠️ Preencha pelo menos o Tema e o Componente Curricular.")
    else:
        st.session_state.texto_gerado = "" # Limpa o resultado anterior
        genai.configure(api_key=api_key)
        
        # Recupera dados para o cabeçalho
        escola = st.session_state.get('escola', "CETI PROFESSOR RALDIR CAVALCANTE BASTOS")
        perfil_prof = utils.carregar_perfil_professor()
        professor = perfil_prof.get("professor", st.session_state.get("professor", "Professor(a)"))
        
        turma_header = turma_sel if turma_sel else publico

        # Construção do Prompt
        prompt = f"""
        Você é um professor especialista e criativo. Crie um roteiro de aula completo seguindo estritamente o modelo abaixo.
        
        **CONTEXTO:**
        - Escola: {escola}
        - Professor: {professor}
        - Turma: {turma_header}
        - **Componente:** {componente}
        - **Tema:** {tema}
        - **Público:** {publico}
        - **Duração:** {duracao}
        - **Metodologia:** {metodologia}
        - **Recursos:** {', '.join(recursos)}
        - **Observações:** {objetivos_especificos}
        
        """
        
        if conteudo_pdf_extra:
            prompt += f"""
            **MATERIAL DE REFERÊNCIA (PDF):**
            Use as informações abaixo como base teórica para o conteúdo da aula:
            --- INÍCIO DO TEXTO DO PDF ---
            {conteudo_pdf_extra[:30000]} 
            --- FIM DO TEXTO DO PDF ---
            (Nota: Se o texto do PDF for muito longo, foque nos pontos principais relacionados ao tema '{tema}')
            """
            
        prompt += f"""
        **MODELO DE SAÍDA (Markdown):**
        
        # 🎨 {tema}
        
        **🏫 Escola:** {escola}  
        **👨‍🏫 Professor:** {professor}  
        **🎓 Turma:** {turma_header}
        **📚 Componente:** {componente}  
        
        ---
        
        ## 📑 Sumário
        1. 🏁 Introdução
        2. 🎯 Objetivos
        3. 💡 Conteúdo
        4. 📖 Glossário
        5. 🛠️ Atividade Prática
        6. 📝 Quiz
        
        ---
        
        ## 🎯 Objetivos de Aprendizagem
        (Liste 3-4 objetivos claros e diretos)
        
        ## 💡 Desenvolvimento do Conteúdo
        (Desenvolva o conteúdo teórico de forma didática, dividido em tópicos ou subtítulos. Use linguagem adequada ao público {publico}. Explique os conceitos chave.)
        
        > **Dica Didática:** (Inclua uma curiosidade, analogia ou sugestão de como o professor pode explicar um ponto difícil deste tema)
        
        ## 📖 Glossário
        (Definição breve de 3-5 termos técnicos importantes citados no conteúdo)
        
        ## 🛠️ Dinâmica / Atividade Prática
        (Descrição de uma atividade prática alinhada à metodologia {metodologia}. Inclua instruções para o professor e para os alunos.)
        
        ## 📝 Quiz de Fixação
        (3 questões de múltipla escolha com gabarito ao final)
        
        **✅ Gabarito:** ...
        
        ---
        *Gere um conteúdo rico, formatado em Markdown, pronto para ser impresso ou projetado.*
        """
        
        texto_gerado_local = None
        erro_msg = ""
        # Lista de modelos para tentar em ordem de preferência (Mais rápido -> Mais robusto -> Legado)
        modelos_para_tentar = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        
        with st.spinner("🤖 Consultando o Gemini para criar sua aula..."):
            for nome_modelo in modelos_para_tentar:
                try:
                    model = genai.GenerativeModel(nome_modelo)
                    response = model.generate_content(prompt)
                    texto_gerado_local = response.text
                    st.success(f"✅ Plano de Aula gerado com sucesso! (Modelo usado: {nome_modelo})")
                    break # Se funcionou, para o loop
                except Exception as e:
                    erro_msg = str(e)
                    continue # Tenta o próximo modelo da lista
            
            if texto_gerado_local:
                st.session_state.texto_gerado = texto_gerado_local
            else:
                st.error(f"Não foi possível gerar o conteúdo com nenhum dos modelos ({', '.join(modelos_para_tentar)}).")
                st.error(f"Último erro: {erro_msg}")
                st.info("Verifique se sua chave de API está correta e se você tem acesso ao modelo Gemini.")

# Exibe o resultado se ele existir no estado da sessão
if st.session_state.texto_gerado:
    st.markdown(st.session_state.texto_gerado)
    
    # Opções de Exportação
    st.divider()
    st.subheader("📥 Exportar")
    
    c_down1, c_down2 = st.columns(2)
    with c_down1:
        st.download_button(
            label="Baixar como Texto (Markdown)",
            data=st.session_state.texto_gerado,
            file_name=f"Plano_Aula_{tema.replace(' ', '_')}.md",
            mime="text/markdown"
        )
    with c_down2:
        pdf_bytes = utils.gerar_pdf_aula_ia(st.session_state.texto_gerado)
        st.download_button(
            label="📄 Baixar como PDF",
            data=pdf_bytes,
            file_name=f"Plano_Aula_{tema.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )