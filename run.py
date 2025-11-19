from agent.main_agent import ConciergeAgent

def main():
    agent = ConciergeAgent()
    print("Concierge Agent v0.1 — type 'exit' to quit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        
        # -------------------------------
        # Notes Tool CLI Commands
        # -------------------------------
        
        if user_input.startswith("note add "):
            from agent.tools.notes_tool import add_note
            content = user_input.replace("note add ", "")
            note = add_note(content)
            print("Note added:", note)
            continue

        if user_input == "note list":
            from agent.tools.notes_tool import list_notes
            print(list_notes())
            continue

        if user_input.startswith("note search "):
            from agent.tools.notes_tool import search_notes
            keyword = user_input.replace("note search ", "")
            print(search_notes(keyword))
            continue

        # -------------------------------
        # Tasks Tool CLI Commands
        # -------------------------------
        
        if user_input.startswith("task add "):
            from agent.tools.tasks_tool import add_task
            title = user_input.replace("task add ", "")
            task = add_task(title)
            print("Task added:", task)
            continue

        if user_input == "task list":
            from agent.tools.tasks_tool import list_tasks
            print(list_tasks())
            continue

        if user_input.startswith("task complete "):
            from agent.tools.tasks_tool import complete_task
            try:
                task_id = int(user_input.replace("task complete ", ""))
            except ValueError:
                print("Task ID must be a number.")
                continue
            result = complete_task(task_id)
            print("Task update:", result)
            continue
        
        # -------------------------------
        # Search Tool CLI Command
        # -------------------------------
        
        if user_input.startswith("search "):
            from agent.tools.search_tool import search
            query = user_input.replace("search ", "")
            results = search(query)
            print(results)
            continue

        # NORMAL AGENT FLOW
        reply = agent.ask(user_input)
        print(f"Agent: {reply}\n")

if __name__ == "__main__":
    main()
