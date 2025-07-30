from jadio_llmnet.core import persistence

def run(args=None):
    if not args:
        print("Usage: llmnet persist --enable | --disable")
        return

    if args[0] == "--enable":
        persistence.enable()
    elif args[0] == "--disable":
        persistence.disable()
    else:
        print("Usage: llmnet persist --enable | --disable")
