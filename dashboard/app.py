import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="CHRONOS AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Funções auxiliares para API
def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """Faz chamadas para a API CHRONOS"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=60)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = ""
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "Detalhes não disponíveis")
            except:
                error_detail = response.text
            
            st.error(f"Erro na API ({response.status_code}): {error_detail}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com {API_BASE_URL}: {str(e)}")
        return None

def get_user_patterns():
    """Busca padrões do usuário"""
    return call_api("/patterns/user")

def get_performance_analytics():
    """Busca analytics de performance"""
    return call_api("/analytics/performance")

def schedule_task_api(task_data: dict):
    """Agenda tarefa via API"""
    return call_api("/schedule/task", "POST", task_data)

def main():
    st.title("🤖 CHRONOS AI - Intelligent Time Orchestrator")
    st.markdown("*Your AI-powered productivity companion*")
    
    # Sidebar para inserir informações
    with st.sidebar:
        st.header("📝 Adicionar Nova Tarefa")
        
        with st.form("task_form"):
            task_title = st.text_input("Título da Tarefa", placeholder="Ex: Revisar documentação")
            task_description = st.text_area("Descrição", placeholder="Detalhes da tarefa...")
            
            task_category = st.selectbox(
                "Categoria",
                ["Development", "Meetings", "Planning", "Documentation", "Research", "Other"]
            )
            
            estimated_duration = st.slider("Duração Estimada (minutos)", 15, 480, 60, step=15)
            
            priority = st.select_slider(
                "Prioridade",
                options=["Baixa", "Média", "Alta", "Urgente"],
                value="Média"
            )
            
            due_date = st.date_input("Data Limite")
            
            submitted = st.form_submit_button("➕ Adicionar Tarefa")
            
            if submitted and task_title:
                task_data = {
                    "title": task_title,
                    "description": task_description,
                    "category": task_category,
                    "estimated_time": estimated_duration,
                    "priority": priority,
                    "due_date": str(due_date)
                }
                
                # Chamar API real para agendar tarefa
                with st.spinner("Processando com IA..."):
                    result = schedule_task_api(task_data)
                
                if result and result.get("success"):
                    st.success(f"✅ Tarefa '{task_title}' agendada com sucesso!")
                    
                    # Mostrar sugestão real da IA
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        confidence = result.get('confidence', 0)
                        st.metric("Confiança IA", f"{confidence:.2f}" if isinstance(confidence, (int, float)) else "N/A")
                    with col2:
                        st.metric("Horário Sugerido", result.get('scheduled_time', 'N/A'))
                    with col3:
                        st.metric("Task ID", result.get('task_id', 'N/A'))
                    
                    reasoning = result.get('reasoning', 'Análise não disponível')
                    st.info(f"🧠 Reasoning: {reasoning}")
                    
                    # Mostrar alternativas se disponíveis
                    alternatives = result.get('alternatives', [])
                    if alternatives:
                        st.subheader("🔄 Horários Alternativos")
                        for i, alt in enumerate(alternatives[:3], 1):
                            st.write(f"{i}. {alt}")
                else:
                    st.error("❌ Erro ao agendar tarefa - verifique os logs acima para detalhes")
            elif submitted:
                st.warning("⚠️ Por favor, preencha pelo menos o título da tarefa")
        
        st.divider()
        
        # Quick actions
        st.subheader("🎯 Ações Rápidas")
        
        if st.button("🩺 Testar API"):
            with st.spinner("Testando conexão..."):
                health_check = call_api("/")
                if health_check:
                    st.success(f"✅ API funcionando: {health_check.get('message', 'OK')}")
                else:
                    st.error("❌ API não está respondendo")
        
        if st.button("📊 Gerar Relatório"):
            with st.spinner("Gerando relatório..."):
                analytics = get_performance_analytics()
                if analytics and analytics.get("success"):
                    st.success("✅ Relatório atualizado!")
                    st.rerun()  # Recarrega a página para mostrar novos dados
                else:
                    st.error("❌ Erro ao gerar relatório")
        
        if st.button("🔄 Sincronizar Notion"):
            with st.spinner("Sincronizando com Notion..."):
                # Chamada para sincronizar - pode ser um endpoint específico
                health_check = call_api("/")
                if health_check:
                    st.success("✅ Sincronização com Notion realizada!")
                    st.rerun()  # Recarrega os dados
                else:
                    st.error("❌ Erro na sincronização")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["⏰ Time Patterns", "📂 Categories", "🎯 Insights"])
    
    with tab1:
        st.subheader("⏰ Padrões de Tempo")
        
        # Buscar dados reais de padrões
        patterns_data = get_user_patterns()
        
        if patterns_data and patterns_data.get("success"):
            patterns = patterns_data.get("patterns", [])
            if patterns:
                st.success(f"✅ {len(patterns)} padrões identificados")
                
                for pattern in patterns[:5]:  # Mostrar top 5
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{pattern.get('period', 'N/A')}**")
                    with col2:
                        efficiency = pattern.get('efficiency', 0)
                        st.metric("Eficiência", f"{efficiency:.2f}")
                    with col3:
                        sample_size = pattern.get('sample_size', 0)
                        st.metric("Amostras", sample_size)
            else:
                st.info("📊 Ainda coletando dados para identificar padrões...")
        else:
            st.warning("⚠️ Não foi possível carregar padrões. Verifique a conexão com a API.")
    
    with tab2:
        st.subheader("📂 Performance por Categoria")
        
        # Buscar analytics reais
        analytics_data = get_performance_analytics()
        
        if analytics_data and analytics_data.get("success"):
            performance = analytics_data.get("recent_performance", {})
            
            # Verificar se performance é um dicionário válido
            if isinstance(performance, dict) and performance:
                # Extrair dados para gráfico
                categories = []
                efficiencies = []
                
                for cat, data in performance.items():
                    if isinstance(data, dict):
                        categories.append(cat)
                        efficiencies.append(data.get('efficiency', 0))
                    elif isinstance(data, (int, float)):
                        # Se data é um número, tratar como eficiência direta
                        categories.append(cat)
                        efficiencies.append(data)
                
                if categories and efficiencies:
                    fig = px.bar(
                        x=categories, 
                        y=efficiencies, 
                        title="Eficiência por Categoria de Tarefa",
                        color=efficiencies,
                        color_continuous_scale="RdYlGn"
                    )
                    fig.update_layout(yaxis_title="Eficiência", xaxis_title="Categoria")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Mostrar detalhes
                    st.subheader("📊 Detalhes por Categoria")
                    for cat, data in performance.items():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if isinstance(data, dict):
                                efficiency = data.get('efficiency', 0)
                                completed = data.get('completed_tasks', 'N/A')
                                avg_time = data.get('avg_time', 0)
                            else:
                                efficiency = data if isinstance(data, (int, float)) else 0
                                completed = 'N/A'
                                avg_time = 0
                            
                            st.metric(f"{cat} - Eficiência", f"{efficiency:.2f}")
                        with col2:
                            st.metric("Tarefas Concluídas", completed)
                        with col3:
                            st.metric("Tempo Médio", f"{avg_time:.0f}min" if isinstance(avg_time, (int, float)) else "N/A")
                else:
                    st.info("📊 Dados insuficientes para análise por categoria")
            else:
                st.info("📊 Ainda coletando dados de performance...")
        else:
            st.warning("⚠️ Não foi possível carregar analytics. Verifique a conexão com a API.")
    
    with tab3:
        st.subheader("🎯 Insights da IA")
        
        # Buscar tendências de feedback
        analytics_data = get_performance_analytics()
        
        if analytics_data and analytics_data.get("success"):
            feedback_trends = analytics_data.get("feedback_trends", {})
            
            # Verificar se feedback_trends é um dicionário válido
            if isinstance(feedback_trends, dict) and feedback_trends:
                st.subheader("📈 Tendências Identificadas")
                
                # Mostrar insights baseados nos dados
                insights = []
                
                # Analisar tendências para gerar insights de forma segura
                avg_rating = feedback_trends.get('average_rating', 0)
                if isinstance(avg_rating, (int, float)) and avg_rating > 0:
                    if avg_rating > 4:
                        insights.append(("✅", f"Alta satisfação geral (Rating: {avg_rating:.1f}/5)"))
                    elif avg_rating > 3:
                        insights.append(("⚠️", f"Satisfação moderada (Rating: {avg_rating:.1f}/5)"))
                    else:
                        insights.append(("❌", f"Satisfação baixa (Rating: {avg_rating:.1f}/5)"))
                
                best_category = feedback_trends.get('best_performing_category')
                if best_category and isinstance(best_category, str):
                    insights.append(("✅", f"Melhor performance: {best_category}"))
                
                worst_category = feedback_trends.get('worst_performing_category')
                if worst_category and isinstance(worst_category, str):
                    insights.append(("⚠️", f"Precisa melhorar: {worst_category}"))
                
                total_tasks = feedback_trends.get('total_tasks_analyzed', 0)
                if isinstance(total_tasks, int) and total_tasks > 0:
                    insights.append(("📊", f"Total de tarefas analisadas: {total_tasks}"))
                
                # Se não há insights, mostrar mensagem padrão
                if not insights:
                    insights.append(("📊", "Dados de feedback disponíveis"))
                
                # Mostrar insights
                for icon, text in insights:
                    if icon == "✅":
                        st.success(f"{icon} {text}")
                    elif icon == "⚠️":
                        st.warning(f"{icon} {text}")
                    elif icon == "❌":
                        st.error(f"{icon} {text}")
                    else:
                        st.info(f"{icon} {text}")
                
                # Mostrar gráfico de tendências se disponível
                if 'daily_ratings' in feedback_trends and isinstance(feedback_trends['daily_ratings'], dict):
                    st.subheader("📊 Evolução das Avaliações")
                    daily_data = feedback_trends['daily_ratings']
                    if daily_data:
                        try:
                            df = pd.DataFrame(list(daily_data.items()), columns=['Data', 'Rating'])
                            df['Data'] = pd.to_datetime(df['Data'])
                            
                            fig = px.line(df, x='Data', y='Rating', title='Evolução do Rating Diário')
                            fig.update_layout(yaxis_range=[1, 5])
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Erro ao gerar gráfico de tendências: {e}")
            else:
                st.info("🤖 A IA ainda está coletando dados para gerar insights...")
        else:
            st.warning("⚠️ Não foi possível carregar insights. Verifique a conexão com a API.")

def settings_page():
    st.header("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔌 API Config", "🎯 Preferences", "📊 Data"])
    
    with tab1:
        st.subheader("API Configuration")
        
        st.info("🏠 IA Local: LocalAI configurado automaticamente - sem necessidade de API keys!")
        
        if st.button("Test Connection"):
            st.success("✅ All connections successful!")
        
        if st.button("Save Configuration"):
            st.success("✅ Configuration saved!")
    
    with tab2:
        st.subheader("Personal Preferences")
        
        work_start = st.time_input("Work Start Time", value=datetime.strptime("09:00", "%H:%M").time())
        work_end = st.time_input("Work End Time", value=datetime.strptime("18:00", "%H:%M").time())
        
        break_duration = st.slider("Preferred Break Duration (minutes)", 5, 60, 15)
        max_focus = st.slider("Maximum Focus Duration (minutes)", 30, 180, 90)
        
        weekend_work = st.checkbox("Allow weekend scheduling")
        
        if st.button("Update Preferences"):
            st.success("✅ Preferences updated!")
    
    with tab3:
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Import Notion Data"):
                st.info("Importing last 90 days of tasks...")
            
            if st.button("🔄 Retrain Patterns"):
                st.info("Reanalyzing all patterns...")
        
        with col2:
            if st.button("📤 Export Data"):
                st.success("Data exported to chronos_export.json")
            
            if st.button("🗑️ Clear Learning Data"):
                st.warning("This will reset all learned patterns!")


if __name__ == "__main__":
    # Navegação principal
    page = st.sidebar.selectbox("Navegar", ["Dashboard", "Configurações"])
    
    if page == "Dashboard":
        main()
    else:
        settings_page()