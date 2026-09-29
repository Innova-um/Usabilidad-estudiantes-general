# Usabilidad estudiantes · Campus Virtual

Tablero sobre el uso del Campus Virtual (Moodle) por parte de los estudiantes de **Pregrado presencial, Distancia y Posgrado** en el periodo académico 2026-2, del **1 de agosto al 28 de septiembre de 2026** (59 días).

Tiene dos vistas, que se eligen con los botones de arriba:

- **Usabilidad del Campus Virtual:** todas las modalidades.
- **Notas estudiantes:** solo Pregrado presencial, con la nota de Moodle sobre lo calificado.

Abre `index.html` en el navegador. No necesita servidor.

## Qué muestra

- Porcentaje de estudiantes que entraron al aula.
- Minutos al día y días con actividad por estudiante activo.
- Tareas y exámenes entregados.
- Nivel de uso y tiempo por modalidad, facultad y programa.
- Qué hacen los estudiantes en el aula: contenidos, tareas, exámenes, foros, actividades completadas e inicios de sesión.
- Regularidad: cuántos días del periodo entró cada estudiante.
- Detalle por estudiante, descargable en CSV.
- **Filtros:** modalidad, facultad y programa, con selección múltiple, y buscador por estudiante. Cada elemento elegido recibe un color que se mantiene en los gráficos; con dos o más elegidos, «¿Qué hacen los estudiantes en el aula?» los compara lado a lado.

## Notas estudiantes

- Estudiantes con nota, nota promedio, estudiantes con nota baja y cursos que van perdiendo.
- Programas de mejor, media y menor nota: todos los programas y por facultad.
- Nota promedio por facultad o programa, distribución (alta, media, baja, sin nota) y nota según el nivel de uso del Campus.
- Detalle por estudiante, descargable en CSV (por defecto, los de nota baja).

## Cómo actualizarlo

1. Guarda en la raíz de esta carpeta (no se sube a GitHub) el informe de Configurable Reports `USABILIDAD ESTUDIANTE20262.xlsx` (consulta por estudiante con la columna `modalidad`). Configurable Reports corta en 5.000 filas por defecto; sube el **Report limit** del bloque antes de exportar.
   También `Informe de notas estudiantes.xlsx` (consulta de notas con la columna `promedio_calificado_0_5`). Si no está, el tablero se genera sin la vista de notas.
2. Para cambiar el periodo o los umbrales de nivel de uso, edita `PERIODOS` y `NIVELES` al inicio de `build/build.py`. `PERIODOS` admite varios archivos para comparar periodos.
3. Ejecuta:

   ```bash
   python build/build.py
   ```

Requisitos: Python 3 con `pandas` y `openpyxl`.

## Notas de cálculo

- **Tiempo de uso:** es una estimación a partir del log de Moodle. Se suma el tiempo entre clics consecutivos y se descartan las pausas de más de 30 minutos. Cuenta toda la actividad del estudiante en la plataforma.
- **Nivel de uso:** alto con 20 min/día o más; medio de 5 a 20; bajo con menos de 5; sin uso si no registró ninguna acción. Los minutos al día se promedian sobre todos los días del periodo.
- **Facultad y programa** salen de las categorías de los cursos matriculados. No cuentan Plurilingüismo ni Estudios Generales. Un estudiante con cursos en varias modalidades o programas aparece en cada uno.
- **Nota sobre lo calificado:** promedio del estudiante solo en las actividades que ya tienen nota, en la escala de la universidad (0 a 500; la consulta entrega 0 a 5 y el script la multiplica por 100, ver `ESCALA_NOTA` en `build/build.py`). El total del curso de Moodle cuenta como 0 lo no calificado y, a mitad de semestre, haría ver bajas casi todas las notas. Alta: 400 a 500; media: 300 a 399; baja: menos de 300.
- `index.html` contiene nombres y usuarios de estudiantes: si lo subes a un repositorio, mantenlo **privado**.
