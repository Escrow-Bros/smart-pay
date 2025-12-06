import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';
import { User, Bot } from 'lucide-react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

// Simple markdown-to-HTML converter for chat messages
function formatMessage(text: string): string {
  return text
    // Bold: **text** or __text__
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    // Italic: *text* or _text_ (but not **text**)
    .replace(/\*([^*]+?)\*/g, '<em>$1</em>')
    .replace(/_([^_]+?)_/g, '<em>$1</em>')
    // Line breaks
    .replace(/\n/g, '<br />')
    // Numbered lists: 1. 2. 3. etc
    .replace(/^(\d+)\.\s+(.+)$/gm, '<li class="ml-4">$2</li>')
    // Wrap consecutive list items in <ol>
    .replace(/(<li class="ml-4">.*<\/li>(\s*<br \/>)*)+/g, (match) => 
      '<ol class="list-decimal ml-4 space-y-1">' + match.replace(/<br \/>/g, '') + '</ol>');
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
          'flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center',
          isUser 
            ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white'
            : 'bg-gradient-to-br from-purple-500 to-pink-600 text-white'
        )}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Message Bubble */}
        <div className="flex flex-col gap-1 min-w-0">
          <div className={cn(
            'rounded-xl sm:rounded-2xl px-3 py-2 sm:px-4 sm:py-3 shadow-lg',
            isUser
              ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white'
              : 'bg-slate-800 text-slate-100 border border-slate-700'
          )}>
            <div className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap break-words prose prose-invert prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-strong:text-cyan-400 prose-strong:font-semibold"
              dangerouslySetInnerHTML={{ __html: formatMessage(content) }}
            />
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
