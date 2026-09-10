from scheduler import start_scheduler

def main():
    print("Starting application...")
    # Start the background ticker thread
    start_scheduler()
    
    print("REPL started. Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            # Read user input
            user_input = input(">> ").strip()
            
            # Handle exit condition
            if user_input.lower() in ("exit", "quit"):
                print("Exiting...")
                break
                
            # Eval & Print stub
            if user_input:
                print(f"You entered: {user_input}")
                
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()