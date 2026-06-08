'use strict';

const logger = require('../logger');

/**
 * Register typing indicator event handlers on a connected socket.
 *
 * Events handled:
 *   typing_start - { roomId: string }
 *   typing_stop  - { roomId: string }
 *
 * @param {import('socket.io').Server} io
 * @param {import('socket.io').Socket} socket
 */
module.exports = function registerPresenceHandlers(io, socket) {
  const userId = socket.data.userId;

  socket.on('typing_start', (data) => {
    const roomId = data && data.roomId;
    if (!roomId || typeof roomId !== 'string') {
      logger.warn({ userId, socketId: socket.id }, 'typing_start_invalid_payload');
      return;
    }
    socket.to(roomId).emit('typing_indicator', { userId, roomId, isTyping: true });
    logger.debug({ userId, roomId }, 'typing_start');
  });

  socket.on('typing_stop', (data) => {
    const roomId = data && data.roomId;
    if (!roomId || typeof roomId !== 'string') {
      logger.warn({ userId, socketId: socket.id }, 'typing_stop_invalid_payload');
      return;
    }
    socket.to(roomId).emit('typing_indicator', { userId, roomId, isTyping: false });
    logger.debug({ userId, roomId }, 'typing_stop');
  });
};
