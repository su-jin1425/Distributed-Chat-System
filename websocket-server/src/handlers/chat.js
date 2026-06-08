export const setupChatHandlers = (io, socket) => {
  // Join a specific room
  socket.on('room:join', (roomId, callback) => {
    socket.join(`room:${roomId}`);
    if (typeof callback === 'function') {
      callback({ status: 'success', roomId });
    }
    // Optionally notify others in room
    socket.to(`room:${roomId}`).emit('room:user_joined', {
      roomId,
      userId: socket.user.id
    });
  });

  // Leave a specific room
  socket.on('room:leave', (roomId, callback) => {
    socket.leave(`room:${roomId}`);
    if (typeof callback === 'function') {
      callback({ status: 'success', roomId });
    }
    socket.to(`room:${roomId}`).emit('room:user_left', {
      roomId,
      userId: socket.user.id
    });
  });

  // Typing indicator
  socket.on('message:typing', (roomId) => {
    socket.to(`room:${roomId}`).emit('message:typing', {
      roomId,
      userId: socket.user.id
    });
  });

  // Client-to-client message read receipts
  socket.on('message:read', (messageId, roomId) => {
    // Broadcast read receipt to room
    socket.to(`room:${roomId}`).emit('message:status_update', {
      messageId,
      roomId,
      userId: socket.user.id,
      status: 'read'
    });
  });
};
