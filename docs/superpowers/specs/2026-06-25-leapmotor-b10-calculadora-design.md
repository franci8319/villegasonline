# Calculadora Leapmotor B10 — Batería y Autonomía

## Contexto

Villegas Online es un sitio estático (GitHub Pages, dominio `villegasonline.es`) con una grilla de apps en [index.html](../../../index.html). Algunas apps son archivos HTML únicos autocontenidos en este mismo repo (ej. [memory.html](../../../memory.html)), otras son subdominios externos. Esta nueva app sigue el patrón de archivo único.

El usuario tiene un Leapmotor B10 (versión 65 kWh útil) y quiere una calculadora para estimar tiempo de carga, autonomía y coste a partir de los datos que tenga a mano en cada momento (% de batería, potencia del punto de carga disponible, etc.).

## Datos oficiales del Leapmotor B10 (fuente: búsqueda web, ficha técnica)

| Versión | Capacidad útil | Autonomía WLTP | Consumo medio WLTP | Carga AC máx | Carga DC máx |
|---|---|---|---|---|---|
| Estándar | 55 kWh | 361 km | ~15,2 kWh/100km | 11 kW | 140 kW |
| Larga autonomía | 65 kWh | 434 km | 17,3 kWh/100km | 11 kW | 168 kW |

Por defecto la app precarga la versión de 65 kWh (la del usuario), seleccionable entre ambas.

## Archivo y ubicación

- Nuevo archivo: `leapmotor-b10.html` en la raíz del repo.
- Nueva card en `index.html`, enlazando a `/leapmotor-b10.html`, usando el emblema oficial de Leapmotor (blanco, recortado del logo oficial) sobre un fondo de gradiente oscuro (negro/gris, coherente con la identidad de marca de Leapmotor).
- Activo de icono: `leapmotor-icon.png` (emblema blanco, fondo transparente) guardado en la raíz del repo junto a los demás iconos.

## Estructura de la calculadora

### Datos del coche (precargados, editables)
- Selector de versión: 55 kWh / 65 kWh → autocompleta capacidad útil, autonomía WLTP, consumo WLTP y potencia máx. DC.
- Capacidad útil (kWh), autonomía WLTP (km) y consumo WLTP (kWh/100km) quedan visibles y editables por si el usuario quiere ajustar a su unidad concreta.

### Inputs del usuario (sección "Carga")
- Batería actual (%) — input numérico 0–100.
- Batería objetivo (%) — input numérico 0–100, debe ser mayor que la actual.
- Tipo de carga: AC (hasta 11 kW) / DC rápida (hasta el máximo de la versión elegida). El tipo limita la potencia máxima aceptada en el siguiente campo.
- Potencia del punto de carga (kW) — lo que el usuario tenga disponible (ej. 7.4, 11, 22, 50, 100, 150...).
- Precio de la luz (€/kWh) — opcional, solo para el cálculo de coste.

### Inputs del usuario (sección "Autonomía")
- Consumo real (kWh/100km) — precargado igual al consumo WLTP de la versión elegida, editable para reflejar la experiencia real del usuario.

### Cálculos y resultados (en vivo, sin botón "Calcular")
1. **Energía a cargar (kWh)** = (objetivo% − actual%) / 100 × capacidad útil.
2. **Potencia efectiva (kW)** = mínimo(potencia del punto de carga introducida, potencia máxima del coche para el tipo de carga elegido — 11 kW AC / 140 o 168 kW DC según versión).
3. **Tiempo de carga estimado** = energía a cargar / potencia efectiva (mostrado en horas y minutos).
4. **Autonomía al % actual** y **autonomía al % objetivo** (km), calculadas dos veces: con el consumo WLTP de fábrica y con el consumo real introducido por el usuario, mostradas lado a lado para comparar.
5. **Coste de la carga (€)** = energía a cargar × precio €/kWh, solo si el usuario ha introducido un precio.
6. **Aviso de carga rápida**: si tipo = DC y objetivo% > 80, mostrar nota: "La carga rápida DC se ralentiza a partir del 80%, el tiempo real puede ser algo mayor."

### Validaciones
- Si objetivo% ≤ actual%: no se muestran resultados de carga, se muestra un mensaje ("el objetivo debe ser mayor que el nivel actual") en su lugar.
- Si potencia del punto de carga es 0 o vacía: el tiempo de carga se muestra como "—" en vez de un número.
- Todos los inputs numéricos llevan `min`/`max` acordes (0–100 para porcentajes, >0 para potencias y capacidad).

## Estilo visual

Coherente con el resto del sitio: fondo azul `#1a4a8a`, tipografía del sistema (la misma familia que `index.html`/`memory.html`), tarjetas/secciones con fondo algo más claro para separar "Datos del coche", "Carga" y "Autonomía". Responsive (apilado en móvil, como el resto de apps del sitio).

## Fuera de alcance (YAGNI)

- Curva de carga DC detallada (modelo de ralentización real por tramos) — se sustituye por un aviso textual simple.
- Pérdidas/eficiencia de carga (AC ~90%, DC ~95%) — no se modela, el coste se calcula sobre la energía nominal de batería.
- Persistencia de datos entre sesiones (localStorage) — no solicitada.
- Geolocalización o lista de puntos de carga — no solicitada.
