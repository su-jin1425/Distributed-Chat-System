'use strict';

const jwt = require('jsonwebtoken');
const config = require('../config');
const logger = require('../logger');

/**
 * Socket.IO authentication middleware.
 * Validates a JWT supplied via socket handshake auth or Authorization header.
 * On success, attaches userId and username to socket.data.
 *
 * @param {import('socket.io').Socket} socket
 * @param {function} next
 */
module.exports = function authMiddleware(socket, next) {
  const authToken = socket.handshake.auth && socket.handshake.auth.token;
  const headerValue = socket.handshake.headers && socket.handshake.headers.authorization;
  const headerToken = headerValue ? headerValue.replace(/^Bearer\s+/i, '') : null;

  const token = authToken || headerToken;

  if (!token) {
    logger.warn({ socketId: socket.id }, 'ws_auth_rejected_no_token');
    return next(new Error('AUTHENTICATION_REQUIRED'));
  }

  try {
    const payload = jwt.verify(token, config.jwtSecret, {
      algorithms: [config.jwtAlgorithm],
    });

    socket.data.userId = String(payload.sub);
    socket.data.username = payload.username || String(payload.sub);

    logger.debug({ socketId: socket.id, userId: socket.data.userId }, 'ws_auth_success');
    return next();
  } catch (err) {
    logger.warn(
      { socketId: socket.id, error: err.message },
      'ws_auth_rejected_invalid_token',
    );
    return next(new Error('AUTHENTICATION_FAILED'));
  }
};
