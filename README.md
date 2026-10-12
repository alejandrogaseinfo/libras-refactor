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

## Mapa de Azure verificado (2026-10-12)

La auditoría de solo lectura mediante Azure CLI verificó los diez recursos siguientes en `rg-libras-prod`, suscripción **ASEINFO Azure** (`75eecb3a-3825-4a53-bd91-09386a38e8a4`), tenant `abcee5bb-aa0e-4ecb-9377-71f4d0f42c2a`. Nueve están en Central US; Azure Bot es global. Son hechos del plano de administración ARM: no se probaron acceso a datos, secretos ni integraciones activas. Esta base mínima conserva esos límites y no configura Teams ni proveedores reales.

| Recurso existente | Estado y función observados |
| --- | --- |
| `app-libras-prod` | App Linux, Running y HTTPS; tiene identidad `SystemAssigned` y la identidad de bot `UserAssigned` |
| `app-libras-staging` | App Linux independiente, Running y HTTPS, con su propia `SystemAssigned`; no es un slot de producción |
| `ASP-rglibrasprod-aee7` | Plan Linux B1 Basic, un worker y dos sitios; ambas apps comparten cómputo |
| `bot-libras-prod` | Azure Bot F0, `UserAssignedMSI`, con `MsTeamsChannel` habilitado y dirigido a producción |
| `id-libras-bot-prod` | Identidad de autenticación del bot, adjunta a producción; no se asume como lectora de datos |
| `id-libras-feedback-export-prod` | Identidad existente, no adjunta a las dos apps inspeccionadas; su nombre sugiere exportación, pero no demuestra actividad ni programación |
| `kv-libras-prod` | Standard, RBAC habilitado, `accessPolicies` vacío, red Allow, acceso público habilitado y eliminación temporal de 90 días |
| `srch-libras-prod` | Free, una réplica y partición, autenticación Entra o clave; claves locales habilitadas y sin identidad de servicio |
| `stlibrasconvprod` | StorageV2 Standard LRS, HTTPS/TLS 1.2, Blob público deshabilitado y red Allow; el contrato de conversaciones usa Azure Tables |
| `stlibrasdbcatalogprod01` | StorageV2 Standard LRS, HTTPS/TLS 1.2, Blob público deshabilitado, clave compartida y endpoint habilitados; destino del catálogo y artefactos publicados según el repositorio |

### Identidades y permisos existentes

| Identidad | Principal/object ID | Client ID, cuando corresponde |
| --- | --- | --- |
| `SystemAssigned` de producción | `2fc398ef-6e81-41c3-b955-62b05d31ac7b` | No devuelto en los metadatos de la app |
| `SystemAssigned` de staging | `cfd4eb89-5e9e-429a-b9db-1f9b98a92b63` | No devuelto en los metadatos de la app |
| `id-libras-bot-prod` | `30fda04b-df31-4747-b70b-5214775194e7` | `bac24639-da91-45a3-ae85-062b07188b9c` |
| `id-libras-feedback-export-prod` | `17eaac8c-4ed4-4700-b5a2-507b97d8391f` | `a8558af3-cfd4-4fc0-a864-85786ac854c1` |

Las cuatro asignaciones directas siguientes pertenecen al principal `SystemAssigned` de producción y no tienen condición. Son permisos ya existentes, no instrucciones para crear, reasignar o ampliar roles. Cada alcance relativo se agrega al prefijo `/subscriptions/75eecb3a-3825-4a53-bd91-09386a38e8a4/resourceGroups/rg-libras-prod`.

| Rol de producción | Alcance relativo exacto |
| --- | --- |
| `Search Index Data Reader` | `/providers/Microsoft.Search/searchServices/srch-libras-prod` — servicio completo |
| `Key Vault Secrets User` | `/providers/Microsoft.KeyVault/vaults/kv-libras-prod` |
| `Storage Table Data Contributor` | `/providers/Microsoft.Storage/storageAccounts/stlibrasconvprod` — cuenta completa |
| `Storage Blob Data Reader` | `/providers/Microsoft.Storage/storageAccounts/stlibrasdbcatalogprod01/blobServices/default/containers/evolution-db-catalog` — solo ese contenedor |

Ambas apps tienen `keyVaultReferenceIdentity=SystemAssigned`: la UAMI del bot no resuelve sus referencias de Key Vault. `msaAppId` del bot coincide con el client ID y el vínculo MSI de `id-libras-bot-prod`. Teams apunta a `https://app-libras-prod-h0azhpfef6d4fyax.centralus-01.azurewebsites.net/api/messages`; staging no recibe ese tráfico ni hereda automáticamente los permisos de producción.

El inventario ARM del grupo devolvió 15 asignaciones y `nextLink=null`. No se encontraron asignaciones coincidentes para staging, la UAMI del bot ni la de exportación en los alcances del grupo/heredados inspeccionados. Esto no demuestra ausencia global de privilegios ni denegación efectiva. Véase la [referencia de consulta de asignaciones](https://learn.microsoft.com/en-us/cli/azure/role/assignment#az-role-assignment-list).

El principal de ingestión de SharePoint `f0ec8ab2-9bf6-4d82-80e0-4ddbbc2fe26e`, cuyo nombre documentado es `libras-sharepoint-ingestion-prod`, es distinto del bot, la app y la sesión CLI, y no es uno de los diez recursos ARM. Tiene `Search Index Data Contributor` sobre todo `srch-libras-prod`, sin condición ni versión de condición. La referencia documenta Graph `Sites.Selected` y lectura concedida por sitio; esos permisos de Graph no se revalidaron en esta auditoría ARM.

### Datos, red y límites de acceso efectivo

El contrato de origen persiste conversaciones en Azure Tables: documenta `librasconversationmap` y configura `librasfeedback`. El rol de producción permite leer, escribir y eliminar entidades a nivel de cuenta; no se ha establecido actividad actual de feedback o exportación. No se le debe tratar como almacenamiento de conversaciones exclusivamente Blob. No se consultaron nombres, valores ni uso actual de secretos; las credenciales OpenAI, SharePoint y ClickUp aparecen como contratos en la documentación del repositorio.

El catálogo contiene esquema, catálogo y artefactos SQL publicados e inmutables; no es una conexión SQL activa. Deben conservarse los vínculos de release, commit, publicación, esquema y citas. Su red tiene default Deny, excepción `AzureServices`, 36 reglas IP/CIDR, cero reglas VNet o de acceso a recursos y ningún endpoint privado; producción no tiene integración VNet. Las reglas coinciden con 5/5 direcciones de salida actuales y 22/22 posibles, sin direcciones fuera del conjunto. Esto solo demuestra coincidencia de metadatos: Azure Storage en la misma región utiliza direcciones privadas y esas reglas públicas no prueban conectividad efectiva. No hubo pruebas del plano de datos. Consulte las [restricciones de reglas IP de Storage](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-limitations#restrictions-for-ip-network-rules).

El broker de ClickUp es código que usa OAuth, el destino fijo `mcp.clickup.com/mcp` y un registro de alcances controlado por el servidor; no demuestra que exista otro servicio ARM de broker. Los roles de Azure no conceden acceso a cuentas externas de ClickUp/OpenAI ni a sitios de SharePoint. Preserve hosting, identidades y configuración existentes; cualquier cambio de permisos, red o integración requiere un alcance posterior explícito. Staging es una app separada con cómputo compartido: antes de usarla deben verificarse sus permisos y configuración propios.

### Procedencia conservada y referencias

Se conservaron cinco despliegues ARM `Incremental` y `Succeeded`; acreditan los destinos indicados, no el operador, flujo original ni plantilla exacta.

| Fecha de 2026 | Despliegue conservado | Destino |
| --- | --- | --- |
| 23 de julio | `searchservice-1784839792935` | Search; coincide con `systemData` |
| 25 de julio | `Microsoft.Web-WebApp-Portal-ffca8dac-8e43` | App de producción y plan compartido |
| 28 de julio | `kv-libras-prod` | Key Vault; coincide con `systemData`, `createdByType=User` |
| 30 de julio | `Microsoft.AzureBot-20260730084456` | Azure Bot |
| 26 de agosto | `stlibrasdbcatalogprod01_1787770750955` | Cuenta del catálogo y servicios Blob/File predeterminados |

La cuenta de conversaciones registra creación `2026-08-08T13:32:38.5783082Z`, pero no se estableció su flujo original de aprovisionamiento. La procedencia y fecha de staging y las dos UAMI siguen incompletas. Los nombres de despliegue sugieren uso del portal, sin probar quién operó ni cómo se provisionó todo.

En la referencia de solo lectura, `infra/azure.bicep` y `botRegistration/azurebot.bicep` —este último asociado a ARM de Toolkit en `m365agents.yml`— declaran plan, app, UAMI, bot y Teams; Search tiene una plantilla separada `azure-search.bicep`. No incluyen Key Vault, las cuentas de almacenamiento, staging, la identidad de exportación ni asignaciones de roles. No debe inferirse que el Bicep versionado creó todos los recursos. Los contratos históricos o previstos también se apoyan en `docs/ai/context/consulta-clickup-live.md`, `docs/ai/validation/2026-10-08-ingestion-readonly.md`, `src/conversation_mapping_store.py` y `src/config.py`; no sustituyen los hechos ARM verificados ni prueban operación activa.

Esta actualización es documental: conserva únicamente la base mínima con Agents API y no despliega, recrea recursos, altera permisos ni envía mensajes de Teams.

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
