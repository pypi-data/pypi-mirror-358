def entrypoint() -> None:
    import argparse

    import uvicorn

    from .config import get_settings

    s = get_settings()
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--host", default=s.HOST)
    parser.add_argument("--port", type=int, default=s.PORT)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    uvicorn.run(
        "phoenix_ai_audit_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )
