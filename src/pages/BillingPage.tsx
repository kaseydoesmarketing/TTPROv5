import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { Check, CreditCard } from 'lucide-react';

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    priceId: null,
    features: [
      '1 YouTube channel',
      '5 A/B tests per month',
      'Basic analytics',
      'Email support'
    ]
  },
  {
    name: 'Pro',
    price: '$29',
    priceId: 'price_pro_monthly',
    features: [
      'Unlimited YouTube channels',
      'Unlimited A/B tests',
      'Advanced analytics',
      'Priority support',
      'API access'
    ],
    popular: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    priceId: null,
    features: [
      'Everything in Pro',
      'Custom integrations',
      'Dedicated account manager',
      'SLA guarantee',
      'White-label options'
    ]
  }
];

export function BillingPage() {
  const [billingStatus, setBillingStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBillingStatus();
  }, []);

  const loadBillingStatus = async () => {
    try {
      setLoading(true);
      const status = await apiClient.getBillingStatus();
      setBillingStatus(status);
    } catch (error) {
      console.error('Failed to load billing status:', error);
      // Don't show error toast for billing - it's optional
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (priceId: string | null) => {
    if (!priceId) {
      toast.info('Contact sales for Enterprise pricing');
      return;
    }

    try {
      const { url } = await apiClient.createCheckoutSession(priceId);
      window.location.href = url;
    } catch (error) {
      toast.error('Failed to start checkout process');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const currentPlan = billingStatus?.plan || 'free';

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
        <p className="text-muted-foreground mt-2">
          Manage your subscription and billing details
        </p>
      </div>

      {billingStatus?.subscription && (
        <Card>
          <CardHeader>
            <CardTitle>Current Subscription</CardTitle>
            <CardDescription>
              You are currently on the {billingStatus.plan} plan
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Status</span>
                <span className="capitalize">{billingStatus.subscription.status}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Next billing date</span>
                <span>
                  {new Date(billingStatus.subscription.current_period_end).toLocaleDateString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div>
        <h2 className="text-2xl font-semibold mb-6">Choose Your Plan</h2>
        <div className="grid gap-6 md:grid-cols-3">
          {PLANS.map((plan) => (
            <Card 
              key={plan.name} 
              className={plan.popular ? 'border-primary shadow-lg' : ''}
            >
              {plan.popular && (
                <div className="bg-primary text-primary-foreground text-center py-2 text-sm font-medium">
                  Most Popular
                </div>
              )}
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <div className="mt-4">
                  <span className="text-3xl font-bold">{plan.price}</span>
                  {plan.price !== 'Custom' && <span className="text-muted-foreground">/month</span>}
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  className="w-full"
                  variant={plan.popular ? 'default' : 'outline'}
                  disabled={currentPlan === plan.name.toLowerCase()}
                  onClick={() => handleSubscribe(plan.priceId)}
                >
                  {currentPlan === plan.name.toLowerCase() 
                    ? 'Current Plan' 
                    : plan.priceId 
                      ? 'Subscribe' 
                      : 'Contact Sales'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Payment Methods</CardTitle>
          <CardDescription>
            Manage your payment methods and billing information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" className="gap-2">
            <CreditCard className="h-4 w-4" />
            Manage Payment Methods
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}