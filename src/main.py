import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="Summarize a GitHub repository with an LLM")
    parser.add_argument("--host",
                        default="127.0.0.1",
                        help="FastAPI host ip (default: 127.0.0.1)")
    parser.add_argument("--port",
                        type=int,
                        default=8000,
                        help="FastAPI port (default: 8000)")
    args = parser.parse_args()

    uvicorn.run("web_api:app", host=args.host, port=args.port)

if __name__ == "__main__":
    main()