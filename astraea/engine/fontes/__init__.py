"""Canais de descoberta. Um por origem, todos cumprindo `aletheia.contrato.Fonte`.

| tipo        | o que alcança                                              | estrato usual      |
|-------------|------------------------------------------------------------|--------------------|
| `gdelt`     | notícias pelo texto, últimos ~90 dias                      | imprensa           |
| `rss`       | o fluxo de um veículo ou repositório                       | imprensa, academico|
| `lista`     | CSV curado à mão (Hemeroteca, acervos sem API)             | imprensa-historica |
"""

from __future__ import annotations

from astraea.engine.contrato import Fonte
from astraea.engine.fontes.gdelt import Gdelt
from astraea.engine.fontes.lista import Lista
from astraea.engine.fontes.rss import Rss
from astraea.engine.http import Transporte, transporte_urllib

TIPOS = {
    "rss": Rss,
    "gdelt": Gdelt,
    "lista": Lista,
}


def construir(cfg: dict, transporte: Transporte = transporte_urllib) -> Fonte:
    tipo = cfg.get("tipo")
    if tipo not in TIPOS:
        raise ValueError(f"tipo de fonte desconhecido: {tipo!r} (conhecidos: {sorted(TIPOS)})")
    if not cfg.get("id"):
        raise ValueError(f"fonte {tipo} sem id")
    return TIPOS[tipo].de_config(cfg, transporte)
