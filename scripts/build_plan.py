#!/usr/bin/env python3
"""Genera data/plan.json: plan de estudio día a día para ambas versiones.

Uso: python3 scripts/build_plan.py
Reglas:
  * Del START al END (inclusive). Cada día tiene 2 temas: 1 del eje disciplinar y 1 del eje general/normativo.
  * Cada 7.º día del plan es de REPASO: repasa los temas de los 6 días anteriores (casos nuevos).
  * Si una lista de temas se agota, vuelve a empezar como "2.ª vuelta" (mayor dificultad, casos nuevos).
  * La dificultad sube por tramos de fecha.
"""
import json, datetime as dt, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
START = dt.date(2026, 11, 15)
END = dt.date(2027, 1, 31)   # víspera del inicio estimado de inscripciones generales (febrero de 2027)
QUESTIONS_PER_TOPIC = 20

META = {
    "start": START.isoformat(),
    "end": END.isoformat(),
    "inscription_estimate": "2027-02-01",
    "inscription_note": ("ESTIMADO: la CNSC no ha fijado el día exacto. Su cronograma preliminar ubica las inscripciones "
                         "en vacantes SIN reserva en febrero de 2027 (las de vacantes reservadas para personas con discapacidad "
                         "van del 23-nov-2026 al 15-ene-2027, Resolución 11673 de 2026). Se toma el 1-feb-2027 como fecha objetivo. "
                         "La prueba escrita se estima para el segundo semestre (octubre) de 2027."),
    "sources": [
        "https://www.concursosdelestado.com/concursos/docentes-fechas",
        "https://caracol.com.co/2026/11/09/concurso-docente-2026-2027-quienes-son-las-unicas-personas-que-tendran-inscripcion-gratuita/",
        "https://www.elcolombiano.com/colombia/concurso-docente-2026-cnsc-fechas-inscripcion-pruebas-OD41420086",
    ],
    "questions_per_topic": QUESTIONS_PER_TOPIC,
    "timezone": "America/Bogota",
}

T = lambda title, focus: {"title": title, "focus": focus}

A_DISC = [
    T("Célula: estructura, organelos y transporte de membrana", "procariota vs eucariota, animal vs vegetal, función de organelos, difusión, ósmosis, transporte activo"),
    T("Fotosíntesis y respiración celular", "fases, reactivos y productos, ubicación, factores limitantes, diseño experimental con variables"),
    T("Genética mendeliana y cuadros de Punnett", "leyes de Mendel, monohíbridos y dihíbridos, dominancia incompleta, codominancia, grupos sanguíneos, herencia ligada al sexo"),
    T("Ecosistemas: flujo de energía, cadenas y redes tróficas", "niveles tróficos, regla del 10 %, pirámides, relaciones interespecíficas, bioacumulación"),
    T("Materia: propiedades, mezclas y métodos de separación", "propiedades generales/específicas, cambios físicos y químicos, sustancias puras, mezclas homogéneas/heterogéneas, filtración, destilación, cromatografía, densidad"),
    T("Educación ambiental: PRAE, PNEA, Ley 1549 de 2012 y CIDEA", "Decreto 1743 de 1994, Política Nacional de Educación Ambiental 2002, Ley 1549, CIDEA, PROCEDA, enfoque sistémico e interdisciplinario"),
    T("ADN, ARN y síntesis de proteínas", "estructura, replicación, transcripción, traducción, código genético, mutaciones"),
    T("División celular: mitosis y meiosis", "ciclo celular, fases, diferencias, variabilidad genética, no disyunción"),
    T("Evolución: selección natural y especiación", "Darwin, Lamarck, evidencias, deriva, aislamiento reproductivo, resistencia a antibióticos"),
    T("Clasificación de los seres vivos y biodiversidad de Colombia", "dominios y reinos, taxonomía, nomenclatura binomial, endemismo, especies amenazadas, ecosistemas estratégicos (páramo)"),
    T("Ciclos biogeoquímicos: agua, carbono y nitrógeno", "procesos, microorganismos, alteraciones humanas, eutrofización"),
    T("Sistemas digestivo y circulatorio", "digestión mecánica y química, enzimas, absorción, corazón, circulación mayor y menor, sangre"),
    T("Sistemas respiratorio y excretor", "intercambio gaseoso, ventilación, nefrona, regulación hídrica"),
    T("Sistemas nervioso y endocrino; homeostasis", "neurona, sinapsis, arco reflejo, hormonas, retroalimentación negativa, glucemia"),
    T("Reproducción humana y educación para la sexualidad", "aparatos reproductores, ciclo menstrual, fecundación, ITS, métodos de prevención, enfoque de derechos"),
    T("Microorganismos, salud y enfermedad", "bacterias, virus, hongos, protozoos, vacunas, inmunidad, antibióticos, epidemiología básica"),
    T("Modelos atómicos y tabla periódica", "Dalton a Bohr y modelo cuántico, partículas subatómicas, isótopos, configuración electrónica, propiedades periódicas"),
    T("Enlace químico y nomenclatura inorgánica", "iónico, covalente, metálico, electronegatividad, óxidos, hidróxidos, ácidos, sales"),
    T("Reacciones químicas y balanceo", "tipos de reacción, ley de conservación de la masa, balanceo por tanteo, evidencias de reacción"),
    T("Estequiometría y reactivo límite", "mol, masa molar, relaciones molares, rendimiento, reactivo límite"),
    T("Soluciones: concentración y diluciones", "% m/m, % m/v, molaridad, C1V1=C2V2, solubilidad y temperatura"),
    T("Ácidos, bases y pH", "Arrhenius, Brønsted-Lowry, escala de pH, indicadores, neutralización, lluvia ácida"),
    T("Gases ideales", "Boyle, Charles, Gay-Lussac, PV=nRT, presión atmosférica, teoría cinética"),
    T("Química orgánica y biomoléculas", "carbono, hidrocarburos, grupos funcionales, carbohidratos, lípidos, proteínas, ácidos nucleicos, enzimas"),
    T("Cinemática: MRU, MRUA y caída libre", "posición, velocidad, aceleración, gráficas, ecuaciones"),
    T("Leyes de Newton y fricción", "inercia, F=ma, acción-reacción, diagramas de cuerpo libre, peso vs masa"),
    T("Trabajo, energía, potencia y conservación", "energía cinética y potencial, conservación, eficiencia, potencia"),
    T("Fluidos: presión, Pascal y Arquímedes", "presión hidrostática, principio de Pascal, empuje, flotación, densidad"),
    T("Termodinámica: calor, temperatura y cambios de fase", "escalas, calor específico, calor latente, conducción, convección, radiación"),
    T("Ondas y sonido", "longitud de onda, frecuencia, v=λf, ondas mecánicas y electromagnéticas, efecto Doppler, resonancia"),
    T("Óptica: reflexión, refracción y lentes", "leyes de reflexión, índice de refracción, lentes convergentes y divergentes, ojo y visión"),
    T("Electricidad y circuitos", "carga, corriente, voltaje, resistencia, ley de Ohm, serie y paralelo, potencia eléctrica"),
    T("Magnetismo y electromagnetismo", "imanes, campo magnético, inducción, motores y generadores"),
    T("Ciencias de la Tierra y el espacio", "estaciones, fases lunares, sistema solar, tectónica de placas, sismos, rocas"),
    T("Cambio climático y efecto invernadero", "gases de efecto invernadero, evidencia, mitigación y adaptación, huella de carbono"),
    T("Recurso hídrico, suelo y conservación", "cuencas, contaminación del agua, erosión, agroquímicos, CTS"),
    T("Residuos sólidos, economía circular y energías renovables", "las 3R/5R, separación en la fuente, compostaje, energías limpias"),
    T("Gestión del riesgo en la escuela", "amenaza, vulnerabilidad, riesgo, plan escolar de gestión del riesgo, Ley 1523 de 2012"),
    T("Didáctica de las ciencias: indagación, trabajo práctico y bioseguridad", "ciclo de indagación, preguntas investigables, variables, laboratorio seguro, ideas previas, cambio conceptual"),
    T("Estándares, DBA y Lineamientos curriculares de Ciencias Naturales", "entornos vivo, físico, CTS; me aproximo al conocimiento como científico; competencias uso comprensivo, explicación, indagación"),
]

A_GEN = [
    T("El concurso docente: etapas, pruebas y puntajes", "CNSC, SIMO, OPEC, convocatoria, prueba de aptitudes y competencias básicas (eliminatoria), psicotécnica, valoración de antecedentes, entrevista, lista de elegibles, periodo de prueba"),
    T("Ley 115 de 1994: fines, objetivos y áreas obligatorias", "artículos 5, 13, 14, 20-23, niveles y ciclos, áreas obligatorias"),
    T("Decreto 1290 de 2009: evaluación y promoción", "SIEE, escala nacional, comisión de evaluación y promoción, promoción anticipada, informes"),
    T("Estatuto docente: Decreto Ley 1278 de 2002", "ingreso, periodo de prueba, escalafón (grados y niveles), evaluaciones, ascenso, retiro"),
    T("Convivencia escolar: Ley 1620 de 2013 y Decreto 1965 de 2013", "sistema nacional, comité escolar de convivencia, ruta de atención integral, situaciones tipo I, II y III"),
    T("Razonamiento cuantitativo: porcentajes, proporciones y estadística", "porcentajes, regla de tres, promedio, mediana, moda, interpretación de tablas"),
    T("Lectura crítica: tesis, argumentos e inferencias", "idea principal, tesis, argumentos, supuestos, inferencias, intención del autor"),
    T("Constitución Política y derecho a la educación", "artículos 1, 4, 44, 67, 68, 125, 130"),
    T("PEI, autonomía escolar y gobierno escolar", "Ley 115 arts. 73, 77, 142-145, Decreto 1860 de 1994, personero, consejo directivo, consejo académico, manual de convivencia"),
    T("Educación inclusiva: Decreto 1421 de 2017, PIAR y DUA", "ajustes razonables, PIAR, DUA, barreras, educación inclusiva"),
    T("Ley 715 de 2001: competencias y funciones del rector", "SGP, entidades territoriales certificadas, funciones de rectores"),
    T("Prueba psicotécnica: competencias comportamentales", "orientación al logro, trabajo en equipo, comunicación, liderazgo, negociación, compromiso social, iniciativa"),
    T("Evaluación formativa, rúbricas y retroalimentación", "evaluación para el aprendizaje, autoevaluación, coevaluación, heteroevaluación, rúbricas, retroalimentación efectiva"),
    T("Teorías del aprendizaje", "Piaget, Vygotsky (ZDP), Ausubel (aprendizaje significativo), Bruner, constructivismo"),
    T("Planeación de clase y secuencias didácticas", "objetivos, desempeños, momentos de la clase, coherencia curricular"),
    T("Código de Infancia y Adolescencia: Ley 1098 de 2006", "protección integral, interés superior, corresponsabilidad, obligaciones de las instituciones educativas"),
    T("Razonamiento cuantitativo: probabilidad e interpretación de gráficas", "probabilidad simple, conteo, gráficas de barras, líneas y circulares"),
    T("Lectura crítica: textos discontinuos y falacias", "tablas, infografías, falacias ad hominem, generalización apresurada, falsa causa"),
    T("Educación rural, Escuela Nueva y enfoque diferencial", "multigrado, guías de aprendizaje, etnoeducación, interculturalidad"),
    T("Uso pedagógico de las TIC", "TPACK, SAMR, recursos educativos abiertos, ciudadanía digital"),
    T("Régimen disciplinario y ética del servidor público", "Ley 1952 de 2019 (Código General Disciplinario), deberes, prohibiciones, faltas"),
    T("Derecho de petición, tutela y participación", "Ley 1755 de 2015, acción de tutela, mecanismos de participación"),
    T("Proyectos pedagógicos transversales", "Ley 115 art. 14, educación para la sexualidad, democracia, tiempo libre, ambiente"),
    T("Competencias y pruebas Saber (ICFES)", "uso comprensivo del conocimiento, explicación de fenómenos, indagación, análisis de resultados"),
    T("Evaluación de desempeño y ascenso: ECDF", "evaluación anual de desempeño, evaluación de competencias para ascenso y reubicación"),
]

B_DISC = [
    T("Naturaleza y evolución de la tecnología", "Guía 30 MEN: técnica, tecnología, ciencia, innovación, invención, artefactos, procesos y sistemas; historia de la tecnología"),
    T("Algoritmos y pensamiento computacional", "descomposición, patrones, abstracción, algoritmos, pseudocódigo, diagramas de flujo, trazas"),
    T("Hardware y arquitectura del computador", "CPU, memoria RAM/ROM, almacenamiento, periféricos, unidades de medida, modelo de von Neumann"),
    T("Electricidad y electrónica básica", "voltaje, corriente, resistencia, ley de Ohm, potencia, circuitos serie y paralelo, componentes, seguridad eléctrica"),
    T("Programación: variables, condicionales y ciclos", "tipos de datos, operadores, if/else, while, for, Scratch y Python, trazas de código"),
    T("Redes e Internet", "LAN/WAN, topologías, IP, DNS, router/switch, modelo TCP/IP, HTTP/HTTPS, Wi-Fi"),
    T("Guía 30: componentes y competencias del área", "apropiación y uso, solución de problemas con tecnología, tecnología y sociedad; grupos de grados; desempeños"),
    T("Sistemas operativos y software", "funciones del SO, tipos de software, licencias, archivos y carpetas, procesos"),
    T("Sistemas numéricos y representación de la información", "binario, decimal, hexadecimal, conversiones, bits y bytes, ASCII/Unicode"),
    T("Ofimática: procesador de texto y hoja de cálculo", "referencias relativas y absolutas, funciones SUMA, PROMEDIO, SI, CONTAR.SI, gráficos"),
    T("Bases de datos y modelo relacional", "tablas, claves primaria y foránea, relaciones, SQL SELECT/WHERE, normalización básica"),
    T("Programación: funciones, listas y estructuras de datos", "funciones, parámetros, retorno, listas/arreglos, recorridos, búsqueda"),
    T("Proceso de diseño tecnológico y solución de problemas", "identificar el problema, requerimientos, alternativas, prototipo, prueba, evaluación"),
    T("Máquinas simples, mecanismos y transmisión de movimiento", "palanca, polea, plano inclinado, engranajes, relación de transmisión"),
    T("Materiales, herramientas y procesos de fabricación", "propiedades de materiales, metales, polímeros, cerámicos, maderas, procesos"),
    T("Electrónica digital y compuertas lógicas", "AND, OR, NOT, NAND, tablas de verdad, álgebra booleana básica"),
    T("Robótica educativa y Arduino", "sensores, actuadores, microcontrolador, entradas/salidas digitales y analógicas, PWM"),
    T("Ciberseguridad y ciudadanía digital", "contraseñas, phishing, malware, huella digital, ciberacoso, grooming"),
    T("Desarrollo web: HTML, CSS y JavaScript", "estructura HTML, selectores CSS, eventos JS, cliente-servidor"),
    T("Ingeniería de software y metodologías ágiles", "ciclo de vida, requisitos, Scrum, pruebas, control de versiones"),
    T("Tecnología, sociedad y ambiente", "impactos, ética, sostenibilidad, obsolescencia, RAEE, brecha digital"),
    T("Inteligencia artificial y datos", "aprendizaje automático, sesgos, uso ético de IA en el aula, datos personales"),
    T("Didáctica de la tecnología e informática", "aprendizaje basado en proyectos y retos, STEM/STEAM, evaluación en tecnología"),
    T("Dibujo técnico y representación gráfica", "vistas, escalas, acotado, isometría, bocetos"),
    T("Energía: fuentes, transformación y uso eficiente", "renovables/no renovables, transformaciones, consumo kWh, eficiencia"),
    T("Programación orientada a objetos", "clases, objetos, atributos, métodos, encapsulamiento, herencia, polimorfismo"),
    T("Computación en la nube, IoT y tecnologías emergentes", "IaaS, PaaS, SaaS, IoT, realidad aumentada, impresión 3D"),
    T("Protección de datos y propiedad intelectual", "Ley 1581 de 2012, habeas data, derechos de autor, licencias libres y Creative Commons"),
]

B_GEN = [
    T("Leyes desde cero: Constitución, Estado social de derecho y jerarquía normativa", "qué es una norma, Constitución, leyes, decretos, decretos ley, resoluciones, acuerdos, cómo se citan, ramas del poder"),
    T("Derecho a la educación y estructura del sector educativo", "arts. 44, 67, 68 de la Constitución; MEN, secretarías, entidades territoriales certificadas, Decreto 1075 de 2015"),
    T("Ley 115 de 1994: fines, niveles, áreas obligatorias y PEI", "art. 5, niveles y grados, art. 23 (Tecnología e Informática), art. 73 PEI, art. 77 autonomía, art. 142 gobierno escolar"),
    T("El concurso docente: etapas, pruebas, puntajes y SIMO", "CNSC, SIMO, OPEC, prueba eliminatoria, psicotécnica, valoración de antecedentes, entrevista, lista de elegibles, periodo de prueba, requisitos para profesionales no licenciados"),
    T("Decreto 1290 de 2009: evaluación y promoción", "SIEE, escala nacional, comisión de evaluación y promoción, promoción anticipada"),
    T("Estatuto docente: Decreto Ley 1278 de 2002", "ingreso, profesionales no licenciados, periodo de prueba, escalafón, evaluaciones, retiro"),
    T("Convivencia escolar: Ley 1620 de 2013 y Decreto 1965 de 2013", "comité escolar de convivencia, ruta de atención integral, situaciones tipo I, II y III"),
    T("Lectura crítica: tesis, argumentos e inferencias", "idea principal, tesis, argumentos, supuestos, inferencias"),
    T("Ley 715 de 2001: competencias y funciones del rector", "SGP, entidades territoriales certificadas, funciones de rectores"),
    T("Razonamiento cuantitativo: porcentajes, proporciones y estadística", "porcentajes, regla de tres, promedio, mediana, moda, tablas"),
    T("Gobierno escolar y manual de convivencia: Decreto 1860 de 1994", "consejo directivo, consejo académico, personero, representante, consejo de padres"),
    T("Educación inclusiva: Decreto 1421 de 2017, PIAR y DUA", "ajustes razonables, PIAR, DUA"),
    T("Código de Infancia y Adolescencia: Ley 1098 de 2006", "protección integral, interés superior, corresponsabilidad, obligaciones de las instituciones"),
    T("Prueba psicotécnica: competencias comportamentales", "orientación al logro, trabajo en equipo, comunicación, liderazgo, negociación"),
    T("Teorías del aprendizaje", "Piaget, Vygotsky, Ausubel, Bruner, constructivismo, conectivismo"),
    T("Evaluación formativa, rúbricas y retroalimentación", "evaluación para el aprendizaje, auto/co/heteroevaluación, rúbricas"),
    T("Régimen disciplinario del servidor público: Ley 1952 de 2019", "deberes, prohibiciones, faltas, sanciones, debido proceso"),
    T("Derecho de petición, acción de tutela y mecanismos de participación", "Ley 1755 de 2015, tutela art. 86, cumplimiento, populares"),
    T("Planeación de clase y secuencias didácticas", "objetivos, desempeños, momentos de la clase"),
    T("Razonamiento cuantitativo: probabilidad e interpretación de gráficas", "probabilidad simple, conteo, gráficas"),
    T("Lectura crítica: textos discontinuos y falacias", "tablas, infografías, falacias"),
    T("Proyectos pedagógicos transversales y educación ambiental", "Ley 115 art. 14, PRAE, educación para la sexualidad"),
    T("Uso pedagógico de las TIC y competencias TIC docentes", "competencias TIC para el desarrollo profesional docente (MEN 2013), TPACK, SAMR"),
    T("Evaluación de desempeño y ascenso: ECDF", "evaluación anual, evaluación de competencias para ascenso y reubicación"),
    T("Educación rural, Escuela Nueva y enfoque diferencial", "multigrado, etnoeducación, interculturalidad"),
]

VERSIONS = {
    "A": {"name": "Ciencias Naturales y Educación Ambiental", "person": "Yasmin",
          "tracks": [("Disciplinar: Ciencias Naturales y Ed. Ambiental", A_DISC), ("Conocimiento general del concurso", A_GEN)]},
    "B": {"name": "Tecnología e Informática", "person": "Andrey",
          "tracks": [("Disciplinar: Tecnología e Informática", B_DISC), ("Leyes y conocimiento general del concurso", B_GEN)]},
}

def difficulty(d):
    if d < dt.date(2026, 12, 13): return "Intermedio"
    if d < dt.date(2027, 1, 10): return "Intermedio-alto"
    return "Alto"

def slug(s):
    import unicodedata, re
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48]

def build_version(v):
    tracks = v["tracks"]; idx = [0] * len(tracks); days = []; week = []
    n_days = (END - START).days + 1
    for i in range(n_days):
        d = START + dt.timedelta(days=i); n = i + 1
        if n % 7 == 0:
            wk = n // 7
            topics = []
            for t, (track_name, _) in enumerate(tracks):
                covered = [x["title"] for x in week if x["track"] == track_name]
                topics.append({"id": f"repaso-s{wk}-{t+1}", "title": f"Repaso semana {wk}: {track_name.split(':')[0]}",
                               "track": track_name, "review": True, "covers": covered,
                               "focus": "casos nuevos e integradores sobre: " + "; ".join(covered)})
            days.append({"n": n, "date": d.isoformat(), "kind": "repaso", "difficulty": difficulty(d), "topics": topics})
            week = []
            continue
        topics = []
        for t, (track_name, lst) in enumerate(tracks):
            k = idx[t]; base = lst[k % len(lst)]; lap = k // len(lst) + 1; idx[t] += 1
            title = base["title"] + (f" ({lap}.ª vuelta)" if lap > 1 else "")
            top = {"id": slug(base["title"]) + (f"-v{lap}" if lap > 1 else ""), "title": title,
                   "track": track_name, "review": False, "focus": base["focus"]}
            topics.append(top); week.append(top)
        days.append({"n": n, "date": d.isoformat(), "kind": "estudio", "difficulty": difficulty(d), "topics": topics})
    return days

plan = {"meta": META, "versions": {}}
for key, v in VERSIONS.items():
    plan["versions"][key] = {"name": v["name"], "person": v["person"],
                             "tracks": [t[0] for t in v["tracks"]], "days": build_version(v)}
(ROOT / "data" / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print("plan.json:", {k: len(v["days"]) for k, v in plan["versions"].items()}, "días")
