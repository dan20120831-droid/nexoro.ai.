from agent.agent import run_agent


def main():
    print("🤖 NEXORA AI запущен.")
    print("Введите задачу или 'exit' для выхода.")

    while True:
        try:
            task = input("\nNEXORA > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход.")
            break

        if task.lower() in {"exit", "quit", "выход"}:
            print("Выход.")
            break

        if not task:
            continue

        try:
            print("\nNEXORA AI:\n")
            print(run_agent(task))
        except Exception as error:
            print(f"\n❌ Ошибка NEXORA: {error}")


if __name__ == "__main__":
    main()
