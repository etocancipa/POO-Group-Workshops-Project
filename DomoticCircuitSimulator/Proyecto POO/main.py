import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QMenu,
    QStatusBar,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtMultimedia import QSound


class BackgroundLabel(QLabel):
    def __init__(self, parent=None, mainwindow=None):
        super().__init__(parent)
        self.mainwindow = mainwindow
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if self.mainwindow is not None:
            if event.button() == Qt.RightButton:
                self.mainwindow.mostrar_menu_dispositivo(event)
            else:
                self.mainwindow.iniciar_arrastre_dispositivo(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mainwindow is not None:
            self.mainwindow.actualizar_arrastre_dispositivo(event)
            self.mainwindow.actualizar_cursor(event.pos())
            self.mainwindow.actualizar_cable_temporal(event.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mainwindow is not None:
            self.mainwindow.finalizar_arrastre_dispositivo(event)
            self.mainwindow.actualizar_cursor(event.pos())
        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ---------------- BASIC WINDOW CONFIGURATION ----------------
        self.setWindowTitle("Elechouse")
        self.setGeometry(500, 20, 1200, 800)
        self.setWindowIcon(QIcon("microcontrolador.png"))

        self.window_initialized = False

        # ---------------- BACKGROUND IMAGES (HOUSE / ROOMS) ----------------
        self.background_images = {
            "menu": "House.jpg",
            "Living_room": "Living_room.png",
            "Kitchen": "Kitchen.png",
            "room": "Room.png",
        }
        self.current_image = "menu"

        # ---------------- AVAILABLE COMPONENT TYPES ----------------
        self.component_files = {
            "Lamp": "Desk Lamp OFF.png",
            "Radio": "Radio.png",
            "Bulb": "Bulb OFF.png",
            "Heat Sensor": "Heat Sensor.png",
            "Computer": "PC OFF.png",
            "Voltage Source": "Voltage Source.png",
            "TV": "TV OFF.png",
            "Motion Sensor": "Motion Sensor.png",
            "Living Room Lamp": "Lamp Living Room OFF.png",
        }

        # ---------------- ROOMS AND DEVICE STORAGE ----------------
        self.rooms = ["Living_room", "Kitchen", "room"]
        self.devices_by_room = {room: [] for room in self.rooms}
        self.connections_by_room = {room: [] for room in self.rooms}
        self.next_device_id = 1

        # ---------------- DRAG STATE ----------------
        self.dragging = False
        self.last_drag_pos = None
        self.selected_device = None

        # ---------------- CONNECTION CREATION STATE ----------------
        self.connection_source = None
        self.temp_connection_pos = None

        # ---------------- PERSISTENCE FILE ----------------
        self.positions_file = "posiciones_dispositivos.json"

        # ---------------- SOUNDS ----------------
        self.alarm_sound = QSound("Security Alarm.wav")
        self.tv_sound = QSound("TV sound.wav")
        self.radio_sound = QSound("Radio Static.wav")
        self.pc_sound = QSound("Computer Typing.wav")
        self.heat_alarm_sound = QSound("Fire Alarm.wav")

        # ---------------- MOTION SENSOR TIMERS ----------------
        self.motion_sensor_delay_ms = 3000
        self.motion_sensor_timers = {}

        # ---------------- GLOBAL TEMPERATURE ----------------
        self.current_temperature = 25  # °C

        # ---------------- ANIMATION STATE ----------------
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.paso_animacion)
        self.animation_active = False
        self.animation_steps_left = 0
        self.highlight_mode = False
        self.highlighted_device = None
        self.animation_type = "agregar"

        # ---------------- MAIN WIDGET AND LAYOUT ----------------
        container_widget = QWidget(self)
        self.setCentralWidget(container_widget)
        main_layout = QVBoxLayout(container_widget)

        # ---------------- TITLE LABEL ----------------
        self.title_label = QLabel("ELECHOUSE", self)
        self.title_label.setFont(QFont("Arial", 26, QFont.Bold))
        self.title_label.setStyleSheet(
            """
            color: #3B3B3B;
            background-color: #F0E4D4;
            padding: 10px 0;
            border-bottom: 1px solid #C8B79F;
            letter-spacing: 1px;
            """
        )
        self.title_label.setAlignment(Qt.AlignCenter)

        # ---------------- BACKGROUND LABEL (ROOM IMAGE) ----------------
        self.background = BackgroundLabel(self, mainwindow=self)
        self.background.setAlignment(Qt.AlignCenter)
        self.background.setMinimumHeight(400)

        # ---------------- ROOM SELECTION BUTTONS ----------------
        self.living_room_button = QPushButton("Living Room", self)
        self.kitchen_button = QPushButton("Kitchen", self)
        self.bedroom_button = QPushButton("Bedroom", self)

        for b in (self.living_room_button, self.kitchen_button, self.bedroom_button):
            b.setStyleSheet("font-size: 16px; padding: 6px 14px;")

        room_buttons_layout = QHBoxLayout()
        room_buttons_layout.addWidget(self.living_room_button)
        room_buttons_layout.addWidget(self.kitchen_button)
        room_buttons_layout.addWidget(self.bedroom_button)

        # ---------------- UPPER LAYOUT (COMPONENTS + TEMPERATURE) ----------------
        actions_layout = QHBoxLayout()

        self.components_combo = QComboBox(self)
        self.components_combo.addItems(self.component_files.keys())
        self.components_combo.setEnabled(False)

        self.add_device_button = QPushButton("Add device", self)
        self.add_device_button.setEnabled(False)

        components_label = QLabel("Component:", self)
        components_label.setObjectName("sectionTitleSmall")

        actions_layout.addWidget(components_label)
        actions_layout.addWidget(self.components_combo)
        actions_layout.addWidget(self.add_device_button)

        self.temperature_label = QLabel("Temperature (°C):", self)
        self.temperature_label.setObjectName("sectionTitleSmall")
        self.temperature_spinbox = QSpinBox(self)
        self.temperature_spinbox.setRange(-20, 80)
        self.temperature_spinbox.setValue(self.current_temperature)
        self.temperature_spinbox.setSuffix(" °C")

        actions_layout.addSpacing(20)
        actions_layout.addWidget(self.temperature_label)
        actions_layout.addWidget(self.temperature_spinbox)

        # ---------------- SIDEBAR: DEVICE LIST ----------------
        self.device_list = QListWidget(self)
        self.device_list.setMinimumWidth(250)

        sidebar_layout = QVBoxLayout()
        self.sidebar_label = QLabel("Devices in the room:", self)
        self.sidebar_label.setObjectName("sectionTitle")
        sidebar_layout.addWidget(self.sidebar_label)
        sidebar_layout.addWidget(self.device_list)

        sidebar_widget = QWidget(self)
        sidebar_widget.setLayout(sidebar_layout)

        # ---------------- CENTRAL LAYOUT: BACKGROUND + SIDEBAR ----------------
        central_layout = QHBoxLayout()
        central_layout.addWidget(self.background, stretch=3)
        central_layout.addWidget(sidebar_widget, stretch=1)

        main_layout.addWidget(self.title_label)
        main_layout.addLayout(room_buttons_layout)
        main_layout.addLayout(actions_layout)
        main_layout.addLayout(central_layout, stretch=1)

        # ---------------- STATUS BAR ----------------
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Select a room to get started.", 3000)

        # ---------------- SIGNAL CONNECTIONS ----------------
        self.living_room_button.clicked.connect(lambda: self.alternar_imagen("Living_room"))
        self.kitchen_button.clicked.connect(lambda: self.alternar_imagen("Kitchen"))
        self.bedroom_button.clicked.connect(lambda: self.alternar_imagen("room"))

        self.add_device_button.clicked.connect(self.agregar_dispositivo)
        self.device_list.currentItemChanged.connect(self.on_lista_dispositivos_changed)
        self.temperature_spinbox.valueChanged.connect(self.on_temperatura_cambiada)

        # Load state from disk
        self.cargar_posiciones_dispositivos()
        self.temperature_spinbox.setValue(self.current_temperature)

        QTimer.singleShot(0, self.actualizar_imagen)
        self.actualizar_lista_dispositivos()

        self.aplicar_estilos()

    # -------------------------------------------------------------------------
    # CONSOLE LOGGING (ONLY TERMINAL) - CLEAN OUTPUT
    # -------------------------------------------------------------------------
    def pretty_name(self, tipo: str) -> str:
        mapping = {
            "Living Room Lamp": "Lamp",
            "Lamp": "Lamp",
            "Bulb": "Bulb",
            "TV": "TV",
            "Radio": "Radio",
            "Computer": "Computer",
            "Heat Sensor": "Heat Sensor",
            "Motion Sensor": "Motion Sensor",
            "Voltage Source": "Voltage Source",
        }
        return mapping.get(tipo, tipo)

    def log(self, message: str):
        print(message)

    # -------------------------------------------------------------------------
    # STYLESHEET
    # -------------------------------------------------------------------------
    def aplicar_estilos(self):
        estilo = """
        QWidget {
            background-color: #F4F1EA;
            color: #333333;
            font-family: 'Arial', 'Segoe UI', sans-serif;
            font-size: 12px;
        }

        QMainWindow { background-color: #F4F1EA; }

        QLabel#sectionTitle {
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 4px;
        }

        QLabel#sectionTitleSmall {
            font-size: 13px;
            font-weight: bold;
        }

        QPushButton {
            background-color: #F0A15E;
            color: #FFFFFF;
            border-radius: 6px;
            border: 1px solid #C47A35;
            padding: 6px 12px;
        }
        QPushButton:hover { background-color: #F4B374; }
        QPushButton:pressed { background-color: #D27B37; }
        QPushButton:disabled {
            background-color: #DDCDB7;
            color: #8B7A65;
            border: 1px solid #C1B19C;
        }

        QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #C1B19C;
            border-radius: 4px;
            padding: 2px 6px;
        }
        QComboBox::drop-down { border: 0px; }

        QSpinBox {
            background-color: #FFFFFF;
            border: 1px solid #C1B19C;
            border-radius: 4px;
            padding: 2px 6px;
        }

        QListWidget {
            background-color: #FFFFFF;
            border-radius: 4px;
            border: 1px solid #C1B19C;
            padding: 4px;
        }
        QListWidget::item { padding: 4px; }
        QListWidget::item:selected {
            background-color: #F2D2A6;
            color: #333333;
        }

        QStatusBar {
            background-color: #E6DDCF;
            color: #333333;
            font-size: 11px;
        }
        """
        self.setStyleSheet(estilo)

    # -------------------------------------------------------------------------
    # COORDINATE CONVERSION
    # -------------------------------------------------------------------------
    def label_pos_to_pixmap_pos(self, pos_label):
        pixmap = self.background.pixmap()
        if pixmap is None:
            return pos_label

        w_label = self.background.width()
        h_label = self.background.height()
        w_pix = pixmap.width()
        h_pix = pixmap.height()

        offset_x = (w_label - w_pix) // 2
        offset_y = (h_label - h_pix) // 2

        return QPoint(pos_label.x() - offset_x, pos_label.y() - offset_y)

    # -------------------------------------------------------------------------
    # LOAD DEVICES AND CONNECTIONS FROM JSON
    # -------------------------------------------------------------------------
    def cargar_posiciones_dispositivos(self):
        if not os.path.exists(self.positions_file):
            return

        try:
            with open(self.positions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        self.devices_by_room = {room: [] for room in self.rooms}
        self.connections_by_room = {room: [] for room in self.rooms}
        max_id = 0

        try:
            self.current_temperature = int(data.get("temperatura", self.current_temperature))
        except Exception:
            pass

        if "dispositivos" in data:
            dispositivos_data = data.get("dispositivos", {})
            conexiones_data = data.get("conexiones", {})

            for room in self.rooms:
                device_list_data = dispositivos_data.get(room, [])
                if not isinstance(device_list_data, list):
                    continue

                for dev in device_list_data:
                    if not isinstance(dev, dict):
                        continue

                    device_type = dev.get("tipo", "")
                    image_path = dev.get("imagen", "")
                    try:
                        x = int(dev.get("x", 0))
                        y = int(dev.get("y", 0))
                    except Exception:
                        x, y = 0, 0

                    connected = bool(dev.get("conectado", True))
                    powered_on = bool(dev.get("encendido", False))
                    try:
                        dev_id = int(dev.get("id", 0))
                    except Exception:
                        dev_id = 0

                    if dev_id <= 0:
                        max_id += 1
                        dev_id = max_id

                    max_id = max(max_id, dev_id)

                    dev_dict = {
                        "id": dev_id,
                        "tipo": device_type,
                        "imagen": image_path,
                        "x": x,
                        "y": y,
                        "rect": None,
                        "conectado": connected,
                        "encendido": powered_on,
                    }

                    if device_type == "Motion Sensor":
                        dev_dict["sensor_armado"] = powered_on

                    self.devices_by_room[room].append(dev_dict)

                room_connections = conexiones_data.get(room, [])
                if isinstance(room_connections, list):
                    valid_connections = []
                    for c in room_connections:
                        if not isinstance(c, dict):
                            continue
                        try:
                            o = int(c.get("origen"))
                            d = int(c.get("destino"))
                        except Exception:
                            continue
                        valid_connections.append({"origen": o, "destino": d})
                    self.connections_by_room[room] = valid_connections

            try:
                self.next_device_id = int(data.get("next_id", max_id + 1))
            except Exception:
                self.next_device_id = max_id + 1

        else:
            for room in self.rooms:
                device_list_data = data.get(room, [])
                if not isinstance(device_list_data, list):
                    continue

                for dev in device_list_data:
                    if not isinstance(dev, dict):
                        continue

                    device_type = dev.get("tipo", "")
                    image_path = dev.get("imagen", "")
                    try:
                        x = int(dev.get("x", 0))
                        y = int(dev.get("y", 0))
                    except Exception:
                        x, y = 0, 0

                    connected = bool(dev.get("conectado", True))
                    powered_on = bool(dev.get("encendido", False))

                    max_id += 1
                    dev_id = max_id

                    dev_dict = {
                        "id": dev_id,
                        "tipo": device_type,
                        "imagen": image_path,
                        "x": x,
                        "y": y,
                        "rect": None,
                        "conectado": connected,
                        "encendido": powered_on,
                    }

                    if device_type == "Motion Sensor":
                        dev_dict["sensor_armado"] = powered_on

                    self.devices_by_room[room].append(dev_dict)

            self.next_device_id = max_id + 1

    # -------------------------------------------------------------------------
    # SAVE DEVICES AND CONNECTIONS IN JSON
    # -------------------------------------------------------------------------
    def guardar_posiciones_dispositivos(self):
        data = {
            "dispositivos": {},
            "conexiones": {},
            "next_id": self.next_device_id,
            "temperatura": self.current_temperature,
        }

        for room, device_list in self.devices_by_room.items():
            data["dispositivos"][room] = []
            for dev in device_list:
                data["dispositivos"][room].append(
                    {
                        "id": int(dev.get("id", 0)),
                        "tipo": dev["tipo"],
                        "imagen": dev["imagen"],
                        "x": int(dev["x"]),
                        "y": int(dev["y"]),
                        "conectado": bool(dev.get("conectado", True)),
                        "encendido": bool(dev.get("encendido", False)),
                    }
                )

        for room, room_connections in self.connections_by_room.items():
            data["conexiones"][room] = []
            for c in room_connections:
                data["conexiones"][room].append(
                    {"origen": int(c["origen"]), "destino": int(c["destino"])}
                )

        try:
            with open(self.positions_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # CHANGE IMAGE / ROOM (WITH CONSOLE MESSAGES)
    # -------------------------------------------------------------------------
    def alternar_imagen(self, key):
        if self.current_image == key:
            self.current_image = "menu"
        else:
            self.current_image = key

        # Reset interaction state
        self.background.setCursor(Qt.ArrowCursor)
        self.dragging = False
        self.last_drag_pos = None
        self.selected_device = None
        self.connection_source = None
        self.temp_connection_pos = None

        if self.current_image == "menu":
            self.add_device_button.setEnabled(False)
            self.components_combo.setEnabled(False)
            self.sidebar_label.setText("Devices in the room:")
            self.log("return to main menu")
        else:
            self.components_combo.setEnabled(True)
            self.add_device_button.setEnabled(True)
            self.sidebar_label.setText(f"Devices in: {self.current_image}")
            self.statusBar().showMessage(
                "It is possible to add devices. A 'Voltage Source' is needed to power loads.",
                5000,
            )

            if self.current_image == "Living_room":
                self.log("entered to living room")
            elif self.current_image == "Kitchen":
                self.log("entered to kitchen")
            elif self.current_image == "room":
                self.log("entered to bedroom")
            else:
                self.log("entered to room")

        self.actualizar_imagen()
        self.actualizar_lista_dispositivos()

    def actualizar_imagen(self):
        key = self.current_image
        base_path = self.background_images[key]
        self.cargar_imagen_con_dispositivos(base_path)

    # -------------------------------------------------------------------------
    # CALCULATE FREE POSITION FOR NEW DEVICES
    # -------------------------------------------------------------------------
    def calcular_posicion_libre(self, device_width, device_height, background_width, background_height, existing_rects):
        margin = 20
        step_x = max(device_width // 2, 40)
        step_y = max(device_height // 2, 40)

        for y in range(margin, max(background_height - device_height - margin, margin), step_y):
            for x in range(margin, max(background_width - device_width - margin, margin), step_x):
                new_rect = QRect(x, y, device_width, device_height)
                if all(not new_rect.intersects(r) for r in existing_rects):
                    existing_rects.append(new_rect)
                    return x, y, new_rect

        x = (background_width - device_width) // 2
        y = (background_height - device_height) // 2
        new_rect = QRect(x, y, device_width, device_height)
        existing_rects.append(new_rect)
        return x, y, new_rect

    # -------------------------------------------------------------------------
    # DRAW BACKGROUND, DEVICES, AND CONNECTIONS
    # -------------------------------------------------------------------------
    def cargar_imagen_con_dispositivos(self, background_path):
        if not os.path.exists(background_path):
            self.background.setPixmap(QPixmap())
            self.background.setText(f"File not found:\n{background_path}")
            return

        background_pix = QPixmap(background_path)
        if background_pix.isNull():
            self.background.setPixmap(QPixmap())
            self.background.setText(f"Could not load:\n{background_path}")
            return

        width = self.background.width()
        height = self.background.height()

        scaled_background = background_pix.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        composed = QPixmap(scaled_background)
        painter = QPainter(composed)

        if self.current_image in self.rooms:
            device_list = self.devices_by_room[self.current_image]
            placed_rects = []

            for dev in device_list:
                image_path = dev.get("imagen", "")
                if not image_path or not os.path.exists(image_path):
                    continue

                device_pix = QPixmap(image_path)
                if device_pix.isNull():
                    continue

                device_height = max(80, scaled_background.height() // 4)

                if dev.get("tipo") == "Living Room Lamp":
                    device_height = int(device_height * 1.5)

                if self.highlight_mode and dev is self.highlighted_device:
                    if self.animation_type in ("agregar", "encender"):
                        device_height = int(device_height * 1.2)
                    elif self.animation_type == "apagar":
                        device_height = int(device_height * 0.8)

                scaled_device = device_pix.scaledToHeight(device_height, Qt.SmoothTransformation)

                if dev["x"] == 0 and dev["y"] == 0:
                    x, y, rect = self.calcular_posicion_libre(
                        scaled_device.width(),
                        scaled_device.height(),
                        scaled_background.width(),
                        scaled_background.height(),
                        placed_rects,
                    )
                    dev["x"], dev["y"] = x, y
                else:
                    x, y = dev["x"], dev["y"]
                    rect = QRect(x, y, scaled_device.width(), scaled_device.height())
                    placed_rects.append(rect)

                painter.drawPixmap(x, y, scaled_device)
                dev["rect"] = rect

            # Draw wires
            pen = QPen(QColor(0, 0, 0), 3)
            painter.setPen(pen)

            connections = self.connections_by_room.get(self.current_image, [])
            for c in connections:
                dev1 = self.obtener_dispositivo_por_id(self.current_image, c["origen"])
                dev2 = self.obtener_dispositivo_por_id(self.current_image, c["destino"])
                if not dev1 or not dev2:
                    continue
                r1 = dev1.get("rect")
                r2 = dev2.get("rect")
                if r1 is None or r2 is None:
                    continue
                painter.drawLine(r1.center(), r2.center())

            # Temporary dashed line
            if self.connection_source is not None and self.temp_connection_pos is not None:
                source_rect = self.connection_source.get("rect")
                if source_rect is not None:
                    p_source = source_rect.center()
                    temp_pen = QPen(QColor(0, 0, 255), 2, Qt.DashLine)
                    painter.setPen(temp_pen)
                    painter.drawLine(p_source, self.temp_connection_pos)

        painter.end()
        self.background.setPixmap(composed)
        self.window_initialized = True

    # -------------------------------------------------------------------------
    # SIDEBAR: DEVICE LIST
    # -------------------------------------------------------------------------
    def actualizar_lista_dispositivos(self):
        self.device_list.clear()
        if self.current_image not in self.rooms:
            return

        device_list = self.devices_by_room[self.current_image]
        for dev in device_list:
            name = dev.get("tipo", "Unknown")
            connected = dev.get("conectado", True)
            powered_on = dev.get("encendido", False)

            if not connected:
                state_emoji = "⚫"
                state_text = "Disconnected"
            else:
                if powered_on:
                    state_emoji = "🟢"
                    state_text = "Connected, ON"
                else:
                    state_emoji = "🔴"
                    state_text = "Connected, OFF"

            item = QListWidgetItem(f"{state_emoji} {name}")

            icon_path = dev.get("imagen", "")
            if icon_path and os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))

            item.setData(Qt.UserRole, dev.get("id", 0))
            item.setToolTip(f"Type: {name}\nStatus: {state_text}\nRoom: {self.current_image}")
            self.device_list.addItem(item)

    def on_lista_dispositivos_changed(self, current, previous):
        if current is None or self.current_image not in self.rooms:
            self.highlighted_device = None
            self.highlight_mode = False
            self.actualizar_imagen()
            return

        dev_id = current.data(Qt.UserRole)
        dev = self.obtener_dispositivo_por_id(self.current_image, dev_id)
        if dev is not None:
            self.highlighted_device = dev
            self.highlight_mode = True
            self.actualizar_imagen()
            self.registrar_interaccion_usuario()

    # -------------------------------------------------------------------------
    # TEMPERATURE CHANGE HANDLING
    # -------------------------------------------------------------------------
    def on_temperatura_cambiada(self, value):
        self.current_temperature = value
        self.statusBar().showMessage(f"Temperature set to {value} °C", 3000)
        self.log(f"Temperature set to {value} °C")
        self.actualizar_alarma_calor()

    # -------------------------------------------------------------------------
    # DEVICE DETECTION BY POSITION (CLICK)
    # -------------------------------------------------------------------------
    def obtener_dispositivo_en_pos(self, pos_label):
        if self.current_image not in self.rooms:
            return None

        device_list = self.devices_by_room[self.current_image]
        if not device_list:
            return None

        interaction_margin = 20
        pos_pix = self.label_pos_to_pixmap_pos(pos_label)

        for dev in reversed(device_list):
            rect = dev.get("rect")
            if rect is None:
                continue
            area = rect.adjusted(-interaction_margin, -interaction_margin, interaction_margin, interaction_margin)
            if area.contains(pos_pix):
                return dev
        return None

    def obtener_dispositivo_por_id(self, room, dev_id):
        for dev in self.devices_by_room.get(room, []):
            if dev.get("id") == dev_id:
                return dev
        return None

    # -------------------------------------------------------------------------
    # DEVICE CONTEXT MENU (RIGHT CLICK)
    # -------------------------------------------------------------------------
    def mostrar_menu_dispositivo(self, event):
        dev = self.obtener_dispositivo_en_pos(event.pos())
        if dev is not None:
            self.registrar_interaccion_usuario()

        if dev is None:
            self.connection_source = None
            self.temp_connection_pos = None
            self.actualizar_imagen()
            return

        menu = QMenu(self)

        accion_encender = None
        accion_apagar = None

        accion_iniciar_conexion = None
        accion_conectar_con_origen = None
        accion_cancelar_origen = None

        if self.connection_source is None:
            accion_iniciar_conexion = menu.addAction("Select as connection source")
        else:
            if self.connection_source is dev:
                accion_cancelar_origen = menu.addAction("Cancel connection source selection")
            else:
                accion_conectar_con_origen = menu.addAction(
                    "Connect with selected source "
                    f"({self.connection_source.get('tipo', 'device')})"
                )

        menu.addSeparator()

        if dev.get("conectado", True) and dev.get("tipo") == "Voltage Source":
            if dev.get("encendido", False):
                accion_apagar = menu.addAction("Turn off")
            else:
                accion_encender = menu.addAction("Turn on")

        menu.addSeparator()
        accion_eliminar = menu.addAction("Remove device")

        accion = menu.exec_(self.background.mapToGlobal(event.pos()))

        if accion == accion_iniciar_conexion:
            self.connection_source = dev
            self.temp_connection_pos = self.label_pos_to_pixmap_pos(event.pos())
            self.statusBar().showMessage(
                "Connection source selected. A right click on another device completes the connection.",
                6000,
            )
            self.actualizar_imagen()
            return

        if accion == accion_cancelar_origen:
            self.connection_source = None
            self.temp_connection_pos = None
            self.statusBar().showMessage("Connection source selection canceled.", 4000)
            self.actualizar_imagen()
            return

        if accion == accion_conectar_con_origen:
            if self.connection_source is not None and self.connection_source is not dev:
                self.agregar_conexion(self.connection_source, dev)
                self.connection_source = None
                self.temp_connection_pos = None
            return

        if accion == accion_encender:
            self.encender_dispositivo(dev)
        elif accion == accion_apagar:
            self.apagar_dispositivo(dev)
        elif accion == accion_eliminar:
            self.eliminar_dispositivo(dev)

    # -------------------------------------------------------------------------
    # CONNECTION MANAGEMENT (WIRES)
    # -------------------------------------------------------------------------
    def agregar_conexion(self, dev_origen, dev_destino):
        if self.current_image not in self.rooms:
            return

        room = self.current_image
        id1 = dev_origen.get("id")
        id2 = dev_destino.get("id")
        if id1 is None or id2 is None or id1 == id2:
            return

        for c in self.connections_by_room[room]:
            if (c["origen"] == id1 and c["destino"] == id2) or (c["origen"] == id2 and c["destino"] == id1):
                return

        self.connections_by_room[room].append({"origen": id1, "destino": id2})
        self.statusBar().showMessage(
            f"'{dev_origen.get('tipo', 'device')}' connected to '{dev_destino.get('tipo', 'device')}'.",
            5000,
        )
        self.log(f"Wire connected: {self.pretty_name(dev_origen.get('tipo'))} -> {self.pretty_name(dev_destino.get('tipo'))}")

        self.guardar_posiciones_dispositivos()
        self.actualizar_cargas_por_fuentes(room)
        self.actualizar_imagen()
        self.actualizar_lista_dispositivos()

        if self.hay_circuito_cerrado(room):
            self.statusBar().showMessage("A closed circuit was detected in this room.", 6000)
            self.log("Circuit: closed circuit detected")

        self.registrar_interaccion_usuario()

    def hay_circuito_cerrado(self, room):
        devices = self.devices_by_room.get(room, [])
        connections = self.connections_by_room.get(room, [])

        if len(devices) < 3 or len(connections) < 3:
            return False

        ids = [dev.get("id") for dev in devices if dev.get("id") is not None]
        if not ids:
            return False

        graph = {i: [] for i in ids}
        for c in connections:
            o = c.get("origen")
            d = c.get("destino")
            if o in graph and d in graph and o != d:
                graph[o].append(d)
                graph[d].append(o)

        visited = set()

        def dfs(u, parent):
            visited.add(u)
            for v in graph[u]:
                if v not in visited:
                    if dfs(v, u):
                        return True
                elif v != parent:
                    return True
            return False

        for node in ids:
            if node not in visited:
                if dfs(node, None):
                    return True

        return False

    # -------------------------------------------------------------------------
    # POWER LOGIC
    # -------------------------------------------------------------------------
    def hay_fuente_activa(self, room):
        if room not in self.rooms:
            return False
        for dev in self.devices_by_room[room]:
            if dev.get("tipo") == "Voltage Source" and dev.get("conectado", False) and dev.get("encendido", False):
                return True
        return False

    def hay_fuente_activa_conectada(self, room, dev):
        if room not in self.rooms:
            return False

        devices = self.devices_by_room.get(room, [])
        connections = self.connections_by_room.get(room, [])
        dev_id = dev.get("id")
        if dev_id is None:
            return False

        active_sources = {
            d.get("id")
            for d in devices
            if d.get("tipo") == "Voltage Source"
            and d.get("conectado", False)
            and d.get("encendido", False)
            and d.get("id") is not None
        }
        if not active_sources:
            return False

        graph = {d.get("id"): [] for d in devices if d.get("id") is not None}
        for c in connections:
            o = c.get("origen")
            d = c.get("destino")
            if o in graph and d in graph and o != d:
                graph[o].append(d)
                graph[d].append(o)

        visited = set()
        stack = [dev_id]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            if u in active_sources:
                return True
            for v in graph.get(u, []):
                if v not in visited:
                    stack.append(v)

        return False

    def actualizar_cargas_por_fuentes(self, room):
        if room not in self.rooms:
            return

        devices = self.devices_by_room.get(room, [])
        for dev in devices:
            if dev.get("tipo") == "Voltage Source":
                continue

            if dev.get("tipo") == "Motion Sensor":
                powered = dev.get("conectado", False) and self.hay_fuente_activa_conectada(room, dev)
                if powered:
                    self.programar_armado_sensor_movimiento(room, dev)
                else:
                    self.desarmar_sensor_movimiento(room, dev)
                continue

            if not dev.get("conectado", False):
                if dev.get("encendido", False):
                    dev["encendido"] = False
                    self.actualizar_imagen_por_estado(dev)
                    if dev.get("tipo") in ("TV", "Radio", "Computer"):
                        self.detener_sonido_dispositivo(dev.get("tipo"))
                    self.log(f"{self.pretty_name(dev.get('tipo'))} forced off (disconnected)")
                continue

            powered = self.hay_fuente_activa_conectada(room, dev)

            if powered and not dev.get("encendido", False):
                dev["encendido"] = True
                self.actualizar_imagen_por_estado(dev)
                if dev.get("tipo") in ("TV", "Radio", "Computer"):
                    self.reproducir_sonido_dispositivo(dev.get("tipo"))
                self.log(f"{self.pretty_name(dev.get('tipo'))} turn on")

            elif not powered and dev.get("encendido", False):
                dev["encendido"] = False
                self.actualizar_imagen_por_estado(dev)
                if dev.get("tipo") in ("TV", "Radio", "Computer"):
                    self.detener_sonido_dispositivo(dev.get("tipo"))
                self.log(f"{self.pretty_name(dev.get('tipo'))} turn off")

        self.actualizar_alarma_calor()

    def actualizar_imagen_por_estado(self, dev):
        path = dev.get("imagen", "")
        if not path:
            return

        base, ext = os.path.splitext(path)

        if dev.get("encendido", False):
            if " OFF" in base:
                on_path = base.replace(" OFF", " ON") + ext
                if os.path.exists(on_path):
                    dev["imagen"] = on_path
        else:
            if " ON" in base:
                off_path = base.replace(" ON", " OFF") + ext
                if os.path.exists(off_path):
                    dev["imagen"] = off_path

    def apagar_cargas_en_habitacion(self, room):
        if room not in self.rooms:
            return
        for dev in self.devices_by_room[room]:
            if dev.get("tipo") != "Voltage Source":
                dev["encendido"] = False
                self.actualizar_imagen_por_estado(dev)
                if dev.get("tipo") in ("TV", "Radio", "Computer"):
                    self.detener_sonido_dispositivo(dev.get("tipo"))

    # -------------------------------------------------------------------------
    # MOTION SENSOR
    # -------------------------------------------------------------------------
    def hay_sensor_movimiento_activo(self, room):
        if room not in self.rooms:
            return False
        for dev in self.devices_by_room.get(room, []):
            if dev.get("tipo") == "Motion Sensor" and dev.get("sensor_armado", False):
                return True
        return False

    def reproducir_alarma_movimiento(self):
        self.log("ALARM: motion detected / user interaction")
        if self.alarm_sound is not None:
            self.alarm_sound.play()

    def reproducir_sonido_dispositivo(self, tipo):
        if tipo == "TV" and self.tv_sound is not None:
            self.tv_sound.play()
        elif tipo == "Radio" and self.radio_sound is not None:
            self.radio_sound.play()
        elif tipo == "Computer" and self.pc_sound is not None:
            self.pc_sound.play()

    def detener_sonido_dispositivo(self, tipo):
        if tipo == "TV" and self.tv_sound is not None:
            self.tv_sound.stop()
        elif tipo == "Radio" and self.radio_sound is not None:
            self.radio_sound.stop()
        elif tipo == "Computer" and self.pc_sound is not None:
            self.pc_sound.stop()

    def programar_armado_sensor_movimiento(self, room, dev):
        dev_id = dev.get("id")
        if dev_id is None:
            return

        if dev.get("sensor_armado", False):
            return

        timer = self.motion_sensor_timers.get(dev_id)
        if timer is not None and timer.isActive():
            return

        timer = QTimer(self)
        timer.setSingleShot(True)

        def al_terminar():
            sensor = self.obtener_dispositivo_por_id(room, dev_id)
            if sensor is None:
                return
            powered = sensor.get("conectado", False) and self.hay_fuente_activa_conectada(room, sensor)
            if not powered:
                return
            self.armar_sensor_movimiento(room, dev_id)

        timer.timeout.connect(al_terminar)
        self.motion_sensor_timers[dev_id] = timer
        timer.start(self.motion_sensor_delay_ms)
        self.log("Motion Sensor arming")

    def armar_sensor_movimiento(self, room, dev_id):
        dev = self.obtener_dispositivo_por_id(room, dev_id)
        if dev is None:
            return

        dev["sensor_armado"] = True
        dev["encendido"] = True
        self.actualizar_imagen_por_estado(dev)
        self.actualizar_imagen()
        self.actualizar_lista_dispositivos()
        self.statusBar().showMessage("Motion sensor armed: any interaction will trigger the alarm.", 5000)
        self.log("Motion Sensor armed")

        timer = self.motion_sensor_timers.pop(dev_id, None)
        if timer is not None:
            timer.stop()

    def desarmar_sensor_movimiento(self, room, dev):
        dev_id = dev.get("id")
        if dev_id is None:
            return

        timer = self.motion_sensor_timers.pop(dev_id, None)
        if timer is not None:
            timer.stop()

        if dev.get("sensor_armado", False) or dev.get("encendido", False):
            dev["sensor_armado"] = False
            dev["encendido"] = False
            self.actualizar_imagen_por_estado(dev)
            self.log("Motion Sensor disarmed")

        if self.alarm_sound is not None:
            self.alarm_sound.stop()

    # -------------------------------------------------------------------------
    # HEAT SENSOR
    # -------------------------------------------------------------------------
    def hay_sensor_calor_activo(self, room):
        if room not in self.rooms:
            return False
        for dev in self.devices_by_room.get(room, []):
            if dev.get("tipo") == "Heat Sensor":
                if dev.get("conectado", False) and self.hay_fuente_activa_conectada(room, dev):
                    return True
        return False

    def actualizar_alarma_calor(self):
        if self.heat_alarm_sound is None:
            return

        should_alarm_sound = False
        if self.current_temperature > 40:
            for room in self.rooms:
                if self.hay_sensor_calor_activo(room):
                    should_alarm_sound = True
                    break

        if should_alarm_sound:
            self.log("ALARM: heat detected (T > 40°C)")
            self.heat_alarm_sound.play()
        else:
            self.heat_alarm_sound.stop()

    # -------------------------------------------------------------------------
    # USER INTERACTION REGISTRATION
    # -------------------------------------------------------------------------
    def registrar_interaccion_usuario(self):
        room = self.current_image
        if self.hay_sensor_movimiento_activo(room):
            self.reproducir_alarma_movimiento()

    # -------------------------------------------------------------------------
    # TURN ON / TURN OFF / REMOVE / ADD
    # -------------------------------------------------------------------------
    def encender_dispositivo(self, dev):
        room = self.current_image

        if not dev.get("conectado", True):
            dev["conectado"] = True

        if dev.get("tipo") != "Voltage Source":
            if not self.hay_fuente_activa(room):
                self.statusBar().showMessage("There is no 'Voltage Source' turned on in this room.", 6000)
                return

            if not self.hay_fuente_activa_conectada(room, dev):
                self.statusBar().showMessage(
                    "This device is not connected by wires to any turned-on 'Voltage Source'.",
                    6000,
                )
                return

        dev["encendido"] = True
        self.actualizar_imagen_por_estado(dev)
        self.log(f"{self.pretty_name(dev.get('tipo'))} turn on")

        if dev.get("tipo") == "Voltage Source":
            self.actualizar_cargas_por_fuentes(room)

        self.highlighted_device = dev
        self.iniciar_animacion("encender")
        self.guardar_posiciones_dispositivos()
        self.actualizar_imagen()
        self.actualizar_lista_dispositivos()
        self.registrar_interaccion_usuario()

    def apagar_dispositivo(self, dev):
        room = self.current_image
        dev["encendido"] = False
        self.actualizar_imagen_por_estado(dev)
        self.log(f"{self.pretty_name(dev.get('tipo'))} turn off")

        if dev.get("tipo") == "Voltage Source":
            self.apagar_cargas_en_habitacion(room)
            self.statusBar().showMessage("Voltage source turned off: all loads in the room were turned off.", 5000)

        self.actualizar_cargas_por_fuentes(room)

        self.highlighted_device = dev
        self.iniciar_animacion("apagar")
        self.guardar_posiciones_dispositivos()
        self.actualizar_imagen()
        self.actualizar_lista_dispositivos()
        self.registrar_interaccion_usuario()

    def eliminar_dispositivo(self, dev):
        if self.current_image not in self.rooms:
            return

        room = self.current_image
        device_list = self.devices_by_room[room]
        if dev not in device_list:
            return

        is_source = dev.get("tipo") == "Voltage Source"
        is_motion_sensor = dev.get("tipo") == "Motion Sensor"

        if is_motion_sensor:
            self.desarmar_sensor_movimiento(room, dev)

        if dev.get("tipo") in ("TV", "Radio", "Computer"):
            self.detener_sonido_dispositivo(dev.get("tipo"))

        device_list.remove(dev)
        self.log(f"{self.pretty_name(dev.get('tipo'))} removed")

        dev_id = dev.get("id")
        if dev_id is not None:
            self.connections_by_room[room] = [
                c for c in self.connections_by_room[room]
                if c["origen"] != dev_id and c["destino"] != dev_id
            ]

        if is_source:
            self.apagar_cargas_en_habitacion(room)
            self.statusBar().showMessage("Voltage source removed: all loads lost power.", 5000)

        self.actualizar_cargas_por_fuentes(room)
        self.highlighted_device = None
        self.guardar_posiciones_dispositivos()
        self.actualizar_imagen()
        self.actualizar_lista_dispositivos()
        self.registrar_interaccion_usuario()

    def agregar_dispositivo(self):
        if self.current_image not in self.rooms:
            return

        room = self.current_image
        component_name = self.components_combo.currentText()
        if not component_name:
            return

        image_file = self.component_files.get(component_name, "")
        if not image_file:
            return

        if component_name == "Voltage Source":
            for dev in self.devices_by_room[room]:
                if dev["tipo"] == "Voltage Source":
                    self.statusBar().showMessage("There is already a 'Voltage Source' in this room.", 4000)
                    return

        dev_id = self.next_device_id
        self.next_device_id += 1

        new_dev = {
            "id": dev_id,
            "tipo": component_name,
            "imagen": image_file,
            "x": 0,
            "y": 0,
            "rect": None,
            "conectado": True,
            "encendido": False,
        }

        if component_name == "Motion Sensor":
            new_dev["sensor_armado"] = False

        self.devices_by_room[room].append(new_dev)
        self.highlighted_device = new_dev
        self.log(f"{self.pretty_name(component_name)} added")

        self.iniciar_animacion("agregar")
        self.guardar_posiciones_dispositivos()
        self.actualizar_imagen()
        self.actualizar_lista_dispositivos()
        self.registrar_interaccion_usuario()

    # -------------------------------------------------------------------------
    # HIGHLIGHT ANIMATION
    # -------------------------------------------------------------------------
    def iniciar_animacion(self, tipo="agregar"):
        self.animation_type = tipo
        self.animation_active = True
        self.animation_steps_left = 6
        self.highlight_mode = False
        self.animation_timer.start(120)

    def paso_animacion(self):
        if self.animation_steps_left <= 0:
            self.animation_timer.stop()
            self.animation_active = False
            self.highlight_mode = False
            self.actualizar_imagen()
            return

        self.highlight_mode = not self.highlight_mode
        self.animation_steps_left -= 1
        self.actualizar_imagen()

    # -------------------------------------------------------------------------
    # DEVICE DRAGGING WITH MOUSE
    # -------------------------------------------------------------------------
    def iniciar_arrastre_dispositivo(self, event):
        if event.button() != Qt.LeftButton:
            return
        if self.current_image not in self.rooms:
            return

        clicked_dev = self.obtener_dispositivo_en_pos(event.pos())
        if clicked_dev is None:
            return

        self.dragging = True
        self.last_drag_pos = self.label_pos_to_pixmap_pos(event.pos())
        self.selected_device = clicked_dev
        self.background.setCursor(Qt.ClosedHandCursor)
        self.registrar_interaccion_usuario()

    def actualizar_arrastre_dispositivo(self, event):
        if not self.dragging or self.selected_device is None:
            return

        rect = self.selected_device.get("rect")
        if rect is None:
            return

        mouse_pix = self.label_pos_to_pixmap_pos(event.pos())
        dx = mouse_pix.x() - self.last_drag_pos.x()
        dy = mouse_pix.y() - self.last_drag_pos.y()

        new_x = rect.x() + dx
        new_y = rect.y() + dy

        pixmap = self.background.pixmap()
        if pixmap is not None:
            max_x = pixmap.width() - rect.width()
            max_y = pixmap.height() - rect.height()
        else:
            max_x = self.background.width() - rect.width()
            max_y = self.background.height() - rect.height()

        max_x = max(max_x, 0)
        max_y = max(max_y, 0)

        new_x = max(0, min(new_x, max_x))
        new_y = max(0, min(new_y, max_y))

        self.selected_device["x"] = new_x
        self.selected_device["y"] = new_y

        self.last_drag_pos = mouse_pix
        self.actualizar_imagen()
        self.registrar_interaccion_usuario()

    def finalizar_arrastre_dispositivo(self, event):
        if self.dragging:
            self.guardar_posiciones_dispositivos()

        self.dragging = False
        self.last_drag_pos = None
        self.selected_device = None

    # -------------------------------------------------------------------------
    # CURSOR UPDATE
    # -------------------------------------------------------------------------
    def actualizar_cursor(self, pos):
        if self.dragging:
            self.background.setCursor(Qt.ClosedHandCursor)
            return

        if self.current_image not in self.rooms:
            self.background.setCursor(Qt.ArrowCursor)
            return

        dev = self.obtener_dispositivo_en_pos(pos)
        self.background.setCursor(Qt.OpenHandCursor if dev is not None else Qt.ArrowCursor)

    # -------------------------------------------------------------------------
    # TEMPORARY WIRE DURING CONNECTION SELECTION
    # -------------------------------------------------------------------------
    def actualizar_cable_temporal(self, pos):
        if self.connection_source is None or self.current_image not in self.rooms:
            self.temp_connection_pos = None
            return

        if not self.dragging:
            self.temp_connection_pos = self.label_pos_to_pixmap_pos(pos)
            self.actualizar_imagen()

    # -------------------------------------------------------------------------
    # WINDOW RESIZE HANDLING
    # -------------------------------------------------------------------------
    def resizeEvent(self, event):
        if self.window_initialized:
            self.actualizar_imagen()
        super().resizeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()