import { stateClient, RedisKeys } from '../redis.js';

export const setupPresenceHandlers = (io, socket) => {
  const userId = socket.user.id;
  const presenceKey = RedisKeys.userPresence(userId);

  // Set user as online
  stateClient.set(presenceKey, 'online', 'EX', 300); // 5 minute TTL
  
  // Heartbeat to keep presence active
  socket.on('presence:heartbeat', () => {
    stateClient.set(presenceKey, 'online', 'EX', 300);
  });

  // Broadcast presence updates to friends/rooms could go here
  // For simplicity, broadcast to all for now
  io.emit('user:presence', {
    userId,
    status: 'online'
  });

  socket.on('disconnect', async () => {
    // Check if user has other active sockets (multi-device)
    const sockets = await io.in(`user:${userId}`).fetchSockets();
    if (sockets.length === 0) {
      await stateClient.del(presenceKey);
      io.emit('user:presence', {
        userId,
        status: 'offline'
      });
    }
  });
};
