class Program:

  def __init__(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.bind(('', 80))
    self.s.listen(5)
    self.loop()

  def web_page(self):
    bme = BME280.BME280(i2c=i2c)
    
    html = """<html><head><meta http-equiv="refresh" content="1"><meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,"><style>body { text-align: center; font-family: "Trebuchet MS", Arial;}
    table { border-collapse: collapse; width:35%; margin-left:auto; margin-right:auto; }
    th { padding: 12px; background-color: #0043af; color: white; }
    tr { border: 1px solid #ddd; padding: 12px; }
    tr:hover { background-color: #bcbcbc; }
    td { border: none; padding: 12px; }
    .sensor { color:white; font-weight: bold; background-color: #bcbcbc; padding: 1px;
    </style></head><body><h1>ESP with BME280</h1>
    <table><tr><th>MEASUREMENT</th><th>VALUE</th></tr>
    <tr><td>Temp. Celsius</td><td><span class="sensor">""" + str(bme.temperature) + """</span></td></tr>
    <tr><td>Temp. Fahrenheit</td><td><span class="sensor">""" + str(round((bme.read_temperature()/100.0) * (9/5) + 32, 2))  + """F</span></td></tr>
    <tr><td>Pressure</td><td><span class="sensor">""" + str(bme.pressure) + """</span></td></tr>
    <tr><td>Humidity</td><td><span class="sensor">""" + str(bme.humidity) + """</span></td></tr></body></html>"""
    return html

  def loop(self):
    while True:
      try:
        if gc.mem_free() < 102000:
          gc.collect()
        conn, addr = self.s.accept()
        conn.settimeout(3.0)
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        conn.settimeout(None)
        request = str(request)
        print('Content = %s' % request)
        response = self.web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
      except OSError as e:
        conn.close()
        print('Connection closed')
        print(e)

if __name__ == "__main__":
  program = Program()