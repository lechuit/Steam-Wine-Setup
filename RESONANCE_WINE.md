# FINAL FANTASY RESONANCE con NotProton

Configuración para FINAL FANTASY RESONANCE (Steam App ID `3259780`) en Steam para macOS. Con estos ajustes el juego superó el aviso de Visual C++ y abrió con Retina desactivado el 8 de noviembre de 2026.

## Instalación guiada desde cero

Descarga y descomprime el [ZIP completo de Steam-Wine-Setup](https://github.com/lechuit/Steam-Wine-Setup/archive/refs/heads/main.zip). En un Mac con Apple Silicon y macOS 15 o posterior, abre Terminal en la carpeta descomprimida y ejecuta:

```sh
bash Instalar.command --resonance
```

Si faltan las herramientas de compilación de Apple, el script abre su instalador. Cuando termine, vuelve a ejecutar el comando. Si faltan Steam o el puente libre, el script pide permiso y usa el código de instalación y de NotProton incluidos en el ZIP. NotProton guarda una copia de Steam, modifica y vuelve a firmar la app, y queda como herramienta predeterminada de compatibilidad para juegos de Windows. Si ya está instalado con el motor Wine 11 esperado, se reutiliza.

Inicia sesión, confirma la instalación del juego en la biblioteca predeterminada y cierra Steam cuando el instalador lo solicite. Si el juego no se abre automáticamente, pulsa **Jugar** en Steam. El primer inicio crea el entorno de Wine y puede tardar más que los siguientes. Cierra el aviso de Visual C++ si aparece, sal de Steam y continúa en Terminal. El instalador espera a que Wine guarde el registro antes de verificar las bibliotecas. Este comando aplica solo el perfil de RESONANCE. Steam y NotProton se comparten entre juegos; para el otro perfil, consulta la [guía de AION 2](AION2_WINE_GPTK.md).

Consulta [las revisiones, los créditos y las licencias](VENDORED_SOURCES.md) de las fuentes incluidas. El instalador usa esas copias locales y aplica el parche de NotProton en el Mac. Se requiere Internet para descargar Steam, los juegos, el motor Wine, Dobby, los componentes del puente y las firmas de Steam según corresponda.

Para consultar el estado sin aplicar cambios:

```sh
bash Instalar.command --status
```

### Reparación después de una actualización de Steam

Si el puente dejó de funcionar tras actualizar Steam y la compilación de NotProton sigue en caché, sal de Steam con **⌘Q** y ejecuta desde la raíz del paquete:

```sh
bash vendor/mac-windows-gaming/scripts/setup-notproton.sh --skip-build
```

Si falta la compilación, ese comando no puede reparar el puente. La instalación guiada se detiene si detecta un puente incompleto o diferente, para que puedas elegir cómo repararlo sin reemplazarlo automáticamente.

## Restaurar la configuración

1. Instala el juego y arráncalo una vez con NotProton para que Steam cree su prefijo de Wine. Si aparece el aviso de Visual C++, cierra el juego.
2. Confirma que Steam descargó **Steamworks Common Redistributables**. El instalador usa `steamapps/common/Steamworks Shared/_CommonRedist/vcredist/2022/VC_redist.x64.exe` de la biblioteca de Steam.
3. Cierra Steam completamente y ejecuta desde la raíz de este repositorio:

   ```sh
   python3 scripts/resonance-wine/install.py status
   python3 scripts/resonance-wine/install.py install
   python3 scripts/resonance-wine/install.py status
   ```

4. Abre Steam y lanza RESONANCE. Si el juego no permite elegir la resolución en el modo actual, prueba el modo **Ventana**.

## Ajustes que se guardan

| Ajuste | Dónde se aplica |
| --- | --- |
| Microsoft Visual C++ Redistributable x64 | Prefijo de RESONANCE: `steamapps/compatdata/3259780/pfx`. |
| Preferencia `native,builtin` para `msvcp140`, `msvcp140_1`, `msvcp140_2`, `vcruntime140` y `vcruntime140_1` | Registro de Wine del mismo prefijo. Wine prueba primero las bibliotecas instaladas por Microsoft. |
| `%command% NOTPROTON_RETINA=0` | Opciones de lanzamiento del juego en Steam. NotProton usa la resolución lógica de la pantalla; el valor depende de la pantalla y de la escala configurada en macOS. |

En un prefijo nuevo, Wine puede registrar Visual C++ como instalado aunque aún use sus bibliotecas internas. El instalador comprueba también que las DLL requeridas sean x64 y que no sean las internas de Wine antes de omitir el paquete de Microsoft.

Para volver al modo Retina, quita `NOTPROTON_RETINA=0` de las opciones de lanzamiento de RESONANCE y conserva las demás. Si reinstalas el juego y se pierde su prefijo, vuelve a ejecutar `install` tras crearlo. El repositorio guarda el procedimiento y sus parámetros; los binarios de Microsoft, partidas, registros y credenciales permanecen fuera de Git.

## Resultado observado

| Sesión | Máxima CPU | Máxima GPU |
| --- | ---: | ---: |
| Antes de desactivar Retina | 86,8 °C | 85,0 °C |
| Después de desactivar Retina | 80,0 °C | 72,8 °C |

Son máximos de las lecturas promedio de los sensores durante cada sesión. Después del cambio, macOS se mantuvo en estado térmico normal. Las sesiones no controlaron la escena ni la carga del juego, así que los valores sirven como referencia y no aíslan el efecto de la resolución.
