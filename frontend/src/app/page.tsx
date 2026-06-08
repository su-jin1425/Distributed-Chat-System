'use client';

import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export default function Home() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // We would normally pass the auth token here
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001';
    
    // We need a dummy token for now since backend auth is enforced
    // In real app, we get this from login
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    
    if (token) {
      const socketInstance = io(wsUrl, {
        auth: { token },
      });

      socketInstance.on('connect', () => {
        setIsConnected(true);
      });

      socketInstance.on('disconnect', () => {
        setIsConnected(false);
      });

      setSocket(socketInstance);

      return () => {
        socketInstance.disconnect();
      };
    }
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">Distributed Chat System</h1>
      <div className="p-6 bg-card rounded-xl shadow-lg border border-border">
        <h2 className="text-2xl mb-4 font-semibold">System Status</h2>
        <div className="flex items-center space-x-2">
          <span className="text-muted-foreground">WebSocket Connection:</span>
          <span className={`font-bold ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <p className="mt-6 text-sm text-muted-foreground max-w-md text-center">
          Please login to connect to the WebSocket server. The backend infrastructure is ready.
        </p>
      </div>
    </main>
  );
}
