import pandas as pd, json, os, sys, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
# Carpeta con los datos crudos (por defecto, la raíz del proyecto; no se suben a GitHub)
POS = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC = POS[0] if POS else os.path.dirname(HERE)
# --out=RUTA: archivo de salida (por defecto index.html en la raíz del proyecto)

# Periodos del Campus Virtual, en orden cronológico: (archivo, etiqueta, fecha inicial, fecha final)
PERIODOS = [
    ("USABILIDAD ESTUDIANTE20262.xlsx", "1 ago – 28 sep", "2026-08-01", "2026-09-28"),
]
# Nivel de uso en el Campus: minutos al día para nivel alto y medio (por debajo, bajo)
NIVELES = (20, 5)
# Configurable Reports corta los informes en este número de filas
LIMITE_MOODLE = 5000

# Métricas del Campus por periodo, en el orden en que se envían al tablero
CAMPUS = [
    "tiempo_dedicado_minutos", "dias_con_actividad_periodo", "inicios_sesion_periodo",
    "contenidos_consultados_periodo", "actividades_completadas_periodo", "examenes_realizados_periodo",
    "tareas_entregadas_periodo", "participacion_foros_periodo", "acciones_totales_periodo",
    "cursos_visitados_periodo",
]
# Categorías transversales: no identifican la facultad ni el programa del estudiante
TRANSVERSAL_FAC = {"Centro de Plurilingüismo", "Departamento de Estudios Generales"}
TRANSVERSAL_PROG = {"Plurilingüismo", "Departamento de Estudios Generales"}
SOLO_TRANSVERSAL = "Solo cursos transversales"
NOMBRE_FAC = {"Facultad de ingenieria": "Facultad de Ingeniería", "OTROS": "Otros"}
NOMBRE_MOD = {"PREGRADO PRESENCIAL": "Pregrado presencial", "DISTANCIA": "Distancia", "POSGRADO": "Posgrado"}

fix = lambda s: re.sub("�+", "Ñ", str(s).strip())
tokens = lambda s: [t.strip() for t in str(s).split("|") if t.strip()] if pd.notna(s) else []

# --- Campus Virtual ---
frames, meta, trunc = [], [], []
for i, (f, label, ini, fin) in enumerate(PERIODOS):
    d = pd.read_excel(os.path.join(SRC, f))
    # La consulta de un solo rango llama «porcentaje_avance» a la columna de avance
    d = d.rename(columns={"porcentaje_avance": "porcentaje_avance_al_cierre"})
    if len(d) == LIMITE_MOODLE:
        trunc.append(label)
    ini, fin = pd.Timestamp(ini), pd.Timestamp(fin)
    fin_exclusivo = fin + pd.Timedelta(days=1)
    # Si el informe se generó antes de terminar el periodo, los días se cuentan hasta la última acción
    ult = pd.to_datetime(d.ultima_accion_periodo.replace("Sin actividad", None).dropna()).max()
    parcial = pd.notna(ult) and ult < fin_exclusivo - pd.Timedelta(hours=1)
    dias = round((ult - ini).total_seconds() / 86400, 2) if parcial else (fin_exclusivo - ini).days
    meta.append({"label": label, "days": dias,
                 "note": f"corte {ult.strftime('%d/%m %H:%M')}" if parcial else "semana completa" if dias == 7 else f"{dias} días completos"})
    frames.append(d.set_index("userid").add_suffix(f"__{i}"))

m = pd.concat(frames, axis=1, join="outer").reset_index()
N = len(PERIODOS)

def first(r, col):
    for i in range(N):
        v = r.get(f"{col}__{i}")
        if pd.notna(v):
            return v
    return None

rows = []
for _, r in m.iterrows():
    facs = sorted({NOMBRE_FAC.get(t, t) for t in tokens(first(r, "facultad")) if t not in TRANSVERSAL_FAC})
    # Las categorías «FACULTAD DE …» son cursos directos de la facultad, no programas
    progs = sorted({t for t in tokens(first(r, "programa")) if t not in TRANSVERSAL_PROG and not t.upper().startswith("FACULTAD")})
    mods = sorted({NOMBRE_MOD.get(t, t.capitalize()) for t in tokens(first(r, "modalidad"))}) if "modalidad__0" in r.index else []
    per = []
    for i in range(N):
        if pd.isna(r.get(f"acciones_totales_periodo__{i}")):
            per.append(None)  # El estudiante no aparece en el informe de ese periodo
        else:
            per.append([int(r[f"{c}__{i}"]) for c in CAMPUS] + [round(float(r[f"porcentaje_avance_al_cierre__{i}"]), 1)])
    ult = [str(r.get(f"ultima_accion_periodo__{i}")) for i in range(N) if pd.notna(r.get(f"ultima_accion_periodo__{i}"))]
    ult = max([u for u in ult if u[:2] == "20"], default="")
    rows.append({"user": str(first(r, "estudiante")).strip().lower(), "name": fix(first(r, "nombre_estudiante")), "last": ult, "mods": mods,
                 "facs": facs or [SOLO_TRANSVERSAL], "progs": progs, "cursos": int(first(r, "cursos_matriculados") or 0), "per": per})

# Facultad de cada programa: la que más se repite entre los estudiantes de una sola facultad
co = collections.defaultdict(collections.Counter)
for s in rows:
    if len(s["facs"]) == 1:
        for p in s["progs"]:
            co[p][s["facs"][0]] += 1
facs = sorted({f for s in rows for f in s["facs"]}, key=lambda f: (f == SOLO_TRANSVERSAL, f))
fac_idx = {f: i for i, f in enumerate(facs)}
progs = sorted({p for s in rows for p in s["progs"]})
prog_idx = {p: i for i, p in enumerate(progs)}
prog_fac = [fac_idx[co[p].most_common(1)[0][0]] if co[p] else -1 for p in progs]
mods = sorted({m for s in rows for m in s["mods"]}, key=lambda m: list(NOMBRE_MOD.values()).index(m) if m in NOMBRE_MOD.values() else 99)
mod_idx = {m: i for i, m in enumerate(mods)}

data = {
    "p": meta, "trunc": trunc, "limit": LIMITE_MOODLE, "lv": NIVELES, "mods": mods,
    "facs": facs, "progs": [[p, prog_fac[i]] for i, p in enumerate(progs)],
    "s": [[s["user"], s["name"], [fac_idx[f] for f in s["facs"]], [prog_idx[p] for p in s["progs"]], s["cursos"], s["per"], s["last"], [mod_idx[m] for m in s["mods"]]] for s in rows],
}

tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
out = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
out = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<meta name="robots" content="noindex, nofollow">\n'
       + out.replace("</style>\n", "</style>\n</head>\n<body>\n", 1) + "\n</body>\n</html>\n")
dest = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--out=")), os.path.join(os.path.dirname(HERE), "index.html"))
open(dest, "w", encoding="utf-8").write(out)
print("ok", len(rows), "estudiantes,", len(facs), "facultades,", len(progs), "programas,", [p["days"] for p in meta], "recortados:", trunc, len(out), dest)
