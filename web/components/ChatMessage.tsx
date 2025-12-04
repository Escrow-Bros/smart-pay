import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

export default function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isUser = role === 'user';
  const [formattedTime, setFormattedTime] = useState<string>('');

  useEffect(() => {
    if (timestamp) {
      setFormattedTime(timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    }
  }, [timestamp]);

  return (
    <div className={cn(
      'flex w-full mb-3 sm:mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={cn(
        'flex max-w-[90%] sm:max-w-[85%] md:max-w-[80%] gap-2 sm:gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}>
        {/* Avatar */}
        <div className={cn(
          'flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs sm:text-sm font-semibold',
          isUser 
            ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white'
            : 'bg-gradient-to-br from-purple-500 to-pink-600 text-white'
        )}>
          {isUser ? '👤' : '🤖'}
        </div>

        {/* Message Bubble */}
        <div className="flex flex-col gap-1 min-w-0">
          <div className={cn(
            'rounded-xl sm:rounded-2xl px-3 py-2 sm:px-4 sm:py-3 shadow-lg',
            isUser
              ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white'
              : 'bg-slate-800 text-slate-100 border border-slate-700'
          )}>
            <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap break-words">
              {content}
            </p>
          </div>

          {/* Timestamp */}
          {timestamp && formattedTime && (
            <span className={cn(
              'text-xs text-slate-500 px-2',
              isUser ? 'text-right' : 'text-left'
            )}>
              {formattedTime}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
