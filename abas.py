import streamlit as st

# Crie um botão para ativar a troca de abas
if st.button("Clique para trocar de aba"):
    # Quando o botão é clicado, altere o valor da guia selecionada para a aba desejada
    st.session_state.selected_tab = "Aba 2"

# Use guias para criar o layout com diferentes abas
with st.expander("Navegar por abas"):
    selected_tab = st.radio("Selecione a aba:", ["Aba 1", "Aba 2"])

    # Guarde a guia selecionada no estado da sessão
    st.session_state.selected_tab = selected_tab

# Exiba conteúdo com base na guia selecionada
if st.session_state.selected_tab == "Aba 1":
    st.write("Conteúdo da Aba 1")
else:
    st.write("Conteúdo da Aba 2")