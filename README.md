# Preparación de Libras con OpenAI Agents

Este proyecto aislado de Python 3.11 prepara la capa de orquestación local de Libras. El diagnóstico sin conexión construye los esquemas de tres herramientas; esto no demuestra que Teams, Azure, ClickUp o las solicitudes a modelos estén listos para operar. Todas las integraciones permanecen sin configurar hasta que se inyecten y revisen explícitamente.

## Inicio rápido (PowerShell)

Ejecute los comandos desde el directorio del proyecto. Utilice su intérprete directamente; activar el entorno es opcional.

```powershell
& 'C:\Users\jgarcia\AppData\Local\Programs\Python\Python311\python.exe' -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
.\.venv\Scripts\python.exe -m libras_agents doctor
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

`requirements.lock` fija las versiones del entorno resuelto en Windows x64 con Python 3.11, incluidas las herramientas de empaquetado, sin registrar una ruta absoluta de instalación editable. Instálelo primero y después instale este paquete en modo editable con `--no-deps --no-build-isolation` para respetar esas versiones. Recree el entorno si cambia la plataforma o la versión de Python admitida. No utilice el repositorio anterior como `PYTHONPATH` ni reutilice sus paquetes incluidos.

## Límites de ejecución

El flujo previsto es **Teams -> adaptador autenticado de Microsoft Agents -> orquestador de OpenAI -> proveedores de lectura acotada para documentos, catálogo de bases de datos y ClickUp**. Los paquetes de alojamiento/MSAL de Microsoft y de Azure Search, Identity, Key Vault y Blob Storage están instalados como preparación; aquí no se inicia ningún cliente, búsqueda de credenciales, servidor ni acceso a cuentas.

`build_agent(model=...)` exige un modelo explícito y no vacío. `run_libras(..., model=..., api_key=...)` valida ambos parámetros antes de llamar al SDK, rechaza la etiqueta del modelo de prueba sin conexión, limita el ciclo a seis turnos y desactiva las trazas y la inclusión de datos sensibles. Quien invoque la función debe proporcionar explícitamente su clave de API autorizada; esta base no selecciona credenciales ni destinos desde el entorno. La CLI no incluye ningún comando para ejecutar un modelo. `.env.example` contiene credenciales vacías y nombres de referencia sin secretos; nunca se carga automáticamente.

Cada herramienta acepta únicamente una consulta de búsqueda acotada y delega en su propio proveedor opcional de lectura asíncrona. Si falta el proveedor, se produce `ProviderUnavailable`, incluso a través del envoltorio del SDK; no se genera evidencia sustitutiva ni una respuesta sintética. Los proveedores deben preservar identificadores de fuente, procedencia de citas y evidencia, autorización en el servidor, límites de resultados y operaciones de solo lectura. No se exponen herramientas genéricas de SQL, HTTP, MCP ni acceso a credenciales.

El diagnóstico utiliza la etiqueta interna `offline-only-test-model` únicamente para construir esquemas sin enviar solicitudes. Informa la presencia de variables de entorno, nunca sus valores; las capacidades siguen como `unconfigured` aunque existan variables. Su comprobación de citas Blob utiliza la función reutilizada. La importación y construcción del SDK no realizan solicitudes de red; las protecciones de privacidad reemplazan las opciones de trazas y registros del entorno y desactivan el registro del SDK antes de construir o ejecutar el agente.

## Inventario de Azure proporcionado

Los nombres siguientes pertenecen al inventario proporcionado de `rg-libras-prod`. No se han verificado su existencia, configuración activa, permisos ni destinos.

| Nombre | Función proporcionada |
| --- | --- |
| `app-libras-prod` | App Service de producción |
| `app-libras-staging` | App Service de pruebas |
| `ASP-rglibrasprod-aee7` | Plan de App Service |
| `bot-libras-prod` | Registro del bot |
| `id-libras-bot-prod` | Identidad administrada del bot |
| `id-libras-feedback-export-prod` | Identidad administrada para exportar comentarios |
| `kv-libras-prod` | Key Vault |
| `srch-libras-prod` | Azure AI Search |
| `stlibrasconvprod` | Cuenta de almacenamiento de conversaciones |
| `stlibrasdbcatalogprod01` | Blob Storage del catálogo de bases de datos |

Utilice primero el entorno de pruebas para una migración posterior autorizada. Esta preparación no incluye scripts de despliegue ni realiza cambios en producción o envía mensajes de Teams.

## Referencias del código y siguiente migración

La referencia de solo lectura es el árbol de trabajo con cambios locales de `C:\cw\Libras`; el commit del repositorio que lo contiene es `2591bdc5e272b26453c6ac30b0c987530c0d5e69`. Ese commit no identifica los bytes exactos de los cambios locales. La [referencia de GitHub](https://github.com/alejandrogaseinfo/Libras) proporcionada devolvió 404 sin acceso autenticado. La base de origen contiene fallos funcionales conocidos; reutilizar su código no demuestra aceptación.

| Componente | Referencia | Requisito de migración |
| --- | --- | --- |
| Entrada de Teams | `src/app.py`, `src/agent.py`, `src/auth_middleware.py` | Autenticar antes de orquestar; preservar la autorización de organización y usuario |
| Búsqueda documental | `src/documentary_tools.py` | Acotar la recuperación y conservar citas y evidencia |
| Catálogo de bases de datos | `src/multisource_retrieval.py`, `AzureBlobCatalogAdapter` | Limitar las lecturas del catálogo; suprimir citas de Blob privado |
| Artefactos SQL | `src/sql_artifact_reader.py` | Preservar vínculos inmutables de versión, commit, publicación y esquema; no exponer ejecución general de SQL |
| ClickUp | `src/clickup_mcp_adapter.py`, `src/clickup_live_client.py` | Preservar lecturas acotadas y autorizadas |
| Función de citas | `src/formatting.py::_is_private_blob_url` | Reutilizada como `libras_agents.evidence.is_private_blob_url`, con protección ante servidores malformados |

El siguiente paso es revisar y migrar un proveedor con pruebas determinísticas de su contrato; después, migrar el adaptador autenticado de Teams como una unidad separada. No copie `handler.py`, el orquestador de Terra ni paquetes incluidos de terceros. Confirme el comportamiento con evidencia de origen aprobada y criterios de aceptación en el entorno de pruebas antes de desplegar.

La conexión de herramientas sigue la [documentación oficial de OpenAI](https://developers.openai.com/api/docs/guides/tools#usage-in-the-agents-sdk); el SDK fijado es `openai-agents==0.23.1`. Las pruebas locales comprueban fallos de herramientas, proveedores inyectados, validación de modelo y clave, protecciones de privacidad y construcción sin conexión. La autenticación activa, calidad de recuperación, entrega en Teams y comportamiento del modelo permanecen sin probar. Lea `agent.md` para conocer las instrucciones del proyecto.
