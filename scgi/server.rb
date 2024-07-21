require 'socket'

server = TCPServer.new(5050)

loop do
  client = server.accept
  puts "Client connected"

  Thread.new do
    while (message = client.gets)
      puts "Received: #{message}"
    end
    client.close
    puts "Client disconnected"
  end
end

