import { Redis } from 'ioredis';
import { config } from './config.js';

export const pubClient = new Redis(config.redisUrl);
export const subClient = pubClient.duplicate();
export const stateClient = pubClient.duplicate();

pubClient.on('error', (err) => console.error('Redis Pub Client Error:', err));
subClient.on('error', (err) => console.error('Redis Sub Client Error:', err));
stateClient.on('error', (err) => console.error('Redis State Client Error:', err));

export const RedisKeys = {
  userPresence: (userId) => `presence:user:${userId}`,
  roomPresence: (roomId) => `presence:room:${roomId}`,
};
