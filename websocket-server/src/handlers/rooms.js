'use strict';

const logger = require('../logger');
const { ROOM_JOINS_TOTAL } = require('../metrics');
const { trackRoomPresence, getRoomPresence } = require('../presence');

/**
 * Register room lifecycle event handlers on a connected socket.
 *
 * Events handled:
 *   join_room  - { roomId: string }
 *   leave_room - { roomId: string }
 *
 * @param {import('socket.io').Server} io
 * @param {import('socket.io').Socket} socket
 */
module.exports = function registerRoomHandlers(io, socket) {
  const userId = socket.data.userId;

  socket.on('join_room', async (data, callback) => {
    const roomId = data && data.roomId;

    if (!roomId || typeof roomId !== 'string') {
      logger.warn({ userId, socketId: socket.id }, 'join_room_invalid_payload');
      if (typeof callback === 'function') {
        callback({ success: false, error: 'INVALID_PAYLOAD' });
      }
      return;
    }

    try {
      socket.join(roomId);
      await trackRoomPresence(roomId, userId, 'join');
      const membersOnline = await getRoomPresence(roomId);

      ROOM_JOINS_TOTAL.inc();

      socket.to(roomId).emit('user_joined', {
        roomId,
        userId,
        timestamp: new Date().toISOString(),
      });

      logger.info({ userId, roomId }, 'user_joined_room');

      if (typeof callback === 'function') {
        callback({ success: true, membersOnline });
      }
    } catch (err) {
      logger.error({ userId, roomId, error: err.message }, 'join_room_error');
      if (typeof callback === 'function') {
        callback({ success: false, error: 'JOIN_FAILED' });
      }
    }
  });

  socket.on('leave_room', async (data, callback) => {
    const roomId = data && data.roomId;

    if (!roomId || typeof roomId !== 'string') {
      logger.warn({ userId, socketId: socket.id }, 'leave_room_invalid_payload');
      if (typeof callback === 'function') {
        callback({ success: false, error: 'INVALID_PAYLOAD' });
      }
      return;
    }

    try {
      socket.leave(roomId);
      await trackRoomPresence(roomId, userId, 'leave');

      socket.to(roomId).emit('user_left', {
        roomId,
        userId,
        timestamp: new Date().toISOString(),
      });

      logger.info({ userId, roomId }, 'user_left_room');

      if (typeof callback === 'function') {
        callback({ success: true });
      }
    } catch (err) {
      logger.error({ userId, roomId, error: err.message }, 'leave_room_error');
      if (typeof callback === 'function') {
        callback({ success: false, error: 'LEAVE_FAILED' });
      }
    }
  });
};
