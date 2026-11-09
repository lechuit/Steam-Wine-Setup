# Steam-Wine-Setup

Este proyecto reúne en **un solo ZIP** el instalador para probar juegos de Windows de tu biblioteca de Steam en un Mac con Apple Silicon, el código base de instalación, el código fuente de NotProton y los perfiles de RESONANCE y AION 2. Una instalación de Steam y NotProton sirve para varios juegos. Cada juego conserva su propio entorno de Wine y puede necesitar ajustes distintos. Si existe una versión nativa para macOS, empieza por esa versión.

**No hay compatibilidad universal.** Un juego puede no arrancar o fallar en videos, controles, modo en línea o rendimiento. El soporte depende del juego, sus servicios y las versiones de macOS, Steam y Wine. No uses este flujo para eludir DRM, restricciones de acceso o sistemas antitrampas. Los juegos con controladores antitrampas de Windows o lanzadores externos pueden quedar fuera de esta configuración.

## 1. Requisitos

- Mac con **Apple Silicon**, **macOS 15 o posterior** y Terminal en modo nativo. La configuración de los perfiles se comprobó en un Mac; esto no certifica todas las versiones de macOS.
- Conexión a Internet y espacio para Steam, Wine y los juegos que elijas.
- Tu propia cuenta de Steam con acceso al juego. Iniciar sesión, aceptar acuerdos y confirmar descargas son pasos manuales.
- Permiso para instalar herramientas y aplicaciones. El instalador solicita las herramientas de línea de comandos de Apple si faltan. El instalador base puede instalar Rosetta, Homebrew, CMake y Steam si hacen falta.

## 2. Qué descargar

1. Descarga el [ZIP del proyecto](https://github.com/lechuit/Steam-Wine-Setup/archive/refs/heads/main.zip) y descomprímelo. Usa la carpeta completa; el archivo `.command` necesita los scripts que están junto a él. Si usas Git, la alternativa es:

   ```sh
   git clone https://github.com/lechuit/Steam-Wine-Setup.git
   cd Steam-Wine-Setup
   ```

2. Para el ZIP de GitHub guardado en Descargas, abre Terminal y entra en la carpeta extraída:

   ```sh
   cd "$HOME/Downloads/Steam-Wine-Setup-main"
   ```

   Si la guardaste en otro lugar, escribe `cd ` y arrastra la carpeta descomprimida a Terminal.

3. Puedes instalar [Steam para macOS desde Valve](https://store.steampowered.com/about/) antes de continuar. Si lo instalas por tu cuenta, déjalo en `/Applications/Steam.app`, ábrelo una vez, inicia sesión y espera las actualizaciones. Luego sal de Steam con **⌘Q**. Si Steam falta, el instalador guiado ofrece instalarlo.

El instalador toma el código de `vendor/mac-windows-gaming` y `vendor/notproton` directamente de la carpeta descomprimida. [mac-windows-gaming-base](https://github.com/lechuit/mac-windows-gaming-base) y [NotProton-Wine11](https://github.com/lechuit/NotProton-Wine11) quedan como respaldo. Consulta [las revisiones, los créditos y las licencias](VENDORED_SOURCES.md).

La instalación requiere Internet: Steam, los juegos, Sikarugir Wine 11, su plantilla, Dobby, los componentes del puente y las firmas de Steam se obtienen por separado según corresponda. Consulta el [inventario de dependencias](vendor/mac-windows-gaming/docs/SOURCES.md). No necesitas instalar la app Whisky.

## 3. Instalar la base para elegir cualquier juego de tu biblioteca

Desde la carpeta del repositorio, ejecuta:

```sh
bash Instalar.command --base-only
```

`--base-only` prepara solo Steam y NotProton. Es el modo predeterminado. Los perfiles se aplican únicamente al elegir `--resonance` o `--aion2`.

1. Si macOS abre el instalador de las herramientas de línea de comandos, completa la instalación y vuelve a ejecutar el comando.
2. Si el puente no está instalado, lee el aviso y confirma con `s` si deseas continuar. NotProton **modifica y vuelve a firmar tu copia local de Steam.app**, guarda una copia y configura la herramienta predeterminada de compatibilidad para juegos de Windows. El acuerdo de Steam restringe las modificaciones del cliente salvo excepciones; revisa las secciones 2.G y 4 antes de aceptar. Si ya tienes la instalación de Wine 11 esperada, el script la reutiliza.
3. Cuando te lo pida, abre Steam, inicia sesión y deja que termine de actualizarse. Después sal con **⌘Q** y continúa en Terminal. Espera a que indique que la base está lista.
4. Abre Steam y elige un título en **Biblioteca**. Para un juego de Windows, comprueba en **Propiedades → Compatibilidad** que se use **NotProton (free, Wine 11)**. Si necesitas elegirlo manualmente, activa **Forzar el uso de una herramienta de compatibilidad** y selecciónalo.
5. Pulsa **Instalar**. Espera que termine la descarga y pulsa **Jugar**. El primer arranque crea un entorno de Wine para ese título. Si falla, revisa primero los requisitos y el tipo de antitrampas o lanzador que usa; la instalación de la base no soluciona automáticamente los errores de cada juego.

## 4. Aplicar perfiles comprobados

| Juego | Qué hacer |
| --- | --- |
| **FINAL FANTASY RESONANCE** | Ejecuta `bash Instalar.command --resonance`. Confirma la descarga en la biblioteca predeterminada de Steam, deja que el primer inicio cree el entorno de Wine y cierra el aviso de Visual C++ si aparece. Cuando el instalador lo pida, sal de Steam. El perfil instala Visual C++ x64 desde Steamworks, prioriza sus bibliotecas y desactiva Retina para el juego. [Guía completa](RESONANCE_WINE.md). |
| **AION 2** | Ejecuta `bash Instalar.command --aion2` y sigue la [guía de AION 2](AION2_WINE_GPTK.md) para las opciones de Steam; los videos de los tutoriales pueden omitirse para evitar el bloqueo observado. |
| **Otros juegos** | Prueba primero con la base. Si necesitas un ajuste, aplícalo solo al juego afectado en sus propiedades. Por ejemplo, `%command% NOTPROTON_RETINA=0` desactiva Retina para ese título. Guarda las opciones anteriores antes de modificarlas. |

Para consultar el estado de la base y los perfiles sin modificarlos:

```sh
bash Instalar.command --status
```

Si Steam se actualiza y deja de cargar NotProton, consulta la [sección de reparación](RESONANCE_WINE.md#reparación-después-de-una-actualización-de-steam). Conserva una copia externa de partidas y preferencias antes de reinstalar o formatear. Si compartes registros para pedir ayuda, elimina tokens, datos de cuenta y rutas personales.

## Licencias, procedencia y uso

- **Proyecto independiente.** Este proyecto no está afiliado, certificado ni respaldado por Valve, Apple, Microsoft ni los editores de los juegos. Los nombres identifican sus productos; las marcas y los juegos pertenecen a sus titulares.
- **Licencias de código.** Los scripts reutilizados proceden de [lechuit/Whisky](https://github.com/lechuit/Whisky/tree/68b075d2) y este proyecto conserva la [GPLv3](LICENSE) y sus avisos. El módulo de AION 2 conserva su [aviso MIT](scripts/aion2-wine-gptk/LICENSE). Las fuentes incluidas mantienen sus [licencias y avisos originales](VENDORED_SOURCES.md). Conserva esos avisos al redistribuir y cumple las obligaciones de código fuente que correspondan a los binarios que distribuyas.
- **Distribución del paquete.** El ZIP contiene scripts, código fuente, documentación y licencias. No incluye juegos, credenciales, Steam, DLL de Valve o Microsoft ni binarios de Apple. El instalador obtiene las dependencias en cada Mac. No redistribuyas componentes de terceros sin comprobar que tienes permiso para hacerlo.
- **Términos de terceros.** La licencia de este repositorio no concede derechos sobre Steam, los juegos ni los componentes descargados. Usa copias a las que tengas acceso autorizado. Revisa el [Acuerdo de suscriptor de Steam](https://store.steampowered.com/subscriber_agreement/), los términos de cada juego y los que acompañan a los componentes de Apple, incluido [Game Porting Toolkit](https://developer.apple.com/games/game-porting-toolkit/). La descarga y la instalación local no sustituyen esos términos ni garantizan que un proveedor admita esta configuración.
- **Sin garantía de funcionamiento.** La compatibilidad puede cambiar con actualizaciones. Consulta las condiciones de garantía y responsabilidad en las licencias aplicables.
