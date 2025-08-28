import sqlite3
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "database.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@dataclass
class Municipio:
    cd_mun: str
    nm_mun: str
    objectid: Optional[int] = None
    area_km2: Optional[float] = None
    total_final_nm_ano: float = 0.0


def insert_municipio(data: Dict[str, Any]) -> None:
    keys = ", ".join(data.keys())
    placeholders = ", ".join([":" + k for k in data.keys()])
    sql = f"INSERT OR REPLACE INTO municipios ({keys}) VALUES ({placeholders})"
    with get_connection() as conn:
        conn.execute(sql, data)
        conn.commit()


def bulk_insert_municipios(rows: Iterable[Dict[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        return
    keys = list(rows[0].keys())
    sql = f"INSERT OR REPLACE INTO municipios ({', '.join(keys)}) VALUES ({', '.join(['?' for _ in keys])})"
    values = [tuple(r[k] for k in keys) for r in rows]
    with get_connection() as conn:
        conn.executemany(sql, values)
        conn.commit()


def list_municipios(limit: int = 1000, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    filters = filters or {}
    where = []
    params: List[Any] = []
    if "cd_mun" in filters:
        where.append("cd_mun = ?")
        params.append(filters["cd_mun"])
    if "nm_mun_like" in filters:
        where.append("nm_mun LIKE ?")
        params.append(f"%{filters['nm_mun_like']}%")
    if "total_min" in filters:
        where.append("total_final_nm_ano >= ?")
        params.append(filters["total_min"])
    if "total_max" in filters:
        where.append("total_final_nm_ano <= ?")
        params.append(filters["total_max"])
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"SELECT * FROM municipios {where_sql} ORDER BY total_final_nm_ano DESC LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def get_municipio_by_cd(cd_mun: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM municipios WHERE cd_mun = ?", (cd_mun,))
        row = cur.fetchone()
        return dict(row) if row else None


def upsert_fator(
    nome_residuo: str,
    fator_producao: float,
    rendimento_biogas: float,
    teor_metano: float,
    unidade: str,
    categoria: str,
) -> None:
    sql = (
        "INSERT INTO fatores_conversao (nome_residuo, fator_producao, rendimento_biogas, teor_metano, unidade, categoria) "
        "VALUES (?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(nome_residuo) DO UPDATE SET "
        "fator_producao=excluded.fator_producao, rendimento_biogas=excluded.rendimento_biogas, teor_metano=excluded.teor_metano, unidade=excluded.unidade, categoria=excluded.categoria"
    )
    with get_connection() as conn:
        conn.execute(sql, (nome_residuo, fator_producao, rendimento_biogas, teor_metano, unidade, categoria))
        conn.commit()


def list_fatores(categoria: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM fatores_conversao"
    params: Tuple[Any, ...] = ()
    if categoria:
        sql += " WHERE categoria = ?"
        params = (categoria,)
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


