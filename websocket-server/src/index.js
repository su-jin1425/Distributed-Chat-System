import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import client from 'prom-client';
import cors from 'cors';

import { config } from './config.js';
import { pubClient, subClient } from './redis.js';
import { authenticateSocket } from './auth.js';
import { setupChatHandlers } from './handlers/chat.js';
import { setupPresenceHandlers } from './handlers/presence.js';

const app = express();
app.use(cors());

const httpServer = createServer(app);

const io = new Server(httpServer, {
  cors: {
    origin: config.corsOrigins,
    methods: ["GET", "POST"],
    credentials: true,
  },
  adapter: createAdapter(pubClient, subClient),
});

// Prometheus metrics setup
const register = new client.Registry();
if (config.prometheusEnabled) {
  client.collectDefaultMetrics({ register });
  
  const connectedClients = new client.Gauge({
    name: 'websocket_connected_clients_total',
    help: 'Total number of connected clients',
  });
  register.registerMetric(connectedClients);

  io.on('connection', () => {
    connectedClients.inc();
  });

  io.on('disconnect', () => {
    connectedClients.dec();
  });

  app.get('/metrics', async (req, res) => {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  });
}

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Redis subscriber for backend events
const redisSubscriber = subClient.duplicate();
redisSubscriber.subscribe('chat_events', 'notification_events', (err, count) => {
  if (err) {
    console.error('Failed to subscribe to Redis channels:', err);
  } else {
    console.log(`Subscribed to ${count} Redis channels.`);
  }
});

redisSubscriber.on('message', (channel, message) => {
  try {
    const data = JSON.parse(message);
    
    if (channel === 'chat_events') {
      if (data.type === 'message.created') {
        const roomId = data.message.room_id;
        io.to(`room:${roomId}`).emit('message:new', data.message);
      } else if (data.type === 'status.updated') {
        const roomId = data.room_id;
        io.to(`room:${roomId}`).emit('message:status_update', data);
      }
    } else if (channel === 'notification_events') {
      const userId = data.user_id;
      io.to(`user:${userId}`).emit('notification:new', data.notification);
    }
  } catch (error) {
    console.error('Error processing Redis message:', error);
  }
});

io.use(authenticateSocket);

io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id} (User: ${socket.user.id})`);
  
  // Join personal user room for direct notifications
  socket.join(`user:${socket.user.id}`);

  setupChatHandlers(io, socket);
  setupPresenceHandlers(io, socket);

  socket.on('disconnect', (reason) => {
    console.log(`Client disconnected: ${socket.id} - ${reason}`);
  });
});

httpServer.listen(config.port, config.host, () => {
  console.log(`WebSocket server running on http://${config.host}:${config.port}`);
});
