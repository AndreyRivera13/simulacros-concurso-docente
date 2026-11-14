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
        "https://www.cnsc.gov.co/sites/default/files/2026-11/res-11673-del-6-de-noviembre-de-2026-inscripciones-pcd.pdf",
        "https://www.cnsc.gov.co/convocatorias/docentes-y-directivos-docentes-2026",
        "https://www.concursosdelestado.com/concursos/docentes-fechas",
        "https://caracol.com.co/2026/11/09/concurso-docente-2026-2027-quienes-son-las-unicas-personas-que-tendran-inscripcion-gratuita/",
        "https://www.elcolombiano.com/colombia/concurso-docente-2026-cnsc-fechas-inscripcion-pruebas-OD41420086",
    ],
    "questions_per_topic": QUESTIONS_PER_TOPIC,
    "timezone": "America/Bogota",
}

# Cada tema declara el EJE OFICIAL al que responde (ver data/guia.json y la pestaña "Guía de estudio").
# Ejes = componentes de la Prueba de Aptitudes y Competencias Básicas (Anexo técnico CNSC 2026, num. 2.1),
# prueba psicotécnica/entrevista (Res. MEN 003842 de 2022) y marco normativo que el Manual de Funciones exige dominar.
# IMPORTANTE: los 6 primeros elementos de cada lista ya se generaron (15-20 nov 2026); NO cambiar sus títulos (ids).
T = lambda title, focus, eje: {"title": title, "focus": focus, "eje": eje}

A_DISC = [
    # --- ya generados (no modificar títulos) ---
    T("Célula: estructura, organelos y transporte de membrana", "procariota vs eucariota, animal vs vegetal, función de organelos, difusión, ósmosis, transporte activo", "cn-vivo"),
    T("Fotosíntesis y respiración celular", "fases, reactivos y productos, ubicación, factores limitantes, diseño experimental con variables", "cn-vivo"),
    T("Genética mendeliana y cuadros de Punnett", "leyes de Mendel, monohíbridos y dihíbridos, dominancia incompleta, codominancia, grupos sanguíneos, herencia ligada al sexo", "cn-vivo"),
    T("Ecosistemas: flujo de energía, cadenas y redes tróficas", "niveles tróficos, regla del 10 %, pirámides, relaciones interespecíficas, bioacumulación", "cn-vivo"),
    T("Materia: propiedades, mezclas y métodos de separación", "propiedades generales/específicas, cambios físicos y químicos, sustancias puras, mezclas homogéneas/heterogéneas, filtración, destilación, cromatografía, densidad", "cn-quimicos"),
    T("Educación ambiental: PRAE, PNEA, Ley 1549 de 2012 y CIDEA", "Decreto 1743 de 1994, Política Nacional de Educación Ambiental 2002, Ley 1549, CIDEA, PROCEDA, enfoque sistémico e interdisciplinario", "cn-ambiental"),
    # --- desde el 22-nov-2026 (revisados contra Estándares, Lineamientos y DBA de Ciencias Naturales) ---
    T("Referentes de calidad: Estándares, Lineamientos y DBA de Ciencias Naturales", "entorno vivo, entorno físico (procesos químicos y físicos), ciencia-tecnología-sociedad; 'me aproximo al conocimiento como científico'; manejo de conocimientos propios; compromisos personales y sociales; DBA por grado", "cn-referentes"),
    T("ADN, ARN y síntesis de proteínas", "estructura, replicación, transcripción, traducción, código genético, mutaciones", "cn-vivo"),
    T("Didáctica de las ciencias: indagación, trabajo práctico y bioseguridad", "ciclo de indagación, preguntas investigables, variables, laboratorio seguro, ideas previas, cambio conceptual (Estándares: me aproximo al conocimiento como científico)", "cn-didactica"),
    T("División celular: mitosis y meiosis", "ciclo celular, fases, diferencias, variabilidad genética, no disyunción", "cn-vivo"),
    T("Evolución: selección natural y especiación", "Darwin, Lamarck, evidencias, deriva, aislamiento reproductivo, resistencia a antibióticos", "cn-vivo"),
    T("Modelos atómicos y tabla periódica", "Dalton a Bohr y modelo cuántico, partículas subatómicas, isótopos, configuración electrónica, propiedades periódicas", "cn-quimicos"),
    T("Cinemática: MRU, MRUA y caída libre", "posición, velocidad, aceleración, gráficas, ecuaciones", "cn-fisicos"),
    T("Clasificación de los seres vivos y biodiversidad de Colombia", "dominios y reinos, taxonomía, nomenclatura binomial, endemismo, especies amenazadas, ecosistemas estratégicos (páramo)", "cn-vivo"),
    T("Ciclos biogeoquímicos: agua, carbono y nitrógeno", "procesos, microorganismos, alteraciones humanas, eutrofización", "cn-ambiental"),
    T("Enlace químico y nomenclatura inorgánica", "iónico, covalente, metálico, electronegatividad, óxidos, hidróxidos, ácidos, sales", "cn-quimicos"),
    T("Leyes de Newton y fricción", "inercia, F=ma, acción-reacción, diagramas de cuerpo libre, peso vs masa", "cn-fisicos"),
    T("Sistemas digestivo y circulatorio", "digestión mecánica y química, enzimas, absorción, corazón, circulación mayor y menor, sangre", "cn-vivo"),
    T("Reacciones químicas y balanceo", "tipos de reacción, ley de conservación de la masa, balanceo por tanteo, evidencias de reacción", "cn-quimicos"),
    T("Trabajo, energía, potencia y conservación", "energía cinética y potencial, conservación, eficiencia, potencia", "cn-fisicos"),
    T("Cambio climático y efecto invernadero", "gases de efecto invernadero, evidencia, mitigación y adaptación, huella de carbono", "cn-ambiental"),
    T("Sistemas respiratorio y excretor", "intercambio gaseoso, ventilación, nefrona, regulación hídrica", "cn-vivo"),
    T("Estequiometría y reactivo límite", "mol, masa molar, relaciones molares, rendimiento, reactivo límite", "cn-quimicos"),
    T("Fluidos: presión, Pascal y Arquímedes", "presión hidrostática, principio de Pascal, empuje, flotación, densidad", "cn-fisicos"),
    T("Sistemas nervioso y endocrino; homeostasis", "neurona, sinapsis, arco reflejo, hormonas, retroalimentación negativa, glucemia", "cn-vivo"),
    T("Soluciones: concentración y diluciones", "% m/m, % m/v, molaridad, C1V1=C2V2, solubilidad y temperatura", "cn-quimicos"),
    T("Termodinámica: calor, temperatura y cambios de fase", "escalas, calor específico, calor latente, conducción, convección, radiación", "cn-fisicos"),
    T("Recurso hídrico, suelo y conservación", "cuencas, contaminación del agua, erosión, agroquímicos, CTS", "cn-ambiental"),
    T("Reproducción humana y educación para la sexualidad", "aparatos reproductores, ciclo menstrual, fecundación, ITS, métodos de prevención, enfoque de derechos", "cn-vivo"),
    T("Ácidos, bases y pH", "Arrhenius, Brønsted-Lowry, escala de pH, indicadores, neutralización, lluvia ácida", "cn-quimicos"),
    T("Ondas y sonido", "longitud de onda, frecuencia, v=λf, ondas mecánicas y electromagnéticas, efecto Doppler, resonancia", "cn-fisicos"),
    T("Microorganismos, salud y enfermedad", "bacterias, virus, hongos, protozoos, vacunas, inmunidad, antibióticos, epidemiología básica", "cn-vivo"),
    T("Gases ideales", "Boyle, Charles, Gay-Lussac, PV=nRT, presión atmosférica, teoría cinética", "cn-quimicos"),
    T("Óptica: reflexión, refracción y lentes", "leyes de reflexión, índice de refracción, lentes convergentes y divergentes, ojo y visión", "cn-fisicos"),
    T("Residuos sólidos, economía circular y energías renovables", "las 3R/5R, separación en la fuente, compostaje, energías limpias", "cn-ambiental"),
    T("Química orgánica y biomoléculas", "carbono, hidrocarburos, grupos funcionales, carbohidratos, lípidos, proteínas, ácidos nucleicos, enzimas", "cn-quimicos"),
    T("Electricidad y circuitos", "carga, corriente, voltaje, resistencia, ley de Ohm, serie y paralelo, potencia eléctrica", "cn-fisicos"),
    T("Ciencias de la Tierra y el espacio", "estaciones, fases lunares, sistema solar, tectónica de placas, sismos, rocas", "cn-fisicos"),
    T("Gestión del riesgo en la escuela", "amenaza, vulnerabilidad, riesgo, plan escolar de gestión del riesgo, Ley 1523 de 2012", "cn-ambiental"),
    T("Magnetismo y electromagnetismo", "imanes, campo magnético, inducción, motores y generadores", "cn-fisicos"),
    T("Competencias científicas y evaluación en Ciencias Naturales", "uso comprensivo del conocimiento científico, explicación de fenómenos, indagación (Estándares/DBA); evaluación formativa en ciencias", "cn-didactica"),
]

# Patrón semanal del eje general desde el 22-nov: lectura crítica, razonamiento cuantitativo y competencias blandas
# aparecen CADA semana (son 3 de los 4 componentes de la prueba eliminatoria); el resto rota normativa y pedagogía.
A_GEN = [
    # --- ya generados (no modificar títulos) ---
    T("El concurso docente: etapas, pruebas y puntajes", "CNSC, SIMO, OPEC, convocatoria, prueba de aptitudes y competencias básicas (eliminatoria), psicotécnica, valoración de antecedentes, entrevista, lista de elegibles, periodo de prueba", "concurso"),
    T("Ley 115 de 1994: fines, objetivos y áreas obligatorias", "artículos 5, 13, 14, 20-23, niveles y ciclos, áreas obligatorias", "norma"),
    T("Decreto 1290 de 2009: evaluación y promoción", "SIEE, escala nacional, comisión de evaluación y promoción, promoción anticipada, informes", "pedagogia"),
    T("Estatuto docente: Decreto Ley 1278 de 2002", "ingreso, periodo de prueba, escalafón (grados y niveles), evaluaciones, ascenso, retiro", "norma"),
    T("Convivencia escolar: Ley 1620 de 2013 y Decreto 1965 de 2013", "sistema nacional, comité escolar de convivencia, ruta de atención integral, situaciones tipo I, II y III", "norma"),
    T("Razonamiento cuantitativo: porcentajes, proporciones y estadística", "porcentajes, regla de tres, promedio, mediana, moda, interpretación de tablas", "rc"),
    # --- desde el 22-nov-2026 ---
    T("Lectura crítica: tesis, argumentos e inferencias", "idea principal, tesis, argumentos, supuestos, inferencias, intención del autor", "lc"),
    T("Competencias blandas: liderazgo y trabajo en equipo", "componente 3 de la prueba (Anexo CNSC 2026 num. 2.1); liderazgo y trabajo en equipo como competencias comportamentales del docente (Res. 003842 de 2022); casos situacionales en la institución", "blandas"),
    T("Constitución Política y derecho a la educación", "artículos 1, 4, 44, 67, 68, 125, 130", "norma"),
    T("Razonamiento cuantitativo: probabilidad e interpretación de gráficas", "probabilidad simple, conteo, gráficas de barras, líneas y circulares", "rc"),
    T("Competencias funcionales del docente: Resolución 003842 de 2022", "gestión académica (dominio curricular, planeación, pedagógicas y didácticas, evaluación), gestión administrativa (recursos, procesos institucionales), gestión comunitaria (comunicación, interacción con el entorno); funciones generales del docente de aula", "pedagogia"),
    T("Planeación de clase y secuencias didácticas", "objetivos, desempeños, momentos de la clase, coherencia curricular con Estándares y DBA", "pedagogia"),
    T("Lectura crítica: textos discontinuos y falacias", "tablas, infografías, falacias ad hominem, generalización apresurada, falsa causa", "lc"),
    T("Competencias blandas: ética y ciudadanía", "componente 3 de la prueba; dilemas éticos en la escuela, ciudadanía, convivencia, respeto a la diferencia, compromiso social e institucional", "blandas"),
    T("PEI, autonomía escolar y gobierno escolar", "Ley 115 arts. 73, 77, 142-145, Decreto 1860 de 1994, personero, consejo directivo, consejo académico, manual de convivencia", "norma"),
    T("Razonamiento cuantitativo: proporcionalidad, medidas y conversiones", "razones, proporcionalidad directa e inversa, unidades, áreas y volúmenes, estimación", "rc"),
    T("Educación inclusiva: Decreto 1421 de 2017, PIAR y DUA", "ajustes razonables, PIAR, DUA, barreras, educación inclusiva", "pedagogia"),
    T("Evaluación formativa, rúbricas y retroalimentación", "evaluación para el aprendizaje, autoevaluación, coevaluación, heteroevaluación, rúbricas, retroalimentación efectiva (Decreto 1290)", "pedagogia"),
    T("Lectura crítica: comprensión y reglas del lenguaje escrito", "cohesión, coherencia, conectores, puntuación, sentido global, uso adecuado del lenguaje escrito para comunicar ideas", "lc"),
    T("Prueba psicotécnica y entrevista: competencias comportamentales", "liderazgo; comunicación y relaciones interpersonales; trabajo en equipo; negociación y mediación; compromiso social e institucional; iniciativa; orientación al logro (Res. 003842 de 2022)", "psico"),
    T("Ley 715 de 2001: competencias y funciones del rector", "SGP, entidades territoriales certificadas, funciones de rectores", "norma"),
    T("Razonamiento cuantitativo: estadística descriptiva y lectura de datos", "media, mediana, moda, rango, tablas de frecuencia, comparación de grupos, conclusiones válidas", "rc"),
    T("Teorías del aprendizaje y enseñanza", "Piaget, Vygotsky (ZDP), Ausubel (aprendizaje significativo), Bruner, constructivismo; competencias pedagógicas para formar y enseñar", "pedagogia"),
    T("Código de Infancia y Adolescencia: Ley 1098 de 2006", "protección integral, interés superior, corresponsabilidad, obligaciones de las instituciones educativas", "norma"),
    T("Lectura crítica: estructura del texto e intención comunicativa", "tipos de texto, estructura argumentativa, punto de vista, contraargumentos, evaluación de la solidez de un argumento", "lc"),
    T("Competencias blandas: comunicación, negociación y mediación de conflictos", "componente 3 de la prueba y competencias comportamentales; mediación escolar, comunicación asertiva con familias y colegas", "blandas"),
    T("Proyectos pedagógicos transversales y PRAE", "Ley 115 art. 14, Decreto 1743 de 1994 (PRAE), educación para la sexualidad, democracia, tiempo libre", "pedagogia"),
    T("Razonamiento cuantitativo: lógica, patrones y resolución de problemas", "secuencias, regularidades, razonamiento inductivo y deductivo, problemas de varios pasos", "rc"),
    T("Uso pedagógico de las TIC", "Competencias TIC para el desarrollo profesional docente (MEN 2013), recursos educativos, uso eficiente de recursos pedagógicos (Res. 003842)", "pedagogia"),
    T("Evaluación del docente: periodo de prueba, desempeño y ascenso (Decreto Ley 1278)", "evaluación de periodo de prueba, evaluación anual de desempeño, evaluación de competencias para ascenso y reubicación", "norma"),
]

B_DISC = [
    # --- ya generados (no modificar títulos) ---
    T("Naturaleza y evolución de la tecnología", "Guía 30 MEN: técnica, tecnología, ciencia, innovación, invención, artefactos, procesos y sistemas; historia de la tecnología", "ti-naturaleza"),
    T("Algoritmos y pensamiento computacional", "descomposición, patrones, abstracción, algoritmos, pseudocódigo, diagramas de flujo, trazas", "ti-problemas"),
    T("Hardware y arquitectura del computador", "CPU, memoria RAM/ROM, almacenamiento, periféricos, unidades de medida, modelo de von Neumann", "ti-uso"),
    T("Electricidad y electrónica básica", "voltaje, corriente, resistencia, ley de Ohm, potencia, circuitos serie y paralelo, componentes, seguridad eléctrica", "ti-naturaleza"),
    T("Programación: variables, condicionales y ciclos", "tipos de datos, operadores, if/else, while, for, Scratch y Python, trazas de código", "ti-problemas"),
    T("Redes e Internet", "LAN/WAN, topologías, IP, DNS, router/switch, modelo TCP/IP, HTTP/HTTPS, Wi-Fi", "ti-uso"),
    # --- desde el 22-nov-2026 (revisados contra Guía 30 de 2008 y Orientaciones Curriculares de T&I de 2022) ---
    T("Componentes del área: Guía 30 (2008) y Orientaciones Curriculares de T&I (2022)", "naturaleza y evolución; uso y apropiación; solución de problemas; tecnología, informática y sociedad; competencias y evidencias de aprendizaje por grupos de grados", "ti-referentes"),
    T("Sistemas operativos, software y herramientas informáticas de uso común", "funciones del SO, tipos de software, archivos y carpetas, procesador de texto y hoja de cálculo para buscar y procesar información (Guía 30)", "ti-uso"),
    T("Proceso de diseño tecnológico y solución de problemas", "identificar el problema, requerimientos y restricciones, alternativas, prototipo, prueba, evaluación; pensamiento de diseño", "ti-problemas"),
    T("Representación de la información: datos, sistema binario y codificación", "bits y bytes, binario/decimal, codificación de texto e imágenes, datos e información (actividades 'desconectadas')", "ti-naturaleza"),
    T("Programación como estrategia de pensamiento computacional: funciones y listas", "funciones, parámetros, retorno, listas/arreglos, recorridos, búsqueda; programación por bloques y textual", "ti-problemas"),
    T("Mecanismos: transmisión de fuerza, potencia y movimiento", "palanca, polea, plano inclinado, engranajes, relación de transmisión", "ti-naturaleza"),
    T("Tecnología, informática y sociedad: impactos, ética y sostenibilidad", "impactos sociales, culturales y ambientales; obsolescencia, RAEE, brecha digital; perspectivas crítica, ética y política", "ti-sociedad"),
    T("Materiales, herramientas, procesos de producción y normas de seguridad", "propiedades de materiales, metales, polímeros, cerámicos, maderas, procesos, elementos de protección", "ti-uso"),
    T("Sistemas de control y robótica educativa", "control eléctrico y electrónico, sensores, actuadores, microcontrolador, entradas y salidas, automatización", "ti-problemas"),
    T("Ciudadanía digital, seguridad informática y derechos digitales", "contraseñas, phishing, malware, huella digital, ciberacoso, grooming, Política de Confianza y Seguridad Digital", "ti-sociedad"),
    T("Representación gráfica: bocetos, dibujos, planos y esquemas", "vistas, escalas, acotado, isometría, bocetos y diseños a mano alzada o con herramientas informáticas", "ti-problemas"),
    T("Energía: fuentes, transformación y uso eficiente", "renovables/no renovables, transformaciones, consumo kWh, eficiencia", "ti-naturaleza"),
    T("Tecnologías emergentes: inteligencia artificial, big data, nube e IoT", "aprendizaje automático, sesgos, analítica de datos, computación en la nube, internet de las cosas, impresión 3D; uso ético", "ti-sociedad"),
    T("Didáctica de la T&I: Movimiento Maker, STEM+ y aprendizaje por proyectos", "estrategias didácticas de las Orientaciones Curriculares 2022, aprendizaje basado en proyectos y retos, estrategias con TIC", "ti-didactica"),
    T("Aplicaciones y páginas web con lenguajes de programación", "cliente-servidor, estructura de una página (HTML/CSS), eventos y lógica (JavaScript), apps móviles como producto tecnológico", "ti-problemas"),
    T("Evaluación en Tecnología e Informática: competencias y evidencias de aprendizaje", "evidencias de aprendizaje por grados, progresión, evaluación formativa del proceso de diseño y de productos", "ti-didactica"),
    T("Aspectos legales y éticos: propiedad intelectual, licencias y datos personales", "derechos de autor, software libre y licencias, Creative Commons, Ley 1581 de 2012 (habeas data)", "ti-sociedad"),
    T("Redes, comunicaciones y servicios de información", "sistemas de comunicación e información, servicios en línea, búsqueda y evaluación de información, uso responsable", "ti-uso"),
]

B_GEN = [
    # --- ya generados (no modificar títulos) ---
    T("Leyes desde cero: Constitución, Estado social de derecho y jerarquía normativa", "qué es una norma, Constitución, leyes, decretos, decretos ley, resoluciones, acuerdos, cómo se citan, ramas del poder", "norma"),
    T("Derecho a la educación y estructura del sector educativo", "arts. 44, 67, 68 de la Constitución; MEN, secretarías, entidades territoriales certificadas, Decreto 1075 de 2015", "norma"),
    T("Ley 115 de 1994: fines, niveles, áreas obligatorias y PEI", "art. 5, niveles y grados, art. 23 (Tecnología e Informática), art. 73 PEI, art. 77 autonomía, art. 142 gobierno escolar", "norma"),
    T("El concurso docente: etapas, pruebas, puntajes y SIMO", "CNSC, SIMO, OPEC, prueba eliminatoria, psicotécnica, valoración de antecedentes, entrevista, lista de elegibles, periodo de prueba, requisitos para profesionales no licenciados", "concurso"),
    T("Decreto 1290 de 2009: evaluación y promoción", "SIEE, escala nacional, comisión de evaluación y promoción, promoción anticipada", "pedagogia"),
    T("Estatuto docente: Decreto Ley 1278 de 2002", "ingreso, profesionales no licenciados, periodo de prueba, escalafón, evaluaciones, retiro", "norma"),
    # --- desde el 22-nov-2026 ---
    T("Convivencia escolar: Ley 1620 de 2013 y Decreto 1965 de 2013", "comité escolar de convivencia, ruta de atención integral, situaciones tipo I, II y III", "norma"),
    T("Lectura crítica: tesis, argumentos e inferencias", "idea principal, tesis, argumentos, supuestos, inferencias", "lc"),
    T("Razonamiento cuantitativo: porcentajes, proporciones y estadística", "porcentajes, regla de tres, promedio, mediana, moda, tablas", "rc"),
    T("Competencias blandas: liderazgo y trabajo en equipo", "componente 3 de la prueba (Anexo CNSC 2026 num. 2.1); liderazgo y trabajo en equipo como competencias comportamentales (Res. 003842 de 2022)", "blandas"),
    T("Competencias funcionales del docente: Resolución 003842 de 2022", "gestión académica, administrativa y comunitaria; funciones generales del docente de aula; requisitos del docente de Tecnología e Informática (licenciaturas e ingenierías habilitadas)", "pedagogia"),
    T("Ley 715 de 2001: competencias y funciones del rector", "SGP, entidades territoriales certificadas, funciones de rectores", "norma"),
    T("Lectura crítica: textos discontinuos y falacias", "tablas, infografías, falacias", "lc"),
    T("Razonamiento cuantitativo: probabilidad e interpretación de gráficas", "probabilidad simple, conteo, gráficas", "rc"),
    T("Competencias blandas: ética y ciudadanía", "componente 3 de la prueba; dilemas éticos en la escuela, ciudadanía, convivencia, compromiso social e institucional", "blandas"),
    T("Gobierno escolar y manual de convivencia: Decreto 1860 de 1994", "consejo directivo, consejo académico, personero, representante, consejo de padres", "norma"),
    T("Planeación de clase y secuencias didácticas", "objetivos, desempeños, momentos de la clase, coherencia con los referentes del MEN", "pedagogia"),
    T("Educación inclusiva: Decreto 1421 de 2017, PIAR y DUA", "ajustes razonables, PIAR, DUA", "pedagogia"),
    T("Lectura crítica: comprensión y reglas del lenguaje escrito", "cohesión, coherencia, conectores, puntuación, uso adecuado del lenguaje escrito", "lc"),
    T("Razonamiento cuantitativo: proporcionalidad, medidas y conversiones", "razones, proporcionalidad directa e inversa, unidades, estimación", "rc"),
    T("Prueba psicotécnica y entrevista: competencias comportamentales", "liderazgo; comunicación y relaciones interpersonales; trabajo en equipo; negociación y mediación; compromiso social e institucional; iniciativa; orientación al logro (Res. 003842 de 2022)", "psico"),
    T("Código de Infancia y Adolescencia: Ley 1098 de 2006", "protección integral, interés superior, corresponsabilidad, obligaciones de las instituciones", "norma"),
    T("Teorías del aprendizaje y enseñanza", "Piaget, Vygotsky, Ausubel, Bruner, constructivismo; competencias pedagógicas para formar y enseñar", "pedagogia"),
    T("Evaluación formativa, rúbricas y retroalimentación", "evaluación para el aprendizaje, auto/co/heteroevaluación, rúbricas (Decreto 1290)", "pedagogia"),
    T("Lectura crítica: estructura del texto e intención comunicativa", "tipos de texto, estructura argumentativa, punto de vista, contraargumentos", "lc"),
    T("Razonamiento cuantitativo: lógica, patrones y resolución de problemas", "secuencias, regularidades, razonamiento inductivo y deductivo, problemas de varios pasos", "rc"),
    T("Competencias blandas: comunicación, negociación y mediación de conflictos", "componente 3 de la prueba y competencias comportamentales; mediación escolar, comunicación asertiva", "blandas"),
    T("Proyectos pedagógicos transversales", "Ley 115 art. 14, PRAE (Decreto 1743 de 1994), educación para la sexualidad, democracia, tiempo libre", "pedagogia"),
    T("Uso pedagógico de las TIC y competencias TIC docentes", "Competencias TIC para el desarrollo profesional docente (MEN 2013): tecnológica, comunicativa, pedagógica, de gestión e investigativa", "pedagogia"),
    T("Evaluación del docente: periodo de prueba, desempeño y ascenso (Decreto Ley 1278)", "evaluación de periodo de prueba, evaluación anual de desempeño, evaluación de competencias para ascenso y reubicación", "norma"),
]

VERSIONS = {
    "A": {"name": "Ciencias Naturales y Educación Ambiental", "person": "Yazmín",
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
                               "track": track_name, "review": True, "covers": covered, "eje": "repaso",
                               "focus": "casos nuevos e integradores sobre: " + "; ".join(covered)})
            days.append({"n": n, "date": d.isoformat(), "kind": "repaso", "difficulty": difficulty(d), "topics": topics})
            week = []
            continue
        topics = []
        for t, (track_name, lst) in enumerate(tracks):
            k = idx[t]; base = lst[k % len(lst)]; lap = k // len(lst) + 1; idx[t] += 1
            title = base["title"] + (f" ({lap}.ª vuelta)" if lap > 1 else "")
            top = {"id": slug(base["title"]) + (f"-v{lap}" if lap > 1 else ""), "title": title,
                   "track": track_name, "review": False, "focus": base["focus"], "eje": base["eje"]}
            topics.append(top); week.append(top)
        days.append({"n": n, "date": d.isoformat(), "kind": "estudio", "difficulty": difficulty(d), "topics": topics})
    return days

plan = {"meta": META, "versions": {}}
for key, v in VERSIONS.items():
    plan["versions"][key] = {"name": v["name"], "person": v["person"],
                             "tracks": [t[0] for t in v["tracks"]], "days": build_version(v)}
(ROOT / "data" / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
print("plan.json:", {k: len(v["days"]) for k, v in plan["versions"].items()}, "días")
