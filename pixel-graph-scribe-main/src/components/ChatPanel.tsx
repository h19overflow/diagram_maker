import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';

export const ChatPanel = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, artistMode, addMessage, setCurrentGraph } = useStore();
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = {
      id: Math.random().toString(36).substr(2, 9),
      role: 'user' as const,
      text: input.trim(),
      timestamp: new Date(),
    };
    
    addMessage(userMessage);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await api.chat({
        message: userMessage.text,
        artist_mode: artistMode,
      });
      
      const assistantMessage = {
        id: Math.random().toString(36).substr(2, 9),
        role: 'assistant' as const,
        text: response.reply,
        graphs: response.graphs,
        timestamp: new Date(),
      };
      
      addMessage(assistantMessage);
      
      // If there are graphs, set the first one as current
      if (response.graphs && response.graphs.length > 0) {
        setCurrentGraph({ mermaid: response.graphs[0].mermaid });
      }
    } catch (error) {
      toast.error('Failed to send message');
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  return (
    <div className="flex flex-col h-full bg-card border-2 border-border">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-6 max-w-lg px-4 animate-fade-in">
              <div className="w-20 h-20 mx-auto bg-primary/10 border-2 border-primary flex items-center justify-center pixel-corners animate-scale-in">
                <Sparkles className="w-10 h-10 text-primary animate-pulse" />
              </div>
              <div className="space-y-3">
                <h3 className="font-bold text-xl text-primary">Welcome to Diagram Studio</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {artistMode 
                    ? '🎨 Artist Mode is ACTIVE! I\'ll automatically convert your text descriptions into beautiful diagrams.'
                    : '💬 Chat mode active. Toggle Artist Mode above to start generating visual diagrams from text!'}
                </p>
              </div>
              
              <div className="p-4 bg-muted/50 border-2 border-border space-y-3 text-left">
                <h4 className="font-bold text-sm text-primary flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  How it works:
                </h4>
                <ul className="text-xs text-muted-foreground space-y-2">
                  <li className="flex gap-2">
                    <span className="text-primary">→</span>
                    <span>Turn on Artist Mode for automatic diagram generation</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">→</span>
                    <span>Describe your process, system, or concept in plain text</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">→</span>
                    <span>AI converts your text into flowcharts, sequences, and more</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">→</span>
                    <span><strong>Note:</strong> Only text content is processed - no images are used</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}
        
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
          >
            <div
              className={`
                max-w-[80%] p-3 border-2 pixel-shadow hover-scale
                ${msg.role === 'user'
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-muted border-border'
                }
              `}
            >
              <p className="text-sm whitespace-pre-wrap break-words">{msg.text}</p>
              
              {msg.graphs && msg.graphs.length > 0 && (
                <div className="mt-3 space-y-2">
                  {msg.graphs.map((graph, idx) => (
                    <button
                      key={idx}
                      onClick={() => setCurrentGraph({ mermaid: graph.mermaid })}
                      className="w-full p-2 bg-card border border-border hover:border-primary hover:bg-primary/5 transition-all hover-scale text-left text-xs"
                    >
                      📊 {graph.type} diagram (click to view)
                    </button>
                  ))}
                </div>
              )}
              
              <div className="text-xs opacity-60 mt-2">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted border-2 border-border p-3 pixel-shadow">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-primary animate-pulse"></div>
                <div className="w-2 h-2 bg-primary animate-pulse delay-100"></div>
                <div className="w-2 h-2 bg-primary animate-pulse delay-200"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <div className="border-t-2 border-border p-4">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Shift+Enter for new line)"
            className="flex-1 resize-none border-2 focus:border-primary bg-background"
            rows={2}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-4 bg-primary hover:bg-primary/90 border-2 border-primary pixel-shadow"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};
