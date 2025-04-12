import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import mlflow
from dotenv import load_dotenv
from app.rag_pipeline import load_vectorstore_from_disk, build_chain

from langchain_openai import ChatOpenAI
from langchain.evaluation.qa import QAEvalChain
from langchain.evaluation.criteria import LabeledCriteriaEvalChain


load_dotenv()

# Configuración
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1_asistente_rrhh")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
DATASET_PATH = "tests/eval_dataset.json"

criteria = {
        "correctness"  :   ("¿Es correcta la respuesta?"),
        "relevance"    :   ("¿Es relevante respecto a la pregunta?"),
        "coherence"    :   ("¿Está bien estructurada la respuesta?"),
        "toxicity"     :   ("¿Contiene lenguaje ofensivo o riesgoso?"),
        "harmfulness"  :   ("¿Podría causar daño la información?")
    }


# Cargar dataset
with open(DATASET_PATH) as f:
    dataset = json.load(f)

# Vectorstore y cadena
vectordb = load_vectorstore_from_disk()
chain = build_chain(vectordb, prompt_version=PROMPT_VERSION)

# LangChain Evaluator
llm = ChatOpenAI(temperature=0)
langchain_eval = QAEvalChain.from_llm(llm)
langchain_criteria = LabeledCriteriaEvalChain.from_llm(
    llm=llm,
    criteria=criteria,
)

# ✅ Establecer experimento una vez
mlflow.set_experiment(f"eval_{PROMPT_VERSION}")
print(f"📊 Experimento MLflow: eval_{PROMPT_VERSION}")

# Evaluación por lote
for i, pair in enumerate(dataset):
    pregunta = pair["question"]
    respuesta_esperada = pair["answer"]

    with mlflow.start_run(run_name=f"eval_q{i+1}"):
        result = chain.invoke({"question": pregunta, "chat_history": []})
        respuesta_generada = result["answer"]

        # Evaluación con LangChain
        graded = langchain_eval.evaluate_strings(
            input=pregunta,
            prediction=respuesta_generada,
            reference=respuesta_esperada
        )
        
        crit = langchain_criteria.evaluate_strings(
            input=pregunta,
            prediction=respuesta_generada,
            reference=respuesta_esperada
        )

        # 🔍 Imprimir el contenido real
        print(f"\n📦 Resultado evaluación LangChain para pregunta {i+1}/{len(dataset)}:")
        print(graded)

        lc_verdict = graded.get("value", "UNKNOWN")
        is_correct = graded.get("score", 0)

        # Log en MLflow
        mlflow.log_param("question", pregunta)
        mlflow.log_param("prompt_version", PROMPT_VERSION)
        mlflow.log_param("chunk_size", CHUNK_SIZE)
        mlflow.log_param("chunk_overlap", CHUNK_OVERLAP)

        mlflow.log_metric("lc_is_correct", is_correct)
        mlflow.log_metric("criteria",    crit.get('score',0))
        mlflow.log_text(crit.get('reasoning'), "full_reasoning.txt")


        print(f"✅ Pregunta: {pregunta}")
        print(f"🧠 LangChain Eval: {lc_verdict}")
        print(f"👌 LangChain Eval w criteria: { crit.get('score',0)}, reasoning {crit.get('reasoning')} ")
