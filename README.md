# Base mínima de Libras con OpenAI Agents API

Esta base mínima y aislada de Python 3.11 prepara el acceso a OpenAI Agents API para un sistema agéntico de Libras. OpenAI administra la orquestación y las sesiones; la aplicación local solo atiende callbacks de lectura autorizados. El diagnóstico construye tres definiciones de funciones sin conectarse a servicios. Esto no representa una refactorización completa ni demuestra que Teams, Azure, ClickUp o la cuenta de OpenAI estén listos para operar.

## Inicio rápido (PowerShell)

Ejecute los comandos desde el directorio del proyecto. Utilice su intérprete directamente; activar el entorno es opcional.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
.\.venv\Scripts\python.exe -m libras_agents doctor
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

`requirements.lock` fija las versiones del entorno resuelto en Windows x64 con Python 3.11, incluidas las herramientas de empaquetado, sin registrar una ruta absoluta de instalación editable. Instálelo primero y después instale este paquete en modo editable con `--no-deps --no-build-isolation` para respetar esas versiones. Recree el entorno si cambia la plataforma o la versión de Python admitida. No utilice el repositorio anterior como `PYTHONPATH` ni reutilice sus paquetes incluidos.

## Límites de ejecución

El flujo previsto es **Teams -> adaptador autenticado de Microsoft Agents -> sesión administrada por OpenAI Agents API -> callbacks locales de lectura acotada para documentos, catálogo de bases de datos y ClickUp**. OpenAI selecciona las herramientas y mantiene el estado de la conversación. La base no contiene un ciclo local de razonamiento de Agents SDK o Responses API. Los paquetes de alojamiento/MSAL de Microsoft y de Azure Search, Identity, Key Vault y Blob Storage están instalados como preparación; aquí no se inicia ningún servidor, búsqueda de credenciales ni acceso a cuentas.

`build_request_manifest(..., agent_id=...)` prepara una solicitud sin enviarla. `run_session(..., agent_id=..., api_key=...)` exige el ID de un agente existente y una clave explícita antes de acceder a `AsyncOpenAI.beta.agents.sessions.create`. El agente guardado aporta el modelo; `model=...` es una sustitución opcional que se omite por completo cuando no se proporciona. La solicitud usa `environment={"type": "none"}`, `stream=True` y las tres definiciones de funciones como lista completa: sustituye todas las herramientas del agente guardado para evitar capacidades adicionales.

El cliente Python `openai==3.29.0` añade `OpenAI-Beta: agents=v1` y la autorización con la clave suministrada. Según el [inicio rápido oficial](https://developers.openai.com/api/docs/guides/agents-api/quickstart), la clave requiere `api.agents.read`, `api.agents.write` y `api.responses.write`. No se ha comprobado el acceso de la cuenta. La CLI solo ofrece el diagnóstico; no crea agentes ni sesiones. `.env.example` incluye `OPENAI_AGENT_ID`, credenciales vacías y nombres sin secretos, y nunca se carga automáticamente. La aplicación no busca claves ni sesiones existentes en el entorno.

Los callbacks `search_documents`, `search_database_catalog` y `search_clickup` aceptan únicamente `query`, con un máximo de 2000 caracteres; delegan en proveedores opcionales de lectura asíncrona. Cada callback dispone de hasta 30 segundos y puede devolver hasta 256000 bytes UTF-8. Se permiten hasta seis llamadas locales por solicitud, sin imponer un límite de turnos al orquestador remoto. Un proveedor ausente produce `ProviderUnavailable`; los errores de autorización y ejecución se conservan localmente. El cliente envía un resultado de herramienta fallido genérico al servicio, sin convertirlo en evidencia ficticia ni exponer el texto de la excepción.

El cliente gestiona el transporte de resultados con los IDs de turno y llamada; la aplicación solo despacha los tres nombres permitidos. Los proveedores deben preservar identificadores de fuente, procedencia de citas y evidencia, autorización en el servidor, límites de resultados y operaciones de solo lectura. No se exponen herramientas genéricas de SQL, HTTP, MCP ni acceso a credenciales. El historial guardado no autoriza volver a ejecutar una llamada.

La observación local espera hasta 120 segundos. Un tiempo agotado o cerrar el flujo **no confirma que el trabajo remoto haya sido cancelado**. Cancelar exige un evento separado `agent.session.input.cancel`; cancelación, eliminación de sesiones, recuperación y continuidad entre mensajes quedan fuera de esta base. `get_final_result()` distingue un turno completado de fallos, cancelaciones o una sesión simplemente inactiva. Consulte la [gestión de turnos y sesiones](https://developers.openai.com/api/docs/guides/agents-api/sessions).

El diagnóstico informa `OpenAI Agents API`, las tres definiciones alojadas y la presencia de variables, nunca sus valores. Las capacidades siguen como `unconfigured`, Teams como `not-wired` y el acceso de cuenta/configuración activa como no verificados. También comprueba la función de citas Blob. La importación y el diagnóstico no realizan solicitudes de red.

## Estado y retención de datos

Agents API conserva el estado de las sesiones. Actualmente solo admite residencia de datos en Estados Unidos y no admite Zero Data Retention (ZDR), incluso con un entorno autohospedado. Desactivar trazas del SDK local no ofrece una protección equivalente ni cambia esa retención. La política de eliminación de sesiones y datos requiere una integración posterior autorizada. Estas limitaciones están documentadas en la [descripción oficial de Agents API](https://developers.openai.com/api/docs/guides/agents-api/overview). Esta preparación no ha creado ninguna sesión real.

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

La conexión de funciones sigue la [documentación oficial de Agents API](https://developers.openai.com/api/docs/guides/agents-api/tools/functions). Las pruebas usan el cliente real de Python y `httpx2.MockTransport` con eventos SSE en memoria para comprobar la ruta beta, encabezados, solicitud y transporte automático de resultados. También verifican callbacks, límites, errores, modelo opcional y diagnóstico sin conexión. La autenticación activa, calidad de recuperación, entrega en Teams y comportamiento real del servicio permanecen sin probar. Lea `agent.md` para conocer las instrucciones del proyecto.
