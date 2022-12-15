from PyQt5 import uic, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice, QTimer
from struct import pack, unpack
from pysolar.solar import get_azimuth, get_altitude
import datetime

app = QtWidgets.QApplication([])
ui = uic.loadUi("com_window.ui")
ui.setWindowTitle("Pivot Support Device Gui")

serial = QSerialPort()
serial.setBaudRate(115200)
portList = []
ports = QSerialPortInfo().availablePorts()
for port in ports:
    portList.append(port.portName())

ui.comL.addItems(portList)

lat = round(55.8)
long = round(37.6)
azimuth = 0
elevation = 0

sys_timer = QTimer(ui)
sun_pos_timer = QTimer(ui)
surveillance = False
set_other_block = False


def onRead():
    if serial.bytesAvailable() == 12:
        rx = serial.read(12)
        print(rx, ' - response from stm')
        try:
            data = unpack('i', rx[0:])
            print(data[0])
        except Exception as e:
            print(e, ' - it is exception ')


def onOpen():
    serial.setPortName(ui.comL.currentText())
    if ui.comL.currentText() != '':
        serial.open(QIODevice.ReadWrite)
        ui.lineConnect.setText('Connection is successful')
        ui.statusbar.showMessage(f'Connection to port: {ui.comL.currentText()}')
        ui.closeB.setEnabled(True)
        ui.setInit.setEnabled(True)
        ui.setAlarm.setEnabled(True)
        ui.setContinue.setEnabled(True)
        ui.cbSun.setCheckable(True)
        ui.cbAngles.setCheckable(True)
        sys_timer.start(8000)
    else:
        ui.lineConnect.setText('Select correct port')
        ui.statusbar.showMessage("Port isn't open")


def onClose():
    serial.close()
    ui.lineConnect.setText('No connection')
    ui.sendB_long.setEnabled(False)
    ui.sendB_lat.setEnabled(False)
    ui.setSun.setEnabled(False)
    ui.setStopsun.setEnabled(False)
    ui.setInit.setEnabled(False)
    ui.sendB_Azimuth.setEnabled(False)
    ui.sendB_Elevation.setEnabled(False)
    ui.setAlarm.setEnabled(False)
    ui.setContinue.setEnabled(False)
    ui.setAngles.setEnabled(False)


def setLat():
    try:
        global lat
        lat = float(ui.textLat.displayText())
        ui.lineLat.setText(f'Accepted {int(lat)}°')
        ui.textLat.setText(' ')
    except:
        ui.lineLat.setText(f'Uncorrected: "{ui.textLat.displayText()}". Write new latitude')
        ui.textLat.setText(' ')
        print('Set correct value')


def setLong():
    try:
        global long
        long = float(ui.textLong.displayText())
        ui.lineLong.setText(f'Accepted {int(long)}°')
        ui.textLong.setText(' ')
    except:
        ui.lineLong.setText(f'Uncorrected: "{ui.textLong.displayText()}". Write new longitude')
        ui.textLong.setText(' ')
        print('Set correct value')


def sunPos():
    global surveillance
    global previous_azimuth
    global azimuth, elevation
    date = datetime.datetime.now(datetime.timezone.utc)
    azimuth = round(get_azimuth(lat, long, date))
    elevation = round(get_altitude(lat, long, date))
    print(azimuth, elevation)
    if azimuth >= 0 and elevation >= 0:
        if not surveillance:
            sun_pos_timer.start(10000)
            surveillance = True
        ui.sunProgress.setText('Wait...')
        outAzimuth = pack('i',azimuth)
        outAltitude = pack('i', elevation)
        amount = pack('i', azimuth + elevation)
        outList = [outAzimuth[0], outAzimuth[1], outAzimuth[2], outAzimuth[3], outAltitude[0], outAltitude[1],
                   outAltitude[2], outAltitude[3], amount[0],  amount[1],  amount[2],  amount[3]]
        messageList = bytearray(outList)
        print(messageList)
        ui.statusbar.showMessage('Send data to PSD')
        serial.write(messageList)
    else:
        ui.statusbar.showMessage('The sun position is out of range ( ')


def sunStop():
    global surveillance
    sun_pos_timer.stop()
    surveillance = False
    if not set_other_block:
        ui.sunStop.setText('Wait...')
        ui.statusbar.showMessage('Stopping process of surveillance')
        print('Stop sun surveillance')
    else:
        ui.statusbar.showMessage('Stopping surveillance due to select other block')


def setInitPosition():
    message = pack('i', 255)
    outList = [0, 0, 0, 0, message[0], message[1], message[2], message[3], message[0], message[1], message[2], message[3]]
    messageList = bytearray(outList)
    ui.initProgress.setText('Wait...')
    ui.statusbar.showMessage('Set zero position')
    print(messageList)
    serial.write(messageList)


def onTimeout():
    ui.initProgress.setText(' ')
    ui.sunProgress.setText(' ')
    ui.anglesProgress.setText(' ')
    ui.statusbar.showMessage(' ')
    ui.lineES.setText('EMERGENCY STOP')
    ui.lineContinue.setText('Continue work')
    ui.sunStop.setText(' ')


def setAzimuth():
    try:
        global azimuth
        azimuth = int(ui.textAzimuth.displayText())
        ui.lineAzimuth.setText(f'Accepted {azimuth}°')
        ui.textAzimuth.setText(' ')
    except:
        print('set correct azimuth')
        ui.lineAzimuth.setText(f'Uncorrected: "{ui.textAzimuth.displayText()}". Write new azimuth')
        ui.textAzimuth.setText(' ')


def setElevation():
    try:
        global elevation
        elevation = int(ui.textElevation.displayText())
        ui.lineElevation.setText(f'Accepted {elevation}°')
        ui.textElevation.setText(' ')
    except:
        print('set correct elevation')
        ui.lineElevation.setText(f'Uncorrected: "{ui.textElevation.displayText()}". Write new elevation')
        ui.textElevation.setText(' ')


def setAngles():
    outAzimuth = pack('i', azimuth)
    outElevation = pack('i', elevation)
    ui.anglesProgress.setText('Wait...')
    amount = pack('i', azimuth + elevation)
    outList = [outAzimuth[0], outAzimuth[1], outAzimuth[2], outAzimuth[3], outElevation[0], outElevation[1],
               outElevation[2], outElevation[3], amount[0], amount[1], amount[2], amount[3]]
    messageList = bytearray(outList)
    print(messageList)
    ui.statusbar.showMessage('Personal settings in progress')
    serial.write(messageList)


def sunTimer():
    if surveillance:
        sunPos()


def setEMSTOP():
    sun_pos_timer.stop()
    data = pack('i', 255)
    ui.lineES.setText('ES is processed')
    amount = pack('i', 510)
    outList = [data[0], data[1], data[2], data[3], data[0], data[1],
               data[2], data[3], amount[0], amount[1], amount[2], amount[3]]
    messageList = bytearray(outList)
    print(messageList)
    ui.statusbar.showMessage('Emergency stop in progress')
    ui.setInit.setEnabled(False)
    ui.cbSun.setCheckState(False)
    ui.cbAngles.setCheckState(False)
    ui.cbSun.setCheckable(False)
    ui.cbAngles.setCheckable(False)
    serial.write(messageList)


def setContinue():
    global surveillance
    surveillance = False
    data = pack('i', 240)
    ui.lineContinue.setText('Accepted')
    outList = [0, 0, 0, 0, data[0], data[1], data[2], data[3], data[0], data[1], data[2], data[3]]
    messageList = bytearray(outList)
    print(messageList)
    ui.statusbar.showMessage('Continue normal work')
    ui.setInit.setEnabled(True)
    ui.cbSun.setCheckable(True)
    ui.cbAngles.setCheckable(True)
    serial.write(messageList)


def cbSunstart():
    if ui.cbSun.isChecked():
        ui.statusbar.showMessage('Sun surveillance block is selected')
        ui.setSun.setEnabled(True)
        ui.sendB_long.setEnabled(True)
        ui.sendB_lat.setEnabled(True)
        ui.setStopsun.setEnabled(True)
        ui.cbAngles.setCheckState(0)
    else:
        ui.sendB_long.setEnabled(False)
        ui.sendB_lat.setEnabled(False)
        ui.setSun.setEnabled(False)
        ui.setStopsun.setEnabled(False)


def cbAngles():
    global set_other_block
    if ui.cbAngles.isChecked():
        ui.statusbar.showMessage('Personal settings block is selected')
        ui.sendB_Azimuth.setEnabled(True)
        ui.sendB_Elevation.setEnabled(True)
        ui.setAngles.setEnabled(True)
        ui.cbSun.setCheckState(0)
        if surveillance:
            set_other_block = True
            sunStop()
    else:
        ui.setAngles.setEnabled(False)
        ui.sendB_Azimuth.setEnabled(False)
        ui.sendB_Elevation.setEnabled(False)


ui.closeB.setEnabled(False)
ui.cbSun.setCheckable(False)
ui.cbAngles.setCheckable(False)
ui.setAngles.setEnabled(False)
ui.sendB_Azimuth.setEnabled(False)
ui.sendB_Elevation.setEnabled(False)
ui.sendB_long.setEnabled(False)
ui.sendB_lat.setEnabled(False)
ui.setSun.setEnabled(False)
ui.setStopsun.setEnabled(False)
ui.setInit.setEnabled(False)
ui.setAlarm.setEnabled(False)
ui.setContinue.setEnabled(False)
serial.readyRead.connect(onRead)
ui.openB.clicked.connect(onOpen)
ui.closeB.clicked.connect(onClose)
ui.sendB_lat.clicked.connect(setLat)
ui.sendB_long.clicked.connect(setLong)
ui.setSun.clicked.connect(sunPos)
ui.setStopsun.clicked.connect(sunStop)
ui.setInit.clicked.connect(setInitPosition)
sys_timer.timeout.connect(onTimeout)
sun_pos_timer.timeout.connect(sunTimer)
ui.sendB_Azimuth.clicked.connect(setAzimuth)
ui.sendB_Elevation.clicked.connect(setElevation)
ui.setAngles.clicked.connect(setAngles)
ui.setAlarm.clicked.connect(setEMSTOP)
ui.setContinue.clicked.connect(setContinue)
ui.cbSun.stateChanged.connect(cbSunstart)
ui.cbAngles.stateChanged.connect(cbAngles)
ui.statusbar.showMessage('Connect your PSD to USB port, choose correct port and open it')

ui.show()
app.exec()
