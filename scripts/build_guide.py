#!/usr/bin/env python3
"""Genera data/guia.json: Guía de estudio basada SOLO en documentos oficiales del concurso docente.

Uso: python3 scripts/build_guide.py   (ejecútelo después de build_plan.py; cruza cada eje con los días del plan)
Para verificar los enlaces: python3 scripts/check_links.py
"""
import json, sys, re, pathlib, datetime as dt

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "data" / "plan.json").read_text())

FP = "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i="
D = lambda id, nombre, emisor, anio, url, por_que, versiones="AB": dict(id=id, nombre=nombre, emisor=emisor, anio=anio, url=url, por_que=por_que, versiones=list(versiones))

DOCS = [
    # --- Concurso 2026-2027 (CNSC) ---
    D("cnsc-conv", "Convocatoria Docentes y Directivos Docentes 2026 (página oficial del proceso)", "CNSC", 2026,
      "https://www.cnsc.gov.co/convocatorias/docentes-y-directivos-docentes-2026",
      "Página oficial donde la CNSC publica acuerdos por entidad territorial, anexo, OPEC, avisos, cronograma y, cuando exista, la Guía de orientación y los ejes temáticos."),
    D("cnsc-anexo", "Anexo técnico de los Procesos de Selección Nos. 2917 a 3006 de 2026 – Docentes y Directivos Docentes (octubre de 2026)", "CNSC", 2026,
      "https://www.cnsc.gov.co/sites/default/files/2026-10/anexo-tecnico-docentes-y-directivos-docentes-2026.pdf",
      "Define los 4 componentes de la prueba de aptitudes y competencias básicas (num. 2.1), la prueba psicotécnica (2.2), mínimos aprobatorios, tablas de valoración de antecedentes (num. 5) y la entrevista (num. 6)."),
    D("cnsc-acuerdo", "Acuerdo CNSC No. 244 del 21 de octubre de 2026 – Proceso de Selección No. 2963 (San José de Cúcuta), ejemplo de Acuerdo de convocatoria", "CNSC", 2026,
      "https://www.cnsc.gov.co/sites/default/files/2026-10/20261021_san-jose-de-cucuta_acuerdo-no244.pdf",
      "Cada entidad territorial tiene su propio Acuerdo (Nos. 233 a 322). Su art. 3 fija las etapas y su art. 13 (Tabla 4) el carácter, mínimo y peso de cada prueba. Revise también el Acuerdo de la entidad a la que se inscriba."),
    D("cnsc-res11673", "Resolución CNSC No. 11673 del 6 de noviembre de 2026 (inscripciones modalidad con reserva para personas con discapacidad)", "CNSC", 2026,
      "https://www.cnsc.gov.co/sites/default/files/2026-11/res-11673-del-6-de-noviembre-de-2026-inscripciones-pcd.pdf",
      "Primer acto del cronograma de inscripciones; sirve para estimar cuándo abren las inscripciones generales."),
    D("cnsc-2022", "Publicación de la Guía de orientación al aspirante – Procesos de Selección Nos. 2150 a 2237 de 2021, 2316 y 2406 de 2022 (26-ago-2022)", "CNSC – Universidad Libre", 2022,
      "https://www.cnsc.gov.co/node/11792",
      "Referencia del concurso anterior (2022): confirma que la Guía de orientación con los ejes la publicó el operador (Universidad Libre) pocas semanas antes de la prueba. El enlace a la guía (historico.cnsc.gov.co) no responde hoy, por eso no se cita su contenido."),
    D("d574", "Decreto 574 de 2022 (concurso docente en zonas rurales)", "Presidencia de la República / MEN", 2022,
      FP + "185446",
      "Referencia 2022: describe oficialmente los componentes lectura crítica y razonamiento cuantitativo y sus pesos (20 % c/u) para la prueba rural. Úselo solo como antecedente: el concurso 2026 aún no publica pesos internos por componente."),
    # --- MEN: manual de funciones y referentes de calidad ---
    D("res3842", "Resolución 003842 del 18 de marzo de 2022 – Manual de Funciones, Requisitos y Competencias para directivos docentes y docentes", "Ministerio de Educación Nacional", 2022,
      "https://www.mineducacion.gov.co/1780/articles-401651_recurso_2.pdf",
      "La CNSC la usa para verificar requisitos y diseñar las pruebas: competencias funcionales (gestión académica, administrativa y comunitaria), 7 competencias comportamentales (psicotécnica y entrevista), funciones del docente de aula y títulos habilitantes por área (2.1.4.6 Ciencias Naturales; 2.1.4.9 Tecnología e Informática)."),
    D("est", "Estándares Básicos de Competencias en Lenguaje, Matemáticas, Ciencias y Ciudadanas (Guía 3)", "Ministerio de Educación Nacional", 2006,
      "https://www.mineducacion.gov.co/1621/articles-116042_archivo_pdf.pdf",
      "Referente de calidad que el Manual de Funciones obliga a dominar; incluye estándares de Ciencias Naturales y de competencias ciudadanas.", "AB"),
    D("est-cn", "Estándares Básicos de Competencias en Ciencias Sociales y Ciencias Naturales (capítulo)", "Ministerio de Educación Nacional", 2006,
      "https://www.mineducacion.gov.co/1621/articles-116042_archivo_pdf3.pdf",
      "Ejes del área: me aproximo al conocimiento como científico, manejo de conocimientos propios (entorno vivo, entorno físico, ciencia-tecnología-sociedad) y compromisos personales y sociales.", "A"),
    D("lin-cn", "Lineamientos curriculares de Ciencias Naturales y Educación Ambiental", "Ministerio de Educación Nacional", 1998,
      "https://www.mineducacion.gov.co/1621/articles-339975_recurso_5.pdf",
      "Fundamentos epistemológicos, pedagógicos y didácticos del área; base para preguntas de enseñanza de las ciencias.", "A"),
    D("dba-cn", "Derechos Básicos de Aprendizaje (DBA) – Ciencias Naturales", "Ministerio de Educación Nacional (Colombia Aprende)", 2016,
      "https://colombiaaprende.edu.co/sites/default/files/files_public/2022-06/DBA_C.Naturales-min.pdf",
      "Aprendizajes estructurantes por grado (1.° a 11.°) con evidencias; útiles para preguntas de planeación y evaluación del área.", "A"),
    D("pnea", "Política Nacional de Educación Ambiental – SINA", "Ministerio del Medio Ambiente y Ministerio de Educación Nacional", 2002,
      "https://www.minambiente.gov.co/wp-content/uploads/2021/10/Politica-Nacional-Educacion-Ambiental.pdf",
      "Marco conceptual de la educación ambiental: PRAE, PROCEDA, CIDEA, enfoque sistémico e interdisciplinario.", "A"),
    D("g30", "Ser competente en tecnología: ¡una necesidad para el desarrollo! – Orientaciones generales para la educación en tecnología (Guía 30)", "Ministerio de Educación Nacional", 2008,
      "https://www.mineducacion.gov.co/1621/articles-160915_archivo_pdf.pdf",
      "Componentes del área (naturaleza y evolución de la tecnología; apropiación y uso; solución de problemas; tecnología y sociedad) y desempeños por grupos de grados.", "B"),
    D("oc-ti", "Orientaciones curriculares para el área de Tecnología e Informática en la educación básica y media", "Ministerio de Educación Nacional", 2022,
      "https://www.mineducacion.gov.co/1780/articles-411706_recurso_5.pdf",
      "Actualiza el área: 4 componentes (naturaleza y evolución; uso y apropiación; solución de problemas; tecnología, informática y sociedad), pensamiento computacional, programación, robótica, IA, ciudadanía digital y estrategias didácticas (Maker, STEM+).", "B"),
    D("oc-ti-ca", "Orientaciones Curriculares de Tecnología e Informática (colección en Colombia Aprende)", "Ministerio de Educación Nacional (Colombia Aprende)", 2022,
      "https://colombiaaprende.edu.co/contenidos/coleccion/orientaciones-curriculares-de-tecnologia-e-informatica",
      "Página oficial de la colección con los materiales de las orientaciones de T&I.", "B"),
    D("tic2013", "Competencias TIC para el desarrollo profesional docente", "Ministerio de Educación Nacional", 2013,
      "https://www.mineducacion.gov.co/1759/articles-339097_archivo_pdf_competencias_tic.pdf",
      "Competencias tecnológica, comunicativa, pedagógica, de gestión e investigativa; apoya la competencia 'uso eficiente de recursos pedagógicos' del Manual."),
    # --- Normas (Gestor Normativo de Función Pública) ---
    D("cp", "Constitución Política de Colombia", "Asamblea Nacional Constituyente", 1991, FP + "4125",
      "Arts. 44, 67 y 68 (derecho a la educación), 125 (mérito) y 130 (CNSC)."),
    D("ley115", "Ley 115 de 1994 – Ley General de Educación", "Congreso de la República", 1994, FP + "292",
      "Fines (art. 5), áreas obligatorias (art. 23: Ciencias Naturales y Ed. Ambiental; Tecnología e Informática), proyectos transversales (art. 14), PEI y gobierno escolar."),
    D("ley715", "Ley 715 de 2001", "Congreso de la República", 2001, FP + "4452",
      "Competencias de la Nación y entidades territoriales en educación, SGP y funciones del rector."),
    D("dl1278", "Decreto Ley 1278 de 2002 – Estatuto de Profesionalización Docente", "Presidencia de la República", 2002, FP + "5353",
      "Ingreso por concurso, periodo de prueba, evaluación, escalafón; arts. 4-6 citados para la prueba psicotécnica."),
    D("d1075", "Decreto 1075 de 2015 – Único Reglamentario del Sector Educación", "Presidencia de la República / MEN", 2015, FP + "77913",
      "Compila la reglamentación del concurso (arts. 2.4.1.1.x) y las competencias funcionales y comportamentales (arts. 2.4.1.5.2.x)."),
    D("d1290", "Decreto 1290 de 2009 – Evaluación del aprendizaje y promoción", "Presidencia de la República / MEN", 2009, FP + "35954",
      "SIEE, escala nacional, promoción: base de la competencia 'evaluación del aprendizaje'."),
    D("ley1620", "Ley 1620 de 2013 – Sistema Nacional de Convivencia Escolar", "Congreso de la República", 2013, FP + "52287",
      "Comité escolar de convivencia y ruta de atención integral."),
    D("d1965", "Decreto 1965 de 2013 (reglamenta la Ley 1620)", "Presidencia de la República / MEN", 2013, FP + "54537",
      "Situaciones tipo I, II y III y protocolos de la ruta de atención."),
    D("d1421", "Decreto 1421 de 2017 – Educación inclusiva para personas con discapacidad", "Presidencia de la República / MEN", 2017, FP + "87040",
      "PIAR, ajustes razonables y DUA."),
    D("ley1098", "Ley 1098 de 2006 – Código de la Infancia y la Adolescencia", "Congreso de la República", 2006, FP + "22106",
      "Protección integral y obligaciones de las instituciones educativas."),
    D("d1860", "Decreto 1860 de 1994 (aspectos pedagógicos y organizativos)", "Presidencia de la República / MEN", 1994, FP + "1289",
      "Gobierno escolar, manual de convivencia y PEI."),
    D("d1743", "Decreto 1743 de 1994 – Proyecto de Educación Ambiental (PRAE)", "Presidencia de la República / MEN", 1994, FP + "1301",
      "Institucionaliza el PRAE en la educación formal.", "AB"),
    D("ley1549", "Ley 1549 de 2012 – Política Nacional de Educación Ambiental", "Congreso de la República", 2012, FP + "48262",
      "Fortalece la institucionalización de la educación ambiental (PRAE, CIDEA).", "A"),
    D("ley1523", "Ley 1523 de 2012 – Gestión del riesgo de desastres", "Congreso de la República", 2012, FP + "47141",
      "Base del plan escolar de gestión del riesgo (tema de Ciencias Naturales y Ed. Ambiental).", "A"),
    D("ley1581", "Ley 1581 de 2012 – Protección de datos personales", "Congreso de la República", 2012, FP + "49981",
      "Aspectos legales de la informática (habeas data) que las Orientaciones de T&I ubican en ética y responsabilidad digital.", "B"),
    D("ley23", "Ley 23 de 1982 – Derechos de autor", "Congreso de la República", 1982, FP + "3431",
      "Norma básica de derecho de autor (incluye la protección del software como obra); tema de aspectos legales de T&I.", "B"),
    D("ley1273", "Ley 1273 de 2009 – Protección de la información y de los datos (delitos informáticos)", "Congreso de la República", 2009, FP + "34492",
      "Tipifica los delitos informáticos; base de seguridad informática y ciudadanía digital.", "B"),
    D("ley1341", "Ley 1341 de 2009 – Marco del sector TIC", "Congreso de la República", 2009, FP + "36913",
      "Principios y organización de las TIC en Colombia (Ministerio TIC, acceso y uso).", "B"),
]

C1 = "Componente 1 de la prueba de aptitudes y competencias básicas (eliminatoria)"
C2 = "Componente 2 de la prueba de aptitudes y competencias básicas (eliminatoria)"
C3 = "Componente 3 de la prueba de aptitudes y competencias básicas (eliminatoria)"
C4 = "Componente 4 de la prueba de aptitudes y competencias básicas: conocimientos disciplinares de la formación requerida para el empleo"
C4P = "Componente 4 de la prueba de aptitudes y competencias básicas: competencias pedagógicas para evaluar, formar y enseñar"
E = lambda id, nombre, componente, oficial, estudiar, docs: dict(id=id, nombre=nombre, componente=componente, oficial=oficial, estudiar=estudiar, docs=docs)

COMUNES_INI = [
    E("concurso", "Cómo funciona el concurso", "Reglas del proceso (no es un componente de la prueba)",
      "Acuerdos de convocatoria 2026 (art. 3 etapas; art. 13 pruebas) y Anexo técnico.",
      ["Las 12 etapas del art. 3 y su orden (pruebas escritas ANTES de la verificación de requisitos mínimos).",
       "Carácter, mínimo aprobatorio y peso de cada prueba (Tabla 4 del art. 13).",
       "Tabla de valoración de antecedentes del docente de aula (Anexo, num. 5.1.4).",
       "Reclamaciones por SIMO, lista de elegibles (2 años) y audiencia pública de escogencia de vacante."],
      ["cnsc-acuerdo", "cnsc-anexo", "cnsc-conv", "d1075", "dl1278", "cp"]),
    E("lc", "Lectura crítica", C1,
      "Anexo 2026, num. 2.1, componente 1. Descripción oficial más reciente: Decreto 574 de 2022 ('comprender textos y emplear de forma adecuada las reglas del lenguaje escrito para comunicar ideas').",
      ["Identificar tesis, argumentos, supuestos e inferencias.",
       "Evaluar la solidez de argumentos y reconocer falacias.",
       "Leer textos discontinuos (tablas, gráficos, infografías).",
       "Cohesión, coherencia y reglas del lenguaje escrito."],
      ["cnsc-anexo", "d574", "est"]),
    E("rc", "Razonamiento cuantitativo", C2,
      "Anexo 2026, num. 2.1, componente 2. Descripción oficial más reciente: Decreto 574 de 2022 ('manejo de las cantidades y los números en diferentes situaciones; aplicación inductiva y deductiva de principios básicos de las matemáticas').",
      ["Porcentajes, razones y proporcionalidad.", "Estadística descriptiva y lectura de tablas y gráficas.",
       "Probabilidad simple y conteo.", "Problemas de varios pasos, patrones y razonamiento inductivo/deductivo."],
      ["cnsc-anexo", "d574", "est"]),
    E("blandas", "Competencias blandas: liderazgo, ética, trabajo en equipo y ciudadanía", C3,
      "Anexo 2026, num. 2.1, componente 3 (texto literal: 'valoración de competencias blandas como liderazgo, ética, trabajo en equipo y ciudadanía'). Se relacionan con las competencias comportamentales de la Res. 003842 de 2022.",
      ["Casos situacionales: decidir la actuación más adecuada del docente.",
       "Liderazgo y trabajo en equipo en la institución.", "Ética profesional y ciudadanía (competencias ciudadanas de los Estándares).",
       "Comunicación, negociación y mediación de conflictos."],
      ["cnsc-anexo", "res3842", "est", "ley1620"]),
]
COMUNES_FIN = [
    E("pedagogia", "Competencias pedagógicas: evaluar, formar y enseñar", C4P,
      "Anexo 2026, num. 2.1, componente 4 ('competencias pedagógicas para evaluar, formar y enseñar') y Res. 003842 de 2022, gestión académica: dominio curricular, planeación y organización, competencias pedagógicas y didácticas, evaluación del aprendizaje.",
      ["Competencias funcionales del docente de aula (gestión académica, administrativa y comunitaria).",
       "Planeación con los referentes de calidad del MEN (Estándares, Lineamientos/Orientaciones, DBA).",
       "Evaluación del aprendizaje: Decreto 1290 de 2009 (SIEE), evaluación formativa y rúbricas.",
       "Educación inclusiva: Decreto 1421 de 2017 (PIAR, ajustes razonables, DUA).",
       "Uso pedagógico de TIC (Competencias TIC MEN 2013) y proyectos pedagógicos transversales (Ley 115 art. 14)."],
      ["cnsc-anexo", "res3842", "d1290", "d1421", "tic2013", "ley115", "d1743"]),
    E("psico", "Prueba psicotécnica y entrevista: competencias comportamentales", "Prueba psicotécnica (clasificatoria, 5 %) y entrevista (clasificatoria, 10 %)",
      "Anexo 2026, num. 2.2 (psicotécnica: arts. 4, 5 y 6 del Decreto Ley 1278 y Manual de Funciones) y num. 6.2 (entrevista: competencias comportamentales de la Res. 003842 de 2022).",
      ["Las 7 competencias comportamentales del docente de aula: liderazgo; comunicación y relaciones interpersonales; trabajo en equipo; negociación y mediación; compromiso social e institucional; iniciativa; orientación al logro.",
       "Función docente y tipos de cargo (Decreto Ley 1278, arts. 4-6)."],
      ["cnsc-anexo", "res3842", "dl1278"]),
    E("norma", "Marco normativo del servicio educativo", "Apoyo transversal (no es un componente separado de la prueba)",
      "No aparece como componente independiente en el Anexo 2026. Se incluye porque la Res. 003842 de 2022 exige al docente 'conocer, dominar y actualizarse en los referentes de calidad y normatividad definida por el MEN' (función general 3) y la gestión administrativa 'comprende el conocimiento y cumplimiento de las normas'; suele aparecer en casos de las competencias pedagógicas, blandas y comportamentales.",
      ["Constitución (arts. 44, 67, 68, 125, 130).", "Ley 115 de 1994 y Decreto 1860 de 1994 (fines, áreas, PEI, gobierno escolar).",
       "Ley 715 de 2001.", "Decreto Ley 1278 de 2002 (estatuto, periodo de prueba, evaluación).",
       "Ley 1620 y Decreto 1965 de 2013 (convivencia).", "Ley 1098 de 2006 (infancia y adolescencia).", "Decreto 1075 de 2015 (compilación)."],
      ["cp", "ley115", "d1860", "ley715", "dl1278", "ley1620", "d1965", "ley1098", "d1075", "res3842"]),
]

A_DISC = [
    E("cn-referentes", "Referentes de calidad de Ciencias Naturales", C4,
      "Res. 003842 de 2022 (función general 3 y gestión académica: dominio curricular) + referentes MEN del área.",
      ["Estructura de los Estándares de Ciencias: me aproximo al conocimiento como científico; manejo de conocimientos propios (entorno vivo, entorno físico, CTS); compromisos personales y sociales.",
       "Lineamientos curriculares de CN y Ed. Ambiental.", "DBA de Ciencias Naturales por grado."],
      ["est-cn", "lin-cn", "dba-cn", "res3842"]),
    E("cn-vivo", "Entorno vivo (biología)", C4,
      "Estándares de Ciencias Naturales: 'manejo de conocimientos propios de las ciencias naturales – entorno vivo'; DBA de CN.",
      ["Célula, metabolismo (fotosíntesis y respiración), genética y herencia, evolución.", "Sistemas del cuerpo humano, homeostasis, reproducción y sexualidad.",
       "Ecosistemas, biodiversidad, microorganismos y salud."],
      ["est-cn", "dba-cn", "lin-cn"]),
    E("cn-quimicos", "Entorno físico: procesos químicos", C4,
      "Estándares de Ciencias Naturales: 'entorno físico – procesos químicos'; DBA de CN.",
      ["Materia, mezclas y separación; modelos atómicos y tabla periódica.", "Enlace, nomenclatura, reacciones, estequiometría, soluciones, ácidos y bases, gases.", "Química orgánica y biomoléculas."],
      ["est-cn", "dba-cn", "lin-cn"]),
    E("cn-fisicos", "Entorno físico: procesos físicos", C4,
      "Estándares de Ciencias Naturales: 'entorno físico – procesos físicos'; DBA de CN.",
      ["Cinemática, dinámica, energía y su conservación.", "Fluidos, termodinámica, ondas, óptica.", "Electricidad, magnetismo; Tierra y universo."],
      ["est-cn", "dba-cn", "lin-cn"]),
    E("cn-ambiental", "Educación ambiental y ciencia, tecnología y sociedad", C4,
      "Área 'Ciencias Naturales y Educación Ambiental' (Ley 115 art. 23); Estándares (CTS); PNEA 2002; Ley 1549 de 2012; Decreto 1743 de 1994 (PRAE).",
      ["PRAE, PROCEDA, CIDEA y enfoque sistémico.", "Ciclos biogeoquímicos, cambio climático, agua y suelo, residuos.", "Gestión del riesgo escolar (Ley 1523 de 2012)."],
      ["pnea", "ley1549", "d1743", "est-cn", "ley1523", "ley115"]),
    E("cn-didactica", "Didáctica y evaluación de las Ciencias Naturales", C4P,
      "Lineamientos de CN (fundamentos pedagógicos y didácticos) y Estándares ('me aproximo al conocimiento como científico'); Res. 003842 (competencias pedagógicas y didácticas).",
      ["Indagación, preguntas investigables, variables y trabajo práctico seguro.", "Ideas previas y cambio conceptual.", "Competencias científicas y evaluación en el área."],
      ["lin-cn", "est-cn", "dba-cn", "res3842"]),
]

B_DISC = [
    E("ti-referentes", "Referentes del área de Tecnología e Informática", C4,
      "Res. 003842 de 2022 (dominio curricular) + Guía 30 (2008) y Orientaciones Curriculares de T&I (2022) del MEN.",
      ["Los 4 componentes de las Orientaciones 2022 y su relación con los de la Guía 30.", "Competencias y evidencias de aprendizaje por grupos de grados.",
       "Títulos habilitantes del docente de T&I (Res. 003842, num. 2.1.4.9: licenciaturas e ingenierías de sistemas, electrónica, mecatrónica, etc.)."],
      ["oc-ti", "g30", "res3842", "oc-ti-ca"]),
    E("ti-naturaleza", "Naturaleza y evolución de la tecnología y la informática", C4,
      "Orientaciones T&I 2022, componente 3.3.1.1; Guía 30, componente 'naturaleza y evolución de la tecnología'.",
      ["Técnica, tecnología, ciencia, innovación; artefactos, procesos, sistemas y servicios; historia.", "Conceptos fundamentales: algoritmo, sistema, estructura, función, recurso, optimización.",
       "Energía, electricidad, mecanismos y representación de la información (binario, datos)."],
      ["oc-ti", "g30"]),
    E("ti-uso", "Uso y apropiación de la tecnología y la informática", C4,
      "Orientaciones T&I 2022, componente 3.3.1.2; Guía 30, 'apropiación y uso de la tecnología'.",
      ["Uso adecuado y seguro de artefactos analógicos y digitales; hardware, sistemas operativos y herramientas informáticas de uso común.",
       "Redes, Internet y servicios de información.", "Materiales, herramientas, procesos y normas de seguridad."],
      ["oc-ti", "g30"]),
    E("ti-problemas", "Solución de problemas con tecnología e informática", C4,
      "Orientaciones T&I 2022, componente 3.3.1.3 (pensamiento tecnológico, de diseño y computacional; estrategias algorítmicas); Guía 30, 'solución de problemas con tecnología'.",
      ["Proceso de diseño y representación gráfica.", "Pensamiento computacional: descomposición, abstracción, algoritmos; programación como estrategia.",
       "Sistemas de control y robótica; aplicaciones y páginas web como productos tecnológicos."],
      ["oc-ti", "g30"]),
    E("ti-sociedad", "Tecnología, informática y sociedad", C4,
      "Orientaciones T&I 2022, componente 3.3.1.4 (dimensiones ética, política y crítica); Guía 30, 'tecnología y sociedad'.",
      ["Impactos sociales, culturales y ambientales; sostenibilidad y residuos electrónicos.", "Ciudadanía digital, seguridad informática y derechos digitales.",
       "Tecnologías emergentes (IA, big data, nube, IoT) y su uso ético; propiedad intelectual y datos personales (Ley 1581 de 2012)."],
      ["oc-ti", "g30", "ley1581"]),
    E("ti-didactica", "Didáctica y evaluación de la Tecnología e Informática", C4P,
      "Orientaciones T&I 2022, cap. 4 (Movimiento Maker, STEM+, programación para el pensamiento computacional, estrategias con TIC) y 3.3.2 (evidencias de aprendizaje).",
      ["Aprendizaje por proyectos y retos, Maker, STEM+.", "Evaluación por evidencias de aprendizaje y progresión por grados.", "Estrategias didácticas con TIC."],
      ["oc-ti", "g30", "tic2013", "res3842"]),
]

VERS = {"A": COMUNES_INI + A_DISC + COMUNES_FIN, "B": COMUNES_INI + B_DISC + COMUNES_FIN}
ids = {d["id"] for d in DOCS}
for v, ejes in VERS.items():
    for e in ejes:
        for d in e["docs"]:
            assert d in ids, (v, e["id"], d)
        days = []
        for day in PLAN["versions"][v]["days"]:
            for t in day["topics"]:
                if t.get("eje") == e["id"]:
                    days.append({"date": day["date"], "n": day["n"], "title": t["title"]})
        e["dias"] = days
    used = {t.get("eje") for d in PLAN["versions"][v]["days"] for t in d["topics"]} - {"repaso"}
    missing = used - {e["id"] for e in ejes}
    assert not missing, (v, missing)
    empty = [e["id"] for e in ejes if not e["dias"]]
    assert not empty, (v, empty)

CONCURSO = {
    "estado_ejes": ("A la fecha (14-nov-2026) la CNSC NO ha publicado la Guía de orientación al aspirante ni los ejes temáticos del concurso 2026-2027. "
                    "El Anexo técnico (octubre de 2026) indica que los publicará el ICFES o la universidad/institución de educación superior contratada. "
                    "Esta guía se basa en lo que SÍ es oficial para 2026 (Acuerdos de convocatoria y Anexo técnico) y en los referentes del MEN que el Manual de Funciones (Res. 003842 de 2022) obliga a dominar. "
                    "Donde se usa el concurso anterior (2022) se indica expresamente."),
    "etapas": ["Convocatoria y divulgación", "Adquisición de derechos de participación e inscripciones (primero modalidad con reserva para personas con discapacidad, luego sin reserva)",
               "Aplicación de las pruebas escritas: aptitudes y competencias básicas + psicotécnica (misma sesión, un solo día)",
               "Publicación de resultados de las pruebas escritas y reclamaciones",
               "Verificación de Requisitos Mínimos (solo a quienes superan la prueba de aptitudes)", "Resultados de la VRM y reclamaciones",
               "Aplicación de valoración de antecedentes y entrevista", "Resultados de antecedentes y entrevista, y reclamaciones",
               "Resultados consolidados", "Lista de elegibles (vigencia 2 años desde su firmeza)",
               "Audiencia pública de escogencia de vacante definitiva en establecimiento educativo", "Nombramiento en periodo de prueba y posesión"],
    "etapas_fuente": "cnsc-acuerdo",
    "pruebas": [
        {"prueba": "Aptitudes y competencias básicas", "caracter": "Eliminatoria", "minimo": "60/100 docentes (70/100 directivos)", "peso_docente": "55 %", "peso_directivo": "55 %",
         "evalua": "4 componentes: 1) lectura crítica; 2) razonamiento cuantitativo; 3) competencias blandas (liderazgo, ética, trabajo en equipo y ciudadanía); 4) conocimientos disciplinares de la formación requerida para el empleo y competencias pedagógicas para evaluar, formar y enseñar."},
        {"prueba": "Psicotécnica", "caracter": "Clasificatoria", "minimo": "No aplica", "peso_docente": "5 %", "peso_directivo": "10 %",
         "evalua": "Actitudes, habilidades, motivaciones e intereses profesionales (D.L. 1278 arts. 4-6 y Res. 003842 de 2022)."},
        {"prueba": "Valoración de antecedentes", "caracter": "Clasificatoria", "minimo": "No aplica", "peso_docente": "30 %", "peso_directivo": "25 %",
         "evalua": "Título de requisito mínimo y formación, Saber Pro, segunda lengua, formación continua y experiencia adicionales."},
        {"prueba": "Entrevista", "caracter": "Clasificatoria", "minimo": "No aplica", "peso_docente": "10 %", "peso_directivo": "10 %",
         "evalua": "Competencias comportamentales de la Res. 003842 de 2022."},
    ],
    "pruebas_fuente": ["cnsc-acuerdo", "cnsc-anexo"],
    "pesos_componentes": "El Anexo 2026 no fija el peso de cada componente dentro de la prueba de aptitudes; lo detallará la Guía de orientación. Como antecedente oficial, en 2022 el Decreto 574 (contexto rural) asignó: lectura crítica 20 %, razonamiento cuantitativo 20 %, conocimientos específicos 40 % y conocimientos pedagógicos 20 %.",
    "antecedentes_docente_aula": [
        ["1. Educación formal mínima", "Título de requisito mínimo (Res. 003842)", "5"],
        ["2. Educación formal adicional en ciencias de la educación", "Licenciatura 10 · Especialización 14 · Maestría 18 · Doctorado 25", "hasta 25"],
        ["3. Educación formal adicional en otras áreas", "Profesional no licenciado 4 · Especialización 6 · Maestría 8 · Doctorado 10", "hasta 10"],
        ["4. Saber Pro y otros criterios", "Saber Pro quintil 5: 9 · quintil 4: 3 · Segunda lengua B2+: 6", "hasta 15"],
        ["5. Formación continua", "Cursos > 100 h o 4 créditos (últimos 5 años) en pedagogía, didáctica o gestión: 1 c/u", "hasta 5"],
        ["6. Experiencia", "Docente relacionada 4/año (máx. 20) · otros cargos docentes 3/año (máx. 15) · otra experiencia educativa 1/año (máx. 5)", "hasta 40"],
    ],
    "antecedentes_fuente": "cnsc-anexo",
    "referencia_2022": ("Concurso anterior: Procesos de Selección Nos. 2150 a 2237 de 2021, 2316 y 2406 de 2022 (operador: Universidad Libre). La CNSC publicó la Guía de orientación el 26-ago-2022, "
                        "con pruebas de 'aptitudes y competencias básicas' (contexto no rural) y de 'conocimientos específicos y pedagógicos' (contexto rural, Decreto 574 de 2022). "
                        "El enlace oficial a esa guía (historico.cnsc.gov.co) no está disponible hoy, por lo que sus ejes no se transcriben aquí."),
    "referencia_2022_fuentes": ["cnsc-2022", "d574"],
}

# ---------- Contenido de estudio por tema (content/temas/*.md) ----------
sys.path.insert(0, str(ROOT / "scripts"))
import md_mini
base_id = lambda i: re.sub(r"-v\d+$", "", i)
content, idmap = {}, {}
for f in sorted((ROOT / "content" / "temas").glob("*.md")):
    meta, body = md_mini.parse_file(f.read_text())
    refs = meta.get("refs", [])
    for r in refs: assert r in ids, (f.name, r)
    assert "Puntos clave" in body and "Trampas frecuentes" in body, f.name
    content[f.stem] = {"html": body, "refs": refs}
    for i in meta["ids"]:
        assert i not in idmap, ("id duplicado", i)
        idmap[i] = f.stem
for v, ejes in VERS.items():
    order, info = [], {}
    for day in PLAN["versions"][v]["days"]:
        for t in day["topics"]:
            if t.get("eje") in (None, "repaso"): continue
            b = base_id(t["id"])
            assert b in idmap, ("tema sin contenido de estudio", v, b)
            if b not in info:
                info[b] = {"id": b, "title": re.sub(r"\s*\((vuelta|repaso)[^)]*\)$", "", t["title"]), "eje": t["eje"], "file": idmap[b], "dias": []}
                order.append(b)
            info[b]["dias"].append({"date": day["date"], "n": day["n"]})
    for e in ejes:
        e["temas"] = [info[b] for b in order if info[b]["eje"] == e["id"]]
        assert e["temas"], (v, e["id"], "eje sin temas")
(ROOT / "data" / "temas.json").write_text(json.dumps({"map": idmap, "content": content}, ensure_ascii=False))
print("temas.json:", len(content), "archivos,", len(idmap), "temas")

guia = {"updated": dt.date.today().isoformat(), "concurso": CONCURSO, "documentos": DOCS,
        "versiones": {v: {"ejes": ejes} for v, ejes in VERS.items()}}
(ROOT / "data" / "guia.json").write_text(json.dumps(guia, ensure_ascii=False, indent=1))
print("guia.json:", {v: len(e) for v, e in VERS.items()}, "ejes;", len(DOCS), "documentos")
