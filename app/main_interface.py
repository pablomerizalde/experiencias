# app/main_interface.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
st.set_page_config(page_title="📚 Chatbot GenAI + Métricas", layout="wide")

import pandas as pd
import mlflow
import json
from app.rag_pipeline import load_vectorstore_from_disk, build_chain


PROMPT_VERSION = 'v1_asistente_cocina'
modo = st.sidebar.radio("Selecciona una vista:", ["🤖 Chatbot", "📊 Métricas"])

vectordb = load_vectorstore_from_disk()
chain = build_chain(vectordb, PROMPT_VERSION)

if modo == "🤖 Chatbot":
    st.title("🤖 Asistente de Cocina 🍕")
    pregunta = st.text_input("¿Qué deseas consultar?")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if pregunta:
        with st.spinner("Consultando en la deliciosa base de datos..."):
            result = chain.invoke({"question": pregunta, "chat_history": st.session_state.chat_history})
            st.session_state.chat_history.append((pregunta, result["answer"]))

    if st.session_state.chat_history:
        for q, a in reversed(st.session_state.chat_history):
            st.markdown(f"**👤 Usuario:** {q}")
            st.markdown(f"**🤖 Bot:** {a}")
            st.markdown("---")

elif modo == "📊 Métricas":
    st.title("📈 Resultados de Evaluación")

    client = mlflow.tracking.MlflowClient()
    experiments = [exp for exp in client.search_experiments() if exp.name.startswith("eval_")]

    if not experiments:
        st.warning("No se encontraron experimentos de evaluación.")
        st.stop()

    exp_names = [exp.name for exp in experiments]
    selected_exp = st.selectbox("Selecciona un experimento:", exp_names)

    experiment = client.get_experiment_by_name(selected_exp)
    runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"])

    if not runs:
        st.warning("No hay ejecuciones registradas.")
        st.stop()

    # Armar dataframe
    data = []
    artifact_path = "full_reasoning.txt"
    for run in runs:
        params = run.data.params
        metrics = run.data.metrics
        try:
            artifact_uri = os.path.join(run.info.artifact_uri, artifact_path)
            local_path = client.download_artifacts(run.info.run_id, artifact_path)
            print(local_path)
            
            with open(local_path, "r") as f:
                full_response = f.read()
        except Exception as e:
            full_response = '' 
    
        data.append({
            "Pregunta": params.get("question"),
            "Prompt": params.get("prompt_version"),
            "Chunk Size": int(params.get("chunk_size", 0)),
            "Chunk Overlap": int(params.get("chunk_overlap", 0)),
            "Correcto (LC)": metrics.get("lc_is_correct", 0),
            "Correcto con criterios": metrics.get("criteria"),
            "razonamiento": full_response 
        })

    df = pd.DataFrame(data)
    st.dataframe(df)

    # Agrupado
    st.subheader("📊 Promedio por configuración")
    metricas = ['Correcto (LC)','Correcto con criterios']
    selected_exp = st.selectbox("Selecciona una metrica:", metricas)
    agrupacion = ['mean', 'sum', 'median', 'std', 'var', 'min']
    selected_agg = st.selectbox("Selecciona una agrupación:", agrupacion)
    grouped = df.groupby(["Prompt", "Chunk Size", "Chunk Overlap"]).agg({selected_exp: selected_agg}).reset_index()
    grouped.rename(columns={selected_exp: "Precisión"}, inplace=True)
    grouped["config"] = grouped["Prompt"] + " | " + grouped["Chunk Size"].astype(str) + " | " + grouped["Chunk Overlap"].astype(str)
    st.bar_chart(grouped.set_index("config")["Precisión"])
