import argparse
from agent import build_agent, get_response

def interactive_loop(agent):
    print("Modo interativo (digite 'exit' ou 'quit' para sair)\n")
    while True:
        try:
            prompt = input("Você: ").strip()
            if prompt.lower() in ("exit", "quit"):
                print("Até mais!")
                break

            resposta, _ = get_response(agent, prompt, use_function_calling=True)
            print(f"Assistente: {resposta}\n")
        except KeyboardInterrupt:
            print("\nAté mais!")
            break

def main():
    parser = argparse.ArgumentParser(
        description="Chat CLI para consultar dados de saúde pública via Function Calling"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        help="Pergunta para o assistente (ex: 'Qual a taxa de mortalidade em Porto Alegre em 2019?')"
    )
    parser.add_argument(
        "--function-calling", "-f",
        action="store_true",
        help="Habilita o uso de Function Calling para execução de ferramentas"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Entra em modo interativo de terminal (REPL)"
    )
    args = parser.parse_args()

    # Instancia o agente com as ferramentas registradas
    agent = build_agent()

    # Se modo interativo foi pedido, entra no loop
    if args.interactive:
        interactive_loop(agent)
        return

    # Modo “one-shot” tradicional
    if not args.prompt:
        parser.error("Você precisa passar --prompt ou usar --interactive para modo interativo.")
    resposta, historico = get_response(agent, args.prompt, use_function_calling=args.function_calling)

    # Exibe resposta final e histórico (opcional)
    print("\n=== Resposta do Assistente ===")
    print(resposta)
    # Se quiser, descomente para ver histórico completo:
    # for msg in historico: print(msg)

if __name__ == "__main__":
    main()


# #!/usr/bin/env python3
# import argparse
# from agent import build_agent, get_response
#
#
# def main():
#     parser = argparse.ArgumentParser(
#         description="Chat CLI para consultar dados de saúde pública via Function Calling"
#     )
#     parser.add_argument(
#         "--prompt", "-p",
#         type=str,
#         required=True,
#         help="Pergunta para o assistente (ex: 'Qual a taxa de mortalidade em Porto Alegre em 2019?')"
#     )
#     parser.add_argument(
#         "--function-calling", "-f",
#         action="store_true",
#         help="Habilita o uso de Function Calling para execução de ferramentas"
#     )
#     args = parser.parse_args()
#
#     # Instancia o agente com as ferramentas registradas
#     agent = build_agent()
#
#     # Executa a conversa e obtém resposta e histórico
#     resposta, historico = get_response(agent, args.prompt, use_function_calling=args.function_calling)
#
#     # Exibe resposta final
#     print("\n=== Resposta do Assistente ===")
#     print(resposta)
#
#     # Exibe histórico completo (útil para debug)
#     print("\n=== Histórico de Mensagens ===")
#     for msg in historico:
#         role = getattr(msg, "role", msg.type)
#         content = getattr(msg, "content", str(msg))
#         print(f"[{role}] {content}")
#
#
# if __name__ == "__main__":
#     main()
