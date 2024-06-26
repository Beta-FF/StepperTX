#import re
from PyQt5.QtWidgets    import QApplication, QMainWindow
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore       import QIODevice
from natsort            import natsorted
import sys

import Ui_StepperTX 

COLOR_GREEN =   "lightgreen"
COLOR_YELLOW =  "#FCCA46"
COLOR_RED =     "coral"
COLOR_WHITE =   "#F0F0F0"

ID_STATE =      '0'
ID_CURRENT =    '1'
ID_TARGET_NEW = '2'
ID_ENCODER =    '3'
ID_HOME =       '4'
ID_HOME_OK =    '5'

def set_style_text(element_comd, background_color = "", text = "", element_text = None):

    if background_color != "":
            element_comd.setStyleSheet("background-color: %s;" %(background_color))
    if element_text == None:
        if text != "":    
            element_comd.setText(text)
    else:
        if text != "":    
            element_text.setText(text)

def uartSend(dataStr):
    #dataStr += '\0'
    uart.write(dataStr.encode())
    #uart.waitForBytesWritten(-1)
    print("qt = " + dataStr)

def uartRead():
    rx = uart.readLine()
    rx = str(rx, 'utf-8').strip()
    print("MCU: " + rx)
    parsing(rx)

def button_send_clicked():
    tx_buf = ui.lineEdit_txLine.displayText()
    if len(tx_buf) != 0:
        tx_buf += ";"
        uartSend(tx_buf)

def slider_focus_changed():
    value = ui.horizontalSlider_focus.value()
    set_style_text(ui.lineEdit_focusLine, "", str(value))

def slider_zoom_changed():
    value = ui.horizontalSlider_zoom.value()
    set_style_text(ui.lineEdit_zoomLine, "", str(value))

def slider_aperture_changed():
    value = ui.horizontalSlider_aperture.value()
    set_style_text(ui.lineEdit_apertureLine, "", str(value))

def slider_released():
    if ui.checkBox_applyManually.isChecked() == False:
        apply_handler() 

def uartScanHandler():
    comb_name = []
    portsAvaible = QSerialPortInfo.availablePorts() #создаем список дотсупных портов
    for port in portsAvaible: # цикл перебора списка
        #port_list.append(port.portName()) # получаем имя порта и заносим в конец port_list
        comb_name.append(port.portName() + ' - ' + port.description())
    ui.comboBox_comPorts.clear()
    if len(comb_name) > 0:  # порты найдены
        comb_name = list(set(comb_name)) # создаем множество из port_list для удаления дубликатов и возвращаем в list
        comb_name = natsorted(comb_name) # сортируем по увеличению
        ui.comboBox_comPorts.addItems(comb_name)
        set_style_text(ui.label_com_status, COLOR_YELLOW, "Не подключен")
    else:
        set_style_text(ui.label_com_status, COLOR_RED, "COM не найдены!")

def button_connect_clicked():
    connect_button_name = ui.pushButton_connect.text()
    comb_name = ui.comboBox_comPorts.currentText().split(' ')
    if connect_button_name == 'Открыть':
        uart.setPortName(comb_name[0])
        if uart.open(QIODevice.OpenModeFlag.ReadWrite) == True:
            uart.setDataTerminalReady(True)
            set_style_text(ui.pushButton_connect, "", "Закрыть")
            ui.groupBox_transmit.setEnabled(True)
            ui.pushButton_home.setEnabled(True)
            set_style_text(ui.label_com_status, COLOR_GREEN, comb_name[0] + " Открыт")
            ui.comboBox_comPorts.setDisabled(True)
            ui.pushButton_scan.setDisabled(True)
        else:
            set_style_text(ui.label_com_status, COLOR_RED, comb_name[0] + " Ошибка!")

    if connect_button_name == 'Закрыть':
        uart.close()
        set_style_text(ui.label_focus_status, COLOR_WHITE, "Статус", ui.label_focus_text)
        set_style_text(ui.label_zoom_status, COLOR_WHITE, "Статус", ui.label_zoom_text)
        set_style_text(ui.label_aperture_status, COLOR_WHITE, "Статус", ui.label_aperture_text)
        set_style_text(ui.pushButton_connect, "", "Открыть")
        ui.groupBox_steppers.setDisabled(True)
        ui.groupBox_transmit.setDisabled(True)
        ui.pushButton_home.setDisabled(True)
        set_style_text(ui.label_com_status, COLOR_YELLOW, comb_name[0] + " Закрыт")
        ui.comboBox_comPorts.setEnabled(True)
        ui.pushButton_scan.setEnabled(True)

def parsing(dataStr):
    dataStr = dataStr.replace(';', '')
    data = dataStr.split(',')
    if data[0] == ID_STATE:
        match data[1]:
            case '0': set_style_text(ui.label_focus_status, COLOR_GREEN, "Прибыл", ui.label_focus_text)
            case '1': set_style_text(ui.label_focus_status, COLOR_YELLOW, "В пути", ui.label_focus_text)
            case '3': set_style_text(ui.label_focus_status, COLOR_YELLOW, "К концевику", ui.label_focus_text)
        match data[2]:
            case '0': set_style_text(ui.label_zoom_status, COLOR_GREEN, "Прибыл", ui.label_zoom_text)
            case '1': set_style_text(ui.label_zoom_status, COLOR_YELLOW, "В пути", ui.label_zoom_text)
            case '3': set_style_text(ui.label_zoom_status, COLOR_YELLOW, "К концевику", ui.label_zoom_text)
        match data[3]: # диафрагма без концевика
            case '0': set_style_text(ui.label_aperture_status, COLOR_GREEN, "Прибыл", ui.label_aperture_text)
            case '1': set_style_text(ui.label_aperture_status, COLOR_YELLOW, "В пути", ui.label_aperture_text)
            #case '3': set_style_text(ui.label_aperture_status, COLOR_YELLOW, "К концевику", ui.label_aperture_text) 
    
    if data[0] == ID_HOME_OK:
        if data[1] == '1':
            ui.groupBox_steppers.setEnabled(True)
            ui.horizontalSlider_focus.setValue(0)
            set_style_text(ui.lineEdit_focusLine, "", "0")
            ui.horizontalSlider_zoom.setValue(0)
            set_style_text(ui.lineEdit_zoomLine, "", "0")
            ui.horizontalSlider_aperture.setValue(0)
            set_style_text(ui.lineEdit_apertureLine, "", "0")

    if data[0] == ID_CURRENT:
        if data[1].isdigit() == True:
            ui.horizontalSlider_focus.setValue(int(data[1]))
            ui.lineEdit_focusLine.setText(data[1])
    if data[0] == ID_CURRENT:
        if data[2].isdigit() == True:
            ui.horizontalSlider_zoom.setValue(int(data[2]))
            ui.lineEdit_zoomLine.setText(data[2])
    if data[0] == ID_CURRENT:
        if data[3].isdigit() == True:
            ui.horizontalSlider_aperture.setValue(int(data[3]))
            ui.lineEdit_apertureLine.setText(data[3])


    # if(data[0] == ID_ENCODER):
    #     if(data[1] == '1'):
    #         value = ui.horizontalSlider_focus.value()
    #         value += int(data[1])
    #         ui.horizontalSlider_focus.setValue(value)
    #         apply_handler()
    #     else:


def checkbox_clicked():
    if ui.checkBox_applyManually.isChecked() == False:
        ui.pushButton_apply.setDisabled(True)
    else:
        ui.pushButton_apply.setEnabled(True)

def button_home_clicked():
    tx_home()

def tx_target_new():
    focus_value = ui.horizontalSlider_focus.value()
    zoom_value = ui.horizontalSlider_zoom.value()
    aperture_value = ui.horizontalSlider_aperture.value()
    uartSend(ID_TARGET_NEW + ",%d,%d,%d;" %(focus_value, zoom_value, aperture_value))
    #tx_buf = "2," + str(focus_value) + "," + str(zoom_value) + "," + str(aperture_value) + ";"

def tx_home():
    uartSend(ID_HOME + ",1;")
    #ui.groupBox_steppers.setEnabled(True)

def apply_handler():
    tx_target_new()

def line_focus_enter():
    text = ui.lineEdit_focusLine.displayText()
    if text.isdigit() == True:
        value = int(text)
        ui.horizontalSlider_focus.setValue(value)
        apply_handler()
    else:
        ui.lineEdit_focusLine.clear()

def line_zoom_enter():
    text = ui.lineEdit_zoomLine.displayText()
    if text.isdigit() == True:
        value = int(text)
        ui.horizontalSlider_zoom.setValue(value)
        apply_handler()
    else:
        ui.lineEdit_focusLine.clear()

def line_aperture_enter():
    text = ui.lineEdit_apertureLine.displayText()
    if text.isdigit() == True:
        value = int(text)
        ui.horizontalSlider_aperture.setValue(value)
        apply_handler()
    else:
        ui.lineEdit_focusLine.clear()


app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = Ui_StepperTX.Ui_MainWindow()
ui.setupUi(MainWindow)

# UART
uart = QSerialPort()
uart.setBaudRate(115200)
uartScanHandler()
ui.groupBox_steppers.setDisabled(True)
ui.groupBox_transmit.setDisabled(True)

# Buttons
ui.pushButton_scan.clicked.connect(uartScanHandler)
ui.pushButton_connect.clicked.connect(button_connect_clicked)
ui.pushButton_apply.clicked.connect(apply_handler)
ui.pushButton_home.clicked.connect(button_home_clicked)
ui.pushButton_send.clicked.connect(button_send_clicked)
# Sliders Changed
ui.horizontalSlider_focus.valueChanged.connect(slider_focus_changed)
ui.horizontalSlider_zoom.valueChanged.connect(slider_zoom_changed)
ui.horizontalSlider_aperture.valueChanged.connect(slider_aperture_changed)
# Sliders Released
ui.horizontalSlider_focus.sliderReleased.connect(slider_released)
ui.horizontalSlider_zoom.sliderReleased.connect(slider_released)
ui.horizontalSlider_aperture.sliderReleased.connect(slider_released)
# Check Box
ui.checkBox_applyManually.clicked.connect(checkbox_clicked)
# Lines Edit
ui.lineEdit_focusLine.editingFinished.connect(line_focus_enter)
ui.lineEdit_zoomLine.editingFinished.connect(line_zoom_enter)
ui.lineEdit_apertureLine.editingFinished.connect(line_aperture_enter)
#ui.lineEdit_txLine.editingFinished.connect(test_func)
# UART RX
uart.readyRead.connect(uartRead)

MainWindow.show()
sys.exit(app.exec())


if data[1] == '0': set_style_text(ui.label_focus_status, COLOR_GREEN, "Arrived", ui.label_focus_text)
if data[1] == '1': set_style_text(ui.label_focus_status, COLOR_YELLOW, "In motion", ui.label_focus_text)
if data[1] == '3': set_style_text(ui.label_focus_status, COLOR_YELLOW, "Home", ui.label_focus_text)

if data[2] == '0': set_style_text(ui.label_zoom_status, COLOR_GREEN, "Arrived", ui.label_zoom_text)
if data[2] == '1': set_style_text(ui.label_zoom_status, COLOR_YELLOW, "In motion", ui.label_zoom_text)
if data[2] == '3': set_style_text(ui.label_zoom_status, COLOR_YELLOW, "Home", ui.label_zoom_text)

if data[3] == '0': set_style_text(ui.label_aperture_status, COLOR_GREEN, "Arrived", ui.label_aperture_text)
if data[3] == '1': set_style_text(ui.label_aperture_status, COLOR_YELLOW, "In motion", ui.label_aperture_text)
if data[3] == '2': set_style_text(ui.label_aperture_status, COLOR_YELLOW, "In motion", ui.label_aperture_text)

set_style_text(ui.label_focus_status, COLOR_YELLOW, "Home", ui.label_focus_text)
set_style_text(ui.label_zoom_status, COLOR_YELLOW, "Home", ui.label_zoom_text)
set_style_text(ui.label_aperture_status, COLOR_YELLOW, "Home", ui.label_aperture_text)