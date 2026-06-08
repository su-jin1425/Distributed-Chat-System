'use strict';

const { redisClient } = require('./redis');
const config = require('./config');
const logger = require('./logger');

/**
 * Mark a user as online and associate their active socket ID.
 * @param {string} userId
 * @param {string} socketId
 */
async function setUserOnline(userId, socketId) {
  const key = `presence:user:${userId}`;
  const payload = JSON.stringify({
    status: 'online',
    socketId,
    lastSeen: new Date().toISOString(),
  });
  await redisClient.setex(key, config.presenceTtlSeconds, payload);
  logger.debug({ userId, socketId }, 'presence_set_online');
}

/**
 * Mark a user as offline. Retains last-seen timestamp for display purposes.
 * @param {string} userId
 */
async function setUserOffline(userId) {
  const key = `presence:user:${userId}`;
  const payload = JSON.stringify({
    status: 'offline',
    lastSeen: new Date().toISOString(),
  });
  await redisClient.setex(key, config.presenceTtlSeconds, payload);
  logger.debug({ userId }, 'presence_set_offline');
}

/**
 * Retrieve the current presence record for a user.
 * Returns { status: 'offline' } if no record exists.
 * @param {string} userId
 * @returns {Promise<object>}
 */
async function getUserPresence(userId) {
  const key = `presence:user:${userId}`;
  const data = await redisClient.get(key);
  if (!data) return { status: 'offline' };
  try {
    return JSON.parse(data);
  } catch {
    return { status: 'offline' };
  }
}

/**
 * Add or remove a user from a room's presence set.
 * @param {string} roomId
 * @param {string} userId
 * @param {'join'|'leave'} action
 */
async function trackRoomPresence(roomId, userId, action) {
  const key = `presence:room:${roomId}`;
  if (action === 'join') {
    await redisClient.sadd(key, userId);
    await redisClient.expire(key, config.presenceTtlSeconds);
  } else {
    await redisClient.srem(key, userId);
  }
}

/**
 * Return all user IDs currently tracked in a room's presence set.
 * @param {string} roomId
 * @returns {Promise<string[]>}
 */
async function getRoomPresence(roomId) {
  const key = `presence:room:${roomId}`;
  return redisClient.smembers(key);
}

module.exports = {
  setUserOnline,
  setUserOffline,
  getUserPresence,
  trackRoomPresence,
  getRoomPresence,
};
