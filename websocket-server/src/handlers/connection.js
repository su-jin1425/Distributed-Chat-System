'use strict';

const logger = require('../logger');
const { ACTIVE_WS_CONNECTIONS } = require('../metrics');
const { setUserOnline, setUserOffline } = require('../presence');
const registerRoomHandlers = require('./rooms');
const registerMessageHandlers = require('./messages');
const registerPresenceHandlers = require('./presenceHandlers');

/**
 * Register the top-level connection handler on the Socket.IO server.
 * Each inbound authenticated connection is instrumented, tracked in presence,
 * and receives all domain-specific sub-handlers.
 *
 * @param {import('socket.io').Server} io
 */
module.exports = function registerConnectionHandlers(io) {
  io.on('connection', async (socket) => {
    const userId = socket.data.userId;

    try {
      ACTIVE_WS_CONNECTIONS.inc();
      await setUserOnline(userId, socket.id);
      logger.info({ userId, socketId: socket.id }, 'client_connected');

      socket.broadcast.emit('presence_updated', { userId, status: 'online' });
    } catch (err) {
      logger.error(
        { userId, socketId: socket.id, error: err.message },
        'connection_setup_error',
      );
    }

    registerRoomHandlers(io, socket);
    registerMessageHandlers(io, socket);
    registerPresenceHandlers(io, socket);

    socket.on('disconnect', async (reason) => {
      try {
        ACTIVE_WS_CONNECTIONS.dec();
        await setUserOffline(userId);
        logger.info({ userId, socketId: socket.id, reason }, 'client_disconnected');
        socket.broadcast.emit('presence_updated', { userId, status: 'offline' });
      } catch (err) {
        logger.error(
          { userId, socketId: socket.id, error: err.message },
          'disconnect_handler_error',
        );
      }
    });

    socket.on('error', (err) => {
      logger.error({ userId, socketId: socket.id, error: err.message }, 'socket_error');
    });
  });
};
