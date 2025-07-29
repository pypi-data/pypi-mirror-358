class APIError(Exception):
    pass


class AuthError(APIError):
    pass


class ToolExecutionError(Exception):
    """Exception levée lors de l'exécution d'un tool"""

    pass


class UnspecifiedClassArgumentError(Exception):
    """Exception levée lorsqu'un argument requis n'est pas spécifié"""

    def __init__(self, argument_name: str):
        super().__init__(
            f"L'argument '{argument_name}' est requis mais n'a pas été spécifié."
        )
        self.argument_name = argument_name
