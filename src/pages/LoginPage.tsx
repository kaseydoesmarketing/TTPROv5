import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

export function LoginPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated, loginWithRedirect } = useAuth0();

  useEffect(() => {
    if (isAuthenticated && user) {
      navigate('/dashboard');
    }
  }, [user, isAuthenticated, navigate]);

  const handleAuth0SignIn = async () => {
    try {
      await loginWithRedirect();
    } catch (error) {
      console.error('Sign in error:', error);
      toast.error('Failed to sign in. Please try again.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Welcome to TitleTesterPro</CardTitle>
          <CardDescription>
            Optimize your YouTube titles with A/B testing
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleAuth0SignIn}
            className="w-full"
            size="lg"
            variant="default"
          >
            Sign in with Auth0
          </Button>
          <p className="mt-4 text-center text-sm text-muted-foreground">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </p>
        </CardContent>
      </Card>
    </div>
  );
}