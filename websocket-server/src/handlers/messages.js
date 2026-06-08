'use strict';

const logger = require('../logger');
const { MESSAGES_TOTAL, MESSAGE_LATENCY, PUBSUB_EVENTS } = require('../metrics');
const { redisClient } = require('../redis');

/**
 * Register message event handlers on a connected socket.
 *
 * Events handled:
 *   send_message  - { roomId, content, messageType?, tempId? }
 *   message_read  - { messageId, roomId }
 *
 * @param {import('socket.io').Server} io
 * @param {import('socket.io').Socket} socket
 */
module.exports = function registerMessageHandlers(io, socket) {
  const userId = socket.data.userId;

  socket.on('send_message', async (data, callback) => {
    const startMs = Date.now();
    const { roomId, content, messageType = 'text', tempId } = data || {};

    if (!roomId || typeof roomId !== 'string' || !content || typeof content !== 'string') {
      logger.warn({ userId, socketId: socket.id }, 'send_message_invalid_payload');
      if (typeof callback === 'function') {
        callback({ success: false, error: 'INVALID_PAYLOAD' });
      }
      return;
    }

    const trimmedContent = content.trim();
    if (!trimmedContent) {
      if (typeof callback === 'function') {
        callback({ success: false, error: 'INVALID_PAYLOAD' });
      }
      return;
    }

    try {
      const event = {
        type: 'chat:message',
        roomId,
        senderId: userId,
        content: trimmedContent,
        messageType,
        tempId: tempId || null,
        timestamp: new Date().toISOString(),
      };

      await redisClient.publish('chat:messages', JSON.stringify(event));

      io.to(roomId).emit('message_received', event);

      const latencySeconds = (Date.now() - startMs) / 1000;
      MESSAGE_LATENCY.observe(latencySeconds);
      MESSAGES_TOTAL.inc({ event_type: 'send_message' });
      PUBSUB_EVENTS.inc({ event_type: 'publish' });

      logger.info(
        { userId, roomId, latencyMs: Date.now() - startMs, messageType },
        'message_sent',
      );

      if (typeof callback === 'function') {
        callback({ success: true, timestamp: event.timestamp });
      }
    } catch (err) {
      logger.error({ userId, roomId, error: err.message }, 'send_message_error');
      if (typeof callback === 'function') {
        callback({ success: false, error: 'SEND_FAILED' });
      }
    }
  });

  socket.on('message_read', async (data, callback) => {
    const { messageId, roomId } = data || {};

    if (!messageId || !roomId) {
      if (typeof callback === 'function') {
        callback({ success: false, error: 'INVALID_PAYLOAD' });
      }
      return;
    }

    try {
      socket.to(roomId).emit('message_read_ack', {
        messageId,
        readBy: userId,
        timestamp: new Date().toISOString(),
      });

      MESSAGES_TOTAL.inc({ event_type: 'message_read' });

      logger.debug({ userId, roomId, messageId }, 'message_read_ack_sent');

      if (typeof callback === 'function') {
        callback({ success: true });
      }
    } catch (err) {
      logger.error({ userId, error: err.message }, 'message_read_error');
      if (typeof callback === 'function') {
        callback({ success: false, error: 'READ_ACK_FAILED' });
      }
    }
  });
};
