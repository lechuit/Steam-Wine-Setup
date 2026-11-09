# AION 2 con Steam y Wine 11

Perfil experimental para AION 2 (Steam App ID `3393110`). En la configuración probada, el arranque directo permitió pasar del launcher y omitir GStreamer permitió continuar después de un tutorial que congelaba el juego. Algunos videos pueden no reproducirse. Esto no garantiza el funcionamiento de todas las sesiones ni de versiones futuras.

## Instalación

1. Desde la carpeta de Steam-Wine-Setup, ejecuta `bash Instalar.command --aion2`. Si faltan Steam o NotProton, el instalador guía la preparación de la base. Cierra Steam completamente cuando se te solicite.
2. Abre Steam, instala AION 2 desde tu biblioteca y selecciona **NotProton (free, Wine 11)** en **Propiedades → Compatibilidad**.
3. En **Propiedades → General → Opciones de lanzamiento**, usa esta línea. Guarda las opciones anteriores si ya tenías ajustes. Mantén un solo `%command%`.

   ```text
   %command% WINEDLLOVERRIDES=gameoverlayrenderer64,gameoverlayrenderer=
   ```

4. Deja Metal HUD desactivado y los gráficos de NotProton en **Automatic**. Pulsa **Jugar**. Si la resolución queda fija, prueba modo **Ventana**; en la pantalla usada para las pruebas, el modo sin Retina permitió seleccionar **1512 × 982**. Puedes limitar los FPS desde los gráficos del juego.

El perfil aplica el ajuste de Wine/Rosetta, desactiva Retina, excluye el overlay nativo y usa el arranque directo sin GStreamer solo para AION 2. El ajuste del overlay de Windows, la resolución y los FPS se eligen en Steam o dentro del juego. La prueba de Esync no se activa por defecto.

## Comprobar o retirar

```sh
python3 scripts/aion2-wine-gptk/install.py status
```

Si una actualización reemplaza el puente, repara la base según la [guía de RESONANCE](RESONANCE_WINE.md#reparación-después-de-una-actualización-de-steam) y vuelve a aplicar el perfil. Para retirarlo, sal de Steam y ejecuta:

```sh
python3 scripts/aion2-wine-gptk/install.py uninstall
```

Retira también la opción de lanzamiento que agregaste en Steam si ya no la necesitas. Conserva las partidas y evita publicar registros sin quitar datos de cuenta y parámetros privados.

El módulo Wine/Rosetta procede de [Yuki-fox/aion2-wine-compat](https://github.com/Yuki-fox/aion2-wine-compat) y conserva su [licencia MIT](scripts/aion2-wine-gptk/LICENSE).
