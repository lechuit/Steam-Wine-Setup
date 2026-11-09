# Código incluido y licencias

Steam-Wine-Setup conserva las dependencias de código en carpetas separadas. El ZIP no necesita clonar estos dos repositorios para preparar la base.

| Carpeta | Origen y revisión | Avisos |
| --- | --- | --- |
| [vendor/mac-windows-gaming](vendor/mac-windows-gaming) | [Xipzer/mac-windows-gaming, cf0dbd8](https://github.com/Xipzer/mac-windows-gaming/tree/cf0dbd830d7f91e33b44d14d66e58cee48dc828e) | [MIT y aviso de Xipzer](vendor/mac-windows-gaming/LICENSE) |
| [vendor/notproton](vendor/notproton) | [NotProtonNot/NotProton, 5b8d186](https://github.com/NotProtonNot/NotProton/tree/5b8d18683b619b66390be8cbcffc1fbf47e45971) | [GPLv3](vendor/notproton/LICENSE), [lsteamclient](vendor/notproton/LICENSE.lsteamclient) y [Steam shim](vendor/notproton/LICENSE.steam-shim) |

La copia de NotProton conserva el árbol del commit indicado, incluidos los recursos de detour del propio proyecto y [su código y scripts de compilación](vendor/notproton/ntdll-patch). El instalador de mac-windows-gaming cambia el paso de obtención del código de NotProton: prepara una copia local de la incluida en el ZIP, verifica su árbol Git y conserva la caché anterior si debe reemplazarla. El parche y las versiones de descarga siguen fijados.

Los repos independientes [mac-windows-gaming-base](https://github.com/lechuit/mac-windows-gaming-base) y [NotProton-Wine11](https://github.com/lechuit/NotProton-Wine11), así como los forks anteriores, permanecen como respaldo. No se necesitan para instalar desde este ZIP.

El ZIP no incluye Steam, Wine, los juegos, DLL de Valve o Microsoft ni binarios de Apple. Dobby, el motor y la plantilla de Wine, los componentes del puente y las firmas de Steam siguen siendo dependencias externas. Conserva los avisos de cada componente y revisa los términos de sus descargas antes de redistribuirlos.
