from .gigachat_entrypoint import GigaChatEntryPoint


class GigaMaxEntryPoint(GigaChatEntryPoint):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        model_id: str = "GigaChat-Max",
        warmup: bool = False,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(
            client_id=client_id, client_secret=client_secret, model_id=model_id, warmup=warmup, temperature=temperature
        )


class GigaMax2EntryPoint(GigaChatEntryPoint):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        model_id: str = "GigaChat-2-Max",
        warmup: bool = False,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(
            client_id=client_id, client_secret=client_secret, model_id=model_id, warmup=warmup, temperature=temperature
        )
