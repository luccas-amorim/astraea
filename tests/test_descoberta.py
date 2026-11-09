"""Canais: gdelt e lista; e o arquivo de referência no Wayback."""

import json
from datetime import date
from urllib.parse import parse_qs, urlsplit

from astraea.engine import arquivo, fontes
from astraea.engine.fontes import gdelt


def _query(url):
    return parse_qs(urlsplit(url).query)


def test_arquivo_resolve_url_exata(rede):
    rede.responder(
        arquivo.CDX,
        json.dumps([["timestamp", "original"], ["20200101000000", "http://x.br/a"]]),
    )
    ts, url = arquivo.Arquivo(transporte=rede).resolver("https://www.x.br/a?utm_source=z")
    assert ts == "20200101000000"
    assert url == f"{arquivo.ARQUIVO}/20200101000000id_/http://x.br/a"
    q = _query(rede.pedidos[-1].url)
    assert q["matchType"] == ["exact"] and q["limit"] == ["-1"]

    rede.rotas[arquivo.CDX] = []
    rede.responder(arquivo.CDX, "[]")
    assert arquivo.Arquivo(transporte=rede).resolver("https://x.br/nunca") is None


# --- gdelt -------------------------------------------------------------------------


def test_gdelt_um_dia_por_vez_dentro_da_janela(rede, fixtures):
    rede.responder(gdelt.URL, fixtures / "gdelt" / "dia.json")
    cfg = {"tipo": "gdelt", "id": "gdelt:carandiru", "busca": "carandiru"}
    fonte = fontes.construir(cfg, rede)
    fonte.hoje = lambda: date(2026, 10, 4)
    refs = list(fonte.listar(date(2020, 1, 1)))  # anterior à janela: cortado

    consultas = [_query(p.url) for p in rede.pedidos if p.url.startswith(gdelt.URL)]
    assert len(consultas) == 91  # 90 dias de janela, mais hoje
    assert consultas[0]["startdatetime"] == ["20260706000000"]
    assert consultas[0]["enddatetime"] == ["20260707000000"]
    assert fonte.desde_efetivo == date(2026, 7, 6)  # vai para o relatório da rodada
    assert {r.id_na_fonte for r in refs} == {
        "https://noticias.exemplo.com/2026/10/02/carandiru-34-anos",
        "https://news.example.org/brazil-prison-massacre",
    }
    assert refs[0].publicado_em == date(2026, 10, 2)


def test_gdelt_dia_cheio_e_repartido_em_seis_horas(rede):
    cheio = {
        "articles": [
            {"url": f"https://x.br/{i}", "seendate": "20261002T000000Z"} for i in range(250)
        ]
    }
    rede.responder(gdelt.URL, json.dumps(cheio))
    rede.responder(gdelt.URL, json.dumps({"articles": []}))
    cfg = {"tipo": "gdelt", "id": "gdelt:x", "busca": "x"}
    fonte = fontes.construir(cfg, rede)
    fonte.hoje = lambda: date(2026, 10, 2)
    list(fonte.listar(date(2026, 10, 2)))
    api = [p for p in rede.pedidos if p.url.startswith(gdelt.URL)]
    faixas = [_query(p.url)["startdatetime"][0] for p in api][1:]
    assert faixas == ["20261002000000", "20261002060000", "20261002120000", "20261002180000"]


# --- lista -------------------------------------------------------------------------


def test_lista_le_csv_relativo_ao_config(rede, tmp_path, fixtures):
    (tmp_path / "listas").mkdir()
    (tmp_path / "listas" / "hemeroteca.csv").write_text(
        "url,titulo,publicado_em\n"
        "https://memoria.bn.br/doc/1,Jornal do Brasil 3/10/1992,1992-10-03\n"
        "https://memoria.bn.br/doc/2,,data-ruim\n"
        ",sem url,\n",
        encoding="utf-8",
    )
    cfg = {"tipo": "lista", "id": "lista:hemeroteca", "arquivo": "listas/hemeroteca.csv",
           "_diretorio_config": str(tmp_path)}  # fmt: skip
    fonte = fontes.construir(cfg, rede)
    refs = list(fonte.listar(date(1990, 1, 1)))
    assert [r.url for r in refs] == ["https://memoria.bn.br/doc/1", "https://memoria.bn.br/doc/2"]
    assert refs[0].publicado_em == date(1992, 10, 3) and refs[1].publicado_em is None
    assert refs[0].titulo == "Jornal do Brasil 3/10/1992"
    rede.responder("https://memoria.bn.br/doc/1", fixtures / "wayback" / "captura.html")
    assert fonte.sentinela(fonte.baixar(refs[0]))
