# Usabilidad estudiantes · Campus Virtual

Tablero sobre el uso del Campus Virtual (Moodle) por parte de los estudiantes de **Pregrado presencial, Distancia y Posgrado** en el periodo académico 2026-2, del **1 de agosto al 28 de septiembre de 2026** (59 días).

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

## Cómo actualizarlo

1. Guarda en la raíz de esta carpeta (no se sube a GitHub) el informe de Configurable Reports `USABILIDAD ESTUDIANTE20262.xlsx` (consulta por estudiante con la columna `modalidad`). Configurable Reports corta en 5.000 filas por defecto; sube el **Report limit** del bloque antes de exportar.
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
- `index.html` contiene nombres y usuarios de estudiantes: si lo subes a un repositorio, mantenlo **privado**.
