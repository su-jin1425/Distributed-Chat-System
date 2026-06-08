'use strict';

const client = require('prom-client');

const { register } = client;

client.collectDefaultMetrics({ register });

const ACTIVE_WS_CONNECTIONS = new client.Gauge({
  name: 'ws_active_connections',
  help: 'Active WebSocket connections',
  registers: [register],
});

const MESSAGES_TOTAL = new client.Counter({
  name: 'ws_messages_total',
  help: 'Total WebSocket messages processed',
  labelNames: ['event_type'],
  registers: [register],
});

const MESSAGE_LATENCY = new client.Histogram({
  name: 'ws_message_latency_seconds',
  help: 'Message processing latency in seconds',
  buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1],
  registers: [register],
});

const PUBSUB_EVENTS = new client.Counter({
  name: 'ws_pubsub_events_total',
  help: 'Total Redis Pub/Sub events processed',
  labelNames: ['event_type'],
  registers: [register],
});

const ROOM_JOINS_TOTAL = new client.Counter({
  name: 'ws_room_joins_total',
  help: 'Total room join events',
  registers: [register],
});

module.exports = {
  register,
  ACTIVE_WS_CONNECTIONS,
  MESSAGES_TOTAL,
  MESSAGE_LATENCY,
  PUBSUB_EVENTS,
  ROOM_JOINS_TOTAL,
};
