class Program:

  class SolarSensor:

    def __init__(self):
      # setup Analogue Digital Converter
        self.adc = ADC(Pin(34))
        self.adc.atten(ADC.ATTN_0DB)
        self.adc.width(ADC.WIDTH_12BIT)

    # calculate Netto sun power
    def read_gross(self):
      return ((self.read_voltage()-(config["offset"]))/config["gain"])/(config["solar_panel_value"])

    # calculate gross sun power
    def read_netto(self):
      bme = BME280.BME280(i2c=i2c)
      diff_t = float(bme.temperature.strip("C"))-25
      netto = self.read_gross()
      return netto - netto*0.004*diff_t

    # read solar sensor voltage
    def read_voltage(self):
      value = 0
      # measures the voltage 200 times and takes the average to combat noise
      for i in range(200):
        value += self.adc.read()
      if value/200 < 1:
        return 0
      else:
        return 1.2*((value/200)/4096)+0.0650

  def __init__(self):
    # setup socket for webpage
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.bind(('', 80))
    self.s.listen(5)
    # create solarsensor object
    self.solar_sensor = self.SolarSensor()
    # set timer to log the values every 1 second
    self.timer = Timer(-1)
    self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self.log_values)
    # begin the webpage loop
    self.loop()

  def web_page(self):
    # read bme sensor
    bme = BME280.BME280(i2c=i2c)
    # html with sensor readings
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
    <tr><td>Solar Power Netto</td><td><span class="sensor">""" + str(self.solar_sensor.read_netto()) + """</span></td></tr>
    <tr><td>Solar Power Gross</td><td><span class="sensor">""" + str(self.solar_sensor.read_gross()) + """</span></td></tr>
    <tr><td>Date</td><td><span class="sensor">""" + str(time.localtime()) + """</span></td></tr>
    <tr><td>voltage</td><td><span class="sensor">""" + str(self.solar_sensor.read_voltage())+ """</span></td></tr>
    <tr><td>adc</td><td><span class="sensor">""" + str(self.solar_sensor.adc.read()) + """</span></td></tr>
    <tr><td>Temp. Celsius</td><td><span class="sensor">""" + str(bme.temperature) + """</span></td></tr>
    <tr><td>Pressure</td><td><span class="sensor">""" + str(bme.pressure) + """</span></td></tr>
    <tr><td>Humidity</td><td><span class="sensor">""" + str(bme.humidity) + """</span></td></tr></body></html>"""
    return html

  def log_values(self, timer):
    # read bme
    bme = BME280.BME280(i2c=i2c)
    # read solar sensor
    solar = int(self.solar_sensor.read_gross())
    temp = bme.temperature
    # read date
    year, month, mday, hour, minute, second, weekday, yearday = time.localtime()
    # add solar sensor temperature and date into 1 string
    log_str = ",".join((str(solar), str(temp), f"{year}-{yearday}-{hour}:{minute}:{second}"))
    # write this string to the log.txt file
    with open("log.txt", "a") as f:
      f.write(log_str + "\n")

  def loop(self):
    while True:
      try:
        # garbage collection
        if gc.mem_free() < 102000:
          gc.collect()
        # accept connection
        conn, addr = self.s.accept()
        conn.settimeout(3.0)
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        conn.settimeout(None)
        request = str(request)
        print('Content = %s' % request)
        # send response
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