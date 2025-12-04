import { cn } from '@/lib/utils';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

export default function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div className={cn(
      'flex w-full mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={cn(
        'flex max-w-[80%] gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}>
        {/* Avatar */}
        <div className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold',
          isUser 
            ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white'
            : 'bg-gradient-to-br from-purple-500 to-pink-600 text-white'
        )}>
          {isUser ? '👤' : '🤖'}
        </div>

        {/* Message Bubble */}
        <div className="flex flex-col gap-1">
          <div className={cn(
            'rounded-2xl px-4 py-3 shadow-lg',
            isUser
              ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white'
              : 'bg-slate-800 text-slate-100 border border-slate-700'
          )}>
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
          </div>

          {/* Timestamp */}
          {timestamp && (
            <span className={cn(
              'text-xs text-slate-500 px-2',
              isUser ? 'text-right' : 'text-left'
            )}>
              {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
