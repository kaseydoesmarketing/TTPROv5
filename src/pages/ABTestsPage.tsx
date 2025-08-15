import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-auth0';
import { toast } from 'sonner';
import { Plus, Play, Pause, Trash2 } from 'lucide-react';

export function ABTestsPage() {
  const [tests, setTests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTests();
  }, []);

  const loadTests = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getABTests();
      setTests(data || []);
    } catch (error) {
      console.error('Failed to load tests:', error);
      toast.error('Failed to load A/B tests');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTest = () => {
    toast.info('Test creation form would open here');
    // In a real app, this would open a modal or navigate to create page
  };

  const handleToggleTest = async (testId: string, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'active' ? 'paused' : 'active';
      await apiClient.updateABTest(testId, { status: newStatus });
      toast.success(`Test ${newStatus === 'active' ? 'activated' : 'paused'}`);
      loadTests();
    } catch (error) {
      toast.error('Failed to update test status');
    }
  };

  const handleDeleteTest = async (testId: string) => {
    if (!confirm('Are you sure you want to delete this test?')) return;
    
    try {
      await apiClient.deleteABTest(testId);
      toast.success('Test deleted successfully');
      loadTests();
    } catch (error) {
      toast.error('Failed to delete test');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">A/B Tests</h1>
          <p className="text-muted-foreground mt-2">
            Create and manage your YouTube title experiments
          </p>
        </div>
        <Button onClick={handleCreateTest} className="gap-2">
          <Plus className="h-4 w-4" />
          Create Test
        </Button>
      </div>

      {tests.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <TestTube className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No tests yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Create your first A/B test to start optimizing your YouTube titles
            </p>
            <Button onClick={handleCreateTest}>
              Create Your First Test
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {tests.map((test) => (
            <Card key={test.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{test.video_title}</CardTitle>
                    <CardDescription>
                      Testing {test.variants?.length || 0} variations
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleTest(test.id, test.status)}
                    >
                      {test.status === 'active' ? (
                        <><Pause className="h-4 w-4 mr-1" /> Pause</>
                      ) : (
                        <><Play className="h-4 w-4 mr-1" /> Resume</>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteTest(test.id)}
                      className="text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Status</span>
                    <span className={`font-medium ${
                      test.status === 'active' ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {test.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Created</span>
                    <span>{new Date(test.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}