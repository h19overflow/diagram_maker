import { Link, useLocation } from 'react-router-dom';
import { FileCode2, Library } from 'lucide-react';

export const TopNav = () => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <nav className="border-b-2 border-border bg-card">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <Link 
              to="/app" 
              className="flex items-center gap-2 font-bold text-lg tracking-tight hover:text-primary transition-colors"
            >
              <FileCode2 className="w-6 h-6" />
              <span className="hidden sm:inline">PIXEL.DIAGRAM</span>
            </Link>
            
            <div className="flex gap-1">
              <Link
                to="/app"
                className={`
                  px-4 py-2 border-2 transition-all pixel-shadow
                  ${isActive('/app') 
                    ? 'bg-primary text-primary-foreground border-primary' 
                    : 'bg-card border-border hover:border-primary'
                  }
                `}
              >
                <span className="hidden sm:inline">Chat & Draft</span>
                <span className="sm:hidden">Chat</span>
              </Link>
              
              <Link
                to="/library"
                className={`
                  px-4 py-2 border-2 transition-all pixel-shadow flex items-center gap-2
                  ${isActive('/library') 
                    ? 'bg-primary text-primary-foreground border-primary' 
                    : 'bg-card border-border hover:border-primary'
                  }
                `}
              >
                <Library className="w-4 h-4" />
                <span className="hidden sm:inline">Library</span>
              </Link>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="hidden md:flex items-center gap-2 text-xs text-muted-foreground">
              <div className="w-2 h-2 bg-primary animate-pulse"></div>
              <span>ONLINE</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};
