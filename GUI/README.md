# Requisitos
+ Descargar el fichero .py y el directorio IMG
+ Instalar las dependencias del fichero dependencias.sh mediante el comando ./dependencias.sh (si no puedes revisa los permisos del fichero).
+ Tener instalada una versión de QEMU compatible con QTEST
+ Para probar la aplicación sin tu propia imagen o kernel incluimos un ELF
+ La aplicación ha sido desarrollada y probada en ubuntu 22

# Uso
+ Para ejecutar el programa es necesario que se encuentre en el mismo directorio que la carpeta IMG y escribir en el terminal: python3 prueba.py

+ Una vez ejecutado debería aparecer una ventana nueva con la interfaz de usuario, el terminal donde se ha ejecutado el comando anterior servirá de debug para ver potenciales errores y mensajes del sistema en caso de error en la aplicación.

+ Si abres la aplicación por primera vez deberás introducir una ruta a QEMU, seleccionando la opción "cargar path a QEMU" donde se abre una ventana para selecciones la ruta a QEMU, es importante asegurarse de que el directorio introducido es el interior de QEMU, donde se encuentra el directorio BUILD. (p.e: /ruta/qemu-master - dentro de esta carpeta se encuentra /build).
+ Una vez introducido correctamente, se creará el fichero path.cof, donde se guardará tu ruta, no tendrás que ponerla más si no mueves el directorio o pruebas otra instalación.

+ Una vez hecho esto verás múltiples botones en la parte superior y una imagen de la Raspberry Pi 3b en el lado izquierdo, veamos las distintas funcionalidades una a una (al pasar el puntero por encima de cada botón aparece su nombre).

	- Cargar kernel / imagen, sus iconos son un chip y (OS) respectivamente, el boton kernel permite cargar un archivo ELF a modo de kernel. Por otro lado el botón imagen permite cargar una imagen de SO .img, junto con su kernel.img y su fichero .dtb. Si hay algún problema cargándo el fichero aparecerá un error,
  	- Play, una vez con el archivo cargado se puede seleccionar Play para comenzar la simulación, se abre un terminal por el que veremos la salida del sistema emulado, ejecutado a partir de los ficheros cargados. En cualquier momento se puede cargar otro fichero bare-metal y reiniciar la simulación con el boto "Reiniciar"
  	- Stop, para la simulación y cierra los terminales de GDB asociados.
	
	- Botones y leds, su icono es el de un botón y un led respectivamente. Al hacer clic aparecerá un botón/led al lado izquierdo de la ventana. Al hacer clic derecho sobre ellos los podremos conectar a un GPIO por medio de un pop up, los GPIO están numerados de 0 al 27. Una vez conectado un led o un botón verás una linea roja que lo une con su respectivo pin en la Raspberry (si te molesta no te preocupes, más adelante lo ocultamos). Los leds comenzarán a recibir el valor del GPIO indicado, realizando consultas periódicas mediante QTEST a QEMU, en caso de recibir un 1 se encienden (color rojo). Al hacer clic sobre un botón se realiza una pulsación, se pone el GPIO correspondiente a 1 y cuando se suelta regresará a 0. Tanto los leds como los botones se pueden tanto desplazar, manteniendo el click derecho del ratón, y eliminar con click central (rueda del ratón). Para usar los leds y los botones es necesario haber introducido un path a QEMU y estar emulando un sistema
	
	- Guardar: Al hacer click se guarda la disposición de items en la pantalla y sus conexiones, no se guarda el estado de QEMU, solo los items gráficos. El guardado actualmente se hace en el directorio donde esta el fichero.py, en un fichero .json.
	
	- Cargar(icono con flecha): Carga los datos guardados con el botón de guardar, limpia toda la pantalla antes de hacerlo, pero no afecta a la ejecución de QEMU.
	
	- Limpiar(escoba): Despeja la pantalla de items eliminándolos todos y sus conexiones.
	
	- Recargar(doble flecha): Reinicia QEMU, si has cargado un path nuevo para QEMU cargará este último.
	
	- Velocidad de consultas(cronómetro): Muestra un pop up donde se puede agregar cierto retraso a las consultas, el valor introducido en segundos se esperará antes de cada consulta a QEMU, sin contar aquellas realizadas manualmente como presionar un botón.
	
	- Ocultar cables (ojo): Oculta/muestra los cables a los pines desde cada item, es útil si hay demasiados en pantalla.
	
	- Click derecho sobre Raspberry Pi 3b: Abre un PopUp que muestra para cada pin de la Raspberry Pi 3 (1-40) su estado actual, si es de tierra o corriente se indica con Ground o Power, para los GPIO se indica el número y si esta configurado como entrada, salida o como modo alternativo (0-5) (esta configuracón se hace de forma interna, no mediante esta herramienta). Debajo hay un link a una página con información más detallada sobre cada pin. Para esta opción es necesario tener una imagen o kernel cargado, de lo contrario no reaccionará.
	
	
