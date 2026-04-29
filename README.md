# Análisis de Vulnerabilidades – FlowiseAI

Este proyecto realiza un análisis de seguridad integral sobre repositorios de la organización FlowiseAI, considerando código fuente, dependencias y configuraciones de CI/CD.

## Motivación

Se selecciona FlowiseAI por su alto impacto en la comunidad de IA:

Plataforma open source para creación de flujos con modelos de lenguaje
Amplia adopción y uso en entornos productivos
Escalabilidad y facilidad de integración

Además, presenta antecedentes relevantes de seguridad, incluyendo vulnerabilidades críticas que permitieron:

Ejecución remota de código en servidores Node.js
Acceso a datos sensibles
Manipulación de lógica de negocio en aplicaciones de IA

Esto lo convierte en un caso representativo para el análisis de seguridad en software moderno.

## Repositorios Analizados

Top 5 repositorios por popularidad:

- Flowise (52.2k ⭐)
- FlowiseChatEmbed (436 ⭐)
- FlowiseDocs (256 ⭐)
- FlowiseEmbedReact (86 ⭐)
- FlowisePy (51 ⭐)
 

## Metodología

El análisis se divide en tres dimensiones:

1. *Código fuente (SAST)*
Herramienta: CodeQL
Objetivo: detectar vulnerabilidades y malas prácticas
2. *Dependencias (SBOM + vulnerabilidades)*
Herramientas: Syft + Grype
Objetivo: identificar librerías vulnerables o desactualizadas
3. *CI/CD (Workflows)*
Herramienta: Checkov
Objetivo: detectar configuraciones inseguras en GitHub Actions

Integrantes: 
* Fabiola Cheuquelaf
* Francisco Cárdenas
* Yasmin Hernández

Ciberseguridad 2026
