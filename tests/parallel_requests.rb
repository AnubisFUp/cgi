require 'net/http'
require 'uri'

# Метод для выполнения запроса и получения ответа
def make_request(url, request_number)
  uri = URI.parse(url)
  response = Net::HTTP.get_response(uri)
  puts "#{request_number}: #{response.body}"
rescue => e
  puts "#{request_number}: Error - #{e.message}"
end

# URL для запросов
url = "http://127.0.0.1:8000"
# Количество параллельных запросов
num_requests = 10

threads = []

# Создание потоков для выполнения запросов
num_requests.times do |i|
  threads << Thread.new { make_request(url, i + 1) }
end

# Ожидание завершения всех потоков
threads.each(&:join)

