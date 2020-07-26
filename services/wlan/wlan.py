from wifi import Cell, Scheme


class Wlan:
    def __init__(self):
        return

    def scan(self, intentMessage):
        # wlan = Cell.all('wlan0')
        wifilist = []
        wlanlist = []

        wlan = Cell.all('wlan0')
        for cell in wlan:
            wifilist.append(cell)

        sentence = ''
        counter = 0
        for cell in wifilist:
            wlanlist.append(cell.ssid)
            counter += 1
            sentence = sentence + ' ' + str(counter) + intentMessage["language"]["wlanName"] + cell.ssid

        return intentMessage["language"]["thereAreFollingWlan"] + sentence

    #TODO connect to Wifi