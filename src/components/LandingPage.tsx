import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { CheckCircle, Play, BarChart3, Clock, Zap } from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
}

export function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Play className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">TitleTesterPro</span>
          </div>
          <Button onClick={onGetStarted} variant="outline">
            Sign In
          </Button>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <Badge variant="secondary" className="mb-4">
          🚀 MVP Launch - Limited Beta
        </Badge>
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          A/B Test Your YouTube Titles
          <span className="text-blue-600 block">Maximize Engagement</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Stop guessing which titles work. Use data-driven A/B testing to optimize your YouTube titles 
          and increase views, engagement, and subscriber growth.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={onGetStarted} size="lg" className="text-lg px-8 py-3">
            Start Testing Free
          </Button>
          <Button variant="outline" size="lg" className="text-lg px-8 py-3">
            Watch Demo
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Why TitleTesterPro?
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <BarChart3 className="h-12 w-12 text-blue-600 mb-4" />
              <CardTitle>Data-Driven Results</CardTitle>
              <CardDescription>
                Get real metrics on views, engagement, and performance for each title variant
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card>
            <CardHeader>
              <Clock className="h-12 w-12 text-green-600 mb-4" />
              <CardTitle>Automated Testing</CardTitle>
              <CardDescription>
                Set rotation schedules and let our system automatically test your title variants
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card>
            <CardHeader>
              <Zap className="h-12 w-12 text-purple-600 mb-4" />
              <CardTitle>Easy Setup</CardTitle>
              <CardDescription>
                Connect your YouTube channel and start testing in minutes, no technical skills required
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-4 py-16 bg-white rounded-lg mx-4">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          How It Works
        </h2>
        <div className="grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-600">1</span>
            </div>
            <h3 className="font-semibold mb-2">Connect YouTube</h3>
            <p className="text-gray-600">Sign in with Google and connect your YouTube channel</p>
          </div>
          
          <div className="text-center">
            <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-green-600">2</span>
            </div>
            <h3 className="font-semibold mb-2">Create Variants</h3>
            <p className="text-gray-600">Add 2-10 different title options for your video</p>
          </div>
          
          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-purple-600">3</span>
            </div>
            <h3 className="font-semibold mb-2">Set Schedule</h3>
            <p className="text-gray-600">Choose rotation timing and test duration</p>
          </div>
          
          <div className="text-center">
            <div className="bg-orange-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-orange-600">4</span>
            </div>
            <h3 className="font-semibold mb-2">Analyze Results</h3>
            <p className="text-gray-600">Review performance data and pick the winning title</p>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Simple Pricing
        </h2>
        <div className="max-w-md mx-auto">
          <Card className="border-2 border-blue-500">
            <CardHeader className="text-center">
              <Badge variant="default" className="w-fit mx-auto mb-2">
                MVP Launch Special
              </Badge>
              <CardTitle className="text-2xl">Free Beta</CardTitle>
              <CardDescription>
                Full access during beta period
              </CardDescription>
              <div className="text-4xl font-bold text-blue-600 mt-4">
                $0<span className="text-lg text-gray-500">/month</span>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  Unlimited A/B tests
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  Up to 10 title variants
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  Automated scheduling
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  Performance analytics
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                  Email support
                </li>
              </ul>
              <Button onClick={onGetStarted} className="w-full mt-6" size="lg">
                Start Free Beta
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* FAQ */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Frequently Asked Questions
        </h2>
        <div className="max-w-3xl mx-auto space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">How does A/B testing work for YouTube titles?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                We automatically rotate between your title variants at scheduled intervals, 
                tracking performance metrics like views, engagement, and click-through rates 
                to determine which title performs best.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Is this compliant with YouTube's terms of service?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Yes, we use YouTube's official API and follow all guidelines. Title changes 
                are made through proper channels and respect all rate limits and quotas.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">How long should I run a test?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                We recommend running tests for at least 24-48 hours to gather sufficient data. 
                The optimal duration depends on your video's typical view pattern and audience.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Play className="h-6 w-6" />
              <span className="text-xl font-bold">TitleTesterPro</span>
            </div>
            <div className="flex space-x-6 text-sm">
              <a href="#" className="hover:text-blue-400">Privacy Policy</a>
              <a href="#" className="hover:text-blue-400">Terms of Service</a>
              <a href="#" className="hover:text-blue-400">Support</a>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            © 2025 TitleTesterPro. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
