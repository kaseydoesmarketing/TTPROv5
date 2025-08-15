import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

interface LoginPageProps {
  onLogin: () => Promise<void>;
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const handleLogin = async () => {
    try {
      await onLogin();
    } catch (error) {
      console.error('Failed to sign in:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">TitleTesterPro</CardTitle>
          <CardDescription>
            A/B test your YouTube titles to maximize engagement
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center text-sm text-gray-600">
            Sign in with your Auth0 account to get started
          </div>
          
          <Button
            onClick={handleLogin}
            className="w-full"
            size="lg"
          >
            Sign In with Auth0
          </Button>
          
          <div className="text-center text-xs text-gray-500">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </div>
        </CardContent>
      </Card>
    </div>
  );
}