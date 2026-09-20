"""Excepciones de negocio. La capa API las traduce a códigos HTTP."""


class ReglaNegocioError(Exception):
    """Se viola una regla de negocio (stock insuficiente, préstamo ya liquidado...). -> 400"""


class NoEncontradoError(Exception):
    """El recurso solicitado no existe. -> 404"""


class PermisoError(Exception):
    """El usuario no puede operar sobre ese recurso. -> 403"""
