@ECHO OFF
ECHO Questo file creerà un file obj di livello LOD2 a partire da un file obj di partenza (via Blender che deve essere installato nel sistema)
PAUSE
REM copy NUL %1.blend
"C:\Program Files\Blender Foundation\Blender\blender.exe" %1.blend -P LOD2_standalone.py