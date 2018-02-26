# -*- coding: utf-8 -*-
import subprocess
import bluetooth
import scratch
import signal
import time

#identyfikator usługi bluetooth
uuid = "00001101-0000-1000-8000-00805F9B34FB"
isRunning = True #stan naszej aplikacji
isConnected = False #stan połaczenia

core = scratch.Scratch() #podłączenie się do scratcha
core.sensorupdate({'bt-recv': -1}) #ustawienie początkowej wartości sesora "bt-recv" na -1

btServer = bluetooth.BluetoothSocket(bluetooth.RFCOMM) #utworzenie gniazda nasłuchującego na połączenie bluetooth
btClient = None #przechowuje połaczenie z klientem

btServer.bind(("", 1)) #ustawiamy nasłuchiwanie na kanał 1
btServer.listen(1) #ustawiamy maksymalną ilość jednoczesnych połączeń na jedno

#rozgłaszamy naszą usługę
bluetooth.advertise_service(btServer, "Raspberry Pi",
							service_id = uuid,
							service_classes = [uuid, bluetooth.SERIAL_PORT_CLASS],
							profiles = [bluetooth.SERIAL_PORT_PROFILE])
out = subprocess.check_output('hciconfig')
m = re.search(r'BD Address: (?P<bda>[A-F0-9]{2}(:[A-F0-9]{2}){5})', out)
bdaddr = m.group('bda')
print("BDA:", bdaddr)

#funkcja, która wykona się w momencie przerwania programu
def signal_kill(signal, frame):
	global isRunning, isConnected
	print("\nCtrl+C captured, Exiting...")
	isRunning = False
	isConnected = False

	#zamykamy wszystkie połączenia
	btClient.close()
	btServer.close()
	core.disconnect()

#funkcja odbierająca komunikaty ze scratcha
def listen():
	while True:
		try:
			yield core.receive()
		except scratch.ScratchError:
			raise StopIteration

#ustawienie przechwytywania przerwania programu
signal.signal(signal.SIGINT, signal_kill)

#Do póki nasz program działa
while isRunning:
	print "Waiting for connection..."

	try:
		btClient, address = btServer.accept() #oczekujemy na połaczenie
	except bluetooth.btcommon.BluetoothError:
		break

	print "Accepted connection from ", address
	core.broadcast('bt-connected') #powiadamiamy scratch że ktoś się z nami podłączył
	isConnected = True #zmieniamy stan na podłączony

	#do póki jesteśmy podłączeni z urządzeniem
	while isConnected:
		#próbujemy odebrać komunikaty ze scratcha
		for msg in listen():
			print msg
			if msg[0] == 'broadcast':
				if msg[1] == "bt-read": #jeśli scratch chce odczytać dane wysłane przez bluetooth
					try:
						data = btClient.recv(1) # odbieramy bajt danych,
												# jeśli nie ma jeszcze danych
												# to program jest zamrażany do czasu ich ostrzymania
						print data
						core.sensorupdate({'bt-recv': data[0]}) #zmieniamy wartość sensora na odebrany bajt danych
						core.broadcast('bt-recv-updated') #powiadamiamy o zmianie wartości sensora
					except bluetooth.btcommon.BluetoothError:
						#jeśli opjawił się błąd to prawdopodobnie połączenie zostało zerwane
						isConnected = False
						break
		time.sleep(1)
