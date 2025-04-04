# 📘 README Template para estudiantes: Chatbot GenAI con GenAIOps

## 🎯 Objetivo
Crear un chatbot basado en LLMs (GPT) que responda preguntas sobre documentos PDF. El proyecto aplica prácticas de GenAIOps incluyendo versionado, evaluación, trazabilidad y visualización de resultados.

---

## 🚀 Cómo usar este repositorio

### 1. Clona el repositorio y entra al proyecto
```bash
git clone https://github.com/darkanita/GenAIOps_Pycon2025.git
cd GenAIOps_Pycon2025
```

### 2. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 3. Configura tu clave de OpenAI
Crea un archivo `.env` con el siguiente contenido:
```env
OPENAI_API_KEY=sk-xxxxxx
```

### 4. Ejecuta la app
```bash
streamlit run app/main_interface.py
```

---

## 🧠 ¿Qué aprenderás?
✅ Ingesta y chunking de PDFs  
✅ Indexación con FAISS y embeddings de OpenAI  
✅ Construcción de RAG pipeline (Retrieval Augmented Generation)  
✅ Evaluación automática de respuestas con DeepEval  
✅ Tracking con MLflow  
✅ Versionamiento de datos con DVC  
✅ Exportación de métricas a CSV y PDF  
✅ Visualización con Streamlit

---

## 🗂️ Estructura del proyecto
```
/genaiops_chatbot_rag/
├── app/                     # Código principal (chatbot + dashboard)
├── data/pdfs/              # PDFs cargados por los usuarios
├── vectorstore/            # Índice de vectores (FAISS)
├── mlruns/                 # Directorio de experimentos MLflow
├── .env                    # Clave API de OpenAI
├── Dockerfile              # Para contenedores
├── dvc.yaml                # Pipeline DVC (opcional)
├── requirements.txt        # Dependencias
```

---

## 🛠️ Herramientas usadas
- **OpenAI / LangChain**: modelo LLM y flujo de RAG
- **MLflow**: seguimiento de prompts y respuestas
- **DVC**: control de versiones de datos y embeddings
- **Streamlit**: interfaz web
- **DeepEval**: evaluación automática de respuestas
- **FAISS**: motor de búsqueda semántica local
- **FPDF + Matplotlib**: generación de PDF con gráficas

---

## 📤 Exportación de resultados
- Puedes descargar métricas como `.csv`
- También puedes generar reportes automáticos en `.pdf` con resumen y gráfico de relevancia

---

## 🧪 Extra: ejecutar con Docker
```bash
# Construir la imagen
docker build -t chatbot-genaiops .

# Ejecutar el contenedor (usando el .env local)
docker run --env-file .env -p 8501:8501 chatbot-genaiops
```

---

## 📌 Notas para estudiantes
- Prueba diferentes versiones de prompts y analiza su impacto
- Revisa las métricas en MLflow
- Explora cómo cambiar chunk size o temperatura afecta las respuestas
- Agrega tu propia métrica si te animas 😉

¡Mucho éxito construyendo tu app GenAI con buenas prácticas! 🚀
