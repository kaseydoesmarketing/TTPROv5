console.log("Using mock Firebase auth for development");

export const auth = {
  currentUser: null,
  onAuthStateChanged: (callback: (user: any) => void) => {
    setTimeout(() => callback(null), 100);
    return () => {}; // unsubscribe function
  },
  signInWithPopup: async () => {
    throw new Error("Mock auth - use development login");
  },
  signOut: async () => {
    console.log("Mock sign out");
  }
};

const app = {
  name: 'mock-app',
  options: {}
};

export default app;
