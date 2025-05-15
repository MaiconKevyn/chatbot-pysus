import argparse
import json
import logging
from typing import Any, Dict, List, Tuple, Union

from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from tools import get_top_ages, get_admission_age_groups, get_top_admission_age_group, get_top_cities

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
LOGGER = logging.getLogger(__name__)

# Registry of available tools by their LangChain `.name`
TOOL_REGISTRY: Dict[str, Any] = {
    get_top_ages.name: get_top_ages,
    get_admission_age_groups.name: get_admission_age_groups,
    get_top_admission_age_group.name: get_top_admission_age_group,
    get_top_cities.name: get_top_cities
}


def build_model(model_name: str = "llama3.2") -> ChatOllama:
    """
    Cria e configura o modelo LLM para Function Calling.
    """
    return ChatOllama(
        model=model_name,
        format="json",    # Garante saída JSON para ferramentas
        temperature=0,      # Saída determinística
    )



def build_agent(model_name: str = "llama3.2") -> Any:
    """
    Vincula as ferramentas ao modelo e retorna o agente.
    """
    model = build_model(model_name)
    tools = list(TOOL_REGISTRY.values())
    return model.bind_tools(tools)

def dispatch_tool_calls(res: Any, messages: List[Any]) -> None:
    """
    Itera sobre chamadas de ferramentas sugeridas pelo LLM, executa cada uma e
    anexa o resultado ao histórico de mensagens.
    """
    for tool_call in getattr(res, "tool_calls", []):
        # Nome da ferramenta
        name = (
            tool_call["name"] if isinstance(tool_call, dict)
            else getattr(tool_call, "name", None)
        )
        LOGGER.debug("Calling tool: %s", name)

        # Seleciona a função da registry
        fn = TOOL_REGISTRY.get(name)
        if fn is None:
            LOGGER.error("Tool '%s' not found in registry", name)
            continue

        # Extrai argumentos (pode ser dict ou JSON string)
        raw_args = None
        if isinstance(tool_call, dict):
            raw_args = tool_call.get("arguments") or tool_call.get("args")
        else:
            raw_args = getattr(tool_call, "arguments", None) or getattr(tool_call, "args", None)

        args: Union[Dict[str, Any], Any] = raw_args
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                LOGGER.warning("Could not parse arguments for tool '%s'", name)
                args = {}

        # PRINT DE DEBUG: função e argumentos extraídos
        print(f"[DEBUG] Function identified: {name}, arguments: {args}")

        # Invoca a ferramenta
        tool_msg = fn.invoke(tool_call)
        messages.append(tool_msg)


def get_response(
    agent: Any,
    prompt: str,
    use_function_calling: bool = True
) -> Tuple[str, List[Any]]:
    """
    Executa a conversa com ou sem Function Calling, retornando
    o conteúdo final e o histórico de mensagens.
    """
    # Mensagens iniciais
    system_prompt = """
    Você é um assistente de saúde pública e um chatbot amigável.
    Quando receber o resultado de uma ferramenta em JSON, **não devolva o JSON cru**:
    - Interprete e explique em linguagem natural em português.
    - Use tom acolhedor: “Claro! …”, “Com certeza! …”, “Veja só: …”.
    - Seja direto na resposta principal e dê contexto breve.
    """
    messages: List[Any] = [SystemMessage(system_prompt), HumanMessage(prompt)]

    if use_function_calling:
        # Primeira invocação para detectar tool calls
        first_res = agent.invoke(messages)
        messages.append(first_res)

        # Executa e anexa resultados das ferramentas
        dispatch_tool_calls(first_res, messages)

        # Resposta final combinando LLM + resultados de ferramentas
        final_res = agent.invoke(messages)
        messages.append(final_res)
        return final_res.content, messages
    else:
        non_fc_res = agent.invoke(messages)
        messages.append(non_fc_res)
        return non_fc_res.content, messages


def interactive_loop(agent: Any) -> None:
    """
    Modo REPL de terminal: lê prompts do usuário até 'exit' ou 'quit'.
    """
    print("Iniciando modo interativo (digite 'exit' para sair)")
    while True:
        try:
            user_input = input("Você: ").strip()
            if user_input.lower() in ("exit", "quit"):
                print("Encerrando.")
                break
            answer, _ = get_response(agent, user_input, use_function_calling=True)
            print(f"Assistente: {answer}\n")
        except KeyboardInterrupt:
            print("\nEncerrando por interrupt.")
            break


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI para consultar dados de saúde pública via Function Calling"
    )
    parser.add_argument(
        "--prompt", "-p", type=str,
        help="Pergunta para o assistente"
    )
    parser.add_argument(
        "--function-calling", "-f", action="store_true",
        help="Habilita Function Calling"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="Inicia modo interativo REPL"
    )
    args = parser.parse_args()

    agent = build_agent()

    if args.interactive:
        interactive_loop(agent)
    else:
        if not args.prompt:
            parser.error("É necessário passar --prompt ou usar --interactive.")
        answer, _ = get_response(
            agent, args.prompt, use_function_calling=args.function_calling
        )
        print(answer)


if __name__ == "__main__":
    main()
