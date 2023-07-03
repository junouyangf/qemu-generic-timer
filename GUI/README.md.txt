--Guía básica simulador qemu--

---REQUISITOS---
Instalar QEMU, debes tener una versión local de QEMU que soporte QTEST.
Instalar las dependencias del fichero dependencias.sh mediante el comando ./Dependencias.sh (si no puedes revisa los permisos del fichero)
Para probar la aplicación sin tu propia imagen o kernel incluimos un .elf
---USO---

+para ejecutar el programa es necesario escribir en el terminal: python3 prueba.py

+Una vez ejecutado debería aparecer una ventana nueva con la interfaz de usuario, el
terminal donde se ha ejecutado el comando anterior servirá de debug para ver potenciales
errores y mensajes del sistema, asi como otros indicadores útiles para saber si esta funcionando
correctamente. Por ejemplo: al introducir valores no válido en elgun campo de texto o rutas a archivos
inexistentes

+Si abres la aplicación por primera vez aparecerá un explorador de archivos para que selecciones el path a QEMU,
es importante asegurarse de que el directorio introducido es el interior de QEMU, donde se encuentra el directorio BUILD.
Una vez introducido correctamente, se creará el fichero path.cof, donde se guardará tu ruta, no tendrás que ponerla más si no
mueves el directorio o pruebas otra instalación.

+Una vez hecho esto verás múltiples botones al lado derecho de la ventana y una raspberry pi 3 en el lado izquierdo, veamos las 
distintas funcionalidades una a una (al pasar el putnero por encima de cada botó aparece su nombre).

	-Cargar kernel / imagen, sus iconos son un chip y (OS) respectivamente,el boton kernel permite cargar un archivo .elf a modo de kernel. 
	Por otro lado el botón imagen permite cargar una imagen de SO .img, junto con su kernel.img y sufichero .dtb .
	Si se cargan los ficheros correctamente se abrirá un nuevo terminal de QEMU, por el que veremos la salida del sistema emulado.
	En cualquier momento se puede repetir este proceso y pasar de un sistema baremetal a otro con SO.
	
	-Botones y leds, su icono es el de un bóoton y un led respectivamente. Al hacer clic aparecerá un botón/led al lado izquierdo
	de la ventana. Al hacer clic sobre ellos los podremos conectar a un GPIO (no a un pin) por medio de un pop up, los GPIO están
	numerados de 0 al 27. Una vez conectado un led o un botón verás una linea roja que lo une con su respectivo pin en la raspberry
	(si te molesta no te preocupes, más adelante lo ocultamos). Los leds comenzarán a recibir el valor del GPIO indicado, realizando 
	consultas periódicas mediante QTEST a QEMU, en caso de recibir un 1 se encienden en color rojo. Al hacer clic sobre un botón
	se realiza una pulsación, se pone el GPIO correspondiente a 1, cuando se suelta regresará a 0. Tanto los leds como los botones
	se pueden desplazar manteniendo clic y eliminar con clic central (rueda del ratón)
	
	-Guardar: Al hacer clic se guarda la disposición de items en la pantalla y sus conexiones, no se guarda el estado de QEMU,
	solo los items gráficos. El guardado actualmente se hace en el directorio donde esta el fichero.py, en un fichero .json.
	
	-Cargar (icono con flecha): carga los datos guardados con el botón de guardar, limpia toda la pantalla antes de hacerlo, pero no afecta a la ejecución
	de QEMU
	
	-Limpiar (escoba): despeja la pantalla de items eliminándolos todos y sus conexiones.
	
	-Recargar(doble flecha): reinicia QEMU, si has cargado un path nuevo para QEMU cargará este último.
	
	-Velocidad de consultas(cronómetro): muestra un pop up donde se puede agregar cierto retraso a las consultas, el valor introducido en segundos
	se esperará antes de cada consulta a QEMU, sin contar aquellas realizadas manualmente como presionar un botón.
	
	-Ocultar cables (ojo): oculta/muestra los cables a los pines desde cada item, es útil si hay demasiados en pantalla
	
	-Clic derecho sobre raspberry PI 3: abre un PopUp que muestra para cada pin de la raspberry pi 3 (1-40) su estado actual, si es de tierra
	o corriente se indica con Ground o Power, para los GPIO se indica el número y si esta configurado como entrada o salida o como modo alternativo (0-5)
	(esta configuracón se hace de forma interna, no mediante esta herramienta) Debajo hay un link a una página con información más detallada sobre cada pin. Para
	Esta opción es necesario tener una imagen o kernel cargado, de lo contrario no reaccionará.
	
	
---KERNEL INCLUIDO---
El .elf que incluimos consiste en un contador creciente, cuyo valor se envía por los GPIO del 1 al 7  ,de forma que si conectamos unos leds a estos GPIO formarán un display
de siete segmentos. El gpio 19 se puede usar como entrada para un botón y alternar de esta forma la velocidad del contador entre lenta y rápida. Para hacer uso del botón es necesario
tener la versión de QEMU parcheada por berdav para permitir interrupciones por GPIO
	
	
	