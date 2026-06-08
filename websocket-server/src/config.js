import dotenv from 'dotenv';

dotenv.config({ path: '../.env' });

export const config = {
  port: process.env.WEBSOCKET_PORT || 8001,
  host: process.env.WEBSOCKET_HOST || '0.0.0.0',
  corsOrigins: process.env.WEBSOCKET_CORS_ORIGINS 
    ? process.env.WEBSOCKET_CORS_ORIGINS.split(',') 
    : ['http://localhost:3000'],
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379/0',
  jwtSecret: process.env.SECRET_KEY || 'dev-secret-key-change-in-production',
  jwtAlgorithm: process.env.ALGORITHM || 'HS256',
  prometheusEnabled: process.env.PROMETHEUS_ENABLED === 'true',
};
