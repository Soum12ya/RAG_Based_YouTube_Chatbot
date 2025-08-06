from langchain_google_genai import ChatGoogleGenerativeAI

def get_answer(prompt: str, model_name: str = "gemini-2.5-pro") -> str:
    try:
        model = ChatGoogleGenerativeAI(model=model_name)
        response = model.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"LLM error: {e}"