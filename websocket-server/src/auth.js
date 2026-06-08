import jwt from 'jsonwebtoken';
import { config } from './config.js';

export const authenticateSocket = (socket, next) => {
  const token = socket.handshake.auth?.token || socket.handshake.query?.token;

  if (!token) {
    return next(new Error('Authentication error: Token missing'));
  }

  try {
    const decoded = jwt.verify(token, config.jwtSecret, {
      algorithms: [config.jwtAlgorithm],
    });
    
    // Extract subject (user ID) from token
    if (!decoded.sub) {
      return next(new Error('Authentication error: Invalid token payload'));
    }
    
    socket.user = { id: decoded.sub };
    next();
  } catch (err) {
    next(new Error('Authentication error: Invalid or expired token'));
  }
};
