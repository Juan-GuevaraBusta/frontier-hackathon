# System Design 01 — Agente computer-use sobre VNC (Reto 1)

Estado: Fase 1 (interrogatorio). Ronda 1 cerrada. Fuente de verdad: `frontier-reto-1/README.md` y `frontier-reto-1/pruebas/*.json`.

## Hallazgos de las pruebas

| Prueba | Tipo | Implicación de diseño |
| --- | --- | --- |
| E1 | crear | Dedupe obligatorio antes de crear (buscar por NIT/nombre). README L100. |
| E2 | actualizar | Localizar registro existente (`CL-0007`) y editar un solo campo. |
| E3 | contar | `respuesta_esperada: 45`: contar a ojo no escala; usar filtros/totales. |
| E4 | exportar | Se evalúan los filtros aplicados al exportar (`estado`, `desde`, `hasta`). |
| E5 | negarse | Homónimos: `fallida` y nombrar documentos `52345678`, `1019876543`. |

## Decisiones cerradas (Ronda 1)

- D1. LLM/VLM vía API permitido. Todo lo demás (cliente RFB, percepción, tools, loop, memoria, seguridad) se construye en casa. Prohibido: tools nativas de computer use (Anthropic computer tool, OpenAI CUA/Operator), SaaS de agentes de UI, MCPs de terceros que operen la UI.
- D2. Proveedor de modelos: OpenRouter (una sola key).
- D3. Percepción: OCR local en CPU como auxiliar; sin GPU ni VLM self-hosted. (Confirmar en R2.2.)
- D4. Presupuesto: ≤ USD 0,20 por tarea. Tiempo: meta < 3:30, kill-switch duro a 4:30.
- D5. Equipo: 2 personas. Ventana: 11:23 → 20:00 (~8,5 h).
- D6. Credenciales del escritorio disponibles; viven en `.env` (gitignored) y en env vars de Render. Nunca en el repo ni en resúmenes.
- D7. Evaluación: todas las tareas sobre la misma app no vista → memoria de app entre tareas, con clave por fingerprint, tratada como pista (siempre se reverifica en pantalla).
- D8. El evaluador puede mandar varias tareas a la vez → concurrencia en proceso (asyncio), candado por URL de escritorio, limitador global hacia OpenRouter.
- D9. Despliegue: Render, web service siempre encendido (plan pago, no free).
- D10. Exportar: verificar filtros visibles antes de exportar + señal visual después. Un solo campo de fecha en la lista = ese es el filtro.

Del README (no negociables): 1280×800, RFB sobre `wss://…/websockify` (L17–24); clic con hold ≥100 ms (L47); esperar repintado ≤1 s (L45–46); seleccionar todo antes de escribir (L48); contrato `/tasks` <2 s y polling 5 s (L72–90); detener al reportar o al timeout (L111–113); sin secretos en resumen (L109, L119); formato `respuesta:` (L103–107).

## Supuestos abiertos

- SUPUESTO S1: el reloj de 5 min arranca al responder `POST /tasks`.
- SUPUESTO S2: no se puede explorar la app de evaluación antes de la primera tarea.
- SUPUESTO S3: pregunta sin respuesta posible → `fallida`, sin línea `respuesta:` (README L58, L107).
- SUPUESTO S4: el servidor VNC acepta keysyms Latin-1 (í, ñ, #) sin modificadores manuales. Validar en spike.
- SUPUESTO S5: precios de imagen en OpenRouter permiten 20–30 pasos con captura dentro de USD 0,20 usando un VLM barato. Validar con 1 llamada real.

## Historial

- v01 (11:23): Ronda 1 respondida.
