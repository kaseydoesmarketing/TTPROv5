import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuthContext } from '../contexts/Auth0Context';
import { Button } from './ui/button';
import { 
  LayoutDashboard, 
  TestTube, 
  Youtube, 
  CreditCard, 
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

export function Layout() {
  const { user, logout } = useAuthContext();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'A/B Tests', href: '/ab-tests', icon: TestTube },
    { name: 'Channels', href: '/channels', icon: Youtube },
    { name: 'Billing', href: '/billing', icon: CreditCard },
  ];

  const handleSignOut = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile menu */}
      <div className={cn(
        "fixed inset-0 z-50 bg-background/80 backdrop-blur-sm lg:hidden",
        mobileMenuOpen ? "block" : "hidden"
      )}>
        <div className="fixed inset-y-0 left-0 z-50 w-72 bg-background border-r">
          <div className="flex items-center justify-between p-6">
            <h2 className="text-lg font-semibold">TitleTesterPro</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setMobileMenuOpen(false)}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          <nav className="px-3 pb-4">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    location.pathname === item.href
                      ? "bg-secondary text-secondary-foreground"
                      : "hover:bg-secondary/50"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-50 lg:block lg:w-72 lg:overflow-y-auto lg:bg-background lg:border-r">
        <div className="flex h-16 shrink-0 items-center px-6">
          <h1 className="text-xl font-bold">TitleTesterPro</h1>
        </div>
        <nav className="flex flex-1 flex-col px-3 pb-4">
          <ul role="list" className="flex flex-1 flex-col gap-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.href}>
                  <Link
                    to={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      location.pathname === item.href
                        ? "bg-secondary text-secondary-foreground"
                        : "hover:bg-secondary/50"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 items-center gap-x-4 border-b bg-background px-4 sm:gap-x-6 sm:px-6 lg:px-8">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setMobileMenuOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1 items-center justify-end gap-x-4">
              <div className="flex items-center gap-x-4">
                <span className="text-sm text-muted-foreground">
                  {user?.email}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleSignOut}
                  className="gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="px-4 py-8 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}