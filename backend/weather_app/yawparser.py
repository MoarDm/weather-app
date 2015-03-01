import httplib
import xml.sax

YANDEX_WEATHER_HOST = 'export.yandex.ru'
YANDEX_WEATHER_PATH = '/weather-ng/forecasts/{city_id}.xml'

WEATHER_STATE_MAP = {
	'weather_type':'weatherType',
	'wind_direction':'windDirection',
	'wind_speed':'windVelocity',
	'temperature':'temperature'
}

class yandex_weather_parser_handler(xml.sax.ContentHandler):
	def __init__(self):
		self.weather_state = {}
		self.weather_state['weatherType'] = ''
		self.weather_state['windDirection'] = ''
		self.weather_state['windVelocity'] = ''
		self.weather_state['temperature'] = ''

		self.elem_stack = []

	def startElement(self, name, attrs):
		self.elem_stack = self.elem_stack + [name]

	def endElement(self, name):
		self.elem_stack = self.elem_stack[:-1]

	def characters(self,content):
		if 'fact' in self.elem_stack:
			if self.elem_stack[-1] in WEATHER_STATE_MAP:
				self.weather_state[WEATHER_STATE_MAP[self.elem_stack[-1]]] += content

	def endDocument(self):
		self.weather_state['temperature'] = float(self.weather_state['temperature'])
		self.weather_state['windDirection'] = self.weather_state['windDirection'].upper()

def parse_weather_info(city_id,prepared_connection=None):
	connection = prepared_connection
	if connection == None:
		connection = httplib.HTTPConnection(YANDEX_WEATHER_HOST)

	path = YANDEX_WEATHER_PATH.format(city_id=city_id)
	connection.request('GET',path)
	response = connection.getresponse()

	if response.status != httplib.OK:
		connection.close( )
		return None

	parser = xml.sax.make_parser()
	sax_handler = yandex_weather_parser_handler( )
	parser.setContentHandler(sax_handler)
	parser.parse(response)

	response.close( )

	if prepared_connection == None:
		connection.close( )

	return sax_handler.weather_state