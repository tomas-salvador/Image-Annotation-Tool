# translations.py
STRINGS = {
    "en": {
        "accept": "Accept",
        "cancel": "Cancel",
        "window_title": "Image Annotation Tool",
        "open_images": "Dataset",
        "open_model": "Model",
        "use_model_button": "Use model",
        "open_folder": "Select image folder",
        "delete_image":"Delete Imagen",
        "confirm_delete_title": "Confirm deletion",
        "confirm_delete_msg": "Are you sure you want to delete this image and its annotations?",
        "assign_label": "Assign Label to Selected",
        "delete_annotation": "Delete Annotation",
        "delete_all_annotations": "Delete All Annotations",
        "confirm_delete_all_title": "Confirm Deletion",
        "confirm_delete_all_msg": "Are you sure you want to delete all annotations for this image?",
        "rect_no_label": "No Label",
        "dialog_edit_label": "Edit Label",
        "edit_classes": "Edit Classes",
        "dialog_new_label": "Enter new label:",
        "nav_title": "Image {current} of {total} - {filename}",
        "copy_prev_labels": "Copy labels from previous image", # Copiar anotaciones anteriores
        # Editar clases:
        "edit_classes": "Edit Classes",
        "new_class": "New Class",
        "delete_class": "Delete",
        "class_type": "Type",
        "class_name": "Name",
        "remap_success_title": "Success",
        "remap_success_msg": "Classes were successfully saved.",
        "confirm_changes_title": "Confirm changes",
        "confirm_changes_text": "Are you sure you want to apply the following changes?",
        "class_editor_title": "Class Editor",
        "default_class_name": "New Class",
        "change_deleted": "Deleted class",
        "change_reordered": "Reordered class",
        "change_name": "Renamed class",
        "change_color": "Color changed",

        # Menu Archivo
        "menu_file": "&File",

        # Editar vista
        "menu_view": "&View",
        "menu_edit_view": "Edit View",
        "edit_view_placeholder": "This feature is not yet implemented.",  # puedes conservarla por si la reutilizas
        "view_editor_title": "Edit View",
        "view_editor_boxes": "Boxes",
        "view_editor_lines": "Lines",
        "view_editor_polylines": "Polylines",
        "view_editor_show_names": "Show label names",
        "view_editor_visible_classes": "Visible classes",
        "view_editor_show_names_block": "Show label names:",

        # Panel de navegacion:
        "invalid_number_title": "Error",
        "invalid_number_msg": "Invalid image number",
        "invalid_input_title": "Error", 
        "invalid_input_msg": "Please enter a valid number",
        "no_images": "No images",
        # Barra de menu
        "menu_help": "&Help",
        "menu_user_manual": "&User Manual",
        "menu_about": "&About...",
        "about_title": "About",
        "manual_title": "User Manual",
        "menu_languages": "Languages",
        "menu_edit": "&Edit",
        "menu_undo": "&Undo",
        "menu_redo": "&Redo",
        "menu_view": "&View",
        "menu_edit_view": "Edit View",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "edit_view_placeholder": "This feature is not yet implemented.",

        # Filtro
        "filter_button": "Filters",
        "filter_title": "Filter by classes",
        "filter_all": "All",
        "filter_warning_no_selection": "You must select at least one class.",
        "filter_warning_no_results": "No images found with the selected classes.",
        "filter_warning_no_images": "No images found.",
        "show_histogram": "Show label histogram",
        # Visibilidad
        "toggle_class_visibility": "Toggle class visibility",
        "open_class_visibility_title": "Filter class visibility",   # en inglés
        # Histograma
        "histogram_title": "Label distribution by class",
        "histogram_no_data": "No annotations found to generate the histogram.",
        "no_labels_dir": "Labels directory not found.",
        "classes": "Classes",
        "annotation_count": "Number of labels",
        "please_wait": "Please wait...",
        "procesing_data": "Processing data...",
        "manual_content": """
<h2>User Manual</h2>

<p><b>Basic Usage:</b></p>
<ul>
    <li><b>Open images:</b> File > Open or click the "Open" button</li>
    <li><b>Delete image:</b> Ctrl + Shift + P</li>
    <li><b>Create annotation:</b> Left click + drag over the image</li>
    <li><b>Edit classes:</b> Click the "Edit" button below the class list</li>
    <li><b>Select annotation:</b> Right click on the box</li>
    <li><b>Edit annotation label:</b> Double right click on a box</li>
    <li><b>Quick relabel:</b> Ctrl + Right click to apply current class without prompt</li>
    <li><b>Resize annotation:</b> Drag a handle (appears when selected)</li>
    <li><b>Move annotation:</b> Drag the box (when selected)</li>
    <li><b>Pan image:</b> Ctrl + Left click + drag</li>
    <li><b>Zoom:</b> Ctrl + mouse wheel</li>
    <li><b>Undo:</b> Ctrl + Z</li>
    <li><b>Redo:</b> Ctrl + Shift + Z</li>
    <li><b>Delete annotation:</b> Select it and press Delete</li>
    <li><b>Delete all annotations:</b> Shift + Delete or Shift + Backspace (no confirmation)</li>
    <li><b>Copy labels from previous image:</b> Shift + -</li>
    <li><b>Copy annotation:</b> Ctrl + C</li>
    <li><b>Paste annotation:</b> Ctrl + V</li>
    <li><b>Assign label:</b> Select annotation(s) and click "Assign Label"</li>
    <li><b>Select class by number:</b> Press 0-9 to select the corresponding class</li>
</ul>

<p><b>Navigation:</b></p>
<ul>
    <li><b>Next image:</b> Right arrow or Space</li>
    <li><b>Previous image:</b> Left arrow</li>
    <li><b>Jump to image:</b> Type number and press Enter</li>
</ul>

<p><b>Annotation Types:</b></p>
<ul>
    <li><b>Box:</b> This is the default type. To create a box, select the corresponding class in the left panel and left-click + drag on the image.</li>
    <li><b>Line:</b> Used to mark straight segments. To use this type, edit the classes (click the "Edit Classes" button) and set the type to "line". Then, select that class in the list and draw with left-click + drag.</li>
    <li><b>Polyline:</b> Used for shapes with multiple points. To activate this type, edit the classes and set the type to "polyline". Then:
        <ul>
            <li>First left click: sets the starting point.</li>
            <li>Subsequent left clicks: add points to the polyline.</li>
            <li>When a polyline is selected, Ctrl + click on one of its points to delete only that point. If deleting it leaves fewer than 2 points, the full polyline is removed.</li>
            <li>Final click (right click): ends the polyline.</li>
        </ul>
    </li>
</ul>

<p><b>Switching between types:</b></p>
<ul>
    <li>The annotation type is defined when editing the classes in the "Class Editor".</li>
    <li>Each class can be set to <i>box</i>, <i>line</i>, or <i>polyline</i>. When you select a class in the left panel, the program will automatically use the configured type.</li>
</ul>

<p><b>Filter images by class:</b></p>
<ul>
    <li><b>Open filters:</b> Click the "Filters" button in the left panel</li>
    <li><b>View all images:</b> Check the "All" option</li>
    <li><b>Filter by specific classes:</b> Uncheck "All" and select one or more classes</li>
    <li><b>Apply filter:</b> Click "Accept" to show only the images containing at least one of the selected classes</li>
    <li><b>No matches:</b> If no images match the selection, the previous filter remains active</li>
</ul>

<p><b>Using YOLO model:</b></p>
<ul>
    <li><b>Load model:</b> Click "Open Model"</li>
    <li><b>Run detection:</b> Ctrl + M</li>
</ul>
"""
    },
    "es": {
        "accept": "Aceptar",
        "cancel": "Cancelar",
        "window_title": "Herramienta de Anotación de Imágenes",
        "open_images": "Conjunto de Datos",
        "open_model": "Modelo",
        "use_model_button": "Usar modelo",
        "open_folder": "Seleccionar carpeta de imágenes",
        "delete_image":"Borrar Imagen",
        "confirm_delete_title": "Confirmar eliminación",
        "confirm_delete_msg": "¿Estás seguro de que quieres eliminar esta imagen y sus anotaciones?",
        "assign_label": "Asignar etiqueta a seleccionados",
        "delete_annotation": "Eliminar anotación",
        "delete_all_annotations": "Eliminar todas las anotaciones",
        "confirm_delete_all_title": "Confirmar eliminación",
        "confirm_delete_all_msg": "¿Estás seguro de que deseas eliminar todas las anotaciones de esta imagen?",
        "rect_no_label": "Sin nombre",
        "edit_classes": "Editar Clases",
        "dialog_edit_label": "Editar Etiqueta",
        "dialog_new_label": "Ingrese nueva etiqueta:",
        "nav_title": "Imagen {current} de {total} - {filename}",
        "copy_prev_labels": "Copiar etiquetas de la imagen anterior",   # Copiar anotaciones anteriores

        # Menu Archivo
        "menu_file": "&Archivo",

        # Editar clases:
        "remap_success_title": "Éxito",
        "edit_classes": "Editar Clases",
        "delete_class": "Eliminar",
        "new_class": "Nueva Clase",
        "delete_class": "Eliminar",
        "class_type": "Tipo",
        "class_name": "Nombre",
        "remap_success_msg": "Las clases fueron guardadas correctamente.",
        "confirm_changes_title": "Confirmar cambios",
        "confirm_changes_text": "¿Seguro que desea aplicar los siguientes cambios?",
        "class_editor_title": "Editor de clases",
        "default_class_name": "Nueva clase",
        "change_deleted": "Clase eliminada",
        "change_reordered": "Clase reordenada",
        "change_name": "Nombre cambiado",
        "change_color": "Color cambiado",

        # Editar vista
        "menu_view": "&Vista",
        "menu_edit_view": "Editar Vista",
        "edit_view_placeholder": "Esta función aún no está implementada.",
        "view_editor_title": "Editar Vista",
        "view_editor_boxes": "Boxes",
        "view_editor_lines": "Lines",
        "view_editor_polylines": "Polylines",
        "view_editor_show_names": "Ver nombres de etiquetas",
        "view_editor_visible_classes": "Clases visibles",
        "view_editor_show_names_block": "Mostrar nombres:",

        #Copiar y pegar:
        "copy_success": "Anotación copiada",
        "paste_success": "Anotación pegada",
        "nothing_to_copy": "No hay anotación seleccionada para copiar",
        "nothing_to_paste": "No hay anotación copiada para pegar",
        # Panel de navegacion:
        "invalid_number_title": "Error",
        "invalid_number_msg": "Número de imagen inválido",
        "invalid_input_title": "Error",
        "invalid_input_msg": "Ingrese un número válido",
        "no_images": "No hay imágenes",
        # Barra de menu
        "menu_help": "&Ayuda",
        "menu_user_manual": "&Manual del usuario",
        "menu_about": "&Acerca de...",
        "about_title": "Acerca del programa",
        "manual_title": "Manual del usuario",
        "menu_languages": "Idioma",
        "menu_edit": "&Editar",
        "menu_undo": "&Deshacer",
        "menu_redo": "&Rehacer",
        "menu_view": "&Vista",
        "menu_edit_view": "Editar Vista",
        "dark_mode": "Modo Oscuro",
        "light_mode": "Modo Claro",
        "edit_view_placeholder": "Esta función aún no está implementada.",

        # Filtro
        "filter_button": "Filtros",
        "filter_title": "Filtrar por clases",
        "filter_all": "Todas",
        "filter_warning_no_selection": "Debes seleccionar al menos una clase.",
        "filter_warning_no_results": "No se encontraron imágenes con las clases seleccionadas.",
        "filter_warning_no_images": "No se encontraron imágenes.",
        # Visibilidad
        "toggle_class_visibility": "Filtrar visibilidad de clases",
        "open_class_visibility_title": "Filtrar visibilidad por clase",
        # Histograma
        "show_histogram": "Histograma de etiquetas",
        "histogram_title": "Distribución de etiquetas por clase",
        "histogram_no_data": "No se encontraron anotaciones para generar el histograma.",
        "no_labels_dir": "No se encontró el directorio de etiquetas.",
        "classes": "Clases",
        "annotation_count": "Cantidad de etiquetas",
        "please_wait": "Espere...",
        "procesing_data": "Processing data...",
        "manual_content": """
<h2>Manual del Usuario</h2>

<p><b>Uso Básico:</b></p>
<ul>
    <li><b>Abrir imágenes:</b> Archivo > Abrir o clic en el botón "Conjunto de Datos"</li>
    <li><b>Eliminar imagen:</b> Ctrl + Shift + P</li>
    <li><b>Crear anotación:</b> Clic izquierdo y arrastrar sobre la imagen</li>
    <li><b>Editar clases:</b> Clic en el botón "Editar Clases" debajo de la lista de clases</li>
    <li><b>Seleccionar anotación:</b> Clic derecho sobre la caja</li>
    <li><b>Editar etiqueta:</b> Doble clic derecho sobre la anotación</li>
    <li><b>Re-etiquetar rápido:</b> Ctrl + Clic derecho aplica la clase actual sin confirmar</li>
    <li><b>Redimensionar:</b> Arrastrar un manejador (esquinas) cuando está seleccionada</li>
    <li><b>Mover anotación:</b> Arrastrar la caja cuando está seleccionada</li>
    <li><b>Desplazar imagen:</b> Ctrl + Clic izquierdo y arrastrar</li>
    <li><b>Zoom:</b> Ctrl + rueda del ratón</li>
    <li><b>Deshacer:</b> Ctrl + Z</li>
    <li><b>Rehacer:</b> Ctrl + Shift + Z</li>
    <li><b>Eliminar anotación:</b> Selecciónala y presiona Supr</li>
    <li><b>Eliminar todas las anotaciones:</b> Shift + Supr o Shift + Retroceso (sin confirmación)</li>
    <li><b>Copiar etiquetas de la anterior:</b> Shift + -</li>
    <li><b>Copiar anotación:</b> Ctrl + C</li>
    <li><b>Pegar anotación:</b> Ctrl + V</li>
    <li><b>Asignar etiqueta:</b> Selecciona anotaciones y haz clic en "Asignar etiqueta"</li>
    <li><b>Seleccionar clase por número:</b> Pulsa 0-9 para seleccionar la clase correspondiente</li>
</ul>

<p><b>Navegación:</b></p>
<ul>
    <li><b>Imagen siguiente:</b> Flecha derecha o barra espaciadora</li>
    <li><b>Imagen anterior:</b> Flecha izquierda</li>
    <li><b>Ir a imagen específica:</b> Escribe el número y presiona Enter</li>
</ul>

<p><b>Tipos de anotaciones:</b></p>
<ul>
    <li><b>Box (caja):</b> Es el tipo por defecto. Para crear una caja, selecciona la clase correspondiente en el panel izquierdo y haz clic izquierdo + arrastrar sobre la imagen.</li>
    <li><b>Línea:</b> Se usa para marcar segmentos. Para usar este tipo, edita las clases (botón "Editar Clases") y asigna el tipo "line" a la clase. Después, selecciona esa clase en la lista y dibuja con clic izquierdo y arrastre.</li>
    <li><b>Polilínea:</b> Se utiliza para formas con múltiples puntos. Para activar este tipo, edita las clases y asigna el tipo "polyline" a la clase. Luego:
        <ul>
            <li>Primer clic izquierdo: marca el inicio.</li>
            <li>Clics izquierdos siguientes: añaden puntos a la polilínea.</li>
            <li>Con la polilinea seleccionada, haz Ctrl + clic sobre uno de sus puntos para borrar solo ese punto. Si al borrarlo quedan menos de 2 puntos, se elimina la polilinea completa.</li>
            <li>Último clic (clic derecho): finaliza la polilínea.</li>
        </ul>
    </li>
</ul>

<p><b>Cambiar entre tipos:</b></p>
<ul>
    <li>Los tipos de anotación se definen al editar las clases en el "Editor de clases".</li>
    <li>Cada clase puede ser de tipo <i>box</i>, <i>line</i> o <i>polyline</i>. Al elegir una clase en la lista izquierda, el programa usará automáticamente el tipo configurado.</li>
</ul>

<p><b>Filtrar imágenes por clase:</b></p>
<ul>
    <li><b>Abrir filtros:</b> Clic en el botón "Filtros" en el panel izquierdo</li>
    <li><b>Ver todas las imágenes:</b> Marca la opción "Todas"</li>
    <li><b>Filtrar por clases específicas:</b> Desmarca "Todas" y selecciona una o varias clases</li>
    <li><b>Aplicar filtro:</b> Haz clic en "Aceptar" para mostrar solo las imágenes que contienen al menos una de las clases seleccionadas</li>
    <li><b>Sin coincidencias:</b> Si no se encuentran imágenes con las clases seleccionadas, se mantiene el filtro anterior</li>
</ul>

<p><b>Uso del modelo YOLO (opcional):</b></p>
<ul>
    <li><b>Cargar modelo:</b> Clic en "Modelo"</li>
    <li><b>Ejecutar detección:</b> Ctrl + M</li>
</ul>
"""
    },
    "it": {
        "accept": "Accetta",
        "cancel": "Annulla",
        "window_title": "Strumento di Annotazione Immagini",
        "open_images": "Dataset",
        "open_model": "Modello",
        "use_model_button": "Usa modello",
        "open_folder": "Seleziona cartella immagini",
        "delete_image":"Elimina immagine",
        "confirm_delete_title": "Conferma eliminazione",
        "confirm_delete_msg": "Sei sicuro di voler eliminare questa immagine e le sue annotazioni?",
        "assign_label": "Assegna etichetta ai selezionati",
        "delete_annotation": "Elimina annotazione",
        "delete_all_annotations": "Elimina tutte le annotazioni",
        "confirm_delete_all_title": "Conferma eliminazione",
        "confirm_delete_all_msg": "Sei sicuro di voler eliminare tutte le annotazioni per questa immagine?",
        "rect_no_label": "Senza etichetta",
        "edit_classes": "Modifica classi",
        "dialog_edit_label": "Modifica etichetta",
        "dialog_new_label": "Inserisci nuova etichetta:",
        "nav_title": "Immagine {current} di {total} - {filename}",
        "copy_prev_labels": "Copia etichette dall'immagine precedente",  # Copiar anotaciones anteriores
        
        # Menu Archivo
        "menu_file": "&File",

        # Editare classi
        "remap_success_title": "Successo",
        "delete_class": "Elimina",
        "remap_success_msg": "Le classi sono state salvate correttamente.",
        "confirm_changes_title": "Conferma modifiche",
        "confirm_changes_text": "Sei sicuro di voler applicare le seguenti modifiche?",
        "class_editor_title": "Editor delle classi",
        "default_class_name": "Nuova classe",
        "change_deleted": "Classe eliminata",
        "change_reordered": "Classe riordinata",
        "change_name": "Nome cambiato",
        "change_color": "Colore cambiato",

        # Editar vista
        "menu_view": "&Vista",
        "menu_edit_view": "Modifica Vista",
        "edit_view_placeholder": "Questa funzione non è ancora implementata.",
        "view_editor_title": "Modifica Vista",
        "view_editor_boxes": "Boxes",
        "view_editor_lines": "Lines",
        "view_editor_polylines": "Polylines",
        "view_editor_show_names": "Mostra i nomi delle etichette",
        "view_editor_visible_classes": "Classi visibili",
        "view_editor_show_names_block": "Mostra i nomi:",

        # Copia/incolla
        "copy_success": "Annotazione copiata",
        "paste_success": "Annotazione incollata",
        "nothing_to_copy": "Nessuna annotazione selezionata da copiare",
        "nothing_to_paste": "Nessuna annotazione copiata da incollare",

        # Navigazione
        "invalid_number_title": "Errore",
        "invalid_number_msg": "Numero immagine non valido",
        "invalid_input_title": "Errore",
        "invalid_input_msg": "Inserisci un numero valido",
        "no_images": "Nessuna immagine",

        # Menu
        "menu_help": "&Aiuto",
        "menu_user_manual": "&Manuale utente",
        "menu_about": "&Informazioni...",
        "about_title": "Informazioni",
        "manual_title": "Manuale utente",
        "menu_languages": "Lingua",
        "menu_edit": "&Modifica",
        "menu_undo": "&Annulla",
        "menu_redo": "&Ripristina",
        "menu_view": "&Vista",
        "menu_edit_view": "Modifica Vista",
        "edit_view_placeholder": "Questa funzione non è ancora implementata.",

        # Filtro
        "filter_button": "Filtri",
        "filter_title": "Filtra per classi",
        "filter_all": "Tutte",
        "filter_warning_no_selection": "Devi selezionare almeno una classe.",
        "filter_warning_no_results": "Nessuna immagine trovata con le classi selezionate.",
        "filter_warning_no_images": "Nessuna immagine trovata.",

        # Visibilidad
        "toggle_class_visibility": "Filtra visibilità classi",
        "open_class_visibility_title": "Filtra visibilità classi",

        # Histogramma
        "show_histogram": "Istogramma etichette",
        "histogram_title": "Distribuzione delle etichette per classe",
        "histogram_no_data": "Nessuna annotazione trovata per generare l'istogramma.",
        "no_labels_dir": "Cartella delle etichette non trovata.",
        "classes": "Classi",
        "annotation_count": "Numero di etichette",
        "please_wait": "Attendere...",
        "procesing_data": "Elaborazione dati...",

        "manual_content": """
    <h2>Manuale Utente</h2>

    <p><b>Uso Base:</b></p>
    <ul>
        <li><b>Apri immagini:</b> File > Apri o clic sul pulsante "Dataset"</li>
        <li><b>Elimina immagine:</b> Ctrl + Shift + P</li>
        <li><b>Crea annotazione:</b> Clic sinistro e trascina sull'immagine</li>
        <li><b>Modifica classi:</b> Clic su "Modifica classi" sotto la lista delle classi</li>
        <li><b>Seleziona annotazione:</b> Clic destro sulla casella</li>
        <li><b>Modifica etichetta:</b> Doppio clic destro sull'annotazione</li>
        <li><b>Rietichettatura rapida:</b> Ctrl + clic destro applica la classe corrente senza conferma</li>
        <li><b>Ridimensiona:</b> Trascina un angolo quando selezionata</li>
        <li><b>Sposta annotazione:</b> Trascina la casella quando selezionata</li>
        <li><b>Sposta immagine:</b> Ctrl + clic sinistro e trascina</li>
        <li><b>Zoom:</b> Ctrl + rotellina del mouse</li>
        <li><b>Annulla:</b> Ctrl + Z</li>
        <li><b>Ripristina:</b> Ctrl + Shift + Z</li>
        <li><b>Elimina annotazione:</b> Selezionala e premi Canc</li>
        <li><b>Elimina tutte le annotazioni:</b> Shift + Canc o Shift + Backspace (senza conferma)</li>
        <li><b>Copia etichette dall'immagine precedente:</b> Shift + -</li>
        <li><b>Copia annotazione:</b> Ctrl + C</li>
        <li><b>Incolla annotazione:</b> Ctrl + V</li>
        <li><b>Assegna etichetta:</b> Seleziona annotazioni e clicca "Assegna etichetta"</li>
        <li><b>Seleziona classe per numero:</b> Premi 0-9 per selezionare la classe corrispondente</li>
    </ul>

    <p><b>Navigazione:</b></p>
    <ul>
        <li><b>Immagine successiva:</b> Freccia destra o barra spaziatrice</li>
        <li><b>Immagine precedente:</b> Freccia sinistra</li>
        <li><b>Vai a immagine:</b> Digita il numero e premi Invio</li>
    </ul>

    <p><b>Filtrare immagini per classe:</b></p>
    <ul>
        <li><b>Apri filtri:</b> Clic su "Filtri" nel pannello sinistro</li>
        <li><b>Mostra tutte le immagini:</b> Seleziona "Tutte"</li>
        <li><b>Filtra per classi specifiche:</b> Deseleziona "Tutte" e scegli una o più classi</li>
        <li><b>Applica filtro:</b> Clicca "Accetta" per mostrare solo le immagini con almeno una delle classi selezionate</li>
        <li><b>Nessuna corrispondenza:</b> Se non ci sono immagini corrispondenti, rimane attivo il filtro precedente</li>
    </ul>

    <p><b>Tipi di annotazioni:</b></p>
    <ul>
        <li><b>Box:</b> Tipo predefinito. Seleziona la classe e clic sinistro + trascina sull'immagine.</li>
        <li><b>Linea:</b> Per segmenti. Imposta la classe come "line" nell'editor delle classi e poi disegna con clic sinistro + trascina.</li>
        <li><b>Polilinea:</b> Per forme con più punti:
            <ul>
                <li>Primo clic sinistro: punto iniziale.</li>
                <li>Clic sinistro successivi: aggiungono punti.</li>
                <li>Con la polilinea selezionata, fai Ctrl + clic su uno dei suoi punti per eliminare solo quel punto. Se dopo l'eliminazione restano meno di 2 punti, viene eliminata l'intera polilinea.</li>
                <li>Clic destro finale: termina la polilinea.</li>
            </ul>
        </li>
    </ul>

    <p><b>Cambio di tipo:</b></p>
    <ul>
        <li>I tipi si definiscono nell'"Editor delle classi".</li>
        <li>Ogni classe può essere <i>box</i>, <i>line</i> o <i>polyline</i>. Selezionando la classe, il programma userà automaticamente il tipo configurato.</li>
    </ul>

    <p><b>Uso del modello YOLO (opzionale):</b></p>
    <ul>
        <li><b>Carica modello:</b> Clic su "Modello"</li>
        <li><b>Esegui rilevamento:</b> Ctrl + M</li>
    </ul>
    """
    },
    "de": {
        "window_title": "Bild-Anmerkungswerkzeug",
        "open_images": "Bild(er) öffnen",
        "open_folder": "Bildordner auswählen",
        "assign_label": "Beschriftung zuweisen",
        "delete_annotation": "Anmerkung löschen",
        "rect_no_label": "Kein Label",
        "dialog_edit_label": "Label bearbeiten",
        "dialog_new_label": "Neues Label eingeben:",
        "nav_title": "Bild {current} von {total} - {filename}",
        "edit_classes": "Klassen bearbeiten",
        "new_class": "Neue Klasse",
        "delete_class": "Löschen",
        "change_color": "Farbe",
        "class_type": "Typ",
        "class_name": "Name",
        # Menu bar
        "menu_help": "&Hilfe",
        "menu_user_manual": "&Benutzerhandbuch",
        "menu_about": "&Über...",
        "about_title": "Über das Programm",
        "manual_title": "Benutzerhandbuch"
    },
    "fr": {
        "window_title": "Outil d'annotation d'images",
        "open_images": "Ouvrir Image(s)",
        "open_folder": "Sélectionner le dossier d'images",
        "assign_label": "Attribuer une étiquette",
        "delete_annotation": "Supprimer l'annotation",
        "rect_no_label": "Pas d'étiquette",
        "dialog_edit_label": "Modifier l'étiquette",
        "dialog_new_label": "Entrez une nouvelle étiquette:",
        "nav_title": "Image {current} sur {total} - {filename}",
        "edit_classes": "Modifier les classes",
        "new_class": "Nouvelle classe",
        "delete_class": "Supprimer",
        "change_color": "Couleur",
        "class_type": "Type",
        "class_name": "Nom",
        # Menu bar
        "menu_help": "&Aide",
        "menu_user_manual": "&Manuel utilisateur",
        "menu_about": "&À propos...",
        "about_title": "À propos",
        "manual_title": "Manuel utilisateur"
    },
    "pt": {
        "window_title": "Ferramenta de Anotação de Imagens",
        "open_images": "Abrir Imagem(s)",
        "open_folder": "Selecionar pasta de imagens",
        "assign_label": "Atribuir rótulo aos selecionados",
        "delete_annotation": "Excluir anotação",
        "rect_no_label": "Sem rótulo",
        "dialog_edit_label": "Editar Rótulo",
        "dialog_new_label": "Digite um novo rótulo:",
        "nav_title": "Imagem {current} de {total} - {filename}",
        "edit_classes": "Editar Classes",
        "new_class": "Nova Classe",
        "delete_class": "Excluir",
        "change_color": "Cor",
        "class_type": "Tipo",
        "class_name": "Nome",
        # Menu bar
        "menu_help": "&Ajuda",
        "menu_user_manual": "&Manual do usuário",
        "menu_about": "&Sobre...",
        "about_title": "Sobre o programa",
        "manual_title": "Manual do usuário"
    },
    "ru": {
        "window_title": "Инструмент аннотации изображений",
        "open_images": "Открыть изображение(я)",
        "open_folder": "Выбрать папку с изображениями",
        "assign_label": "Назначить метку выделенным",
        "delete_annotation": "Удалить аннотацию",
        "rect_no_label": "Без метки",
        "dialog_edit_label": "Редактировать метку",
        "dialog_new_label": "Введите новую метку:",
        "nav_title": "Изображение {current} из {total} - {filename}",
        "edit_classes": "Редактировать классы",
        "new_class": "Новый класс",
        "delete_class": "Удалить",
        "change_color": "Цвет",
        "class_type": "Тип",
        "class_name": "Имя",
        # Menu bar
        "menu_help": "&Справка",
        "menu_user_manual": "&Руководство пользователя",
        "menu_about": "&О программе...",
        "about_title": "О программе",
        "manual_title": "Руководство пользователя"
    }
}

# Diccionario de idiomas disponibles
LANGUAGES = {
    "en": "English",
    "es": "Español",
    #"de": "Deutsch",
    #"fr": "Français",
    #"pt": "Português",
    #"ru": "Русский",
    "it": "Italiano" 
}
