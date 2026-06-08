'use strict';

const pino = require('pino');
const config = require('./config');

const isProduction = config.environment === 'production';

const transport = isProduction
  ? undefined
  : {
      target: 'pino-pretty',
      options: {
        colorize: true,
        translateTime: 'SYS:standard',
        ignore: 'pid,hostname',
      },
    };

const logger = pino({
  level: config.logLevel,
  base: { service: 'websocket-server' },
  timestamp: pino.stdTimeFunctions.isoTime,
  ...(transport ? { transport } : {}),
});

module.exports = logger;
