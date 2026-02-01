from ai_assistant import AdaptiveAssistant


def main() -> None:
    assistant = AdaptiveAssistant()
    print("Assistant IA adaptatif (entrez 'quit' pour sortir)")
    while True:
        user_input = input("> ")
        if user_input.lower() in {"quit", "exit"}:
            break
        response = assistant.interact(user_input)
        print(response)
        print(assistant.summary())


if __name__ == "__main__":
    main()
