'use strict';

const fastify = require('fastify')({
  logger: true
})

// Declare a route
fastify.get('/', function (request, reply) {
  reply.send('https://t.me/mp_pro_bot')
})

// Run the server
fastify.listen({ port: 3000, host: '127.0.0.1' }, function (err, address) {
  if (err) {
    fastify.log.error(err)
    process.exit(1)
  }
  // Server is now listening on ${address}
})